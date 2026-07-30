#!/usr/bin/env python3
"""Cross-platform project checks with explicit code trust and a minimized environment."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys

from harnesslib.guardrails import GuardrailError, load_json_object, sanitize_environment


ROOT = Path(__file__).resolve().parents[1]
SAFE = ROOT / "scripts" / "safe_exec.py"


def manifest() -> dict:
    return load_json_object(ROOT / "harness.json")


def policy() -> dict:
    return load_json_object(ROOT / "security-policy.json")


def limits() -> dict[str, int]:
    configured = manifest().get("execution_limits", {})
    return {
        "default_command_timeout_seconds": int(configured.get("default_command_timeout_seconds", 300)),
        "kill_grace_seconds": int(configured.get("kill_grace_seconds", 5)),
        "failure_tail_lines": int(configured.get("failure_tail_lines", 120)),
        "max_output_buffer_bytes": int(configured.get("max_output_buffer_bytes", 262144)),
    }


def package_projects() -> list[tuple[Path, dict[str, str]]]:
    """Return root and immediate-child npm projects in deterministic order."""
    manifests = [ROOT / "package.json", *sorted(ROOT.glob("*/package.json"))]
    projects: list[tuple[Path, dict[str, str]]] = []
    for package_path in manifests:
        if not package_path.is_file() or "node_modules" in package_path.parts:
            continue
        try:
            value = json.loads(package_path.read_text(encoding="utf-8"))
            scripts = value.get("scripts", {})
        except (OSError, ValueError, TypeError):
            continue
        if isinstance(scripts, dict):
            projects.append((package_path.parent, scripts))
    return projects


def npm_executable() -> str | None:
    return shutil.which("npm.cmd") or shutil.which("npm") if os.name == "nt" else shutil.which("npm")


def node_executable() -> str | None:
    return shutil.which("node.exe") or shutil.which("node") if os.name == "nt" else shutil.which("node")


def npm_command(project: Path, *arguments: str) -> list[str]:
    npm = npm_executable()
    if npm is None:
        raise RuntimeError("npm unavailable")
    relative = project.relative_to(ROOT)
    if relative == Path("."):
        return [npm, *arguments]
    return [npm, "--prefix", str(relative), *arguments]


def command_environment(allow_secret_env: bool) -> dict[str, str]:
    configured = policy()["execution"]
    return sanitize_environment(
        os.environ,
        configured["allowed_environment"],
        configured["secret_name_pattern"],
        allow_secret_names=allow_secret_env,
    )


def run(
    label: str,
    command: list[str],
    timeout: int,
    *,
    allow_secret_env: bool = False,
) -> int:
    config = limits()
    environment = command_environment(allow_secret_env)
    return subprocess.run(
        [
            sys.executable,
            str(SAFE),
            "--label",
            label,
            "--timeout",
            str(timeout),
            "--grace",
            str(config["kill_grace_seconds"]),
            "--tail-lines",
            str(config["failure_tail_lines"]),
            "--max-buffer-bytes",
            str(config["max_output_buffer_bytes"]),
            "--",
            *command,
        ],
        cwd=ROOT,
        env=environment,
        check=False,
    ).returncode


def override(name: str) -> list[str] | None:
    raw = os.environ.get(name)
    return shlex.split(raw, posix=os.name != "nt") if raw else None


def trust_granted(cli_value: bool) -> bool:
    return cli_value or os.environ.get("HARNESS_TRUST_PROJECT_CODE") == "1"


def blocked_project_commands(labels: list[str], trusted: bool) -> tuple[int, int] | None:
    if labels and not trusted:
        for label in labels:
            print(f"INCOMPLETE {label}: project-owned code execution requires --trust-project-code")
        return 0, len(labels)
    return None


def run_npm_scripts(
    script_names: tuple[str, ...],
    *,
    trusted: bool,
    allow_secret_env: bool,
) -> tuple[int, int]:
    candidates: list[tuple[Path, str]] = []
    for project, scripts in package_projects():
        candidates.extend((project, name) for name in script_names if name in scripts)
    blocked = blocked_project_commands(
        [f"npm {project.relative_to(ROOT)} {name}" for project, name in candidates],
        trusted,
    )
    if blocked:
        return blocked

    ran = incomplete = 0
    for project, script_name in candidates:
        label = f"npm {project.relative_to(ROOT)} {script_name}"
        if npm_executable() is None:
            print(f"INCOMPLETE {label}: npm unavailable")
            incomplete += 1
            continue
        ran += 1
        if run(
            label,
            npm_command(project, "run", script_name),
            limits()["default_command_timeout_seconds"],
            allow_secret_env=allow_secret_env,
        ):
            return ran, -1
    return ran, incomplete


def check_test(*, trusted: bool, allow_secret_env: bool) -> tuple[int, int]:
    custom = override("HARNESS_TEST_COMMAND")
    if custom:
        blocked = blocked_project_commands(["custom project tests"], trusted)
        if blocked:
            return blocked
        return (
            (1, 0)
            if run(
                "custom project tests",
                custom,
                limits()["default_command_timeout_seconds"],
                allow_secret_env=allow_secret_env,
            )
            == 0
            else (1, -1)
        )

    filters = override("HARNESS_NPM_TEST_FILTERS")
    if filters:
        candidates = [
            (project, scripts)
            for project, scripts in package_projects()
            if "test" in scripts
        ]
        blocked = blocked_project_commands(
            [f"npm {project.relative_to(ROOT)} filtered tests" for project, _ in candidates],
            trusted,
        )
        if blocked:
            return blocked
        ran = incomplete = 0
        for project, _scripts in candidates:
            label = f"npm {project.relative_to(ROOT)} filtered tests"
            if npm_executable() is None:
                print(f"INCOMPLETE {label}: npm unavailable")
                incomplete += 1
                continue
            ran += 1
            if run(
                label,
                npm_command(project, "test", "--", *filters),
                limits()["default_command_timeout_seconds"],
                allow_secret_env=allow_secret_env,
            ):
                return ran, -1
    else:
        ran, incomplete = run_npm_scripts(
            ("test",),
            trusted=trusted,
            allow_secret_env=allow_secret_env,
        )
    if incomplete < 0:
        return ran, incomplete

    python_project = (ROOT / "pyproject.toml").is_file() or (ROOT / "requirements.txt").is_file()
    tests = (ROOT / "tests").is_dir() or (ROOT / "test").is_dir()
    if python_project and tests:
        blocked = blocked_project_commands(["pytest"], trusted)
        if blocked:
            return ran + blocked[0], incomplete + blocked[1]
        if shutil.which("pytest"):
            ran += 1
            if run(
                "pytest",
                ["pytest"],
                limits()["default_command_timeout_seconds"],
                allow_secret_env=allow_secret_env,
            ):
                return ran, -1
        else:
            print("INCOMPLETE pytest: test tree detected but pytest unavailable")
            incomplete += 1
    return ran, incomplete


def check_lint(*, trusted: bool, allow_secret_env: bool) -> tuple[int, int]:
    custom = override("HARNESS_LINT_COMMAND")
    if custom:
        blocked = blocked_project_commands(["custom project lint"], trusted)
        if blocked:
            return blocked
        return (
            (1, 0)
            if run(
                "custom project lint",
                custom,
                limits()["default_command_timeout_seconds"],
                allow_secret_env=allow_secret_env,
            )
            == 0
            else (1, -1)
        )

    ran, incomplete = run_npm_scripts(
        ("lint", "typecheck"),
        trusted=trusted,
        allow_secret_env=allow_secret_env,
    )
    if incomplete < 0:
        return ran, incomplete
    python_project = (ROOT / "pyproject.toml").is_file() or (ROOT / "setup.cfg").is_file()
    if python_project:
        if shutil.which("ruff"):
            ran += 1
            if run(
                "ruff check",
                ["ruff", "check", "."],
                limits()["default_command_timeout_seconds"],
            ):
                return ran, -1
        else:
            print("INCOMPLETE Ruff: Python lint configuration detected but Ruff unavailable")
            incomplete += 1
    return ran, incomplete


def check_build(*, trusted: bool, allow_secret_env: bool) -> tuple[int, int]:
    custom = override("HARNESS_BUILD_COMMAND")
    if custom:
        blocked = blocked_project_commands(["custom project build"], trusted)
        if blocked:
            return blocked
        return (
            (1, 0)
            if run(
                "custom project build",
                custom,
                limits()["default_command_timeout_seconds"],
                allow_secret_env=allow_secret_env,
            )
            == 0
            else (1, -1)
        )
    return run_npm_scripts(
        ("build",),
        trusted=trusted,
        allow_secret_env=allow_secret_env,
    )


def check_security(*, external: bool) -> tuple[int, int]:
    command = [
        sys.executable,
        "-B",
        str(ROOT / "scripts" / "security_assurance.py"),
        "--root",
        str(ROOT),
        "--profile",
        "ci",
    ]
    if external:
        command.append("--external")
    code = run("security assurance", command, limits()["default_command_timeout_seconds"])
    if code == 0:
        return 1, 0
    if code == 3:
        return 1, 1
    return 1, -1


def check_ui(*, release: bool) -> tuple[int, int]:
    command = [
        sys.executable,
        "-B",
        str(ROOT / "scripts" / "ui_quality.py"),
        "--root",
        str(ROOT),
        "--profile",
        "release" if release else "ci",
    ]
    code = run("UI quality assurance", command, limits()["default_command_timeout_seconds"])
    if code == 0:
        return 1, 0
    if code == 3:
        return 1, 1
    return 1, -1


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("mode", choices=("test", "lint", "build", "security", "ui"))
    result.add_argument("--trust-project-code", action="store_true")
    result.add_argument(
        "--allow-secret-env",
        action="store_true",
        help="pass allowlisted secret-named variables to explicitly trusted project code",
    )
    result.add_argument(
        "--external-security",
        action="store_true",
        help="allow read-only dependency advisory network checks",
    )
    result.add_argument("--release", action="store_true", help="use release-grade UI evidence status")
    return result


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    trusted = trust_granted(arguments.trust_project_code)
    try:
        ran, incomplete = {
            "test": lambda: check_test(trusted=trusted, allow_secret_env=arguments.allow_secret_env),
            "lint": lambda: check_lint(trusted=trusted, allow_secret_env=arguments.allow_secret_env),
            "build": lambda: check_build(trusted=trusted, allow_secret_env=arguments.allow_secret_env),
            "security": lambda: check_security(external=arguments.external_security),
            "ui": lambda: check_ui(release=arguments.release),
        }[arguments.mode]()
    except (GuardrailError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"FAIL project {arguments.mode}: invalid Harness configuration: {exc}", file=sys.stderr)
        return 2
    if incomplete < 0:
        return 1
    if incomplete:
        print(f"INCOMPLETE project {arguments.mode}: {incomplete} applicable check(s) unavailable or unauthorized")
        return 3
    if ran == 0:
        print(f"NOT_APPLICABLE project {arguments.mode}: no applicable command discovered")
        return 0
    print(f"PASS project {arguments.mode}: {ran} applicable command(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
