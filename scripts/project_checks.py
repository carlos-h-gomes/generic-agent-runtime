#!/usr/bin/env python3
"""Cross-platform project check discovery with bounded non-interactive execution."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAFE = ROOT / "scripts" / "safe_exec.py"


def limits() -> dict[str, int]:
    values = {
        "default_command_timeout_seconds": 300,
        "kill_grace_seconds": 5,
        "failure_tail_lines": 120,
    }
    try:
        configured = json.loads((ROOT / "harness.json").read_text(encoding="utf-8")).get(
            "execution_limits", {}
        )
        values.update({key: configured[key] for key in values if key in configured})
    except (OSError, ValueError, TypeError):
        pass
    return values


def package_projects() -> list[tuple[Path, dict[str, str]]]:
    """Return root and immediate-child npm projects in deterministic order."""
    manifests = [ROOT / "package.json", *sorted(ROOT.glob("*/package.json"))]
    projects: list[tuple[Path, dict[str, str]]] = []
    for manifest in manifests:
        if not manifest.is_file():
            continue
        try:
            value = json.loads(manifest.read_text(encoding="utf-8"))
            scripts = value.get("scripts", {})
        except (OSError, ValueError, TypeError):
            continue
        if isinstance(scripts, dict):
            projects.append((manifest.parent, scripts))
    return projects


def npm_executable() -> str | None:
    if os.name == "nt":
        return shutil.which("npm.cmd") or shutil.which("npm")
    return shutil.which("npm")


def node_executable() -> str | None:
    if os.name == "nt":
        return shutil.which("node.exe") or shutil.which("node")
    return shutil.which("node")


def npm_command(project: Path, *arguments: str) -> list[str]:
    npm = npm_executable()
    if npm is None:
        raise RuntimeError("npm unavailable")
    relative = project.relative_to(ROOT)
    if relative == Path("."):
        return [npm, *arguments]
    return [npm, "--prefix", str(relative), *arguments]


def run(label: str, command: list[str], timeout: int) -> int:
    config = limits()
    environment = os.environ.copy()
    environment.setdefault("CI", "1")
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


def run_npm_scripts(script_names: tuple[str, ...]) -> tuple[int, int]:
    ran = incomplete = 0
    projects = package_projects()
    for project, scripts in projects:
        for script_name in script_names:
            if script_name not in scripts:
                continue
            label = f"npm {project.relative_to(ROOT)} {script_name}"
            if npm_executable() is None:
                print(f"SKIP {label}: npm unavailable")
                incomplete += 1
                continue
            ran += 1
            if run(label, npm_command(project, "run", script_name), limits()["default_command_timeout_seconds"]):
                return ran, -1
    return ran, incomplete


def check_test() -> tuple[int, int]:
    custom = override("HARNESS_TEST_COMMAND")
    if custom:
        return (1, 0) if run("custom project tests", custom, limits()["default_command_timeout_seconds"]) == 0 else (1, -1)

    filters = override("HARNESS_NPM_TEST_FILTERS")
    if filters:
        ran = incomplete = 0
        for project, scripts in package_projects():
            if "test" not in scripts:
                continue
            label = f"npm {project.relative_to(ROOT)} filtered tests"
            if npm_executable() is None:
                print(f"SKIP {label}: npm unavailable")
                incomplete += 1
                continue
            ran += 1
            if run(
                label,
                npm_command(project, "test", "--", *filters),
                limits()["default_command_timeout_seconds"],
            ):
                return ran, -1
    else:
        ran, incomplete = run_npm_scripts(("test",))
    if incomplete < 0:
        return ran, incomplete

    python_project = (ROOT / "pyproject.toml").is_file() or (ROOT / "requirements.txt").is_file()
    tests = (ROOT / "tests").is_dir() or (ROOT / "test").is_dir()
    if python_project and tests:
        if shutil.which("pytest"):
            ran += 1
            if run("pytest", ["pytest"], limits()["default_command_timeout_seconds"]):
                return ran, -1
        else:
            print("SKIP pytest: test tree detected but pytest unavailable")
            incomplete += 1
    return ran, incomplete


def check_lint() -> tuple[int, int]:
    custom = override("HARNESS_LINT_COMMAND")
    if custom:
        return (1, 0) if run("custom project lint", custom, limits()["default_command_timeout_seconds"]) == 0 else (1, -1)

    ran, incomplete = run_npm_scripts(("lint", "typecheck"))
    if incomplete < 0:
        return ran, incomplete

    python_project = (ROOT / "pyproject.toml").is_file() or (ROOT / "setup.cfg").is_file()
    if python_project:
        if shutil.which("ruff"):
            ran += 1
            if run("ruff check", ["ruff", "check", "."], limits()["default_command_timeout_seconds"]):
                return ran, -1
        else:
            print("SKIP Ruff: Python lint configuration detected but Ruff unavailable")
            incomplete += 1
    return ran, incomplete


def check_build() -> tuple[int, int]:
    custom = override("HARNESS_BUILD_COMMAND")
    if custom:
        return (1, 0) if run("custom project build", custom, limits()["default_command_timeout_seconds"]) == 0 else (1, -1)
    return run_npm_scripts(("build",))


def check_security() -> tuple[int, int]:
    commands: list[tuple[str, list[str]]] = []
    missing = 0
    timeout = limits()["default_command_timeout_seconds"]

    node = node_executable()
    boundary_scripts = (
        ("n8n credential and workflow boundaries", ROOT / "scripts" / "check-n8n-security.mjs"),
        ("systemd RF security boundaries", ROOT / "scripts" / "check-systemd-security.mjs"),
    )
    for label, script in boundary_scripts:
        if not script.is_file():
            continue
        if node:
            commands.append((label, [node, str(script)]))
        else:
            print(f"SKIP {label}: Node.js unavailable")
            missing += 1

    if shutil.which("semgrep"):
        commands.append(("Semgrep SAST", ["semgrep", "scan", "--config=p/default", "--config=p/secrets", "--error", "."]))
    else:
        print("SKIP Semgrep unavailable")
        missing += 1

    if shutil.which("gitleaks") and (ROOT / ".git").is_dir():
        commands.append(("Gitleaks", ["gitleaks", "detect", "--no-banner", "--redact", "--source", "."]))
    elif shutil.which("trufflehog"):
        commands.append(("TruffleHog", ["trufflehog", "filesystem", ".", "--no-verification"]))
    else:
        print("SKIP secret scanner unavailable")
        missing += 1

    if shutil.which("trivy"):
        commands.append(("Trivy dependencies", ["trivy", "fs", "--scanners", "vuln", "--severity", "HIGH,CRITICAL", "--ignore-unfixed", "."]))
    else:
        audited = 0
        if npm_executable() is not None:
            for project, _scripts in package_projects():
                if (project / "package-lock.json").is_file():
                    commands.append((f"npm audit {project.relative_to(ROOT)}", npm_command(project, "audit", "--audit-level=high")))
                    audited += 1
        if audited == 0 and ((ROOT / "requirements.txt").is_file() or (ROOT / "pyproject.toml").is_file()) and shutil.which("pip-audit"):
            commands.append(("pip-audit", ["pip-audit"]))
            audited += 1
        if audited == 0:
            print("SKIP dependency scanner unavailable")
            missing += 1

    infrastructure = any((ROOT / name).is_file() for name in ("Dockerfile", "docker-compose.yml", "compose.yml")) or any(ROOT.glob("*.tf"))
    if infrastructure:
        if shutil.which("trivy"):
            commands.append(("Trivy infrastructure", ["trivy", "config", "."]))
        else:
            print("SKIP infrastructure scan: Trivy unavailable")
            missing += 1

    for label, command in commands:
        if run(label, command, timeout):
            return len(commands), -1
    return len(commands), missing


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("test", "lint", "build", "security"))
    arguments = parser.parse_args(argv)
    ran, incomplete = {
        "test": check_test,
        "lint": check_lint,
        "build": check_build,
        "security": check_security,
    }[arguments.mode]()
    if incomplete < 0:
        return 1
    if incomplete:
        print(f"INCOMPLETE {arguments.mode}: {incomplete} applicable checks unavailable")
        return 3
    print(f"PASS project {arguments.mode}: {ran} applicable command(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
