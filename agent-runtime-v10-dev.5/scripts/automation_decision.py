#!/usr/bin/env python3
"""Validate a code, n8n, or hybrid automation execution-plane decision."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import schema_lite


ROOT = Path(__file__).resolve().parents[1]


def load_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("decision must be a JSON object")
    return value


def semantic_errors(decision: dict) -> list[str]:
    errors: list[str] = []
    plane = decision.get("execution_plane")
    status = decision.get("status")
    blockers = decision.get("hard_blockers") or []
    handling = decision.get("blocker_handling") or []
    if plane == "n8n" and blockers:
        errors.append("n8n cannot own a workload with hard blockers")
    if plane == "hybrid" and blockers and not handling:
        errors.append("hybrid decisions must explain how every hard blocker is extracted to code")
    if status == "approved" and plane in {"n8n", "hybrid"}:
        cost = decision.get("cost") or {}
        if cost.get("pricing_status") == "unknown":
            errors.append("approved n8n or hybrid decisions require verified or not-applicable pricing evidence")
        if (decision.get("reliability") or {}).get("replay_safe") is not True:
            errors.append("approved n8n or hybrid decisions must be replay safe")
    if status == "approved" and (decision.get("approval") or {}).get("required") is True:
        approval = decision.get("approval") or {}
        if approval.get("status") != "approved" or not approval.get("reference"):
            errors.append("required approval must be approved with a reference")
    return errors


def validate_decision(decision_path: Path, schema_path: Path) -> list[str]:
    decision = load_object(decision_path)
    schema = load_object(schema_path)
    schema_lite.check_schema(schema)
    try:
        schema_lite.validate(decision, schema)
    except schema_lite.SchemaValidationError as exc:
        return [str(exc)]
    return semantic_errors(decision)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("decision", type=Path)
    result.add_argument(
        "--schema",
        type=Path,
        default=ROOT / "schemas" / "automation-decision.schema.json",
    )
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        errors = validate_decision(args.decision.resolve(), args.schema.resolve())
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, schema_lite.SchemaValidationError) as exc:
        print(f"FAIL automation decision: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"FAIL automation decision: {error}", file=sys.stderr)
        return 1
    print(f"PASS automation decision: {args.decision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
