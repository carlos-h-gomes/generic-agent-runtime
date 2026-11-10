#!/usr/bin/env python3
"""Emit a cost-review contract without claiming that project costs were measured."""

from __future__ import annotations

import json
import sys


REPORT = {
    "schema_version": "1.0",
    "status": "requires_project_review",
    "drivers": [
        "model/input/output/cached tokens and parallel agents",
        "paid API requests and retries",
        "compute duration and concurrency",
        "storage, retention, egress, queues, and log cardinality",
        "recurring jobs, fan-out, replay, and unbounded loops",
    ],
    "required_evidence": [
        "authoritative pricing source, currency, region, and checked date",
        "expected, burst, and worst-case volume with formula",
        "per-unit and monthly exposure",
        "hard caps, alert action and owner, degradation, and kill switch",
    ],
    "note": "This checklist is not a cost pass; use the finops GateResult for the active task.",
}


def main() -> int:
    if len(sys.argv) != 1:
        print("FAIL cost check is read-only and accepts no output-path arguments", file=sys.stderr)
        return 2
    rendered = json.dumps(REPORT, indent=2, ensure_ascii=False) + "\n"
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
