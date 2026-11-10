#!/usr/bin/env python3
"""Validate the project truth index and release documentation lifecycle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
TRUTH = Path("SOURCE-OF-TRUTH.md")
TECHNICAL = Path("docs/TECHNICAL-DOCUMENTATION.md")
USER_MANUAL = Path("docs/USER-MANUAL.md")
PLACEHOLDER = re.compile(r"<[^>]+>|\b(?:UNINITIALIZED|not set)\b", re.IGNORECASE)

TRUTH_HEADINGS = {
    "## Project identity and release",
    "## Architecture profile",
    "## Authoritative source map",
    "## Active work and decisions",
    "## Risks and unknowns",
    "## Last qualified evidence",
    "## Reconciliation rule",
}
TECHNICAL_HEADINGS = {
    "## Purpose, scope, and users",
    "## Architecture and runtime boundaries",
    "## Module and directory responsibilities",
    "## API contracts and integrations",
    "## Data ownership, schemas, and migrations",
    "## Authentication, authorization, and security controls",
    "## Configuration and environments",
    "## Local development, build, and tests",
    "## Deployment, compatibility, migration, and rollback",
    "## Observability, alerts, and incident response",
    "## Backup, restore, and recovery",
    "## Operations, support, and troubleshooting",
    "## Known limitations and residual risks",
    "## Evidence and authoritative references",
}
USER_HEADINGS = {
    "## Product purpose and prerequisites",
    "## Access and first use",
    "## Navigation",
    "## Features and expected outcomes",
    "## Primary workflows",
    "## Forms, validation, and feedback",
    "## Roles, permissions, and restrictions",
    "## Loading, empty, failure, degraded, and recovery states",
    "## Accessibility and supported interaction methods",
    "## Troubleshooting and frequently asked questions",
    "## Support and escalation",
    "## Version and release notes",
}


def headings(text: str) -> set[str]:
    return {line.strip() for line in text.splitlines() if line.startswith("## ")}


def check_document(path: Path, required: set[str], failures: list[str]) -> str:
    if not path.is_file():
        failures.append(f"missing document: {path.as_posix()}")
        return ""
    text = path.read_text(encoding="utf-8")
    for heading in sorted(required - headings(text)):
        failures.append(f"missing heading in {path.as_posix()}: {heading}")
    return text


def active_tasks(root: Path) -> list[tuple[Path, dict]]:
    result: list[tuple[Path, dict]] = []
    task_root = root / "docs" / "ai" / "tasks"
    if not task_root.is_dir():
        return result
    for path in sorted(task_root.glob("*.task.json")):
        if path.name.startswith("_"):
            continue
        value = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(value, dict) and value.get("status") not in {"done", "blocked_external"}:
            result.append((path, value))
    return result


def local_markdown_links(root: Path, path: Path, text: str, failures: list[str]) -> None:
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
        target = target.split("#", 1)[0]
        if not target or "://" in target or target.startswith(("mailto:", "#")):
            continue
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(root)
        except ValueError:
            failures.append(f"documentation link escapes project: {path.relative_to(root)} -> {target}")
            continue
        if not resolved.exists():
            failures.append(f"broken documentation link: {path.relative_to(root)} -> {target}")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    result.add_argument("--profile", choices=("dev", "ci", "release"), default="ci")
    return result


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    root = arguments.root.resolve()
    application_detected = (root / "backend").exists() or (root / "frontend").exists()
    if not application_detected:
        print("NOT_APPLICABLE documentation: no application boundary detected")
        return 0
    try:
        failures: list[str] = []
        truth_text = check_document(root / TRUTH, TRUTH_HEADINGS, failures)
        technical_text = check_document(root / TECHNICAL, TECHNICAL_HEADINGS, failures)
        user_text = check_document(root / USER_MANUAL, USER_HEADINGS, failures)
        for path, text in ((root / TRUTH, truth_text), (root / TECHNICAL, technical_text), (root / USER_MANUAL, user_text)):
            if text:
                local_markdown_links(root, path, text, failures)
        if truth_text:
            for required_pointer in (
                "docs/ai/architecture-policy.json",
                "docs/TECHNICAL-DOCUMENTATION.md",
                "docs/USER-MANUAL.md",
                "docs/architecture/DIRECTORY-MAP.md",
            ):
                if f"`{required_pointer}`" not in truth_text:
                    failures.append(f"truth index does not name required authority: {required_pointer}")
                elif not (root / required_pointer).exists():
                    failures.append(f"truth index authority does not exist: {required_pointer}")
        for path, task in active_tasks(root):
            impact = task.get("documentation_impact")
            if not isinstance(impact, dict) or impact.get("level") not in {"none", "technical", "user_manual", "both"} or not impact.get("reason"):
                failures.append(f"active task lacks documentation impact: {path.relative_to(root)}")
        if arguments.profile == "release":
            for relative, text in ((TRUTH, truth_text), (TECHNICAL, technical_text), (USER_MANUAL, user_text)):
                if text and PLACEHOLDER.search(text):
                    failures.append(f"release document contains uninitialized placeholder: {relative.as_posix()}")
                if text and re.search(r"^Status:\s*(?:DRAFT|UNINITIALIZED)", text, re.MULTILINE | re.IGNORECASE):
                    failures.append(f"release document is not approved/current: {relative.as_posix()}")
        if failures:
            for failure in failures[:100]:
                print(f"FAIL documentation: {failure}")
            if len(failures) > 100:
                print(f"FAIL documentation: {len(failures) - 100} additional failures omitted")
            return 1 if arguments.profile == "release" else 3
        print("PASS documentation: truth index, impact classification, technical documentation, and user manual")
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(f"FAIL documentation: invalid project evidence: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
