#!/usr/bin/env python3
"""Security policy, lifecycle, secret, source, and deployment assurance."""

from __future__ import annotations

import argparse
import ast
from datetime import date
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

from harnesslib.guardrails import (
    GuardrailError,
    load_json_object,
    parse_date,
    sanitize_environment,
    semver_tuple,
)
from harnesslib.reporting import CheckReport
import schema_lite


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
IGNORED_PARTS = {
    ".git",
    ".next",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "venv",
}
ALLOWED_ENV_EXAMPLES = {".env.example", ".env.sample", ".env.template"}
SENSITIVE_NAMES = {
    ".dockerconfigjson",
    ".netrc",
    ".npmrc",
    ".pypirc",
    "auth.json",
    "credentials",
    "credentials.json",
    "id_ed25519",
    "id_rsa",
    "kubeconfig",
    "secrets.json",
    "terraform.tfstate",
    "terraform.tfstate.backup",
}
SENSITIVE_SUFFIXES = {
    ".db",
    ".har",
    ".kdbx",
    ".key",
    ".ovpn",
    ".p12",
    ".pcap",
    ".pem",
    ".pfx",
    ".sqlite",
    ".tfstate",
}
TEXT_SUFFIXES = {
    ".cjs",
    ".env",
    ".js",
    ".json",
    ".jsx",
    ".mjs",
    ".py",
    ".sh",
    ".ts",
    ".tsx",
    ".yaml",
    ".yml",
}
SECRET_PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "github_token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    "slack_token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    "generic_assignment": re.compile(
        r"""(?ix)\b(?:password|passwd|secret|api[_-]?key|access[_-]?token)\b
        \s*[:=]\s*["'][^"'\r\n]{8,}["']"""
    ),
}


def iter_source_files(root: Path, suffixes: set[str] | None = None):
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in IGNORED_PARTS for part in path.relative_to(root).parts):
            continue
        if path.stat().st_size > 2_097_152:
            continue
        if suffixes is None or path.suffix.lower() in suffixes:
            yield path


def load_policy(root: Path, policy_path: Path) -> dict:
    policy = load_json_object(policy_path)
    schema_path = root / "schemas" / "security-policy.schema.json"
    schema = load_json_object(schema_path)
    schema_lite.check_schema(schema)
    schema_lite.validate(policy, schema)
    return policy


def package_projects(root: Path) -> list[tuple[Path, dict]]:
    manifests = [root / "package.json", *sorted(root.glob("*/package.json"))]
    result: list[tuple[Path, dict]] = []
    for path in manifests:
        if not path.is_file() or "node_modules" in path.parts:
            continue
        try:
            value = load_json_object(path)
        except GuardrailError:
            continue
        result.append((path.parent, value))
    return result


def package_uses_next(package: dict) -> bool:
    for group in ("dependencies", "devDependencies", "optionalDependencies"):
        values = package.get(group, {})
        if isinstance(values, dict) and "next" in values:
            return True
    return False


def locked_next_version(project: Path) -> str | None:
    lock = project / "package-lock.json"
    if not lock.is_file():
        return None
    try:
        value = load_json_object(lock, max_bytes=16_777_216)
    except GuardrailError:
        return None
    packages = value.get("packages")
    if isinstance(packages, dict):
        item = packages.get("node_modules/next")
        if isinstance(item, dict) and isinstance(item.get("version"), str):
            return item["version"]
    dependencies = value.get("dependencies")
    if isinstance(dependencies, dict):
        item = dependencies.get("next")
        if isinstance(item, dict) and isinstance(item.get("version"), str):
            return item["version"]
    return None


