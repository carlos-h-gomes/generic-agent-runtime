#!/usr/bin/env python3
"""Validate an open, vendor-neutral solution decision."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import schema_lite


DEFAULT_ROOT = Path(__file__).resolve().parents[1]


def semantic_errors(decision: dict) -> list[str]:
    if decision.get("status") != "approved":
        return []
    errors: list[str] = []
    components = decision.get("components") or []
    if any(component.get("authority") == "unresolved" for component in components):
        errors.append("approved decisions cannot contain unresolved component authority")
    if not any(component.get("system_of_record") for component in components):
        errors.append("approved decisions require an explicit system of record")
    security = decision.get("security") or {}
    required_security = ("credentials_external", "least_privilege", "input_validation", "egress_scoped", "sensitive_data_minimized", "risky_capabilities_reviewed")
    if not all(security.get(name) is True for name in required_security):
        errors.append("approved decisions require all universal security controls")
    operations = decision.get("operations") or {}
    if not operations.get("environment_separation"):
        errors.append("approved decisions require environment separation")
    cost = decision.get("cost") or {}
    if cost.get("pricing_status") == "unknown" or cost.get("unbounded_exposure") is True:
        errors.append("approved decisions require bounded, known or not-applicable cost")
    approval = decision.get("approval") or {}
    if approval.get("status") not in {"not_required", "approved"}:
        errors.append("approved decisions require closed approval state")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("decision", type=Path)
    parser.add_argument("--schema", type=Path, default=DEFAULT_ROOT / "schemas" / "solution-decision.schema.json")
    args = parser.parse_args(argv)
    try:
        decision = json.loads(args.decision.read_text(encoding="utf-8"))
        schema = json.loads(args.schema.read_text(encoding="utf-8"))
        schema_lite.validate(decision, schema)
        errors = semantic_errors(decision)
    except (OSError, UnicodeError, json.JSONDecodeError, schema_lite.SchemaValidationError) as exc:
        print(f"FAIL solution decision: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"FAIL solution decision: {error}", file=sys.stderr)
        return 1
    print(f"PASS solution decision: {decision['decision_id']} ({decision['status']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
