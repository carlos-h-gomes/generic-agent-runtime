#!/usr/bin/env python3
"""Execute and grade cases from the behavioral evaluation suite.

The suite in docs/harness/evaluation-cases.json is a specification. This tool
turns a case into a runnable, gradable artifact without inventing a verdict.

Design rules, consistent with the harness itself:

- Synthetic fixtures only. The tool never touches a real repository.
- Mechanically decidable assertions are decided from the filesystem or the
  captured transcript.
- Everything else is reported as `manual` and blocks a pass until a human
  records a verdict. An unresolved assertion is `incomplete`, never `pass`.
- Aggregates only. Raw transcripts stay outside the recorded result.

Usage:

    python scripts/run_evaluation.py materialize --case H4-01 --out runs/H4-01-r1
    # run your agent host inside runs/H4-01-r1/repo using runs/H4-01-r1/prompt.txt
    # save the agent output to runs/H4-01-r1/transcript.txt
    python scripts/run_evaluation.py grade --dir runs/H4-01-r1
    python scripts/run_evaluation.py aggregate --runs runs --out evaluation-run.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES_PATH = ROOT / "docs" / "harness" / "evaluation-cases.json"
RESULT_SCHEMA_VERSION = "1.0"

# Assertions this tool can decide without human judgement.
FILESYSTEM_ASSERTIONS = {
    "repository_writes",
    "task_file_writes",
    "changed_files",
    "unrelated_files_changed",
    "first_target_writes",
    "source_of_truth_overwritten",
    "risk_register_overwritten",
    "bridge_history_overwritten",
}
TRANSCRIPT_ASSERTIONS = {
    "answer_has_source_pointers",
}


def fail(message: str) -> "None":
    print(f"ERROR {message}", file=sys.stderr)
    raise SystemExit(2)


def load_suite() -> dict:
    if not CASES_PATH.is_file():
        fail(f"missing {CASES_PATH}")
    suite = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    fixture = suite.get("fixture") or {}
    fixture_path = ROOT / fixture.get("path", "")
    if not fixture_path.is_file():
        fail(f"missing fixture file {fixture_path}")
    digest = hashlib.sha256(fixture_path.read_bytes()).hexdigest()
    expected = fixture.get("sha256")
    if expected and digest != expected:
        fail(
            "fixture hash mismatch: the suite pins "
            f"{expected} but {fixture_path.name} hashes to {digest}"
        )
    suite["_fixtures"] = json.loads(fixture_path.read_text(encoding="utf-8"))
    suite["_fixture_sha256"] = digest
    return suite


def find_case(suite: dict, case_id: str) -> dict:
    for case in suite.get("cases", []):
        if case.get("id") == case_id:
            return case
    known = ", ".join(c.get("id", "?") for c in suite.get("cases", []))
    fail(f"unknown case {case_id}. Known ids: {known}")
    return {}


def snapshot(root: Path) -> dict:
    state = {}
    for path in sorted(root.rglob("*")):
        if path.is_dir() or ".git" in path.parts:
            continue
        rel = path.relative_to(root).as_posix()
        state[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return state


def diff(before: dict, after: dict) -> dict:
    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    modified = sorted(k for k in set(before) & set(after) if before[k] != after[k])
    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "changed_count": len(added) + len(removed) + len(modified),
    }


def parse_assertion(raw: str) -> tuple:
    match = re.match(r"^([A-Za-z0-9_/\.\-]+)\s*(<=|>=|<|>|=)\s*(.*)$", raw)
    if not match:
        return raw, "=", ""
    return match.group(1), match.group(2), match.group(3)


def compare(actual: int, operator: str, expected: str) -> "bool | None":
    try:
        target = int(expected)
    except ValueError:
        return None
    if operator in ("=", "=="):
        return actual == target
    if operator == "<":
        return actual < target
    if operator == "<=":
        return actual <= target
    if operator == ">":
        return actual > target
    if operator == ">=":
        return actual >= target
    return None


def cmd_materialize(args: argparse.Namespace) -> int:
    suite = load_suite()
    case = find_case(suite, args.case)
    fixture_name = case.get("fixture")
    repositories = suite["_fixtures"].get("repositories", {})
    if fixture_name not in repositories:
        fail(f"case {args.case} references unknown fixture {fixture_name}")

    out = Path(args.out).resolve()
    repo = out / "repo"
    if out.exists() and any(out.iterdir()):
        fail(f"{out} already exists and is not empty")
    repo.mkdir(parents=True)

    for rel, content in repositories[fixture_name].get("files", {}).items():
        target = repo / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    (out / "prompt.txt").write_text(case.get("prompt", ""), encoding="utf-8")

    environment = repositories[fixture_name].get("environment", {})
    if environment:
        (out / "environment.json").write_text(json.dumps(environment, indent=2), encoding="utf-8")
    (out / "before.json").write_text(
        json.dumps(
            {
                "suite_id": suite.get("suite_id"),
                "fixture_revision": suite["_fixtures"].get("fixture_revision"),
                "fixture_sha256": suite["_fixture_sha256"],
                "case_id": case.get("id"),
                "fixture": fixture_name,
                "state": snapshot(repo),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"case        {case.get('id')}")
    print(f"fixture     {fixture_name} ({len(repositories[fixture_name].get('files', {}))} files)")
    print(f"repo        {repo}")
    if environment:
        print(f"environment {out / 'environment.json'} (synthetic values, export before the run)")
    print(f"prompt      {out / 'prompt.txt'}")
    print()
    print("Next: run your agent host with that prompt, with the repo as its working")
    print("directory and without network access. Save its output to transcript.txt")
    print(f"in {out}, then run: python scripts/run_evaluation.py grade --dir {out}")
    return 0


def cmd_grade(args: argparse.Namespace) -> int:
    run_dir = Path(args.dir).resolve()
    before_path = run_dir / "before.json"
    repo = run_dir / "repo"
    if not before_path.is_file() or not repo.is_dir():
        fail(f"{run_dir} is not a materialized run directory")

    before = json.loads(before_path.read_text(encoding="utf-8"))
    suite = load_suite()
    case = find_case(suite, before["case_id"])

    if before.get("fixture_sha256") != suite["_fixture_sha256"]:
        fail("fixture changed between materialize and grade; the run is void")

    after = snapshot(repo)
    delta = diff(before["state"], after)
    task_changes = [
        p
        for p in delta["added"] + delta["removed"] + delta["modified"]
        if p.startswith("docs/ai/tasks/")
    ]

    transcript_path = run_dir / "transcript.txt"
    transcript = (
        transcript_path.read_text(encoding="utf-8", errors="replace")
        if transcript_path.is_file()
        else ""
    )

    manual_path = run_dir / "manual-verdicts.json"
    manual = (
        json.loads(manual_path.read_text(encoding="utf-8"))
        if manual_path.is_file()
        else {}
    )

    results = []
    for raw in case.get("hard_assertions", []):
        name, operator, expected = parse_assertion(raw)
        entry = {"assertion": raw, "method": "manual", "status": "incomplete"}

        if name in FILESYSTEM_ASSERTIONS:
            if name == "repository_writes":
                actual = delta["changed_count"]
            elif name == "task_file_writes":
                actual = len(task_changes)
            elif name == "changed_files" and not expected.strip().isdigit():
                wanted = sorted(p.strip() for p in expected.split(",") if p.strip())
                observed = sorted(delta["added"] + delta["removed"] + delta["modified"])
                entry.update(
                    {
                        "method": "filesystem",
                        "observed": observed,
                        "status": "pass" if observed == wanted else "fail",
                    }
                )
                results.append(entry)
                continue
            elif name in ("changed_files", "unrelated_files_changed", "first_target_writes"):
                actual = delta["changed_count"]
            else:
                actual = len(
                    [p for p in delta["modified"] + delta["removed"] if name.split("_")[0] in p]
                )
            verdict = compare(actual, operator, expected)
            entry.update({"method": "filesystem", "observed": actual})
            if verdict is None:
                entry["status"] = "incomplete"
                entry["note"] = "expected value is not numeric; record a manual verdict"
            else:
                entry["status"] = "pass" if verdict else "fail"

        elif name in TRANSCRIPT_ASSERTIONS and transcript:
            pointers = [p for p in before["state"] if p in transcript]
            entry.update(
                {
                    "method": "transcript",
                    "observed": pointers,
                    "status": "pass" if pointers else "fail",
                }
            )

        if entry["status"] == "incomplete" and raw in manual:
            recorded = manual[raw]
            entry.update(
                {
                    "method": "manual",
                    "status": recorded.get("status", "incomplete"),
                    "grader_note": recorded.get("note", ""),
                }
            )

        results.append(entry)

    statuses = {r["status"] for r in results}
    if "fail" in statuses:
        overall = "fail"
    elif "incomplete" in statuses or not results:
        overall = "incomplete"
    else:
        overall = "pass"

    result = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "suite_id": suite.get("suite_id"),
        "fixture_sha256": suite["_fixture_sha256"],
        "case_id": case.get("id"),
        "expected_route": case.get("expected_route", []),
        "host": args.host or "unrecorded",
        "repeat": args.repeat,
        "status": overall,
        "filesystem_delta": delta,
        "assertions": results,
        "transcript_captured": bool(transcript),
        "notes": "Aggregate evidence only. Raw transcripts are not stored in this file.",
    }
    (run_dir / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"case   {result['case_id']}")
    print(f"host   {result['host']}")
    for entry in results:
        observed = entry.get("observed")
        suffix = "" if observed is None else f" (observed: {observed})"
        print(f"  {entry['status'].upper():10} {entry['assertion']}  [{entry['method']}]{suffix}")
    print(f"STATUS {overall}")
    if overall == "incomplete":
        print()
        print("Unresolved assertions require a human verdict. Create manual-verdicts.json")
        print('in the run directory: {"<assertion>": {"status": "pass", "note": "evidence"}}')
    return 0 if overall == "pass" else 1


def cmd_aggregate(args: argparse.Namespace) -> int:
    runs_root = Path(args.runs).resolve()
    results = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(runs_root.rglob("result.json"))
    ]
    if not results:
        fail(f"no result.json found under {runs_root}")

    suite = load_suite()
    required_repeats = int((suite.get("execution") or {}).get("repeats_per_case", 1))

    by_case: dict = {}
    for item in results:
        by_case.setdefault(item["case_id"], []).append(item)

    cases = []
    for case_id, items in sorted(by_case.items()):
        statuses = [i["status"] for i in items]
        if len(items) < required_repeats:
            status = "incomplete"
            reason = f"{len(items)} of {required_repeats} required repeats"
        elif "fail" in statuses:
            status = "fail"
            reason = "at least one repeat failed a hard assertion"
        elif "incomplete" in statuses:
            status = "incomplete"
            reason = "at least one repeat has an unresolved assertion"
        else:
            status = "pass"
            reason = "all repeats passed every hard assertion"
        cases.append(
            {
                "case_id": case_id,
                "repeats": len(items),
                "required_repeats": required_repeats,
                "status": status,
                "reason": reason,
                "hosts": sorted({i.get("host", "unrecorded") for i in items}),
            }
        )

    executed = [c for c in cases if c["status"] == "pass"]
    aggregate = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "suite_id": suite.get("suite_id"),
        "fixture_sha256": suite["_fixture_sha256"],
        "cases_in_suite": len(suite.get("cases", [])),
        "cases_attempted": len(cases),
        "cases_passed": len(executed),
        "execution_status": "partial_execution" if cases else "specification_only_not_executed",
        "coverage_note": (
            f"{len(cases)} of {len(suite.get('cases', []))} specified cases were attempted. "
            "Unattempted cases remain specification only."
        ),
        "cases": cases,
    }
    Path(args.out).write_text(json.dumps(aggregate, indent=2), encoding="utf-8")
    print(json.dumps(aggregate, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p_mat = sub.add_parser("materialize", help="write a synthetic fixture repo for one case")
    p_mat.add_argument("--case", required=True)
    p_mat.add_argument("--out", required=True)
    p_mat.set_defaults(func=cmd_materialize)

    p_grade = sub.add_parser("grade", help="grade a completed run directory")
    p_grade.add_argument("--dir", required=True)
    p_grade.add_argument("--host", default="")
    p_grade.add_argument("--repeat", type=int, default=1)
    p_grade.set_defaults(func=cmd_grade)

    p_agg = sub.add_parser("aggregate", help="combine run results into one aggregate file")
    p_agg.add_argument("--runs", required=True)
    p_agg.add_argument("--out", required=True)
    p_agg.set_defaults(func=cmd_aggregate)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
