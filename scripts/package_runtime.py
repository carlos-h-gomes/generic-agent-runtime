#!/usr/bin/env python3
"""Build a deterministic, clean Generic Agent Runtime distribution."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import stat
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath


class PackageError(RuntimeError):
    pass


SENSITIVE_SUFFIXES = {".env", ".key", ".pem", ".p12", ".pfx", ".crt", ".cer", ".log", ".har", ".pcap", ".sqlite", ".db", ".jsonl"}
SENSITIVE_NAMES = {"id_rsa", "id_ed25519", "credentials", "credentials.json", "secrets.json"}


def portable_name(path: Path) -> str:
    name = PurePosixPath(*path.parts).as_posix()
    if not name or name.startswith("/") or ".." in PurePosixPath(name).parts or "\\" in name:
        raise PackageError(f"unsafe package path: {name!r}")
    return name


def is_reparse_point(path: Path) -> bool:
    attributes = getattr(path.lstat(), "st_file_attributes", 0)
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def sensitive_path(name: str) -> bool:
    path = PurePosixPath(name)
    basename = path.name.lower()
    return basename.startswith(".env") or basename in SENSITIVE_NAMES or path.suffix.lower() in SENSITIVE_SUFFIXES


def add_file(payload: dict[str, bytes], root: Path, name: str, source: Path) -> None:
    resolved_root = root.resolve()
    resolved = source.resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise PackageError(f"package source escapes repository root: {source}") from exc
    for candidate in (source, *source.parents):
        if candidate == resolved_root.parent:
            break
        if candidate.exists() and (candidate.is_symlink() or is_reparse_point(candidate)):
            raise PackageError(f"symlink/junction sources are not packaged: {candidate}")
        if candidate.resolve() == resolved_root:
            break
    if sensitive_path(name):
        raise PackageError(f"sensitive file class is not packaged: {name}")
    if name in payload:
        raise PackageError(f"duplicate package path: {name}")
    before = source.stat()
    content = source.read_bytes()
    after = source.stat()
    fingerprint_before = (before.st_size, before.st_mtime_ns, getattr(before, "st_ino", None))
    fingerprint_after = (after.st_size, after.st_mtime_ns, getattr(after, "st_ino", None))
    if fingerprint_before != fingerprint_after or len(content) != after.st_size:
        raise PackageError(f"source changed while packaging: {source}")
    payload[name] = content


def add_tree(payload: dict[str, bytes], root: Path, source: Path, target_prefix: str) -> None:
    root = root.resolve()
    source = source if source.is_absolute() else root / source
    resolved_source = source.resolve()
    try:
        resolved_source.relative_to(root)
    except ValueError as exc:
        raise PackageError(f"package source escapes repository root: {source}") from exc
    for candidate in (source, *source.parents):
        if candidate == root.parent:
            break
        if candidate.exists() and (candidate.is_symlink() or is_reparse_point(candidate)):
            raise PackageError(f"symlink/junction sources are not packaged: {candidate}")
        if candidate.resolve() == root:
            break
    if not source.is_dir():
        raise PackageError(f"package source directory is missing: {source}")
    for path in sorted(item for item in source.rglob("*") if item.is_file()):
        relative = path.relative_to(source)
        if any(part == "__pycache__" for part in relative.parts) or path.suffix in {".pyc", ".zip"} or path.name == ".bridge.lock":
            continue
        name = portable_name(Path(target_prefix) / relative)
        add_file(payload, root, name, path)


def build_payload(root: Path) -> tuple[dict[str, bytes], dict]:
    manifest = json.loads((root / "harness.json").read_text(encoding="utf-8"))
    payload: dict[str, bytes] = {}

    for name in ("AGENTS.md", "CLAUDE.md", "GEMINI.md", "harness.json"):
        add_file(payload, root, name, root / name)
    for directory in (".agents", "schemas", "prompt-templates", "scripts", "docs/harness"):
        add_tree(payload, root, root / directory, directory)

    scaffold = root / manifest["distribution"]["scaffold_root"]
    try:
        scaffold.resolve().relative_to(root)
    except ValueError as exc:
        raise PackageError("distribution.scaffold_root escapes the repository") from exc
    add_tree(payload, root, scaffold, "")
    add_file(payload, root, "docs/harness/CHANGELOG.md", root / "CHANGELOG.md")

    for name in ("quality-gates.md", "release-checklist.md", "standards.md"):
        add_file(payload, root, f"docs/ai/{name}", root / "docs" / "ai" / name)
    for path in sorted((root / "docs" / "ai" / "tasks").glob("_*")):
        if path.is_file():
            add_file(payload, root, f"docs/ai/tasks/{path.name}", path)

    payload["docs/ai/bridge/ledger.jsonl"] = b""
    manifest_name = manifest["distribution"]["manifest"]
    if manifest_name in payload:
        raise PackageError(f"manifest path collides with source: {manifest_name}")
    lines = [f"{hashlib.sha256(payload[name]).hexdigest()}  {name}\n" for name in sorted(payload)]
    payload[manifest_name] = "".join(lines).encode("utf-8")
    return payload, manifest


def validate_payload(payload: dict[str, bytes], manifest: dict) -> None:
    required = {
        "AGENTS.md",
        "CLAUDE.md",
        "GEMINI.md",
        "harness.json",
        "MANIFEST.sha256",
        "schemas/task-contract.schema.json",
        "schemas/gate-result.schema.json",
        "schemas/bridge-event.schema.json",
        ".agents/skills/core/agent-orchestration/SKILL.md",
        "docs/ai/constitution.md",
        "docs/ai/quality-gates.md",
        "docs/ai/tasks/_TASK_TEMPLATE.md",
        "docs/ai/bridge/board.md",
        "docs/ai/bridge/ledger.jsonl",
        "docs/harness/INSTALL.md",
        "docs/harness/CHANGELOG.md",
        "scripts/bridge.py",
        "scripts/run.ps1",
    }
    missing = required - payload.keys()
    if missing:
        raise PackageError(f"missing package files: {sorted(missing)}")
    forbidden = [
        name
        for name in payload
        if name.startswith("scaffold/")
        or name.endswith((".zip", ".pyc", ".bridge.lock", "ledger-archive.jsonl"))
        or "__pycache__" in name
        or (name.startswith("docs/ai/tasks/20") and not name.startswith("docs/ai/tasks/_"))
    ]
    if forbidden:
        raise PackageError(f"maintainer/live/generated files in payload: {forbidden}")
    if payload["docs/ai/bridge/ledger.jsonl"]:
        raise PackageError("packaged bridge ledger must be empty")
    expected_skills = len(manifest["core_skills"]) + len(manifest["specialist_skills"])
    packaged_skills = sum(1 for name in payload if name.endswith("/SKILL.md"))
    if packaged_skills != expected_skills:
        raise PackageError(f"skill count mismatch: {packaged_skills} != {expected_skills}")


def archive_bytes(payload: dict[str, bytes], manifest: dict) -> bytes:
    year, month, day = map(int, manifest["released"].split("-"))
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        for name in sorted(payload):
            info = zipfile.ZipInfo(name, date_time=(year, month, day, 0, 0, 0))
            info.create_system = 3
            executable = name.startswith("scripts/") and (name.endswith(".sh") or name.endswith(".py"))
            permissions = 0o755 if executable else 0o644
            info.external_attr = (stat.S_IFREG | permissions) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            package.writestr(info, payload[name], compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return buffer.getvalue()


def safe_output(root: Path, requested: Path, manifest: dict) -> Path:
    output = requested if requested.is_absolute() else root / requested
    output = output.resolve()
    try:
        output.relative_to(root.resolve())
    except ValueError as exc:
        raise PackageError("package output must stay within the repository root") from exc
    default_name = manifest["distribution"]["archive"]
    if output.name != default_name:
        raise PackageError(f"package output filename must be {default_name}")
    return output


def write_atomic(path: Path, content: bytes, replace: bool = False) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        if replace:
            os.replace(temp_name, path)
        else:
            try:
                os.link(temp_name, path)
            except FileExistsError as exc:
                raise PackageError(f"output already exists; pass --replace explicitly: {path}") from exc
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    result.add_argument("--out", type=Path, help="output path within the repository root")
    result.add_argument("--check", action="store_true", help="validate and hash the proposed package without writing it")
    result.add_argument("--replace", action="store_true", help="replace the canonical v4 archive if it already exists")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = args.root.resolve()
    try:
        payload, manifest = build_payload(root)
        validate_payload(payload, manifest)
        content = archive_bytes(payload, manifest)
        digest = hashlib.sha256(content).hexdigest()
        if args.check:
            print(f"PASS package plan: {len(payload)} files, {len(content)} bytes, sha256={digest}")
            return 0
        output = safe_output(root, args.out or Path(manifest["distribution"]["archive"]), manifest)
        if output.exists() and not args.replace:
            raise PackageError(f"output already exists; inspect it and pass --replace explicitly: {output}")
        write_atomic(output, content, replace=args.replace)
        print(f"PASS wrote {output}: {len(payload)} files, {len(content)} bytes, sha256={digest}")
        return 0
    except (PackageError, OSError, UnicodeError, json.JSONDecodeError, KeyError, ValueError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
