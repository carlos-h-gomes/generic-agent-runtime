#!/usr/bin/env python3
"""Structural and archive validation for the Generic Agent Runtime."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import stat
import subprocess
import sys
import unicodedata
import zipfile
from pathlib import Path, PurePosixPath

import schema_lite

PLACEHOLDERS = {"see above", "tbd", "todo", "n/a", "na", "placeholder"}
GATE_IDS = {
    "architecture_uml",
    "code_quality_testing",
    "ux_product",
    "security_compliance",
    "data_integration",
    "finops",
    "observability_release",
    "ai_llm",
}
TASK_STATES = {
    "draft",
    "ready",
    "needs_input",
    "awaiting_approval",
    "in_progress",
    "validation_failed",
    "blocked_external",
    "paused_for_review",
    "ready_for_review",
    "done",
}
READ_ONLY_MODES = {"answer", "inspect", "diagnose", "review"}
GATE_STATES = {"passed", "passed_with_conditions", "blocked", "not_applicable"}


class Report:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.passes: list[str] = []
        self.skips: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        (self.passes if condition else self.failures).append(message)

    def skip(self, message: str) -> None:
        self.skips.append(message)

    def emit(self) -> int:
        for message in self.passes:
            print(f"PASS {message}")
        for message in self.skips:
            print(f"SKIP {message}")
        for message in self.failures:
            print(f"FAIL {message}", file=sys.stderr)
        print(f"SUMMARY pass={len(self.passes)} skip={len(self.skips)} fail={len(self.failures)}")
        return 1 if self.failures else 0


def load_json(path: Path, report: Report) -> dict | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        report.failures.append(f"JSON parse {path}: {exc}")
        return None
    if not isinstance(value, dict):
        report.failures.append(f"JSON object required: {path}")
        return None
    return value


def has_placeholder(value: object) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in PLACEHOLDERS
    if isinstance(value, list):
        return any(has_placeholder(item) for item in value)
    if isinstance(value, dict):
        return any(has_placeholder(item) for item in value.values())
    return False


def validate_task(path: Path, task: dict, report: Report) -> None:
    required = {
        "schema_version",
        "task_id",
        "status",
        "mode",
        "outcome",
        "acceptance_criteria",
        "scope",
        "risk",
        "authorization",
        "files",
        "gates",
        "skills",
        "approvals",
        "context",
        "coordination",
        "validation",
        "next_action",
    }
    label = path.as_posix()
    report.check(required.issubset(task), f"task required fields: {label}")
    report.check(task.get("schema_version") == "1.0", f"task contract version 1.0: {label}")
    report.check(task.get("status") in TASK_STATES, f"task state is canonical: {label}")
    report.check(not has_placeholder(task), f"task has no placeholder values: {label}")
    criteria = task.get("acceptance_criteria")
    report.check(isinstance(criteria, list) and bool(criteria) and all(isinstance(item, str) and item.strip() for item in criteria), f"task has observable criteria: {label}")

    authorization = task.get("authorization") or {}
    writes = authorization.get("writes") or {}
    if task.get("mode") in READ_ONLY_MODES:
        report.check(writes.get("allowed") is False, f"read-only task forbids writes: {label}")
    files = task.get("files") or {}
    if task.get("mode") == "change":
        discoverable = bool(files.get("owned") or files.get("discover"))
        report.check(writes.get("allowed") is True and discoverable, f"change task has write authority and file scope: {label}")

    scope = task.get("scope") or {}
    context = task.get("context") or {}
    if task.get("work_level") in {2, 3} or scope.get("size") in {"cross_boundary", "system"}:
        report.check(bool(context.get("task_file")), f"persistent task has Markdown context pointer: {label}")
        gate_ids = [gate.get("id") for gate in task.get("gates", []) if isinstance(gate, dict)]
        report.check(set(gate_ids) == GATE_IDS, f"cross-boundary task records every canonical gate: {label}")

    gates = task.get("gates") or []
    gate_ids: list[str] = []
    gates_valid = isinstance(gates, list)
    for gate in gates if isinstance(gates, list) else []:
        if not isinstance(gate, dict):
            gates_valid = False
            continue
        gate_ids.append(gate.get("id"))
        if gate.get("id") not in GATE_IDS or not str(gate.get("reason", "")).strip():
            gates_valid = False
        if gate.get("status") in {"not_applicable", "deferred"} and not gate.get("reason"):
            gates_valid = False
        if gate.get("status") == "deferred" and not gate.get("owner"):
            gates_valid = False
    report.check(gates_valid and len(gate_ids) == len(set(gate_ids)), f"task gates are unique and reasoned: {label}")

    validation = task.get("validation") or {}
    report.check(isinstance(validation.get("max_attempts"), int) and validation.get("max_attempts") >= 1, f"task validation attempt limit is explicit: {label}")
    gaps = validation.get("not_validated") or []
    gaps_ok = isinstance(gaps, list) and all(
        isinstance(gap, dict)
        and gap.get("disposition") in {"out_of_scope", "accepted_residual", "blocked"}
        and bool(gap.get("area"))
        and bool(gap.get("reason"))
        and (gap.get("disposition") != "accepted_residual" or bool(gap.get("acceptance_ref")))
        for gap in gaps
    )
    report.check(gaps_ok, f"task validation gaps are typed and scoped: {label}")
    if task.get("status") == "done":
        report.check(bool(validation.get("evidence")), f"done task records positive validation evidence: {label}")
        completed_gates = all(
            isinstance(gate, dict)
            and gate.get("status") in {"passed", "passed_with_conditions", "not_applicable"}
            and (gate.get("status") == "not_applicable" or bool(gate.get("artifact")))
            for gate in gates
        )
        approvals_closed = all(
            isinstance(approval, dict) and approval.get("status") in {"not_required", "approved"}
            for approval in (task.get("approvals") or [])
        )
        report.check(completed_gates and approvals_closed, f"done task has resolved gates and approvals: {label}")


def validate_gate_result(path: Path, gate: dict, report: Report) -> None:
    label = path.as_posix()
    required = {
        "schema_version",
        "task_id",
        "gate",
        "phase",
        "revision",
        "status",
        "applicability",
        "summary",
        "checks",
        "findings",
        "evidence",
        "approval",
        "generated_at",
    }
    report.check(required.issubset(gate), f"GateResult required fields: {label}")
    status = gate.get("status")
    report.check(gate.get("schema_version") == "1.0" and gate.get("gate") in GATE_IDS and status in GATE_STATES, f"GateResult identity/status is canonical: {label}")
    applicability = gate.get("applicability") or {}
    report.check(applicability.get("applicable") is (status != "not_applicable"), f"GateResult applicability matches status: {label}")
    checks = gate.get("checks") or []
    evidence = gate.get("evidence") or []
    findings = gate.get("findings") or []
    if status in {"passed", "passed_with_conditions"}:
        checks_ok = bool(checks) and all(item.get("status") in {"passed", "not_applicable"} for item in checks if isinstance(item, dict))
        blockers = [item for item in findings if isinstance(item, dict) and item.get("blocking") and item.get("state") == "open"]
        report.check(checks_ok and bool(evidence) and not blockers, f"passing GateResult has checks, evidence, and no open blocker: {label}")
    if status == "passed":
        unresolved = [item for item in findings if isinstance(item, dict) and item.get("state") in {"open", "deferred"}]
        report.check(not unresolved, f"passed GateResult has no unresolved condition: {label}")
    refs_ok = True
    for finding in findings if isinstance(findings, list) else []:
        if not isinstance(finding, dict):
            refs_ok = False
        elif finding.get("state") == "risk_accepted" and not finding.get("risk_acceptance_ref"):
            refs_ok = False
        elif finding.get("state") == "deferred" and (not finding.get("owner") or finding.get("blocking")):
            refs_ok = False
    approval = gate.get("approval") or {}
    if approval.get("required") is True and approval.get("status") == "not_required":
        refs_ok = False
    if approval.get("required") is False and approval.get("status") != "not_required":
        refs_ok = False
    if approval.get("status") == "approved" and not approval.get("evidence_ref"):
        refs_ok = False
    report.check(refs_ok, f"GateResult approvals and condition ownership are consistent: {label}")


def skill_frontmatter(path: Path) -> tuple[str | None, str | None]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return None, None
    name = re.search(r"^name:\s*([^\n]+)$", match.group(1), re.MULTILINE)
    description = re.search(r'^description:\s*["\']?(.+?)["\']?$', match.group(1), re.MULTILINE)
    return (name.group(1).strip() if name else None, description.group(1).strip() if description else None)


def validate_json_schemas(
    root: Path,
    schema_paths: list[Path],
    manifest: dict,
    tasks: list[tuple[Path, dict]],
    gates: list[tuple[Path, dict]],
    report: Report,
    strict: bool,
) -> None:
    schemas: dict[str, dict] = {}
    try:
        for path in schema_paths:
            schema = json.loads(path.read_text(encoding="utf-8"))
            schemas[path.name] = schema
            schema_lite.check_schema(schema)
        security_policy = json.loads((root / "security-policy.json").read_text(encoding="utf-8"))
        ui_review = json.loads((root / "docs" / "ai" / "ui-review.json").read_text(encoding="utf-8"))
        target_example = json.loads(
            (root / "security" / "examples" / "authorized-target.example.json").read_text(encoding="utf-8")
        )
        plan_example = json.loads(
            (root / "security" / "examples" / "loopback-plan.json").read_text(encoding="utf-8")
        )
        maintainer_marker = manifest.get("distribution", {}).get("maintainer_marker", ".harness-source")
        architecture_path = (
            root / "scaffold" / "docs" / "ai" / "architecture-policy.json"
            if (root / maintainer_marker).is_file()
            else root / "docs" / "ai" / "architecture-policy.json"
        )
        architecture_policy = json.loads(architecture_path.read_text(encoding="utf-8"))
        project_template = json.loads(
            (root / "project-templates" / "python-react-hybrid" / "template-manifest.json").read_text(encoding="utf-8")
        )
        for _path, task in tasks:
            schema_lite.validate(task, schemas["task-contract.schema.json"])
        for _path, gate in gates:
            schema_lite.validate(gate, schemas["gate-result.schema.json"])
        schema_lite.validate(manifest, schemas["harness.schema.json"])
        schema_lite.validate(security_policy, schemas["security-policy.schema.json"])
        schema_lite.validate(ui_review, schemas["ui-review.schema.json"])
        schema_lite.validate(target_example, schemas["authorized-target.schema.json"])
        schema_lite.validate(plan_example, schemas["security-test-plan.schema.json"])
        schema_lite.validate(architecture_policy, schemas["architecture-policy.schema.json"])
        schema_lite.validate(project_template, schemas["project-template.schema.json"])
        template = json.loads((root / "docs" / "ai" / "tasks" / "_GATE_RESULT_TEMPLATE.json").read_text(encoding="utf-8"))
        schema_lite.validate(template, schemas["gate-result.schema.json"])
    except Exception as exc:
        report.failures.append(f"bundled JSON Schema validation: {exc}")
        return
    report.passes.append(
        f"bundled contract validation ({len(schema_paths)} schemas, {len(tasks)} tasks, "
        f"{len(gates)} gate results, policy, UI, target, plan, manifest, template)"
    )

    try:
        import jsonschema  # type: ignore
    except ImportError:
        report.skip("optional jsonschema meta-schema validator absent; bundled contract validator passed")
        return
    try:
        format_checker = jsonschema.FormatChecker()
        for schema in schemas.values():
            jsonschema.Draft202012Validator.check_schema(schema)
        for path, task in tasks:
            jsonschema.Draft202012Validator(schemas["task-contract.schema.json"], format_checker=format_checker).validate(task)
        for path, gate in gates:
            jsonschema.Draft202012Validator(schemas["gate-result.schema.json"], format_checker=format_checker).validate(gate)
        jsonschema.Draft202012Validator(schemas["harness.schema.json"], format_checker=format_checker).validate(manifest)
        jsonschema.Draft202012Validator(schemas["security-policy.schema.json"], format_checker=format_checker).validate(security_policy)
        jsonschema.Draft202012Validator(schemas["ui-review.schema.json"], format_checker=format_checker).validate(ui_review)
        jsonschema.Draft202012Validator(schemas["authorized-target.schema.json"], format_checker=format_checker).validate(target_example)
        jsonschema.Draft202012Validator(schemas["security-test-plan.schema.json"], format_checker=format_checker).validate(plan_example)
        jsonschema.Draft202012Validator(schemas["architecture-policy.schema.json"], format_checker=format_checker).validate(architecture_policy)
        jsonschema.Draft202012Validator(schemas["project-template.schema.json"], format_checker=format_checker).validate(project_template)
        jsonschema.Draft202012Validator(schemas["gate-result.schema.json"], format_checker=format_checker).validate(template)
    except Exception as exc:  # jsonschema exposes several validation exception types
        report.failures.append(f"JSON Schema validation: {exc}")
    else:
        report.passes.append(
            f"optional JSON Schema 2020-12 meta-validation ({len(schema_paths)} schemas and instances)"
        )


def source_checks(root: Path, report: Report, static_only: bool, strict: bool) -> dict | None:
    manifest_path = root / "harness.json"
    manifest = load_json(manifest_path, report)
    if not manifest:
        return None

    maintainer_marker = manifest.get("distribution", {}).get("maintainer_marker", ".harness-source")
    maintainer_source = (root / maintainer_marker).is_file()
    required_paths = [
        "AGENTS.md",
        "CLAUDE.md",
        "GEMINI.md",
        "harness.json",
        "schemas/harness.schema.json",
        "schemas/task-contract.schema.json",
        "schemas/gate-result.schema.json",
        "schemas/bridge-event.schema.json",
        "scripts/runtime_check.py",
        "scripts/bridge.py",
        "scripts/safe_exec.py",
        "scripts/project_checks.py",
        "scripts/security_assurance.py",
        "scripts/adversarial_lab.py",
        "scripts/ui_quality.py",
        "scripts/architecture_check.py",
        "scripts/bootstrap_project.py",
        "scripts/documentation_check.py",
        "scripts/schema_lite.py",
        "security-policy.json",
        "schemas/security-policy.schema.json",
        "schemas/authorized-target.schema.json",
        "schemas/security-test-plan.schema.json",
        "schemas/ui-review.schema.json",
        "schemas/architecture-policy.schema.json",
        "schemas/project-template.schema.json",
        "docs/ai/ui-review.json",
        "docs/ai/threat-model.md",
        "docs/ai/incident-response.md",
        "docs/harness/MIGRATION-4.2-5.0.md",
        "docs/harness/SECURITY-MODEL.md",
        "docs/harness/SECURITY-OPERATIONS.md",
        "docs/harness/ADVERSARIAL-TESTING.md",
        "docs/harness/UI-QUALITY.md",
        "docs/harness/QUALIFICATION-5.0.md",
        "docs/harness/MIGRATION-5.0-6.0.md",
        "docs/harness/QUALIFICATION-6.0.md",
        "docs/harness/HYBRID-ARCHITECTURE.md",
        "docs/harness/PROJECT-TRUTH.md",
        "docs/harness/DOCUMENTATION-LIFECYCLE.md",
        "project-templates/python-react-hybrid/template-manifest.json",
        "docs/harness/evaluation-suite.md",
        "docs/harness/evaluation-cases.json",
        "docs/harness/evaluation-fixtures.json",
    ]
    if maintainer_source:
        required_paths += [maintainer_marker, "README.md", "CHANGELOG.md", "scripts/package_runtime.py", "scaffold/docs/ai/constitution.md"]
    else:
        required_paths += ["docs/harness/INSTALL.md", "docs/harness/CHANGELOG.md"]
    missing = [item for item in required_paths if not (root / item).is_file()]
    report.check(not missing, f"required source files present{': ' + ', '.join(missing) if missing else ''}")
    if missing:
        return manifest

    report.check(bool(re.fullmatch(r"\d+\.\d+\.\d+", str(manifest.get("version", "")))), "manifest uses semantic version")
    report.check(manifest.get("contract_versions") == {"task": "1.0", "gate_result": "1.0", "bridge_event": "2.0"}, "manifest contract versions preserve v4.2 compatibility")
    report.check(
        manifest.get("policy_versions")
        == {
            "security": "1.0",
            "authorized_target": "1.0",
            "security_test_plan": "1.0",
            "ui_review": "1.0",
            "architecture_policy": "1.0",
            "project_template": "1.0",
            "source_of_truth": "1.0",
            "release_documentation": "1.0",
        },
        "manifest policy versions are canonical",
    )

    evaluation = load_json(root / "docs" / "harness" / "evaluation-cases.json", report)
    fixtures_path = root / "docs" / "harness" / "evaluation-fixtures.json"
    fixtures = load_json(fixtures_path, report)
    evaluation_ok = bool(
        evaluation
        and fixtures
        and evaluation.get("execution_status") == "specification_only_not_executed"
        and evaluation.get("suite_id") == "harness-v6-behavior-1"
        and len(evaluation.get("cases") or []) >= 27
        and evaluation.get("fixture", {}).get("revision") == fixtures.get("fixture_revision")
        and evaluation.get("fixture", {}).get("sha256") == hashlib.sha256(fixtures_path.read_bytes()).hexdigest()
    )
    report.check(evaluation_ok, "behavioral evaluation manifest pins synthetic fixtures, prompts, assertions, repeats, and thresholds")

    agents = (root / "AGENTS.md").read_bytes()
    line_count = len(agents.decode("utf-8").splitlines())
    budget = manifest.get("instruction_budget") or {}
    report.check(len(agents) <= budget.get("agents_md_max_bytes", 0), f"AGENTS.md byte budget ({len(agents)}/{budget.get('agents_md_max_bytes')})")
    report.check(line_count <= budget.get("agents_md_max_lines", 0), f"AGENTS.md line budget ({line_count}/{budget.get('agents_md_max_lines')})")
    report.check(b"Version: 6.0" in agents, "AGENTS.md version matches release family")
    claude = (root / "CLAUDE.md").read_text(encoding="utf-8")
    report.check("@AGENTS.md" in claude and len(claude.encode("utf-8")) <= 4096, "CLAUDE.md is a thin AGENTS adapter")
    gemini = (root / "GEMINI.md").read_text(encoding="utf-8")
    report.check("@AGENTS.md" in gemini and len(gemini.encode("utf-8")) <= 4096, "GEMINI.md is a thin AGENTS adapter")

    schema_paths = [
        root / "schemas" / name
        for name in (
            "harness.schema.json",
            "task-contract.schema.json",
            "gate-result.schema.json",
            "bridge-event.schema.json",
            "security-policy.schema.json",
            "authorized-target.schema.json",
            "security-test-plan.schema.json",
            "ui-review.schema.json",
            "architecture-policy.schema.json",
            "project-template.schema.json",
        )
    ]
    schemas_ok = True
    for path in schema_paths:
        value = load_json(path, report)
        if not value or value.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            schemas_ok = False
    report.check(schemas_ok, "all schemas declare JSON Schema 2020-12")

    expected_groups = {
        "core": set(manifest.get("core_skills") or []),
        "specialists": set(manifest.get("specialist_skills") or []),
    }
    inventory_ok = True
    for group, expected in expected_groups.items():
        base = root / ".agents" / "skills" / group
        actual = {item.name for item in base.iterdir() if item.is_dir() and (item / "SKILL.md").is_file()} if base.exists() else set()
        if actual != expected:
            inventory_ok = False
            report.failures.append(f"{group} skill inventory mismatch: expected {sorted(expected)}, found {sorted(actual)}")
        for name in actual:
            found_name, description = skill_frontmatter(base / name / "SKILL.md")
            if found_name != name or not description:
                inventory_ok = False
                report.failures.append(f"invalid skill frontmatter: {group}/{name}")
            policy_path = base / name / "agents" / "openai.yaml"
            if not policy_path.is_file():
                inventory_ok = False
                report.failures.append(f"missing skill invocation policy: {group}/{name}")
            elif name not in {"implementation", "project-profiling", "validation"} and "allow_implicit_invocation: false" not in policy_path.read_text(encoding="utf-8"):
                inventory_ok = False
                report.failures.append(f"heavy skill must be explicit-only: {group}/{name}")
            if description and len(description) > 240:
                inventory_ok = False
                report.failures.append(f"skill description exceeds 240 characters: {group}/{name}")
    report.check(inventory_ok, "skill inventory and frontmatter match manifest")

    python_ok = True
    for path in sorted((root / "scripts").glob("*.py")):
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeError) as exc:
            python_ok = False
            report.failures.append(f"Python syntax {path}: {exc}")
    report.check(python_ok, "Python scripts parse without generating cache files")

    canonical_files = [root / "AGENTS.md", root / "CLAUDE.md"]
    canonical_files += list((root / ".agents" / "skills").glob("*/*/SKILL.md"))
    canonical_files += list((root / "prompt-templates").glob("*.txt"))
    canonical_files += [
        root / "docs" / "ai" / "quality-gates.md",
        root / "docs" / "ai" / "release-checklist.md",
        root / "docs" / "ai" / "standards.md",
        root / "docs" / "ai" / "conventions.md",
    ]
    forbidden = {"prompt injection is prevented", "prompt injection prevented", "checkout tested end-to-end in production with a real card"}
    unsafe: list[str] = []
    for path in canonical_files:
        text = path.read_text(encoding="utf-8").lower()
        for phrase in forbidden:
            if phrase in text:
                unsafe.append(f"{path.relative_to(root)}: {phrase}")
    report.check(not unsafe, f"canonical guidance avoids unsafe absolute claims{': ' + '; '.join(unsafe) if unsafe else ''}")

    tasks: list[tuple[Path, dict]] = []
    for path in sorted((root / "docs" / "ai" / "tasks").glob("*.task.json")):
        if path.name.startswith("_"):
            continue
        task = load_json(path, report)
        if task:
            tasks.append((path.relative_to(root), task))
            validate_task(path.relative_to(root), task, report)
    if maintainer_source:
        report.check(bool(tasks), "at least one active machine task contract is present in maintainer source")
    elif not tasks:
        report.skip("fresh distribution has no active task contract yet")
    gates: list[tuple[Path, dict]] = []
    for path in sorted((root / "docs" / "ai" / "tasks").glob("*.gates/*.json")):
        gate = load_json(path, report)
        if gate:
            relative = path.relative_to(root)
            gates.append((relative, gate))
            validate_gate_result(relative, gate, report)
    validate_json_schemas(root, schema_paths, manifest, tasks, gates, report, strict)

    if not static_only:
        bridge = subprocess.run(
            [sys.executable, str(root / "scripts" / "bridge.py"), "--root", str(root), "doctor"],
            text=True,
            capture_output=True,
            check=False,
            timeout=15,
        )
        report.check(bridge.returncode == 0, f"bridge doctor{': ' + (bridge.stderr.strip() or bridge.stdout.strip()) if bridge.returncode else ''}")
    return manifest


def safe_zip_name(name: str) -> bool:
    path = PurePosixPath(name)
    canonical = PurePosixPath(name.rstrip("/")).as_posix() + ("/" if name.endswith("/") else "")
    return (
        bool(name)
        and not name.startswith(("/", "\\"))
        and "\\" not in name
        and ".." not in path.parts
        and not re.match(r"^[A-Za-z]:", name)
        and not any(ord(char) < 32 for char in name)
        and name == unicodedata.normalize("NFC", name)
        and name == canonical
    )


def archive_checks(root: Path, archive: Path, manifest: dict | None, report: Report) -> None:
    if not archive.is_file():
        report.failures.append(f"archive not found: {archive}")
        return
    try:
        with zipfile.ZipFile(archive) as package:
            infos = package.infolist()
            limits = (manifest or {}).get("archive_limits") or {
                "max_entries": 2048,
                "max_name_length": 240,
                "max_member_uncompressed_bytes": 8388608,
                "max_total_uncompressed_bytes": 67108864,
                "max_compression_ratio": 200,
            }
            regular_infos = [item for item in infos if not item.is_dir()]
            total_size = sum(item.file_size for item in regular_infos)
            resource_bounds_ok = (
                len(infos) <= limits["max_entries"]
                and all(len(item.filename) <= limits["max_name_length"] for item in infos)
                and all(
                    0 <= item.file_size <= limits["max_member_uncompressed_bytes"]
                    for item in regular_infos
                )
                and total_size <= limits["max_total_uncompressed_bytes"]
                and all(
                    item.file_size == 0
                    or (
                        item.compress_size > 0
                        and item.file_size / item.compress_size <= limits["max_compression_ratio"]
                    )
                    for item in regular_infos
                )
            )
            report.check(
                resource_bounds_ok,
                "archive entry, name, member, aggregate, and compression-ratio bounds",
            )
            if not resource_bounds_ok:
                return
            all_names = [item.filename for item in infos]
            names = [item.filename for item in infos if not item.is_dir()]
            entry_types_ok = True
            for item in infos:
                mode = item.external_attr >> 16
                if mode and not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
                    entry_types_ok = False
            report.check(
                len(all_names) == len(set(all_names)) and all(safe_zip_name(name) for name in all_names) and entry_types_ok,
                "archive paths and entry types are unique and traversal-safe",
            )
            metadata_ok = package.comment == b"" and all(
                not (item.flag_bits & 0x1)
                and item.compress_type in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}
                and item.extra == b""
                and item.comment == b""
                for item in infos
            )
            report.check(
                names == sorted(names) and len({name.casefold() for name in all_names}) == len(all_names) and metadata_ok,
                "archive entries and metadata are deterministic and portable",
            )
            required = {
                "AGENTS.md",
                "CLAUDE.md",
                "GEMINI.md",
                "harness.json",
                "MANIFEST.sha256",
                "SBOM.cdx.json",
                "PROVENANCE.intoto.json",
                "security-policy.json",
                "docs/harness/INSTALL.md",
                "docs/harness/CHANGELOG.md",
                "docs/harness/MIGRATION-4.2-5.0.md",
                "docs/harness/SECURITY-MODEL.md",
                "docs/harness/SECURITY-OPERATIONS.md",
                "docs/harness/ADVERSARIAL-TESTING.md",
                "docs/harness/UI-QUALITY.md",
                "docs/harness/QUALIFICATION-5.0.md",
                "docs/harness/MIGRATION-5.0-6.0.md",
                "docs/harness/QUALIFICATION-6.0.md",
                "docs/harness/HYBRID-ARCHITECTURE.md",
                "docs/harness/PROJECT-TRUTH.md",
                "docs/harness/DOCUMENTATION-LIFECYCLE.md",
                "SOURCE-OF-TRUTH.md",
                "docs/TECHNICAL-DOCUMENTATION.md",
                "docs/USER-MANUAL.md",
                "docs/architecture/DIRECTORY-MAP.md",
                "schemas/task-contract.schema.json",
                "schemas/security-policy.schema.json",
                "schemas/authorized-target.schema.json",
                "schemas/security-test-plan.schema.json",
                "schemas/ui-review.schema.json",
                "schemas/architecture-policy.schema.json",
                "schemas/project-template.schema.json",
                ".agents/skills/core/task-triage/SKILL.md",
                "docs/ai/constitution.md",
                "docs/ai/quality-gates.md",
                "docs/ai/ui-review.json",
                "docs/ai/threat-model.md",
                "docs/ai/incident-response.md",
                "docs/ai/architecture-policy.json",
                "docs/ai/tasks/_TASK_TEMPLATE.md",
                "docs/ai/bridge/ledger.jsonl",
                "scripts/bridge.py",
                "scripts/security_assurance.py",
                "scripts/adversarial_lab.py",
                "scripts/ui_quality.py",
                "scripts/architecture_check.py",
                "scripts/bootstrap_project.py",
                "scripts/documentation_check.py",
                "project-templates/python-react-hybrid/template-manifest.json",
                "prompt-templates/09-generate-python-react-application.txt",
            }
            report.check(required.issubset(names), "archive contains the portable runtime and clean memory templates")
            report.check("README.md" not in names and "CHANGELOG.md" not in names, "archive does not overwrite a consumer project's root README or changelog")
            excluded = [
                name
                for name in names
                if name.startswith("scaffold/")
                or re.match(r"docs/ai/tasks/20\d\d-", name)
                or name.endswith(("ledger-archive.jsonl", ".bridge.lock", ".pyc"))
                or "__pycache__" in name
                or name.endswith(".zip")
            ]
            report.check(not excluded, f"archive excludes maintainer/live/generated state{': ' + ', '.join(excluded) if excluded else ''}")
            ledger = package.read("docs/ai/bridge/ledger.jsonl") if "docs/ai/bridge/ledger.jsonl" in names else b"missing"
            report.check(ledger == b"", "packaged bridge ledger is empty")

            manifest_name = (manifest or {}).get("distribution", {}).get("manifest", "MANIFEST.sha256")
            manifest_lines = package.read(manifest_name).decode("utf-8").splitlines()
            recorded: dict[str, str] = {}
            manifest_valid = True
            for line in manifest_lines:
                if "  " not in line:
                    manifest_valid = False
                    continue
                digest, name = line.split("  ", 1)
                if not re.fullmatch(r"[0-9a-f]{64}", digest) or name in recorded:
                    manifest_valid = False
                recorded[name] = digest
            expected_names = set(names) - {manifest_name}
            if set(recorded) != expected_names:
                manifest_valid = False
            for name, digest in recorded.items():
                if hashlib.sha256(package.read(name)).hexdigest() != digest:
                    manifest_valid = False
            report.check(manifest_valid, "MANIFEST.sha256 exactly covers and verifies archive files")

            released = (manifest or {}).get("released")
            if released and re.fullmatch(r"\d{4}-\d{2}-\d{2}", released):
                year, month, day = map(int, released.split("-"))
                report.check(all(item.date_time[:3] == (year, month, day) for item in infos), "archive timestamps use the release date")
            package_manifest = json.loads(package.read("harness.json"))
            report.check(not manifest or package_manifest.get("version") == manifest.get("version"), "archive manifest version matches source")
            sbom = json.loads(package.read("SBOM.cdx.json"))
            report.check(
                sbom.get("bomFormat") == "CycloneDX"
                and sbom.get("specVersion") == "1.7"
                and sbom.get("metadata", {}).get("component", {}).get("version") == package_manifest.get("version"),
                "archive CycloneDX SBOM identifies the release",
            )
            provenance = json.loads(package.read("PROVENANCE.intoto.json"))
            report.check(
                provenance.get("_type") == "https://in-toto.io/Statement/v1"
                and provenance.get("predicateType") == "https://slsa.dev/provenance/v1"
                and bool(provenance.get("subject")),
                "archive contains deterministic SLSA-shaped provenance",
            )
    except (OSError, UnicodeError, json.JSONDecodeError, zipfile.BadZipFile, KeyError) as exc:
        report.failures.append(f"archive validation failed: {exc}")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    result.add_argument("--static", action="store_true", help="skip live bridge doctor")
    result.add_argument("--strict", action="store_true", help="run release-grade bundled contract validation")
    result.add_argument("--archive", type=Path, help="also verify a built distribution archive")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = args.root.resolve()
    report = Report()
    manifest = source_checks(root, report, args.static, args.strict)
    if args.archive:
        archive = args.archive if args.archive.is_absolute() else root / args.archive
        archive_checks(root, archive, manifest, report)
    return report.emit()


if __name__ == "__main__":
    raise SystemExit(main())
