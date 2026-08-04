#!/usr/bin/env python3
"""Plan, apply, or verify a non-overwriting Harness adoption."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
from typing import Any

import schema_lite


ROOT = Path(__file__).resolve().parents[1]
DISCOVERY_MARKERS = (
    "package.json", "pyproject.toml", "requirements.txt", "Pipfile", "pom.xml",
    "build.gradle", "build.gradle.kts", "go.mod", "Cargo.toml", "composer.json",
    "Gemfile", "Dockerfile", "docker-compose.yml", "compose.yml", "src", "app",
    "backend", "frontend",
)


class AdoptionError(RuntimeError):
    pass


class AdoptionBlocked(AdoptionError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AdoptionError(f"JSON object required: {path}")
    return value


def is_reparse(path: Path) -> bool:
    attributes = getattr(path.lstat(), "st_file_attributes", 0)
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def portable_path(raw: str) -> PurePosixPath:
    value = PurePosixPath(raw)
    if (
        not raw
        or raw.startswith(("/", "\\"))
        or "\\" in raw
        or value.is_absolute()
        or ".." in value.parts
        or any(not part or any(ord(char) < 32 for char in part) for part in value.parts)
    ):
        raise AdoptionError(f"unsafe portable path: {raw!r}")
    return value


def contained(root: Path, raw: str) -> Path:
    value = portable_path(raw)
    candidate = (root / Path(*value.parts)).resolve(strict=False)
    resolved_root = root.resolve()
    try:
        candidate.relative_to(resolved_root)
    except ValueError as exc:
        raise AdoptionError(f"path escapes root: {raw}") from exc
    return candidate


def reject_linked_ancestors(root: Path, candidate: Path) -> None:
    root = root.resolve()
    current = candidate
    while True:
        if current.exists() and (current.is_symlink() or is_reparse(current)):
            raise AdoptionError(f"symlink or reparse path is not allowed: {current}")
        if current == root:
            return
        if root not in current.parents:
            raise AdoptionError(f"path escapes checked root: {candidate}")
        current = current.parent


def resolve_directory(path: Path, *, label: str) -> Path:
    resolved = path.resolve()
    if not resolved.is_dir():
        raise AdoptionError(f"{label} must be an existing directory: {resolved}")
    if resolved.is_symlink() or is_reparse(resolved):
        raise AdoptionError(f"{label} cannot be a symlink or reparse point: {resolved}")
    return resolved


def parse_manifest(source: Path, manifest_name: str) -> tuple[dict[str, str], bytes]:
    manifest_path = contained(source, manifest_name)
    text = manifest_path.read_bytes()
    recorded: dict[str, str] = {}
    for line in text.decode("utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            raise AdoptionError(f"invalid manifest line: {line!r}")
        name = portable_path(match.group(2)).as_posix()
        if name == manifest_name or name in recorded:
            raise AdoptionError(f"invalid or duplicate manifest entry: {name}")
        recorded[name] = match.group(1)
    if not recorded:
        raise AdoptionError("source manifest is empty")
    return recorded, text


def verify_source(source_raw: Path) -> dict:
    source = resolve_directory(source_raw, label="source")
    if (source / ".harness-source").exists():
        raise AdoptionError("adoption must run from a clean portable distribution, not maintainer source")
    harness = load_object(source / "harness.json")
    distribution = harness.get("distribution") or {}
    manifest_name = distribution.get("manifest", "MANIFEST.sha256")
    recorded, manifest_bytes = parse_manifest(source, manifest_name)
    policy = load_object(source / "adoption-policy.json")
    if policy.get("schema_version") != "1.0" or policy.get("harness_version") != harness.get("version"):
        raise AdoptionError("adoption policy version does not match Harness")
    required = {"harness.json", "adoption-policy.json", "scripts/adopt_harness.py"}
    if not required.issubset(recorded):
        raise AdoptionError(f"portable distribution is missing adoption files: {sorted(required - recorded.keys())}")
    limits = harness.get("archive_limits") or {}
    total = 0
    files: dict[str, bytes] = {}
    for name, expected in sorted(recorded.items()):
        path = contained(source, name)
        reject_linked_ancestors(source, path)
        if not path.is_file():
            raise AdoptionError(f"manifest file is missing: {name}")
        content = path.read_bytes()
        if len(content) > limits.get("max_member_uncompressed_bytes", 8 * 1024 * 1024):
            raise AdoptionError(f"source member exceeds limit: {name}")
        total += len(content)
        if digest_bytes(content) != expected:
            raise AdoptionError(f"source manifest hash mismatch: {name}")
        files[name] = content
    if total > limits.get("max_total_uncompressed_bytes", 64 * 1024 * 1024):
        raise AdoptionError("source distribution exceeds aggregate size limit")
    source_fingerprint = digest_bytes(manifest_bytes + canonical({"version": harness.get("version")}))
    return {
        "root": source,
        "harness": harness,
        "policy": policy,
        "recorded": recorded,
        "files": files,
        "fingerprint": source_fingerprint,
    }


def ownership(name: str, policy: dict) -> str | None:
    if name in policy.get("excluded_files", []):
        return None
    if name in policy.get("shared_files", []):
        return "shared"
    if name in policy.get("project_owned_files", []):
        return "project"
    if name in policy.get("harness_owned_files", []):
        return "harness"
    matches: list[str] = []
    if any(name.startswith(prefix) for prefix in policy.get("project_owned_prefixes", [])):
        matches.append("project")
    if any(name.startswith(prefix) for prefix in policy.get("harness_owned_prefixes", [])):
        matches.append("harness")
    if len(matches) > 1:
        raise AdoptionError(f"ambiguous ownership classification: {name}")
    if matches:
        return matches[0]
    raise AdoptionError(f"unclassified distribution path: {name}")


def existing_version(target: Path) -> str | None:
    path = target / "harness.json"
    if not path.is_file() or path.is_symlink() or is_reparse(path):
        return None
    try:
        manifest = load_object(path)
    except (OSError, UnicodeError, json.JSONDecodeError, AdoptionError):
        return None
    if manifest.get("name") != "generic-agent-runtime" or not isinstance(manifest.get("distribution"), dict):
        return None
    required_markers = (
        target / "scripts" / "runtime_check.py",
        target / ".agents" / "skills" / "core" / "task-triage" / "SKILL.md",
        target / "docs" / "harness" / "INSTALL.md",
    )
    if not all(item.is_file() and not item.is_symlink() and not is_reparse(item) for item in required_markers):
        return None
    value = manifest.get("version")
    return value if isinstance(value, str) and re.fullmatch(r"\d+\.\d+\.\d+", value) else None


def version_tuple(value: str) -> tuple[int, int, int]:
    if not re.fullmatch(r"\d+\.\d+\.\d+", value):
        raise AdoptionError(f"invalid semantic version: {value}")
    return tuple(int(part) for part in value.split("."))  # type: ignore[return-value]


def target_has_user_content(target: Path) -> bool:
    ignored = {".git", ".gitignore", ".gitattributes", ".gitkeep"}
    return any(item.name not in ignored for item in target.iterdir())


def classify(source_version: str, target: Path, requested: str) -> tuple[str, str, str, str, str | None]:
    found = existing_version(target)
    if found is None:
        harness_posture = "absent" if not (target / "harness.json").exists() else "modified_or_unknown"
    elif found == source_version:
        harness_posture = "current"
    elif version_tuple(found) < version_tuple(source_version) and version_tuple(found) >= (4, 2, 0):
        harness_posture = "prior_supported"
    else:
        harness_posture = "modified_or_unknown"

    if requested == "auto":
        mode = "upgrade" if found else ("brownfield" if target_has_user_content(target) else "greenfield")
    else:
        mode = requested
    if mode == "greenfield" and target_has_user_content(target):
        raise AdoptionBlocked("greenfield mode requires an empty target apart from Git metadata")
    if mode == "upgrade" and harness_posture not in {"current", "prior_supported"}:
        raise AdoptionBlocked("upgrade mode requires a readable current or supported prior Harness")

    hybrid_dirs = [
        "backend/app/controllers", "backend/app/services", "backend/app/models", "backend/app/schemas",
        "backend/app/repositories", "frontend/src/api", "frontend/src/components", "frontend/src/pages",
    ]
    if all((target / item).is_dir() for item in hybrid_dirs):
        application = "python_react_hybrid"
    elif any((target / item).exists() for item in DISCOVERY_MARKERS):
        application = "observed"
    elif not target_has_user_content(target):
        application = "empty"
    else:
        application = "unknown"

    if mode == "greenfield":
        disposition = "initialize_target"
    elif mode == "upgrade" or application == "python_react_hybrid":
        disposition = "preserve"
    elif application in {"observed", "unknown"}:
        disposition = "profile_required"
    else:
        disposition = "preserve"
    return mode, harness_posture, application, disposition, found


def state_for(path: Path) -> str | None:
    if not path.exists():
        return None
    if path.is_symlink() or is_reparse(path) or not path.is_file():
        return "non_regular"
    return digest_bytes(path.read_bytes())


def fingerprint_target(target: Path, names: list[str]) -> str:
    inventory: list[list[str | None]] = []
    for name in sorted(set([*names, *DISCOVERY_MARKERS])):
        path = contained(target, name)
        reject_linked_ancestors(target, path)
        if path.is_dir() and not path.is_symlink() and not is_reparse(path):
            value = "directory"
        else:
            value = state_for(path)
        inventory.append([name, value])
    return digest_bytes(canonical(inventory))


def plan_digest(plan: dict) -> str:
    unsigned = dict(plan)
    unsigned.pop("plan_digest", None)
    return digest_bytes(canonical(unsigned))


def build_plan(
    source_data: dict,
    target_raw: Path,
    requested_mode: str,
    accepted_shared: set[str] | None = None,
) -> dict:
    target = resolve_directory(target_raw, label="target")
    accepted_shared = accepted_shared or set()
    for name in accepted_shared:
        portable_path(name)
        if ownership(name, source_data["policy"]) != "shared":
            raise AdoptionError(f"--accept-shared is allowed only for a declared shared file: {name}")
    source_version = source_data["harness"]["version"]
    mode, harness_posture, application, disposition, found = classify(source_version, target, requested_mode)
    operations: list[dict] = []
    conflicts: list[str] = []
    approvals: set[str] = set()
    accepted_used: set[str] = set()
    names: list[str] = []
    for name, content in sorted(source_data["files"].items()):
        owner = ownership(name, source_data["policy"])
        if owner is None:
            continue
        names.append(name)
        destination = contained(target, name)
        reject_linked_ancestors(target, destination)
        target_hash = state_for(destination)
        source_hash = digest_bytes(content)
        if mode == "brownfield" and disposition == "profile_required" and name == "docs/ai/architecture-policy.json":
            action, reason = "skip", "brownfield architecture requires evidence-backed project profiling"
        elif target_hash is None:
            action, reason = "create", f"missing {owner}-owned file"
        elif target_hash == source_hash:
            action, reason = "preserve", "existing file is byte-identical"
        elif owner == "project":
            action, reason = "preserve", "project-owned content is never overwritten"
        elif owner == "shared" and name in accepted_shared:
            action, reason = "preserve", "operator marked this exact target hash as reconciled shared content"
            accepted_used.add(name)
        elif owner == "shared":
            action, reason = "conflict", "differing shared content requires deliberate reconciliation"
        elif harness_posture == "prior_supported" and mode == "upgrade":
            action, reason = "replace", "approved prior-Harness upgrade may replace Harness-owned content"
            approvals.add("replace_harness_owned")
        else:
            action, reason = "conflict", "Harness ownership is not established for differing existing content"
        if action == "conflict":
            conflicts.append(name)
        operations.append({
            "path": name, "ownership": owner, "action": action, "content_source": "distribution",
            "source_sha256": source_hash, "target_sha256": target_hash, "reason": reason,
        })

    unused_acceptance = accepted_shared - accepted_used
    if unused_acceptance:
        raise AdoptionError(
            "--accept-shared requires differing existing shared content: "
            + ", ".join(sorted(unused_acceptance))
        )

    state_name = ".harness/adoption-state.json"
    names.append(state_name)
    state_hash = state_for(contained(target, state_name))
    if state_hash is None:
        state_action, state_reason = "create", "record verified local adoption identity"
    elif mode == "upgrade" and harness_posture == "prior_supported":
        state_action, state_reason = "replace", "update prior adoption identity after approved upgrade"
        approvals.add("replace_harness_owned")
    else:
        state_action, state_reason = "conflict", "existing adoption state must be reconciled before replacement"
        conflicts.append(state_name)
    operations.append({
        "path": state_name, "ownership": "generated", "action": state_action, "content_source": "generated",
        "source_sha256": None, "target_sha256": state_hash, "reason": state_reason,
    })

    target_fingerprint = fingerprint_target(target, names)
    seed = canonical({"source": source_data["fingerprint"], "target": str(target), "target_fingerprint": target_fingerprint, "mode": mode})
    plan_id = "adopt-" + digest_bytes(seed)[:16]
    status = "blocked" if conflicts else ("awaiting_approval" if approvals else "ready")
    plan = {
        "$schema": "schemas/adoption-plan.schema.json",
        "schema_version": "1.0",
        "plan_id": plan_id,
        "status": status,
        "source": {
            "version": source_version,
            "archive": source_data["harness"]["distribution"]["archive"],
            "manifest": source_data["harness"]["distribution"]["manifest"],
        },
        "target": {"identifier": str(target), "existing_harness_version": found},
        "adoption_mode": mode,
        "harness_posture": harness_posture,
        "application_posture": application,
        "architecture_disposition": disposition,
        "operations": operations,
        "conflicts": sorted(conflicts),
        "reconciled_shared": sorted(accepted_used),
        "approvals": sorted(approvals),
        "source_fingerprint": source_data["fingerprint"],
        "target_fingerprint": target_fingerprint,
        "plan_digest": "",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    plan["plan_digest"] = plan_digest(plan)
    return plan


def validate_plan(plan: dict, schema_path: Path) -> None:
    schema = load_object(schema_path)
    schema_lite.check_schema(schema)
    schema_lite.validate(plan, schema)
    if plan.get("plan_digest") != plan_digest(plan):
        raise AdoptionError("plan digest does not match plan content")


def write_exclusive(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(content)


def adoption_state(plan: dict) -> bytes:
    value = {
        "schema_version": "1.0",
        "status": "applied",
        "harness_version": plan["source"]["version"],
        "adoption_mode": plan["adoption_mode"],
        "harness_posture_before": plan["harness_posture"],
        "application_posture": plan["application_posture"],
        "architecture_disposition": plan["architecture_disposition"],
        "source_fingerprint": plan["source_fingerprint"],
        "plan_id": plan["plan_id"],
        "plan_digest": plan["plan_digest"],
        "applied_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8") + b"\n"


def apply_plan(source_data: dict, target_raw: Path, plan: dict, *, approve_replace: bool) -> None:
    target = resolve_directory(target_raw, label="target")
    if str(target) != plan["target"]["identifier"]:
        raise AdoptionError("plan target does not match requested target")
    if plan["source_fingerprint"] != source_data["fingerprint"]:
        raise AdoptionError("plan source fingerprint does not match current distribution")
    names = [item["path"] for item in plan["operations"]]
    if fingerprint_target(target, names) != plan["target_fingerprint"]:
        raise AdoptionBlocked("target changed after plan; generate and review a new plan")
    if plan["conflicts"] or plan["status"] == "blocked":
        raise AdoptionBlocked("plan contains conflicts; reconcile them and generate a new plan")
    if "replace_harness_owned" in plan["approvals"] and not approve_replace:
        raise AdoptionBlocked("Harness-owned replacements require --approve-replace")

    writes: list[tuple[dict, Path, bytes]] = []
    for item in plan["operations"]:
        path = contained(target, item["path"])
        reject_linked_ancestors(target, path)
        current = state_for(path)
        if current != item["target_sha256"]:
            raise AdoptionBlocked(f"destination drift before apply: {item['path']}")
        if item["action"] in {"preserve", "skip"}:
            continue
        if item["action"] not in {"create", "replace"}:
            raise AdoptionBlocked(f"non-applicable operation blocks apply: {item['path']}")
        if item["content_source"] == "distribution":
            content = source_data["files"].get(item["path"])
            if content is None or digest_bytes(content) != item["source_sha256"]:
                raise AdoptionError(f"planned source content is unavailable: {item['path']}")
        else:
            content = adoption_state(plan)
        writes.append((item, path, content))

    created: list[Path] = []
    replaced: list[tuple[Path, Path]] = []
    rollback_root = contained(target, f".harness/rollback/{plan['plan_digest']}")
    try:
        for item, path, content in writes:
            if item["action"] == "create":
                write_exclusive(path, content)
                created.append(path)
                continue
            backup = contained(rollback_root, item["path"])
            reject_linked_ancestors(target, backup)
            write_exclusive(backup, path.read_bytes())
            temp = path.with_name(f".{path.name}.{plan['plan_digest'][:12]}.tmp")
            reject_linked_ancestors(target, temp)
            write_exclusive(temp, content)
            os.replace(temp, path)
            replaced.append((path, backup))
    except OSError as exc:
        rollback_errors: list[str] = []
        for path in reversed(created):
            try:
                if path.is_file() and not path.is_symlink():
                    path.unlink()
            except OSError as rollback_exc:
                rollback_errors.append(f"remove {path}: {rollback_exc}")
        for path, backup in reversed(replaced):
            try:
                temp = path.with_name(f".{path.name}.rollback.tmp")
                write_exclusive(temp, backup.read_bytes())
                os.replace(temp, path)
            except OSError as rollback_exc:
                rollback_errors.append(f"restore {path}: {rollback_exc}")
        suffix = f"; rollback errors: {'; '.join(rollback_errors)}" if rollback_errors else ""
        raise AdoptionError(f"apply failed and rollback was attempted: {exc}{suffix}") from exc


def verify_installation(source_data: dict, target_raw: Path) -> list[str]:
    target = resolve_directory(target_raw, label="target")
    errors: list[str] = []
    state_path = target / ".harness" / "adoption-state.json"
    try:
        state = load_object(state_path)
    except (OSError, UnicodeError, json.JSONDecodeError, AdoptionError) as exc:
        return [f"adoption state is missing or invalid: {exc}"]
    if state.get("harness_version") != source_data["harness"].get("version"):
        errors.append("installed Harness version does not match source")
    if state.get("source_fingerprint") != source_data["fingerprint"]:
        errors.append("installed source fingerprint does not match source")
    for name, content in sorted(source_data["files"].items()):
        owner = ownership(name, source_data["policy"])
        if owner != "harness":
            continue
        path = contained(target, name)
        reject_linked_ancestors(target, path)
        if state_for(path) != digest_bytes(content):
            errors.append(f"Harness-owned file missing or changed: {name}")
    return errors


def save_plan(path_raw: Path, plan: dict) -> None:
    path = path_raw.resolve(strict=False)
    parent = path.parent.resolve()
    if not parent.is_dir() or parent.is_symlink() or is_reparse(parent):
        raise AdoptionError(f"plan output parent must be an existing safe directory: {parent}")
    reject_linked_ancestors(parent, path)
    write_exclusive(path, json.dumps(plan, indent=2, ensure_ascii=False).encode("utf-8") + b"\n")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--source", type=Path, default=ROOT)
    result.add_argument("--schema", type=Path, default=ROOT / "schemas" / "adoption-plan.schema.json")
    sub = result.add_subparsers(dest="command", required=True)
    plan = sub.add_parser("plan")
    plan.add_argument("--target", type=Path, required=True)
    plan.add_argument("--mode", choices=("auto", "greenfield", "brownfield", "upgrade"), default="auto")
    plan.add_argument("--accept-shared", action="append", default=[], metavar="PATH")
    plan.add_argument("--out", type=Path)
    apply = sub.add_parser("apply")
    apply.add_argument("--target", type=Path, required=True)
    apply.add_argument("--plan", type=Path, required=True)
    apply.add_argument("--approve-replace", action="store_true")
    verify = sub.add_parser("verify")
    verify.add_argument("--target", type=Path, required=True)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        source_data = verify_source(args.source)
        schema_path = args.schema.resolve()
        if args.command == "plan":
            plan = build_plan(source_data, args.target, args.mode, set(args.accept_shared))
            validate_plan(plan, schema_path)
            if args.out:
                save_plan(args.out, plan)
            print(json.dumps(plan, indent=2, ensure_ascii=False))
            return 3 if plan["status"] in {"blocked", "awaiting_approval"} else 0
        if args.command == "apply":
            plan = load_object(args.plan.resolve())
            validate_plan(plan, schema_path)
            apply_plan(source_data, args.target, plan, approve_replace=args.approve_replace)
            print(f"PASS Harness adoption applied: {args.target.resolve()}")
            return 0
        errors = verify_installation(source_data, args.target)
        if errors:
            for error in errors:
                print(f"INCOMPLETE Harness adoption: {error}", file=sys.stderr)
            return 3
        print(f"PASS Harness adoption verified: {args.target.resolve()}")
        return 0
    except AdoptionBlocked as exc:
        print(f"INCOMPLETE Harness adoption: {exc}", file=sys.stderr)
        return 3
    except (AdoptionError, OSError, UnicodeError, json.JSONDecodeError, schema_lite.SchemaValidationError, ValueError, KeyError, TypeError) as exc:
        print(f"FAIL Harness adoption: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