def node_pin_majors(project: Path, package: dict) -> set[int]:
    majors: set[int] = set()
    for name in (".nvmrc", ".node-version"):
        path = project / name
        if path.is_file():
            match = re.search(r"\b(?:v)?(\d+)(?:\.\d+)?(?:\.\d+)?\b", path.read_text(encoding="utf-8", errors="replace"))
            if match:
                majors.add(int(match.group(1)))
    engines = package.get("engines", {})
    if isinstance(engines, dict) and isinstance(engines.get("node"), str):
        majors.update(int(item) for item in re.findall(r"(?<!\d)(\d{2})(?:\.\d+)?", engines["node"]))
    dockerfile = project / "Dockerfile"
    if dockerfile.is_file():
        for match in re.findall(r"(?im)^\s*FROM\s+node:(\d+)(?:[.-]|$)", dockerfile.read_text(encoding="utf-8", errors="replace")):
            majors.add(int(match))
    return majors


def check_policy_freshness(policy: dict, report: CheckReport) -> None:
    checked = parse_date(policy.get("checked_at"), "checked_at")
    expires = parse_date(policy.get("expires_at"), "expires_at")
    if expires < checked:
        report.failed("security policy expires before it was checked")
    elif date.today() > expires:
        report.gap(f"security policy expired on {expires.isoformat()}; refresh from authoritative sources")
    else:
        report.passed(f"security policy is fresh through {expires.isoformat()}")


def check_sensitive_files(root: Path, report: CheckReport) -> None:
    findings: list[str] = []
    for path in iter_source_files(root):
        relative = path.relative_to(root).as_posix()
        name = path.name.lower()
        if name in ALLOWED_ENV_EXAMPLES:
            continue
        if name.startswith(".env") or name in SENSITIVE_NAMES or path.suffix.lower() in SENSITIVE_SUFFIXES:
            findings.append(relative)
    if findings:
        report.failed(f"restricted sensitive file classes present: {', '.join(findings[:20])}")
    else:
        report.passed("no restricted credential, key, capture, database, or state file class detected")


def check_secret_content(root: Path, report: CheckReport) -> None:
    findings: list[str] = []
    for path in iter_source_files(root, TEXT_SUFFIXES):
        relative = path.relative_to(root).as_posix()
        if relative.startswith(("docs/harness/evaluation-fixtures", "scripts/test_")):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern_id, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{relative}:{pattern_id}")
    if findings:
        report.failed(f"secret-like content detected (values redacted): {', '.join(findings[:20])}")
    else:
        report.passed("built-in redacted secret-content scan found no credential pattern")


