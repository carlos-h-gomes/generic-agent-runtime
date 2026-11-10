#!/usr/bin/env python3
"""Detect a web UI and validate its product, accessibility, responsive, and visual evidence."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from harnesslib.guardrails import GuardrailError, load_json_object, resolve_under_root
from harnesslib.reporting import CheckReport
import schema_lite


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
UI_PACKAGES = {
    "@angular/core",
    "@remix-run/react",
    "@sveltejs/kit",
    "astro",
    "next",
    "nuxt",
    "react",
    "solid-js",
    "svelte",
    "vue",
}
MANUAL_CHECK_IDS = {"keyboard", "focus", "zoom_reflow"}


def package_manifests(root: Path) -> list[dict]:
    values: list[dict] = []
    for path in [root / "package.json", *sorted(root.glob("*/package.json"))]:
        if not path.is_file() or "node_modules" in path.parts:
            continue
        try:
            values.append(load_json_object(path))
        except GuardrailError:
            continue
    return values


def detect_ui(root: Path) -> tuple[bool, list[str]]:
    evidence: list[str] = []
    for package in package_manifests(root):
        dependencies: set[str] = set()
        for group in ("dependencies", "devDependencies", "peerDependencies"):
            values = package.get(group, {})
            if isinstance(values, dict):
                dependencies.update(values)
        found = sorted(dependencies & UI_PACKAGES)
        if found:
            evidence.append(f"UI package(s): {', '.join(found)}")
    if (root / "index.html").is_file() and any((root / name).is_dir() for name in ("src", "app", "pages")):
        evidence.append("root index.html plus source tree")
    return bool(evidence), evidence


def validate_pointer(root: Path, value: str) -> bool:
    try:
        path = resolve_under_root(root, value)
    except GuardrailError:
        return False
    return path.is_file()


def validate_review(root: Path, review: dict, profile: str, report: CheckReport) -> None:
    status = review.get("status")
    required_status = "approved" if profile == "release" else "ready"
    allowed = {"approved"} if profile == "release" else {"ready", "approved"}
    if status not in allowed:
        report.gap(f"UI review status is {status!r}; {required_status!r} or stronger is required")
        return
    report.passed(f"UI review status is {status}")

    evidence_items = review.get("evidence", [])
    evidence_ids = {
        item.get("id")
        for item in evidence_items
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    missing_pointers = [
        item.get("pointer")
        for item in evidence_items
        if isinstance(item, dict)
        and isinstance(item.get("pointer"), str)
        and not validate_pointer(root, item["pointer"])
    ]
    if missing_pointers:
        report.failed(f"UI evidence pointer is missing or escapes root: {', '.join(missing_pointers)}")
    else:
        report.passed(f"UI evidence pointers exist ({len(evidence_items)})")

    state_errors: list[str] = []
    for name, state in review.get("states", {}).items():
        if not isinstance(state, dict):
            state_errors.append(name)
            continue
        refs = state.get("evidence_refs", [])
        if state.get("status") == "covered" and (not refs or not set(refs).issubset(evidence_ids)):
            state_errors.append(f"{name}:covered_without_evidence")
        if state.get("status") == "not_applicable" and len(str(state.get("reason", "")).strip()) < 8:
            state_errors.append(f"{name}:weak_not_applicable_reason")
    if state_errors:
        report.failed(f"UI state coverage is incomplete: {', '.join(state_errors)}")
    else:
        report.passed("UI state matrix is complete and evidence-linked")

    viewports = review.get("responsive", {}).get("viewports", [])
    widths = [item.get("width") for item in viewports if isinstance(item, dict) and isinstance(item.get("width"), int)]
    if any(width <= 390 for width in widths) and any(width >= 1280 for width in widths):
        report.passed("responsive evidence declares compact and wide viewports")
    else:
        report.failed("responsive evidence must include a compact viewport <=390px and wide viewport >=1280px")

    accessibility = review.get("accessibility", {})
    manual = accessibility.get("manual_checks", [])
    manual_ids = {item.get("id") for item in manual if isinstance(item, dict)}
    if accessibility.get("standard") == "WCAG 2.2 AA" and MANUAL_CHECK_IDS.issubset(manual_ids):
        report.passed("WCAG 2.2 AA plus keyboard, focus, and zoom/reflow manual checks are recorded")
    else:
        report.failed("accessibility evidence lacks WCAG 2.2 AA or required manual checks")

    visual = review.get("visual", {})
    baselines = visual.get("baselines", [])
    missing_baselines = [item for item in baselines if isinstance(item, str) and not validate_pointer(root, item)]
    if missing_baselines:
        report.failed(f"visual baseline is missing or escapes root: {', '.join(missing_baselines)}")
    elif not visual.get("environment") or visual.get("diff_status") not in {"passed", "reviewed_changes"}:
        report.failed("visual evidence lacks deterministic environment or reviewed diff status")
    else:
        report.passed(f"visual evidence is deterministic and reviewed ({len(baselines)} baseline(s))")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    result.add_argument("--review", type=Path, default=Path("docs/ai/ui-review.json"))
    result.add_argument("--profile", choices=("dev", "ci", "release"), default="ci")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = args.root.resolve()
    report = CheckReport("ui_quality")
    try:
        review_path = args.review if args.review.is_absolute() else root / args.review
        review = load_json_object(review_path)
        schema = load_json_object(root / "schemas" / "ui-review.schema.json")
        schema_lite.check_schema(schema)
        schema_lite.validate(review, schema)
        detected, triggers = detect_ui(root)
        declared = bool(review.get("applicability", {}).get("applicable"))
        if not detected and not declared:
            report.na("no web UI trigger detected and UI review declares not applicable")
            return report.emit()
        if not declared:
            report.gap(f"web UI detected but review is uninitialized ({'; '.join(triggers)})")
            return report.emit()
        report.passed(f"UI review applicability is declared ({'; '.join(triggers) if triggers else 'manual trigger'})")
        validate_review(root, review, args.profile, report)
    except (GuardrailError, schema_lite.SchemaValidationError, OSError, KeyError, TypeError) as exc:
        print(f"FAIL invalid UI review configuration: {exc}", file=sys.stderr)
        return 2
    return report.emit()


if __name__ == "__main__":
    raise SystemExit(main())
