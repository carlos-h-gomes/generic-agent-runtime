#!/usr/bin/env python3
"""Read-only structural and semantic checks for GAR environment and promotion contracts."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import schema_lite


BOUNDARIES = ("identity", "secrets", "data", "storage", "network")
STAGING_EVIDENCE_STATES = {
    "staging_verified",
    "awaiting_production_approval",
    "production_approved",
    "promoted",
    "monitoring",
    "completed",
    "rolled_back",
}
PRODUCTION_STATES = {"promoted", "monitoring", "completed", "rolled_back"}
APPROVAL_STATES = PRODUCTION_STATES | {"production_approved"}


class ContractError(ValueError):
    """The input could not be parsed or did not match its JSON schema."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"JSON object required: {path}")
    return value


def validate_contract(value: dict[str, Any], schema_path: Path) -> None:
    schema = load_json(schema_path)
    try:
        schema_lite.check_schema(schema)
        schema_lite.validate(value, schema)
    except schema_lite.SchemaValidationError as exc:
        raise ContractError(f"schema validation failed: {exc}") from exc


def canonical_digest(value: dict[str, Any]) -> str:
    """Bind supplied evidence; the top-level schema location is transport metadata."""
    payload = {key: item for key, item in value.items() if key != "$schema"}
    return hashlib.sha256(json.dumps(
        payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")).hexdigest()


def evidence_time(value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ContractError("invalid evidence timestamp") from exc
    if parsed.tzinfo is None:
        raise ContractError("evidence timestamp must have a timezone")
    return parsed.astimezone(timezone.utc)


def check_parity(policy: dict[str, Any], now: datetime) -> tuple[list[str], list[str]]:
    blockers: list[str] = []
    incomplete: list[str] = []
    parity = policy["parity"]
    if parity is None:
        return [], ["reviewed structural parity evidence is missing"]
    if parity["policy_revision"] != policy["policy_revision"]:
        blockers.append("parity policy revision is stale")
    for field in ("reviewer", "reviewed_at", "evidence_ref"):
        if parity[field] is None:
            incomplete.append(f"parity.{field} is missing")
    reviewed_at = evidence_time(parity["reviewed_at"])
    if reviewed_at is not None and reviewed_at > now:
        blockers.append("parity review is in the future")
    for name in ("staging", "production"):
        binding = parity[name]
        for field in ("configuration_sha256", "topology_sha256"):
            if binding[field] is None:
                incomplete.append(f"parity.{name}.{field} is missing")
            elif binding[field] != policy["environments"][name][field]:
                blockers.append(f"parity.{name}.{field} does not match the observed environment")
        if binding["normalized_topology_sha256"] is None:
            incomplete.append(f"parity.{name} normalized topology is missing")
    if parity["staging"]["normalized_topology_sha256"] != parity["production"]["normalized_topology_sha256"]:
        blockers.append("normalized staging and production topology differ")
    observed = set(parity["observed_differences"])
    if not observed <= set(policy["allowed_structural_differences"]):
        blockers.append("parity contains undeclared structural differences")
    raw_differs = any(
        parity["staging"][field] != parity["production"][field]
        for field in ("configuration_sha256", "topology_sha256")
    )
    if raw_differs and not observed:
        blockers.append("different environment identities lack reviewed difference evidence")
    return blockers, incomplete


def check_policy(policy: dict[str, Any], *, require_ready: bool = False,
                 now: datetime | None = None) -> tuple[list[str], list[str]]:
    blockers: list[str] = []
    incomplete: list[str] = []
    if not require_ready:
        return blockers, incomplete

    if policy["status"] != "active":
        incomplete.append("environment policy is not active")
    if policy["project_id"] == "uninitialized-project":
        incomplete.append("project_id is not initialized")

    environments = policy["environments"]
    for name in ("staging", "production"):
        environment = environments[name]
        if environment["state"] != "verified":
            incomplete.append(f"{name} environment is not verified")
        for field in ("owner", "configuration_sha256", "topology_sha256", "capacity_class"):
            if environment[field] is None:
                incomplete.append(f"{name}.{field} is not recorded")

    for boundary in BOUNDARIES:
        if policy["isolation"][boundary] == "shared":
            blockers.append(f"{boundary} isolation is shared")
        elif policy["isolation"][boundary] == "unknown":
            incomplete.append(f"{boundary} isolation is unknown")
        field = f"{boundary}_boundary"
        staging_ref = environments["staging"][field]
        production_ref = environments["production"][field]
        if staging_ref is None or production_ref is None:
            incomplete.append(f"{boundary} boundary references are incomplete")
        elif staging_ref == production_ref:
            blockers.append(f"{boundary} boundary is shared between staging and production")

    staging_data = policy["staging_data"]
    if staging_data["strategy"] in {"unknown", "production_data_exception"}:
        exception_ref = staging_data["production_data_exception_ref"]
        if staging_data["strategy"] == "unknown":
            incomplete.append("staging data strategy is unknown")
        elif exception_ref is None:
            blockers.append("production-data staging strategy lacks an exception evidence reference")
    elif staging_data["production_data_exception_ref"] is not None:
        blockers.append("production_data_exception_ref is set for a non-exception staging strategy")

    if policy["cost_guardrails"]["status"] != "complete":
        incomplete.append("cost guardrails are not complete")
    parity_blockers, parity_incomplete = check_parity(policy, now or datetime.now(timezone.utc))
    blockers.extend(parity_blockers)
    incomplete.extend(parity_incomplete)
    return blockers, incomplete


def _require_identity(record: dict[str, Any], section_name: str, messages: list[str]) -> None:
    section = record[section_name]
    for field in ("artifact_sha256", "configuration_sha256", "migration_id"):
        if section[field] != record[field]:
            messages.append(f"{section_name}.{field} does not match the promotion identity")


def check_promotion(policy: dict[str, Any], record: dict[str, Any], *,
                    require_ready: bool = False, now: datetime | None = None) -> tuple[list[str], list[str]]:
    blockers: list[str] = []
    incomplete: list[str] = []
    state = record["state"]
    now = now or datetime.now(timezone.utc)
    staging = record["staging"]
    approval = record["approval"]
    production = record["production"]

    if record["project_id"] != policy["project_id"]:
        blockers.append("promotion project_id does not match the environment policy")
    if record["policy_revision"] != policy["policy_revision"]:
        blockers.append("promotion policy_revision does not match the environment policy")
    if record["environment_policy_sha256"] != canonical_digest(policy):
        blockers.append("promotion environment policy digest does not match current policy content")
    if require_ready and state not in APPROVAL_STATES:
        incomplete.append("promotion state is not production-approved or a deployed receipt")

    active_id = record["concurrency"]["active_production_promotion_id"]
    if active_id not in {None, record["promotion_id"]}:
        blockers.append("another production promotion is active")

    if state in STAGING_EVIDENCE_STATES or approval["status"] == "approved":
        policy_blockers, policy_incomplete = check_policy(policy, require_ready=True, now=now)
        blockers.extend(policy_blockers)
        incomplete.extend(policy_incomplete)
        _require_identity(record, "staging", blockers)
        if staging["deployment_id"] is None or staging["deployed_at"] is None:
            incomplete.append("staging deployment evidence is incomplete")
        if staging["tests"] != "passed":
            blockers.append("staging tests have not passed")
        if staging["gates"] != "passed":
            blockers.append("staging gates have not passed")
        if not staging["rollback_rehearsed"]:
            blockers.append("staging rollback was not rehearsed")
        for field in ("verified_at", "valid_until", "checks_evidence_ref"):
            if staging[field] is None:
                incomplete.append(f"staging.{field} is missing")

    if state in APPROVAL_STATES or approval["status"] == "approved":
        if approval["status"] != "approved" or approval["approver"] is None or approval["approved_at"] is None:
            blockers.append("exact production approval is incomplete")
        for field in ("artifact_sha256", "configuration_sha256", "migration_id", "policy_revision",
                      "environment_policy_sha256", "source_revision"):
            if approval[field] != record[field]:
                blockers.append(f"approval.{field} does not match the promotion identity")
        if approval["staging_evidence_sha256"] != canonical_digest(staging):
            blockers.append("approval staging evidence digest does not match the verified checks")
        for field in ("monitoring_owner", "monitoring_window_minutes", "rollback_plan_ref", "rollback_trigger"):
            if production[field] is None:
                incomplete.append(f"production.{field} is required before production approval")
        if not production["rollback_rehearsed"]:
            blockers.append("production recovery plan was not rehearsed")
        permitted_rollback = {"verified"} if state == "rolled_back" else {"available"}
        if production["rollback_status"] not in permitted_rollback:
            blockers.append("production recovery is not available or the rollback state is inconsistent")

    if state in PRODUCTION_STATES:
        _require_identity(record, "production", blockers)
        if production["deployment_id"] is None or production["deployed_at"] is None:
            incomplete.append("production deployment evidence is incomplete")
        if state != "rolled_back":
            for field in ("tests", "gates"):
                if production[field] in {"failed", "incomplete"}:
                    blockers.append(f"production {field} are {production[field]}")
            if production["smoke_check"] == "failed" or production["monitoring_status"] == "failed":
                blockers.append("production smoke or monitoring failed")
    elif state not in {"failed", "blocked_recovery"}:
        if production["deployed_at"] is not None or production["deployment_id"] is not None:
            blockers.append("production deployment evidence contradicts the undeployed state")

    if state in {"monitoring", "completed"}:
        for field in ("tests", "gates"):
            if production[field] != "passed":
                blockers.append(f"production {field} have not passed")
        if production["smoke_check"] != "passed":
            blockers.append("production smoke check has not passed")
        if production["monitoring_status"] not in {"active", "passed"}:
            blockers.append("production monitoring is not active or passed")

    if state == "completed":
        if production["monitoring_status"] != "passed":
            blockers.append("production monitoring has not passed")

    if state == "rolled_back" and record["production"]["rollback_status"] != "verified":
        blockers.append("rolled-back state lacks verified rollback evidence")
    if state == "blocked_recovery":
        blockers.append("recovery remains blocked")
    if require_ready and state in {"failed", "rejected"}:
        blockers.append("failed or rejected promotion is not production-ready")

    timeline = {
        "staging deployment": evidence_time(staging["deployed_at"]),
        "staging verification": evidence_time(staging["verified_at"]),
        "production approval": evidence_time(approval["approved_at"]),
        "production deployment": evidence_time(production["deployed_at"]),
    }
    observed = [(label, value) for label, value in timeline.items() if value is not None]
    for label, value in observed:
        if value > now:
            blockers.append(f"{label} is in the future")
    for (left_label, left), (right_label, right) in zip(observed, observed[1:]):
        if left > right:
            blockers.append(f"{left_label} occurs after {right_label}")
    parity = policy["parity"]
    reviewed_at = evidence_time(parity["reviewed_at"]) if parity is not None else None
    verified_at = timeline["staging verification"]
    if reviewed_at is not None and verified_at is not None and reviewed_at > verified_at:
        blockers.append("parity review postdates staging verification")
    valid_until = evidence_time(staging["valid_until"])
    if valid_until is not None:
        if verified_at is not None and verified_at >= valid_until:
            blockers.append("staging evidence has no positive validity window")
        for label in ("production approval", "production deployment"):
            value = timeline[label]
            if value is not None and value > valid_until:
                blockers.append(f"{label} is after staging evidence expired")
        if state in STAGING_EVIDENCE_STATES and state not in PRODUCTION_STATES and now > valid_until:
            blockers.append("staging evidence has expired for undeployed readiness")
    return list(dict.fromkeys(blockers)), list(dict.fromkeys(incomplete))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--promotion", type=Path)
    parser.add_argument("--require-production-ready", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    script_root = Path(__file__).resolve().parent.parent
    try:
        policy = load_json(args.policy)
        validate_contract(policy, script_root / "schemas" / "environment-policy.schema.json")
        blockers, incomplete = check_policy(policy, require_ready=args.require_production_ready)
        if args.promotion:
            promotion = load_json(args.promotion)
            validate_contract(promotion, script_root / "schemas" / "promotion-record.schema.json")
            promotion_blockers, promotion_incomplete = check_promotion(
                policy, promotion, require_ready=args.require_production_ready
            )
            blockers.extend(promotion_blockers)
            incomplete.extend(promotion_incomplete)
    except ContractError as exc:
        print(f"INVALID {exc}", file=sys.stderr)
        return 2

    blockers = list(dict.fromkeys(blockers))
    incomplete = list(dict.fromkeys(incomplete))
    for message in blockers:
        print(f"BLOCKER {message}", file=sys.stderr)
    for message in incomplete:
        print(f"INCOMPLETE {message}")
    if blockers:
        return 1
    if incomplete:
        return 3
    print("PASS environment and promotion contracts are structurally and semantically consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