def dotted_name(node: ast.AST) -> str:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def check_source_execution(root: Path, report: CheckReport) -> None:
    findings: list[str] = []
    dangerous_calls = {"eval", "exec", "os.system", "pickle.loads", "marshal.loads"}
    subprocess_calls = {
        "subprocess.call",
        "subprocess.check_call",
        "subprocess.check_output",
        "subprocess.Popen",
        "subprocess.run",
    }
    for path in iter_source_files(root, {".py"}):
        relative = path.relative_to(root).as_posix()
        if relative.startswith("scripts/test_"):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = dotted_name(node.func)
            if name in dangerous_calls:
                findings.append(f"{relative}:{node.lineno}:{name}")
            if name in subprocess_calls and any(
                keyword.arg == "shell"
                and isinstance(keyword.value, ast.Constant)
                and keyword.value.value is True
                for keyword in node.keywords
            ):
                findings.append(f"{relative}:{node.lineno}:{name}(shell=True)")

    js_patterns = {
        "eval": re.compile(r"\beval\s*\("),
        "new_function": re.compile(r"\bnew\s+Function\s*\("),
        "child_process_exec": re.compile(r"\b(?:child_process\.)?exec\s*\("),
    }
    for path in iter_source_files(root, {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx"}):
        relative = path.relative_to(root).as_posix()
        if relative.startswith(("scripts/test_", "test", "tests")):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern_id, pattern in js_patterns.items():
            if pattern.search(text):
                findings.append(f"{relative}:{pattern_id}")

    if findings:
        report.failed(f"dangerous execution primitive requires review: {', '.join(findings[:30])}")
    else:
        report.passed("built-in source scan found no eval, unsafe deserialization, shell=True, or JS exec primitive")


def check_node_projects(root: Path, policy: dict, profile: str, report: CheckReport) -> None:
    projects = package_projects(root)
    if not projects:
        report.na("no npm project detected for lockfile/runtime/framework lifecycle checks")
        return
    node_policy = policy["runtimes"]["node"]
    allowed_node = set(node_policy["allowed_lts_majors"])
    next_policy = policy["frameworks"]["next"]
    supported_next = {item["major"]: item["minimum"] for item in next_policy["supported"]}
    lock_names = {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lock", "bun.lockb"}

    for project, package in projects:
        label = project.relative_to(root).as_posix() or "."
        locks = [name for name in lock_names if (project / name).is_file()]
        if locks:
            report.passed(f"{label}: dependency lockfile present ({', '.join(sorted(locks))})")
        elif policy["release"]["require_lockfile"]:
            report.failed(f"{label}: package manifest has no recognized dependency lockfile")

        lifecycle = package.get("scripts", {})
        risky = sorted(
            name
            for name in ("preinstall", "install", "postinstall", "prepare")
            if isinstance(lifecycle, dict) and name in lifecycle
        )
        if risky:
            report.gap(f"{label}: package lifecycle scripts require provenance review ({', '.join(risky)})")
        else:
            report.passed(f"{label}: no package install lifecycle script declared")

        uses_next = package_uses_next(package)
        if not uses_next:
            continue
        version = locked_next_version(project)
        if version is None:
            report.gap(f"{label}: exact installed Next.js version is not available from package-lock.json")
        else:
            parsed = semver_tuple(version)
            if parsed is None:
                report.failed(f"{label}: prerelease or non-exact Next.js version is blocked ({version})")
            elif parsed[0] not in supported_next:
                report.failed(f"{label}: Next.js {version} is outside supported policy majors {sorted(supported_next)}")
            elif parsed < semver_tuple(supported_next[parsed[0]]):  # type: ignore[operator]
                report.failed(
                    f"{label}: Next.js {version} is below security floor {supported_next[parsed[0]]}"
                )
            else:
                report.passed(f"{label}: Next.js {version} meets the dated security floor")

        pin_majors = node_pin_majors(project, package)
        if not pin_majors:
            report.gap(f"{label}: Next.js deployment has no verifiable Node major pin")
        elif not pin_majors.issubset(allowed_node):
            report.failed(
                f"{label}: Node pin includes unsupported major(s) {sorted(pin_majors - allowed_node)}; allowed {sorted(allowed_node)}"
            )
        else:
            report.passed(f"{label}: Node deployment pin is within supported LTS majors {sorted(pin_majors)}")

        if profile == "release":
            for relative in policy["release"]["required_web_artifacts"]:
                artifact = project / relative
                if not artifact.is_file() or artifact.stat().st_size < 80:
                    report.gap(f"{label}: required web release artifact is missing or uninitialized: {relative}")


def check_deployment_files(root: Path, profile: str, report: CheckReport) -> None:
    dockerfiles = sorted(root.glob("**/Dockerfile"))
    dockerfiles = [item for item in dockerfiles if not any(part in IGNORED_PARTS for part in item.relative_to(root).parts)]
    if not dockerfiles:
        report.na("no Dockerfile detected for container hardening checks")
    for path in dockerfiles:
        relative = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        users = re.findall(r"(?im)^\s*USER\s+([^\s#]+)", text)
        if not users or users[-1].casefold() in {"0", "root"}:
            report.failed(f"{relative}: final container user is missing or root")
        else:
            report.passed(f"{relative}: final container user is non-root")
        from_lines = re.findall(r"(?im)^\s*FROM\s+([^\s]+)", text)
        if from_lines and all("@sha256:" in item for item in from_lines):
            report.passed(f"{relative}: base images are digest pinned")
        elif profile == "release":
            report.gap(f"{relative}: base image tags are not pinned by digest")
        if re.search(r"(?im)^\s*(?:COPY|ADD)\s+.*\.env", text):
            report.failed(f"{relative}: Docker build copies an environment file")
        if re.search(r"(?im)^\s*ADD\s+https?://", text):
            report.failed(f"{relative}: remote ADD is prohibited")

    compose_files = [
        path
        for name in ("compose.yml", "compose.yaml", "docker-compose.yml", "docker-compose.yaml")
        for path in root.glob(f"**/{name}")
        if not any(part in IGNORED_PARTS for part in path.relative_to(root).parts)
    ]
    for path in sorted(set(compose_files)):
        relative = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        unsafe = []
        if re.search(r"(?im)^\s*privileged\s*:\s*true\b", text):
            unsafe.append("privileged")
        if re.search(r"(?im)^\s*network_mode\s*:\s*[\"']?host\b", text):
            unsafe.append("host network")
        if "/var/run/docker.sock" in text:
            unsafe.append("Docker socket")
        if unsafe:
            report.failed(f"{relative}: unsafe container boundary ({', '.join(unsafe)})")
        else:
            report.passed(f"{relative}: no privileged, host-network, or Docker-socket boundary detected")


def run_external_dependency_scans(root: Path, policy: dict, report: CheckReport) -> None:
    projects = package_projects(root)
    if not projects:
        report.na("no dependency manifest requires an external advisory scan")
        return
    safe = root / "scripts" / "safe_exec.py"
    limits = load_json_object(root / "harness.json")["execution_limits"]
    environment = sanitize_environment(
        os.environ,
        policy["execution"]["allowed_environment"],
        policy["execution"]["secret_name_pattern"],
    )
    scanner = shutil.which("osv-scanner")
    commands: list[tuple[str, list[str]]] = []
    if scanner:
        commands.append(("OSV dependency scan", [scanner, "scan", "source", "--recursive", str(root)]))
    else:
        npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
        if npm:
            for project, _ in projects:
                if (project / "package-lock.json").is_file():
                    commands.append(
                        (
                            f"npm audit {project.relative_to(root)}",
                            [npm, "--prefix", str(project), "audit", "--audit-level=high"],
                        )
                    )
    if not commands:
        report.gap("dependency project detected but OSV-Scanner/npm audit is unavailable")
        return
    for label, command in commands:
        completed = subprocess.run(
            [
                sys.executable,
                str(safe),
                "--label",
                label,
                "--timeout",
                str(limits["default_command_timeout_seconds"]),
                "--grace",
                str(limits["kill_grace_seconds"]),
                "--tail-lines",
                str(limits["failure_tail_lines"]),
                "--max-buffer-bytes",
                str(limits["max_output_buffer_bytes"]),
                "--",
                *command,
            ],
            cwd=root,
            env=environment,
            check=False,
        )
        if completed.returncode:
            report.failed(f"{label} failed with exit {completed.returncode}")
            return
        report.passed(label)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    result.add_argument("--policy", type=Path)
    result.add_argument("--profile", choices=("dev", "ci", "release"), default="ci")
    result.add_argument(
        "--external",
        action="store_true",
        help="allow read-only advisory scanner network access; never executes project scripts",
    )
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = args.root.resolve()
    policy_path = (args.policy if args.policy and args.policy.is_absolute() else root / (args.policy or "security-policy.json")).resolve()
    report = CheckReport("security_assurance")
    try:
        policy = load_policy(root, policy_path)
        check_policy_freshness(policy, report)
        check_sensitive_files(root, report)
        check_secret_content(root, report)
        check_source_execution(root, report)
        check_node_projects(root, policy, args.profile, report)
        check_deployment_files(root, args.profile, report)
        if args.external:
            run_external_dependency_scans(root, policy, report)
        elif package_projects(root):
            report.gap("external dependency advisory scan was not authorized; rerun with --external")
        else:
            report.na("external dependency advisory scan is not applicable")
    except (GuardrailError, schema_lite.SchemaValidationError, OSError, KeyError, TypeError) as exc:
        print(f"FAIL invalid security assurance configuration: {exc}", file=sys.stderr)
        return 2
    return report.emit()


if __name__ == "__main__":
    raise SystemExit(main())
