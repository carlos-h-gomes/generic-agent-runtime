#!/usr/bin/env python3
"""Plan or apply the packaged hybrid project template without overwriting files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys


ROOT = Path(__file__).resolve().parents[1]


class BootstrapError(RuntimeError):
    pass


def is_reparse(path: Path) -> bool:
    attributes = getattr(path.lstat(), "st_file_attributes", 0)
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def portable_path(raw: str) -> PurePosixPath:
    value = PurePosixPath(raw)
    if (
        not raw
        or raw.startswith("/")
        or "\\" in raw
        or value.is_absolute()
        or ".." in value.parts
        or any(not part or any(ord(char) < 32 for char in part) for part in value.parts)
    ):
        raise BootstrapError(f"unsafe template path: {raw!r}")
    return value


def ensure_contained(root: Path, candidate: Path) -> Path:
    resolved_root = root.resolve()
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise BootstrapError(f"path escapes target root: {candidate}") from exc
    return resolved


def reject_linked_ancestors(root: Path, candidate: Path) -> None:
    current = candidate
    while True:
        if current.exists() and (current.is_symlink() or is_reparse(current)):
            raise BootstrapError(f"symlink or reparse path is not allowed: {current}")
        if current == root:
            return
        if root not in current.parents:
            raise BootstrapError(f"path escapes checked root: {candidate}")
        current = current.parent


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def load_template() -> tuple[Path, dict, dict[str, bytes]]:
    harness = json.loads((ROOT / "harness.json").read_text(encoding="utf-8"))
    template_root = ensure_contained(ROOT, ROOT / harness["distribution"]["project_template_root"])
    if not template_root.is_dir() or template_root.is_symlink() or is_reparse(template_root):
        raise BootstrapError("project template root is missing or unsafe")
    manifest_path = template_root / "template-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "1.0" or manifest.get("template_id") != "python-react-hybrid":
        raise BootstrapError("unsupported project template manifest")
    files: dict[str, bytes] = {}
    for raw in manifest.get("files", []):
        name = portable_path(raw).as_posix()
        if name in files:
            raise BootstrapError(f"duplicate template file: {name}")
        source = ensure_contained(template_root, template_root / Path(*PurePosixPath(name).parts))
        reject_linked_ancestors(template_root, source)
        if not source.is_file():
            raise BootstrapError(f"template file is missing: {name}")
        before = source.stat()
        content = source.read_bytes()
        after = source.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise BootstrapError(f"template file changed during read: {name}")
        files[name] = content
    if not files:
        raise BootstrapError("template manifest has no files")
    for raw in manifest.get("minimum_directories", []):
        portable_path(raw)
    return template_root, manifest, files


def target_root(raw: Path, template_root: Path) -> Path:
    target = raw.resolve()
    if not target.is_dir():
        raise BootstrapError(f"target must be an existing directory: {target}")
    reject_linked_ancestors(target, target)
    if target == template_root or template_root in target.parents:
        raise BootstrapError("target cannot be the packaged template tree")
    return target


def inspect(target: Path, manifest: dict, files: dict[str, bytes]) -> dict:
    missing_dirs: list[str] = []
    directory_conflicts: list[str] = []
    for raw in manifest["minimum_directories"]:
        name = portable_path(raw).as_posix()
        destination = ensure_contained(target, target / Path(*PurePosixPath(name).parts))
        reject_linked_ancestors(target, destination)
        if destination.exists() and not destination.is_dir():
            directory_conflicts.append(name)
        elif not destination.is_dir():
            missing_dirs.append(name)

    missing_files: list[str] = []
    identical_files: list[str] = []
    conflicting_files: list[str] = []
    for name, content in files.items():
        destination = ensure_contained(target, target / Path(*PurePosixPath(name).parts))
        reject_linked_ancestors(target, destination)
        if not destination.exists():
            missing_files.append(name)
        elif not destination.is_file():
            conflicting_files.append(name)
        elif sha256(destination.read_bytes()) == sha256(content):
            identical_files.append(name)
        else:
            conflicting_files.append(name)
    return {
        "missing_dirs": missing_dirs,
        "directory_conflicts": directory_conflicts,
        "missing_files": missing_files,
        "identical_files": identical_files,
        "conflicting_files": conflicting_files,
    }


def report(state: dict, *, mode: str) -> None:
    print(
        f"{mode.upper()} hybrid bootstrap: "
        f"{len(state['missing_dirs'])} directories and {len(state['missing_files'])} files missing; "
        f"{len(state['identical_files'])} identical; "
        f"{len(state['directory_conflicts']) + len(state['conflicting_files'])} conflicts"
    )
    conflicts = [
        *(f"directory:{name}" for name in state["directory_conflicts"]),
        *(f"file:{name}" for name in state["conflicting_files"]),
    ]
    for item in conflicts[:50]:
        print(f"CONFLICT {item}")
    if len(conflicts) > 50:
        print(f"CONFLICT ... {len(conflicts) - 50} additional items omitted")


def apply(target: Path, state: dict, files: dict[str, bytes], *, skip_existing: bool) -> None:
    conflicts = state["directory_conflicts"] + state["conflicting_files"]
    if conflicts and not skip_existing:
        raise BootstrapError("conflicts block apply; inspect plan or pass --skip-existing for a non-overwriting merge")
    for raw in state["missing_dirs"]:
        destination = ensure_contained(target, target / Path(*PurePosixPath(raw).parts))
        destination.mkdir(parents=True, exist_ok=True)
    for name in state["missing_files"]:
        destination = ensure_contained(target, target / Path(*PurePosixPath(name).parts))
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            with destination.open("xb") as handle:
                handle.write(files[name])
        except FileExistsError as exc:
            raise BootstrapError(f"destination appeared during apply; no overwrite performed: {name}") from exc


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("mode", choices=("plan", "apply"), nargs="?", default="plan")
    result.add_argument("--target", type=Path, default=ROOT)
    result.add_argument(
        "--skip-existing",
        action="store_true",
        help="during apply, keep differing existing files and create only missing files",
    )
    return result


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    try:
        template_root, manifest, files = load_template()
        target = target_root(arguments.target, template_root)
        state = inspect(target, manifest, files)
        report(state, mode=arguments.mode)
        conflicts = state["directory_conflicts"] + state["conflicting_files"]
        if arguments.mode == "plan":
            return 3 if conflicts else 0
        if conflicts and not arguments.skip_existing:
            print("INCOMPLETE hybrid bootstrap: conflicts block apply; no files were written")
            return 3
        apply(target, state, files, skip_existing=arguments.skip_existing)
        final = inspect(target, manifest, files)
        report(final, mode="result")
        if final["missing_dirs"] or final["missing_files"]:
            return 3
        if final["directory_conflicts"] or final["conflicting_files"]:
            return 3
        return 0
    except (BootstrapError, OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"FAIL hybrid bootstrap: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
