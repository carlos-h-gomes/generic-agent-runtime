#!/usr/bin/env python3
"""Inventory, plan, apply, verify, and restore reversible local archive bundles."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


RUNTIME_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_POLICY = RUNTIME_ROOT / "workspace-hygiene-policy.json"
ARCHIVE_ID = re.compile(r"^arc-[0-9]{8}T[0-9]{6}Z-[a-z0-9][a-z0-9-]{0,47}$")
PLAN_ID = re.compile(r"^plan-[a-f0-9]{16}$")


class HygieneError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


def write_atomic(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        temporary.write_bytes(json_bytes(value))
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def append_jsonl(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def append_jsonl_atomic(path: Path, value: object, max_bytes: int) -> None:
    """Append one bounded JSONL event without leaving a partial record."""
    existing = path.read_bytes() if path.exists() else b""
    record = (json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    if len(existing) + len(record) > max_bytes:
        raise HygieneError(f"archive index exceeds {max_bytes} bytes: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        with temporary.open("wb") as handle:
            handle.write(existing)
            handle.write(record)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def read_index_events(path: Path, max_bytes: int) -> list[dict]:
    if not path.is_file() or path.stat().st_size > max_bytes:
        return []
    events = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            value = json.loads(line)
            if not isinstance(value, dict):
                return []
            events.append(value)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return []
    return events


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise HygieneError(f"invalid JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise HygieneError(f"{path} must contain a JSON object")
    return value


def load_policy(path: Path) -> dict:
    policy = load_json(path)
    required = {
        "$schema", "schema_version", "archive_directory", "index_file", "manifest_file", "journal_file",
        "payload_directory", "default_mode", "follow_links", "automatic_purge", "classification",
        "protected_exact", "protected_prefixes", "protected_names", "protected_suffixes", "sensitive_names",
        "sensitive_suffixes", "reference_extensions", "max_reference_file_bytes", "max_hash_file_bytes",
        "max_index_file_bytes", "active_discovery_excludes", "restore_overwrite",
    }
    if set(policy) != required:
        raise HygieneError("workspace hygiene policy fields do not match contract")
    if policy.get("schema_version") != "1.0" or policy.get("archive_directory") != "_archives":
        raise HygieneError("unsupported workspace hygiene policy")
    if policy.get("follow_links") is not False or policy.get("automatic_purge") is not False or policy.get("restore_overwrite") is not False:
        raise HygieneError("policy must deny link following and automatic purge")
    classification = policy.get("classification")
    if not isinstance(classification, dict) or classification.get("unknown_state") != "protected" or classification.get("age_alone_is_sufficient") is not False:
        raise HygieneError("workspace hygiene classification policy is unsafe")
    list_fields = (
        "protected_exact", "protected_prefixes", "protected_names", "protected_suffixes", "sensitive_names",
        "sensitive_suffixes", "reference_extensions", "active_discovery_excludes",
    )
    if any(not isinstance(policy.get(field), list) for field in list_fields):
        raise HygieneError("workspace hygiene policy list field is invalid")
    if any(not isinstance(policy.get(field), int) or policy[field] < 1024 for field in ("max_reference_file_bytes", "max_hash_file_bytes", "max_index_file_bytes")):
        raise HygieneError("workspace hygiene policy size limit is invalid")
    return policy


def root_path(raw: Path) -> Path:
    expanded = raw.expanduser().absolute()
    if is_link(expanded):
        raise HygieneError("workspace root cannot be a symlink or reparse point")
    root = expanded.resolve()
    if not root.is_dir():
        raise HygieneError(f"workspace root is not a directory: {root}")
    return root


def is_link(path: Path) -> bool:
    try:
        information = path.lstat()
    except OSError:
        return False
    attributes = getattr(information, "st_file_attributes", 0)
    return path.is_symlink() or bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def safe_relative(raw: str) -> str:
    normalized = raw.replace("\\", "/")
    path = PurePosixPath(normalized)
    if not normalized or path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise HygieneError(f"unsafe relative path: {raw!r}")
    if any(not part or any(ord(char) < 32 for char in part) for part in path.parts):
        raise HygieneError(f"unsafe relative path: {raw!r}")
    return path.as_posix()


def within(root: Path, relative: str) -> Path:
    relative = safe_relative(relative)
    candidate = root.joinpath(*PurePosixPath(relative).parts)
    try:
        candidate.resolve(strict=False).relative_to(root)
    except ValueError as exc:
        raise HygieneError(f"path escapes workspace: {relative}") from exc
    return candidate


def relative_name(root: Path, path: Path) -> str:
    return PurePosixPath(*path.relative_to(root).parts).as_posix()


def has_link_component(root: Path, path: Path) -> bool:
    current = root
    for part in path.relative_to(root).parts:
        current = current / part
        if current.exists() and is_link(current):
            return True
    return False


def iter_files(root: Path, policy: dict, *, include_archives: bool = False) -> list[Path]:
    archive_name = policy["archive_directory"]
    files: list[Path] = []
    for current, directories, names in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        kept = []
        for name in sorted(directories):
            child = current_path / name
            if is_link(child):
                continue
            if name == archive_name and not include_archives:
                continue
            kept.append(name)
        directories[:] = kept
        for name in sorted(names):
            path = current_path / name
            if not is_link(path) and path.is_file():
                files.append(path)
    return sorted(files, key=lambda item: relative_name(root, item))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def file_entries(root: Path, candidate: Path) -> list[dict]:
    if has_link_component(root, candidate):
        raise HygieneError(f"links and reparse points are protected: {relative_name(root, candidate)}")
    if candidate.is_file():
        paths = [candidate]
    elif candidate.is_dir():
        paths = []
        for current, directories, names in os.walk(candidate, topdown=True, followlinks=False):
            current_path = Path(current)
            for name in list(directories):
                child = current_path / name
                if is_link(child):
                    raise HygieneError(f"archive candidate contains a link: {relative_name(root, child)}")
            for name in names:
                child = current_path / name
                if is_link(child) or not child.is_file():
                    raise HygieneError(f"archive candidate contains an unsupported entry: {relative_name(root, child)}")
                paths.append(child)
    else:
        raise HygieneError(f"archive candidate does not exist: {relative_name(root, candidate)}")
    if not paths:
        raise HygieneError(f"empty directories are not archive candidates: {relative_name(root, candidate)}")
    return [
        {"path": relative_name(root, path), "size": path.stat().st_size, "sha256": sha256_file(path)}
        for path in sorted(paths, key=lambda item: relative_name(root, item))
    ]


def workspace_fingerprint(root: Path, policy: dict) -> str:
    digest = hashlib.sha256()
    for path in iter_files(root, policy):
        relative = relative_name(root, path)
        if relative.endswith(".archive-plan.json"):
            continue
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(path.stat().st_size).encode("ascii"))
        digest.update(b"\0")
        digest.update(sha256_file(path).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def task_status(path: Path) -> str | None:
    if not path.name.endswith(".task.json"):
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return value.get("status") if isinstance(value, dict) and isinstance(value.get("status"), str) else None


def protection_reason(root: Path, path: Path, relative: str, policy: dict) -> str | None:
    parts = PurePosixPath(relative).parts
    if policy["archive_directory"] in parts:
        return "existing archive material"
    if has_link_component(root, path):
        return "symlink or reparse boundary"
    lower = relative.lower()
    exact = {item.lower() for item in policy["protected_exact"]}
    if lower in exact or any(lower.startswith(item.rstrip("/").lower() + "/") for item in exact):
        return "default protected authority or runtime path"
    if any(lower.startswith(prefix.lower()) for prefix in policy["protected_prefixes"]):
        return "default protected runtime prefix"
    basename = path.name.lower()
    if basename in {name.lower() for name in policy["protected_names"]}:
        return "default protected authority, release, or dependency file"
    if any(basename.endswith(suffix.lower()) for suffix in policy["protected_suffixes"]):
        return "default protected release or dependency artifact"
    if basename.startswith(".env") or basename in {name.lower() for name in policy["sensitive_names"]}:
        return "secret or credential class requires containment, not archive"
    if any(basename.endswith(suffix.lower()) for suffix in policy["sensitive_suffixes"]):
        return "sensitive or live-state file class requires a separate procedure"
    if relative.startswith("docs/ai/tasks/") and path.is_file() and path.name.endswith(".task.json"):
        status = task_status(path)
        if status != "done":
            return f"task contract is not done (status={status or 'unknown'})"
    return None


def active_references(root: Path, candidate_relative: str, candidate: Path, policy: dict, ignored: set[Path] | None = None) -> list[str]:
    ignored = {item.resolve(strict=False) for item in (ignored or set())}
    references = []
    needle = candidate_relative.replace("\\", "/")
    for path in iter_files(root, policy):
        resolved = path.resolve(strict=False)
        if resolved in ignored or path == candidate or candidate in path.parents:
            continue
        if path.name.endswith(".archive-plan.json"):
            continue
        if path.suffix.lower() not in policy["reference_extensions"] or path.stat().st_size > policy["max_reference_file_bytes"]:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        if needle in text:
            references.append(relative_name(root, path))
    return sorted(set(references))


def inventory(root: Path, policy: dict) -> dict:
    records = []
    duplicate_candidates: dict[tuple[int, str], list[int]] = {}
    max_hash = int(policy["max_hash_file_bytes"])
    for path in iter_files(root, policy, include_archives=True):
        relative = relative_name(root, path)
        parts = PurePosixPath(relative).parts
        if policy["archive_directory"] in parts and policy["payload_directory"] in parts:
            records.append({"path": relative, "state": "archived", "reason": "archive payload", "size": path.stat().st_size})
            continue
        reason = protection_reason(root, path, relative, policy)
        status = task_status(path)
        if reason:
            state = "protected"
            state_reason = reason
        elif status == "done":
            state = "archive_candidate"
            state_reason = "task_done"
        elif "reference" in {part.lower() for part in parts[:-1]}:
            state = "reference"
            state_reason = "documented reference location"
        else:
            state = "active"
            state_reason = "no positive inactivity evidence"
        record = {"path": relative, "state": state, "reason": state_reason, "size": path.stat().st_size}
        if path.stat().st_size <= max_hash:
            record["sha256"] = sha256_file(path)
            duplicate_candidates.setdefault((record["size"], record["sha256"]), []).append(len(records))
        records.append(record)
    duplicate_groups = []
    for (size, digest), indexes in duplicate_candidates.items():
        if len(indexes) < 2:
            continue
        paths = [records[index]["path"] for index in indexes]
        duplicate_groups.append({"size": size, "sha256": digest, "paths": paths})
        canonical = paths[0]
        for index in indexes[1:]:
            if records[index]["state"] == "active":
                records[index]["state"] = "archive_candidate"
                records[index]["reason"] = f"exact_duplicate; canonical={canonical}"
    return {
        "schema_version": "1.0",
        "generated_at": utc_now(),
        "workspace_root": str(root),
        "default_mode": "plan_only",
        "automatic_purge": False,
        "active_discovery_excludes": policy["active_discovery_excludes"],
        "counts": {state: sum(1 for item in records if item["state"] == state) for state in policy["classification"]["states"]},
        "duplicate_groups": sorted(duplicate_groups, key=lambda item: item["paths"]),
        "items": records,
    }


def slug_value(raw: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")[:48]
    if not slug:
        raise HygieneError("archive slug must contain a letter or digit")
    return slug


def build_plan(args: argparse.Namespace, root: Path, policy: dict) -> dict:
    if not args.out.name.endswith(".archive-plan.json"):
        raise HygieneError("plan output must end with .archive-plan.json so it stays outside workspace fingerprints")
    candidates = [safe_relative(value) for value in args.candidate]
    if len(candidates) != len(set(name.lower() for name in candidates)):
        raise HygieneError("duplicate or case-aliased candidate path")
    evidence = sorted(set(args.evidence or []))
    allowed_evidence = set(policy["classification"]["positive_candidate_signals"])
    if not evidence or any(item not in allowed_evidence for item in evidence):
        raise HygieneError(f"classification evidence must come from {sorted(allowed_evidence)}")
    confidence = str(args.confidence).lower()
    if confidence not in {"low", "medium", "high"}:
        raise HygieneError("confidence must be low, medium, or high")
    owner = str(args.owner).strip()
    if len(owner) < 2:
        raise HygieneError("plan requires a concrete owner")
    reason = str(args.reason).strip()
    if len(reason) < 8:
        raise HygieneError("plan requires a concrete reason")
    retained_canonical = safe_relative(args.retained_canonical) if args.retained_canonical else None
    supersedes = sorted({safe_relative(value) for value in (args.supersedes or [])})
    if "exact_duplicate" in evidence and not retained_canonical:
        raise HygieneError("exact_duplicate evidence requires --retained-canonical")
    if "explicitly_superseded" in evidence and not supersedes:
        raise HygieneError("explicitly_superseded evidence requires --supersedes")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive_id = args.archive_id or f"arc-{timestamp}-{slug_value(args.slug)}"
    if not ARCHIVE_ID.fullmatch(archive_id):
        raise HygieneError("invalid archive id")
    items = []
    roots = set()
    candidate_paths = []
    for relative in candidates:
        path = within(root, relative)
        if not path.exists():
            raise HygieneError(f"candidate does not exist: {relative}")
        protection = protection_reason(root, path, relative, policy)
        if protection:
            raise HygieneError(f"protected candidate {relative}: {protection}")
        candidate_paths.append((relative, path))
    for index, (left, _) in enumerate(candidate_paths):
        left_path = PurePosixPath(left)
        for right, _ in candidate_paths[index + 1 :]:
            right_path = PurePosixPath(right)
            if left_path in right_path.parents or right_path in left_path.parents:
                raise HygieneError("candidate paths cannot overlap")
    for relative, path in candidate_paths:
        references = active_references(root, relative, path, policy)
        if references:
            raise HygieneError(f"active references block {relative}: {references}")
        if retained_canonical:
            canonical = within(root, retained_canonical)
            if not canonical.is_file() or not path.is_file():
                raise HygieneError("retained canonical duplicate checks require files")
            if canonical.stat().st_size != path.stat().st_size or sha256_file(canonical) != sha256_file(path):
                raise HygieneError(f"retained canonical is not an exact duplicate of {relative}")
        if relative == retained_canonical or relative in supersedes:
            raise HygieneError("candidate cannot be its own canonical or superseding target")
        parent_relative = relative_name(root, path.parent) if path.parent != root else ""
        archive_root = f"{parent_relative + '/' if parent_relative else ''}{policy['archive_directory']}"
        roots.add(archive_root)
        destination = f"{archive_root}/{archive_id}/{policy['payload_directory']}/{relative}"
        items.append(
            {
                "source": relative,
                "destination": destination,
                "kind": "directory" if path.is_dir() else "file",
                "classification": "archive_candidate",
                "classification_reason": reason,
                "confidence": confidence,
                "classification_evidence": evidence,
                "references_checked": references,
                "retained_canonical": retained_canonical,
                "supersedes": supersedes,
                "restore_consequence": f"Restore returns {relative} only when the original path is collision-free.",
                "entries": file_entries(root, path),
            }
        )
    if len(roots) != 1:
        raise HygieneError(f"one bundle must have one ownership boundary; resolved archive roots: {sorted(roots)}")
    base = {
        "schema_version": "1.0",
        "created_at": utc_now(),
        "workspace_root": str(root),
        "workspace_fingerprint": workspace_fingerprint(root, policy),
        "archive_id": archive_id,
        "archive_root": roots.pop(),
        "owner": owner,
        "reason": reason,
        "authorization_required": True,
        "items": items,
        "exclusions": ["purge", "overwrite", "links", "external paths", "active references", "protected material"],
        "rollback": "Reverse completed journaled moves in order; never overwrite a live source path.",
        "restore": "Restore requires separate authorization, unchanged payload hashes, and collision-free original paths.",
    }
    identifier = hashlib.sha256(json_bytes(base)).hexdigest()[:16]
    return {"$schema": "schemas/archive-plan.schema.json", "plan_id": f"plan-{identifier}", **base}


def validate_plan(plan: dict, root: Path, policy: dict) -> None:
    if plan.get("schema_version") != "1.0" or not PLAN_ID.fullmatch(str(plan.get("plan_id", ""))):
        raise HygieneError("unsupported or invalid archive plan")
    if not ARCHIVE_ID.fullmatch(str(plan.get("archive_id", ""))):
        raise HygieneError("invalid archive id in plan")
    if plan.get("authorization_required") is not True or not isinstance(plan.get("items"), list) or not plan["items"]:
        raise HygieneError("archive plan lacks authorization or items")
    allowed_keys = {
        "$schema", "plan_id", "schema_version", "created_at", "workspace_root", "workspace_fingerprint",
        "archive_id", "archive_root", "owner", "reason", "authorization_required", "items", "exclusions",
        "rollback", "restore",
    }
    if set(plan) != allowed_keys:
        raise HygieneError("archive plan fields do not match contract")
    base = {key: value for key, value in plan.items() if key not in {"$schema", "plan_id"}}
    expected_id = f"plan-{hashlib.sha256(json_bytes(base)).hexdigest()[:16]}"
    if plan["plan_id"] != expected_id:
        raise HygieneError("archive plan digest does not match its contents")
    if Path(str(plan["workspace_root"])).resolve() != root:
        raise HygieneError("plan targets a different workspace root")
    if not re.fullmatch(r"[a-f0-9]{64}", str(plan.get("workspace_fingerprint", ""))):
        raise HygieneError("invalid workspace fingerprint in plan")
    if len(str(plan.get("owner", "")).strip()) < 2 or len(str(plan.get("reason", "")).strip()) < 8:
        raise HygieneError("archive plan lacks owner or reason")
    archive_root = safe_relative(str(plan["archive_root"]))
    archive_parts = PurePosixPath(archive_root).parts
    if archive_parts[-1] != policy["archive_directory"] or archive_parts.count(policy["archive_directory"]) != 1:
        raise HygieneError("plan archive root is not one strategic _archives boundary")
    exclusions = ["purge", "overwrite", "links", "external paths", "active references", "protected material"]
    if plan.get("exclusions") != exclusions:
        raise HygieneError("archive plan exclusions were changed")
    allowed_evidence = set(policy["classification"]["positive_candidate_signals"])
    sources: list[str] = []
    destinations: set[str] = set()
    expected_item_keys = {
        "source", "destination", "kind", "classification", "classification_reason", "confidence",
        "classification_evidence", "references_checked", "retained_canonical", "supersedes",
        "restore_consequence", "entries",
    }
    for item in plan["items"]:
        if not isinstance(item, dict) or set(item) != expected_item_keys:
            raise HygieneError("archive plan item fields do not match contract")
        source = safe_relative(str(item["source"]))
        destination = safe_relative(str(item["destination"]))
        expected_destination = PurePosixPath(
            archive_root, plan["archive_id"], policy["payload_directory"], source
        ).as_posix()
        if destination != expected_destination or destination.lower() in destinations:
            raise HygieneError("archive plan destination is invalid or duplicated")
        destinations.add(destination.lower())
        if item.get("kind") not in {"file", "directory"} or item.get("classification") != "archive_candidate":
            raise HygieneError("archive plan item classification is invalid")
        evidence = item.get("classification_evidence")
        if not isinstance(evidence, list) or not evidence or any(value not in allowed_evidence for value in evidence):
            raise HygieneError("archive plan item evidence is invalid")
        if item.get("confidence") not in {"low", "medium", "high"}:
            raise HygieneError("archive plan item confidence is invalid")
        if item.get("classification_reason") != plan["reason"]:
            raise HygieneError("archive plan item reason does not match plan")
        if not isinstance(item.get("references_checked"), list) or not isinstance(item.get("supersedes"), list):
            raise HygieneError("archive plan item reference metadata is invalid")
        canonical = item.get("retained_canonical")
        if canonical is not None:
            canonical = safe_relative(str(canonical))
        if "exact_duplicate" in evidence and not canonical:
            raise HygieneError("exact duplicate plan item lacks retained canonical")
        if "explicitly_superseded" in evidence and not item["supersedes"]:
            raise HygieneError("superseded plan item lacks superseding pointer")
        for value in item["supersedes"]:
            safe_relative(str(value))
        entries = item.get("entries")
        if not isinstance(entries, list) or not entries:
            raise HygieneError("archive plan item has no file entries")
        for entry in entries:
            if not isinstance(entry, dict) or set(entry) != {"path", "size", "sha256"}:
                raise HygieneError("archive plan file entry is invalid")
            entry_path = safe_relative(str(entry["path"]))
            if PurePosixPath(source) != PurePosixPath(entry_path) and PurePosixPath(source) not in PurePosixPath(entry_path).parents:
                raise HygieneError("archive plan file entry escapes its source")
            if not isinstance(entry["size"], int) or entry["size"] < 0 or not re.fullmatch(r"[a-f0-9]{64}", str(entry["sha256"])):
                raise HygieneError("archive plan file entry metadata is invalid")
        sources.append(source)
    if len(sources) != len(set(value.lower() for value in sources)):
        raise HygieneError("duplicate or case-aliased candidate path")
    for index, left in enumerate(sources):
        left_path = PurePosixPath(left)
        for right in sources[index + 1:]:
            right_path = PurePosixPath(right)
            if left_path in right_path.parents or right_path in left_path.parents:
                raise HygieneError("candidate paths cannot overlap")


def entries_match(root: Path, entries: list[dict], source_prefix: str, destination_prefix: str | None = None) -> tuple[bool, list[str]]:
    problems = []
    for entry in entries:
        entry_path = safe_relative(entry["path"])
        if destination_prefix is None:
            target_relative = entry_path
        else:
            source = PurePosixPath(source_prefix)
            child = PurePosixPath(entry_path)
            if child == source:
                target_relative = destination_prefix
            else:
                target_relative = PurePosixPath(destination_prefix, child.relative_to(source)).as_posix()
        path = within(root, target_relative)
        if not path.is_file():
            problems.append(f"missing {target_relative}")
            continue
        if path.stat().st_size != int(entry["size"]) or sha256_file(path) != entry["sha256"]:
            problems.append(f"hash or size mismatch {target_relative}")
    return not problems, problems


def apply_plan(root: Path, policy: dict, plan_path: Path, authorization_ref: str) -> Path:
    if len(authorization_ref.strip()) < 3:
        raise HygieneError("apply requires a concrete authorization reference")
    plan = load_json(plan_path)
    validate_plan(plan, root, policy)
    if workspace_fingerprint(root, policy) != plan["workspace_fingerprint"]:
        raise HygieneError("workspace fingerprint changed; regenerate the plan")
    archive_root_relative = safe_relative(plan["archive_root"])
    bundle_relative = f"{archive_root_relative}/{plan['archive_id']}"
    bundle = within(root, bundle_relative)
    if bundle.exists():
        raise HygieneError(f"archive bundle already exists: {bundle_relative}")
    preflight: list[tuple[dict, Path, Path]] = []
    for item in plan["items"]:
        source_relative = item["source"]
        destination_relative = item["destination"]
        source = within(root, source_relative)
        destination = within(root, destination_relative)
        if has_link_component(root, source) or has_link_component(root, destination.parent):
            raise HygieneError(f"links and reparse points are protected: {source_relative}")
        reason = protection_reason(root, source, source_relative, policy)
        if reason:
            raise HygieneError(f"candidate became protected {source_relative}: {reason}")
        references = active_references(root, source_relative, source, policy, {plan_path})
        if references:
            raise HygieneError(f"new active references block {source_relative}: {references}")
        matches, problems = entries_match(root, item["entries"], source_relative)
        if not matches:
            raise HygieneError("source changed: " + "; ".join(problems))
        if item.get("retained_canonical"):
            canonical = within(root, item["retained_canonical"])
            if not source.is_file() or not canonical.is_file() or source.stat().st_size != canonical.stat().st_size or sha256_file(source) != sha256_file(canonical):
                raise HygieneError(f"retained canonical no longer matches {source_relative}")
        if destination.exists():
            raise HygieneError(f"archive destination exists: {destination_relative}")
        preflight.append((item, source, destination))
    plan_digest = sha256_file(plan_path)
    manifest_path = bundle / policy["manifest_file"]
    journal_path = bundle / policy["journal_file"]
    index_path = within(root, f"{archive_root_relative}/{policy['index_file']}")
    manifest = {
        "$schema": "schemas/archive-manifest.schema.json",
        "schema_version": "1.0",
        "archive_id": plan["archive_id"],
        "status": "applying",
        "created_at": utc_now(),
        "workspace_root": str(root),
        "workspace_fingerprint": plan["workspace_fingerprint"],
        "plan_id": plan["plan_id"],
        "plan_sha256": plan_digest,
        "archive_root": archive_root_relative,
        "owner": plan["owner"],
        "reason": plan["reason"],
        "authorization_ref": authorization_ref.strip(),
        "moves": plan["items"],
        "verification": {"status": "pending", "problems": []},
        "restore": {"status": "available", "overwrite": False},
    }
    moved: list[tuple[Path, Path]] = []
    bundle.mkdir(parents=True, exist_ok=False)
    write_atomic(manifest_path, manifest)
    try:
        for item, source, destination in preflight:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
            moved.append((source, destination))
            append_jsonl(journal_path, {"event": "move", "at": utc_now(), "source": item["source"], "destination": item["destination"]})
        verification_problems = []
        for item in plan["items"]:
            source = within(root, item["source"])
            if source.exists():
                verification_problems.append(f"source still exists: {item['source']}")
            matches, problems = entries_match(root, item["entries"], item["source"], item["destination"])
            if not matches:
                verification_problems.extend(problems)
        if verification_problems:
            raise HygieneError("archive verification failed: " + "; ".join(verification_problems))
        manifest["status"] = "archived"
        manifest["verification"] = {"status": "passed", "verified_at": utc_now(), "problems": []}
        write_atomic(manifest_path, manifest)
        append_jsonl_atomic(
            index_path,
            {"schema_version": "1.0", "event": "archived", "at": utc_now(), "archive_id": plan["archive_id"], "manifest": relative_name(root, manifest_path), "reason": plan["reason"], "sources": [item["source"] for item in plan["items"]]},
            int(policy["max_index_file_bytes"]),
        )
        return manifest_path
    except Exception as exc:
        rollback_problems = []
        for source, destination in reversed(moved):
            try:
                source.parent.mkdir(parents=True, exist_ok=True)
                if source.exists() or not destination.exists():
                    raise HygieneError(f"cannot reverse {destination} to {source}")
                shutil.move(str(destination), str(source))
                append_jsonl(journal_path, {"event": "rollback", "at": utc_now(), "source": relative_name(root, source), "destination": relative_name(root, destination)})
            except Exception as rollback_exc:  # preserve exact recovery evidence
                rollback_problems.append(str(rollback_exc))
        if not rollback_problems:
            for item in plan["items"]:
                matches, problems = entries_match(root, item["entries"], item["source"])
                if not matches:
                    rollback_problems.extend(problems)
        if rollback_problems:
            manifest["status"] = "blocked_recovery"
            manifest["verification"] = {"status": "failed", "problems": [str(exc), *rollback_problems]}
            write_atomic(manifest_path, manifest)
        else:
            manifest["status"] = "rolled_back"
            manifest["verification"] = {"status": "failed", "problems": [str(exc)]}
            write_atomic(manifest_path, manifest)
            try:
                append_jsonl_atomic(
                    index_path,
                    {"schema_version": "1.0", "event": "rolled_back", "at": utc_now(), "archive_id": plan["archive_id"], "manifest": relative_name(root, manifest_path), "reason": str(exc), "sources": [item["source"] for item in plan["items"]]},
                    int(policy["max_index_file_bytes"]),
                )
            except Exception:
                pass
        raise HygieneError(str(exc)) from exc


def validate_manifest(manifest: dict, root: Path, policy: dict, manifest_path: Path) -> Path:
    required = {
        "$schema", "schema_version", "archive_id", "status", "created_at", "workspace_root",
        "workspace_fingerprint", "plan_id", "plan_sha256", "archive_root", "owner", "reason",
        "authorization_ref", "moves", "verification", "restore",
    }
    if set(manifest) != required or manifest.get("schema_version") != "1.0":
        raise HygieneError("manifest fields do not match contract")
    if not ARCHIVE_ID.fullmatch(str(manifest.get("archive_id", ""))):
        raise HygieneError("invalid archive id in manifest")
    if Path(str(manifest.get("workspace_root", ""))).resolve() != root:
        raise HygieneError("manifest targets a different workspace root")
    archive_root = safe_relative(str(manifest.get("archive_root", "")))
    parts = PurePosixPath(archive_root).parts
    if parts[-1] != policy["archive_directory"] or parts.count(policy["archive_directory"]) != 1:
        raise HygieneError("manifest archive root is invalid")
    expected_bundle = within(root, f"{archive_root}/{manifest['archive_id']}")
    expected_manifest = expected_bundle / policy["manifest_file"]
    if manifest_path.resolve() != expected_manifest.resolve(strict=False) or has_link_component(root, manifest_path):
        raise HygieneError("manifest path does not match its archive bundle")
    if manifest.get("status") not in {"applying", "archived", "rolled_back", "blocked_recovery", "restored"}:
        raise HygieneError("manifest status is invalid")
    if not re.fullmatch(r"plan-[a-f0-9]{16}", str(manifest.get("plan_id", ""))) or not re.fullmatch(r"[a-f0-9]{64}", str(manifest.get("plan_sha256", ""))):
        raise HygieneError("manifest plan identity is invalid")
    moves = manifest.get("moves")
    if not isinstance(moves, list) or not moves:
        raise HygieneError("manifest has no moves")
    seen = set()
    for item in moves:
        if not isinstance(item, dict) or "source" not in item or "destination" not in item or "entries" not in item:
            raise HygieneError("manifest move is invalid")
        source = safe_relative(str(item["source"]))
        destination = safe_relative(str(item["destination"]))
        expected = PurePosixPath(archive_root, manifest["archive_id"], policy["payload_directory"], source).as_posix()
        if destination != expected or source.lower() in seen:
            raise HygieneError("manifest move destination is invalid or duplicated")
        seen.add(source.lower())
        if not isinstance(item["entries"], list) or not item["entries"]:
            raise HygieneError("manifest move has no entries")
        for entry in item["entries"]:
            if not isinstance(entry, dict) or set(entry) != {"path", "size", "sha256"}:
                raise HygieneError("manifest entry is invalid")
            entry_path = safe_relative(str(entry["path"]))
            if PurePosixPath(source) != PurePosixPath(entry_path) and PurePosixPath(source) not in PurePosixPath(entry_path).parents:
                raise HygieneError("manifest entry escapes its source")
    return expected_bundle


def verify_manifest(root: Path, policy: dict, manifest_path: Path) -> dict:
    manifest = load_json(manifest_path)
    validate_manifest(manifest, root, policy, manifest_path)
    if manifest.get("status") != "archived":
        raise HygieneError("manifest is not in archived state")
    problems = []
    for item in manifest["moves"]:
        source = within(root, item["source"])
        if source.exists():
            problems.append(f"source exists: {item['source']}")
        matches, entry_problems = entries_match(root, item["entries"], item["source"], item["destination"])
        if not matches:
            problems.extend(entry_problems)
    index_path = within(root, f"{manifest['archive_root']}/{policy['index_file']}")
    expected_manifest = relative_name(root, manifest_path)
    events = read_index_events(index_path, int(policy["max_index_file_bytes"]))
    if not any(event.get("event") == "archived" and event.get("archive_id") == manifest["archive_id"] and event.get("manifest") == expected_manifest for event in events):
        problems.append("archive index entry missing")
    result = {"archive_id": manifest["archive_id"], "status": "passed" if not problems else "failed", "problems": problems}
    if problems:
        raise HygieneError("; ".join(problems))
    return result


def restore_manifest(root: Path, policy: dict, manifest_path: Path, authorization_ref: str) -> dict:
    if len(authorization_ref.strip()) < 3:
        raise HygieneError("restore requires a concrete authorization reference")
    manifest = load_json(manifest_path)
    bundle = validate_manifest(manifest, root, policy, manifest_path)
    if manifest.get("status") != "archived":
        raise HygieneError("only an archived manifest can be restored")
    index_path = within(root, f"{manifest['archive_root']}/{policy['index_file']}")
    events = read_index_events(index_path, int(policy["max_index_file_bytes"]))
    expected_manifest = relative_name(root, manifest_path)
    if not any(event.get("event") == "archived" and event.get("archive_id") == manifest["archive_id"] and event.get("manifest") == expected_manifest for event in events):
        raise HygieneError("archive index entry missing")
    journal_path = bundle / policy["journal_file"]
    restored: list[tuple[Path, Path]] = []
    for item in manifest["moves"]:
        source = within(root, item["source"])
        destination = within(root, item["destination"])
        if source.exists():
            raise HygieneError(f"restore collision: {item['source']}")
        matches, problems = entries_match(root, item["entries"], item["source"], item["destination"])
        if not matches:
            raise HygieneError("archive payload changed: " + "; ".join(problems))
    try:
        for item in reversed(manifest["moves"]):
            source = within(root, item["source"])
            destination = within(root, item["destination"])
            source.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(destination), str(source))
            restored.append((source, destination))
            append_jsonl(journal_path, {"event": "restore", "at": utc_now(), "source": item["source"], "destination": item["destination"], "authorization_ref": authorization_ref.strip()})
        problems = []
        for item in manifest["moves"]:
            matches, entry_problems = entries_match(root, item["entries"], item["source"])
            if not matches:
                problems.extend(entry_problems)
        if problems:
            raise HygieneError("restored payload verification failed: " + "; ".join(problems))
        manifest["status"] = "restored"
        manifest["restore"] = {"status": "restored", "restored_at": utc_now(), "authorization_ref": authorization_ref.strip(), "overwrite": False}
        write_atomic(manifest_path, manifest)
        append_jsonl_atomic(index_path, {"schema_version": "1.0", "event": "restored", "at": utc_now(), "archive_id": manifest["archive_id"], "manifest": expected_manifest, "sources": [item["source"] for item in manifest["moves"]]}, int(policy["max_index_file_bytes"]))
    except Exception as exc:
        rollback_problems = []
        for source, destination in reversed(restored):
            try:
                destination.parent.mkdir(parents=True, exist_ok=True)
                if destination.exists() or not source.exists():
                    raise HygieneError(f"cannot reverse restore {source}")
                shutil.move(str(source), str(destination))
                append_jsonl(journal_path, {"event": "restore_rollback", "at": utc_now(), "source": relative_name(root, source), "destination": relative_name(root, destination)})
            except Exception as rollback_exc:
                rollback_problems.append(str(rollback_exc))
        if rollback_problems:
            manifest["status"] = "blocked_recovery"
            manifest["restore"] = {"status": "blocked_recovery", "problems": [str(exc), *rollback_problems]}
            write_atomic(manifest_path, manifest)
        else:
            manifest["status"] = "archived"
            manifest["restore"] = {"status": "available", "overwrite": False, "last_error": str(exc)}
            write_atomic(manifest_path, manifest)
        raise HygieneError(str(exc)) from exc
    return {"archive_id": manifest["archive_id"], "status": "restored", "sources": [item["source"] for item in manifest["moves"]]}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    commands = result.add_subparsers(dest="command", required=True)
    inventory_command = commands.add_parser("inventory", help="read-only lifecycle inventory")
    inventory_command.add_argument("--root", type=Path, required=True)
    plan_command = commands.add_parser("plan", help="write a reviewable plan without moving candidates")
    plan_command.add_argument("--root", type=Path, required=True)
    plan_command.add_argument("--candidate", action="append", required=True)
    plan_command.add_argument("--evidence", action="append", required=True)
    plan_command.add_argument("--confidence", choices=("low", "medium", "high"), required=True)
    plan_command.add_argument("--owner", required=True)
    plan_command.add_argument("--retained-canonical")
    plan_command.add_argument("--supersedes", action="append")
    plan_command.add_argument("--reason", required=True)
    plan_command.add_argument("--slug", required=True)
    plan_command.add_argument("--archive-id")
    plan_command.add_argument("--out", type=Path, required=True)
    apply_command = commands.add_parser("apply", help="apply one authorized unchanged plan")
    apply_command.add_argument("--root", type=Path, required=True)
    apply_command.add_argument("--plan", type=Path, required=True)
    apply_command.add_argument("--authorization-ref", required=True)
    verify_command = commands.add_parser("verify", help="verify an archived bundle")
    verify_command.add_argument("--root", type=Path, required=True)
    verify_command.add_argument("--manifest", type=Path, required=True)
    restore_command = commands.add_parser("restore", help="restore without overwriting active paths")
    restore_command.add_argument("--root", type=Path, required=True)
    restore_command.add_argument("--manifest", type=Path, required=True)
    restore_command.add_argument("--authorization-ref", required=True)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        policy = load_policy(args.policy.resolve())
        root = root_path(args.root)
        if args.command == "inventory":
            output = inventory(root, policy)
        elif args.command == "plan":
            output = build_plan(args, root, policy)
            write_atomic(args.out.resolve(), output)
            output = {"status": "planned", "plan_id": output["plan_id"], "archive_id": output["archive_id"], "archive_root": output["archive_root"], "items": len(output["items"]), "out": str(args.out.resolve())}
        elif args.command == "apply":
            manifest_path = apply_plan(root, policy, args.plan.resolve(), args.authorization_ref)
            output = {"status": "archived", "manifest": str(manifest_path), "archive_id": load_json(manifest_path)["archive_id"]}
        elif args.command == "verify":
            output = verify_manifest(root, policy, args.manifest.resolve())
        else:
            output = restore_manifest(root, policy, args.manifest.resolve(), args.authorization_ref)
        print(json.dumps(output, indent=2, ensure_ascii=False, sort_keys=True))
        return 0
    except HygieneError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
