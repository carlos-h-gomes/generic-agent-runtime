#!/usr/bin/env python3
"""Portable advisory coordination bridge for Harness 4.2."""

from __future__ import annotations

import argparse
import contextlib
import fnmatch
import hashlib
import html
import json
import os
import re
import socket
import sys
import tempfile
import time
import unicodedata
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath

EVENTS = {"claim", "release", "start", "progress", "done", "blocked", "handoff", "note"}
TERMINAL = {"done"}
NOTE_LIMIT = 140
COMPACT_THRESHOLD = 200
COMPACT_KEEP = 100
DEFAULT_LEASE_MINUTES = 60
MAX_LEASE_MINUTES = 7 * 24 * 60
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")


class BridgeError(RuntimeError):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo is not None else None
    except ValueError:
        return None


def bridge_paths(root: Path) -> dict[str, Path]:
    base = root.resolve() / "docs" / "ai" / "bridge"
    return {
        "base": base,
        "ledger": base / "ledger.jsonl",
        "archive": base / "ledger-archive.jsonl",
        "board": base / "board.md",
        "lock": base / ".bridge.lock",
    }


def ensure_files(paths: dict[str, Path]) -> None:
    paths["base"].mkdir(parents=True, exist_ok=True)
    if not paths["ledger"].exists():
        paths["ledger"].write_bytes(b"")


def process_alive(pid: object) -> bool:
    try:
        numeric = int(pid)
        if numeric <= 0:
            return False
        if os.name == "nt":
            return windows_process_alive(numeric)
        os.kill(numeric, 0)
        return True
    except PermissionError:
        return True
    except (TypeError, ValueError, ProcessLookupError, OSError):
        return False


def windows_process_alive(pid: int) -> bool:
    """Query a Windows process without using os.kill(pid, 0), which terminates it."""
    import ctypes
    from ctypes import wintypes

    process_query_limited_information = 0x1000
    still_active = 259
    error_invalid_parameter = 87
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel32.GetExitCodeProcess.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL

    handle = kernel32.OpenProcess(process_query_limited_information, False, pid)
    if not handle:
        return ctypes.get_last_error() != error_invalid_parameter
    try:
        exit_code = wintypes.DWORD()
        if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
            return True
        return exit_code.value == still_active
    finally:
        kernel32.CloseHandle(handle)


def recoverable_stale_lock(path: Path) -> bool:
    try:
        age = time.time() - path.stat().st_mtime
        if age <= 30:
            return False
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("host") == socket.gethostname() and bool(data.get("token")) and not process_alive(data.get("pid"))
    except (OSError, UnicodeError, json.JSONDecodeError, AttributeError):
        return False


@contextlib.contextmanager
def bridge_lock(paths: dict[str, Path], timeout: float = 5.0):
    ensure_files(paths)
    deadline = time.monotonic() + timeout
    token = str(uuid.uuid4())
    while True:
        try:
            fd = os.open(paths["lock"], os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump({"pid": os.getpid(), "host": socket.gethostname(), "token": token, "created": iso_utc(utc_now())}, handle)
            break
        except FileExistsError:
            try:
                if recoverable_stale_lock(paths["lock"]):
                    paths["lock"].unlink(missing_ok=True)
                    continue
            except FileNotFoundError:
                continue
            if time.monotonic() >= deadline:
                raise BridgeError(f"bridge lock timeout: {paths['lock']}")
            time.sleep(0.05)
    try:
        yield
    finally:
        try:
            current = json.loads(paths["lock"].read_text(encoding="utf-8"))
            if current.get("token") == token:
                paths["lock"].unlink(missing_ok=True)
        except (OSError, UnicodeError, json.JSONDecodeError, AttributeError):
            pass


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def normalize_path(value: str) -> str:
    value = unicodedata.normalize("NFC", value.strip().replace("\\", "/"))
    while value.startswith("./"):
        value = value[2:]
    if not value or value.startswith("/") or ":" in value or any(ord(char) < 32 for char in value):
        raise BridgeError(f"claim path must be repository-relative: {value!r}")
    parts = PurePosixPath(value).parts
    if any(part in {"", ".", ".."} for part in parts):
        raise BridgeError(f"unsafe claim path: {value!r}")
    return str(PurePosixPath(*parts))


def static_prefix(pattern: str) -> str:
    positions = [pattern.find(char) for char in "*?[" if char in pattern]
    end = min(positions) if positions else len(pattern)
    return pattern[:end].rstrip("/")


def path_overlap(left: str, right: str) -> bool:
    left = normalize_path(left).casefold()
    right = normalize_path(right).casefold()
    if left == right or fnmatch.fnmatchcase(left, right) or fnmatch.fnmatchcase(right, left):
        return True
    left_glob = any(char in left for char in "*?[")
    right_glob = any(char in right for char in "*?[")
    if not left_glob and not right_glob:
        return left.startswith(right.rstrip("/") + "/") or right.startswith(left.rstrip("/") + "/")
    left_base, right_base = static_prefix(left), static_prefix(right)
    if not left_base or not right_base:
        return True
    return (
        left_base == right_base
        or left_base.startswith(right_base.rstrip("/") + "/")
        or right_base.startswith(left_base.rstrip("/") + "/")
    )


def read_raw(paths: dict[str, Path]) -> list[dict]:
    if not paths["ledger"].exists():
        return []
    events: list[dict] = []
    with paths["ledger"].open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise BridgeError(f"invalid JSON at ledger line {line_number}: {exc.msg}") from exc
            if not isinstance(raw, dict):
                raise BridgeError(f"ledger line {line_number} is not an object")
            raw["_line"] = line_number
            events.append(raw)
    return events


def canonical(raw: dict, index: int) -> dict:
    if raw.get("v") == 2:
        event = dict(raw)
    else:
        event = {
            "v": 1,
            "id": f"legacy-{index}",
            "ts": raw.get("ts"),
            "run": raw.get("run") or "legacy",
            "a": raw.get("a"),
            "e": raw.get("e"),
            "t": raw.get("t"),
            "f": raw.get("f") or [],
            "n": raw.get("n") or "",
            "nx": raw.get("nx") or "",
            "lease": raw.get("lease"),
        }
    event["_index"] = index
    event["_line"] = raw.get("_line", index + 1)
    event.setdefault("f", [])
    event.setdefault("n", "")
    event.setdefault("nx", "")
    event.setdefault("lease", None)
    return event


def read_events(paths: dict[str, Path]) -> list[dict]:
    return [canonical(raw, index) for index, raw in enumerate(read_raw(paths))]


def validate_event(event: dict, strict_v2: bool = False) -> list[str]:
    errors: list[str] = []
    required = ("id", "ts", "run", "a", "e", "t", "f", "n", "nx")
    if strict_v2 and event.get("v") != 2:
        errors.append("new event is not v2")
    if event.get("v") == 2:
        allowed = {"v", "id", "ts", "run", "a", "e", "t", "f", "n", "nx", "lease", "_index", "_line"}
        extras = set(event) - allowed
        if extras:
            errors.append(f"unexpected properties: {sorted(extras)}")
    for key in required:
        if key not in event or event[key] is None:
            errors.append(f"missing {key}")
    if event.get("v") == 2:
        for key in ("run", "a", "t"):
            if not isinstance(event.get(key), str) or not IDENTIFIER.fullmatch(event[key]):
                errors.append(f"invalid {key} identifier")
            elif unicodedata.normalize("NFC", event[key]) != event[key]:
                errors.append(f"{key} identifier is not NFC-normalized")
        if isinstance(event.get("run"), str) and len(event["run"]) > 100:
            errors.append("run identifier exceeds 100 characters")
        if isinstance(event.get("a"), str) and len(event["a"]) > 100:
            errors.append("actor identifier exceeds 100 characters")
        try:
            if str(uuid.UUID(str(event.get("id")))).lower() != str(event.get("id")).lower():
                errors.append("event id is not a canonical UUID")
        except (ValueError, AttributeError):
            errors.append("event id is not a UUID")
    if event.get("e") not in EVENTS:
        errors.append(f"invalid event {event.get('e')!r}")
    if not isinstance(event.get("f"), list):
        errors.append("f is not an array")
    else:
        normalized_files: list[str] = []
        for value in event["f"]:
            try:
                normalized_files.append(normalize_path(value).casefold())
            except (BridgeError, TypeError) as exc:
                errors.append(str(exc))
        if len(normalized_files) != len(set(normalized_files)):
            errors.append("f contains duplicate portable paths")
    if not isinstance(event.get("n"), str) or len(event.get("n", "")) > NOTE_LIMIT:
        errors.append("note exceeds 140 characters or is not text")
    if not isinstance(event.get("nx"), str) or len(event.get("nx", "")) > NOTE_LIMIT:
        errors.append("next exceeds 140 characters or is not text")
    for key in ("n", "nx"):
        value = event.get(key)
        if isinstance(value, str) and any(ord(char) < 32 for char in value):
            errors.append(f"{key} contains a control character")
    if not parse_time(event.get("ts")):
        errors.append("invalid timestamp")
    if event.get("lease") and not parse_time(event.get("lease")):
        errors.append("invalid lease timestamp")
    if event.get("e") == "claim" and not event.get("f"):
        errors.append("claim requires at least one file")
    if event.get("v") == 2 and event.get("e") == "claim" and not event.get("lease"):
        errors.append("v2 claim requires a lease")
    if event.get("v") == 2 and event.get("e") != "claim" and event.get("lease") is not None:
        errors.append("only claim events may carry a lease")
    return errors


def event_errors(events: list[dict]) -> list[str]:
    errors: list[str] = []
    ids: set[str] = set()
    for event in events:
        for error in validate_event(event):
            errors.append(f"line {event.get('_line')}: {error}")
        if event.get("v") == 2:
            if event.get("id") in ids:
                errors.append(f"line {event.get('_line')}: duplicate event id {event.get('id')}")
            ids.add(event.get("id"))
    try:
        errors.extend(overlap_errors(active_claims(events)))
    except (BridgeError, TypeError) as exc:
        errors.append(f"claim reconstruction failed: {exc}")
    return errors


def active_claims(events: list[dict], now: datetime | None = None) -> dict[tuple[str, str, str, str], dict]:
    now = now or utc_now()
    active: dict[tuple[str, str, str, str], dict] = {}
    for event in events:
        run, actor, task = event.get("run"), event.get("a"), event.get("t")
        if event.get("e") == "claim":
            for path in event.get("f", []):
                key = (run, actor, task, normalize_path(path).casefold())
                active[key] = event
        elif event.get("e") in {"release", "done"}:
            files = {normalize_path(path).casefold() for path in event.get("f", [])}
            for key in list(active):
                same_owner = key[0] == run and key[1] == actor and key[2] == task
                if same_owner and (not files or key[3] in files):
                    active.pop(key, None)
    for key, event in list(active.items()):
        lease = parse_time(event.get("lease"))
        if lease and lease <= now:
            active.pop(key, None)
    return active


def overlap_errors(claims: dict[tuple[str, str, str, str], dict]) -> list[str]:
    errors: list[str] = []
    items = list(claims.items())
    for index, (left_key, _) in enumerate(items):
        for right_key, _ in items[index + 1 :]:
            if left_key[:3] == right_key[:3]:
                continue
            if path_overlap(left_key[3], right_key[3]):
                errors.append(
                    f"overlapping claims: {left_key[3]} ({left_key[0]}/{left_key[1]}) and "
                    f"{right_key[3]} ({right_key[0]}/{right_key[1]})"
                )
    return errors


def append_event(paths: dict[str, Path], event: dict) -> None:
    with paths["ledger"].open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def board_text(events: list[dict]) -> str:
    claims = active_claims(events)
    latest_ts = events[-1].get("ts", "never") if events else "never"
    run_state: dict[tuple[str, str], dict] = {}
    blockers: dict[tuple[str, str], dict] = {}
    for event in events:
        key = (event.get("run"), event.get("t"))
        if event.get("e") in {"start", "progress", "blocked", "handoff", "done"}:
            run_state[key] = event
        if event.get("e") == "blocked":
            blockers[key] = event
        elif event.get("e") in {"progress", "done"}:
            blockers.pop(key, None)

    lines = [
        "# Agent Bridge Board",
        "",
        "Generated from `ledger.jsonl`; manual edits are overwritten.",
        "",
        f"- Updated: {latest_ts}",
        f"- Ledger events: {len(events)}",
        "",
        "## Active runs",
        "",
    ]
    active_runs = [(key, event) for key, event in run_state.items() if event.get("e") not in TERMINAL]
    if not active_runs:
        lines.append("None.")
    else:
        lines.extend(["| Run | Task | State | Actor | Note | Next |", "|---|---|---|---|---|---|"])
        for (run, task), event in sorted(active_runs):
            lines.append(
                f"| {markdown_cell(run)} | {markdown_cell(task)} | {markdown_cell(event.get('e'))} | {markdown_cell(event.get('a'))} | "
                f"{markdown_cell(event.get('n') or '')} | {markdown_cell(event.get('nx') or '')} |"
            )
    lines.extend(["", "## Active claims", ""])
    if not claims:
        lines.append("None.")
    else:
        lines.extend(["| Path | Run / actor | Task | Since | Lease |", "|---|---|---|---|---|"])
        for (run, actor, task, path), event in sorted(claims.items()):
            lines.append(
                f"| `{markdown_cell(path)}` | {markdown_cell(run)} / {markdown_cell(actor)} | {markdown_cell(task)} | "
                f"{markdown_cell(event.get('ts'))} | {markdown_cell(event.get('lease') or 'legacy/unbounded')} |"
            )
    lines.extend(["", "## Blockers", ""])
    if not blockers:
        lines.append("None.")
    else:
        for event in blockers.values():
            lines.append(f"- {markdown_cell(event.get('run'))}/{markdown_cell(event.get('t'))}: {markdown_cell(event.get('n'))}")
    lines.append("")
    return "\n".join(lines)


def markdown_cell(value: object) -> str:
    escaped = html.escape(str(value or ""), quote=True).replace("`", "&#96;")
    return escaped.replace("\\", "\\\\").replace("|", "\\|").replace("\r", " ").replace("\n", " ").replace("\t", " ")


def refresh_board(paths: dict[str, Path], events: list[dict] | None = None) -> str:
    content = board_text(events if events is not None else read_events(paths))
    atomic_write(paths["board"], content)
    return content


def command_init(paths: dict[str, Path]) -> int:
    with bridge_lock(paths):
        ensure_files(paths)
        events = read_events(paths)
        errors = event_errors(events)
        if errors:
            raise BridgeError("ledger is invalid; doctor before init: " + "; ".join(errors[:3]))
        refresh_board(paths, events)
    print(f"PASS bridge initialized: {paths['base']}")
    return 0


def command_log(paths: dict[str, Path], args: argparse.Namespace) -> int:
    if args.event not in EVENTS:
        raise BridgeError(f"invalid event: {args.event}")
    if len(args.note) > NOTE_LIMIT or len(args.next) > NOTE_LIMIT:
        raise BridgeError("note and next are limited to 140 characters; put detail in the task file")
    if not 1 <= args.lease_minutes <= MAX_LEASE_MINUTES:
        raise BridgeError(f"lease_minutes must be between 1 and {MAX_LEASE_MINUTES}")
    files = [normalize_path(item) for item in (args.files.split(",") if args.files else []) if item.strip()]
    if args.event == "claim" and not files:
        raise BridgeError("claim requires a comma-separated file list")
    now = utc_now()
    lease = iso_utc(now + timedelta(minutes=args.lease_minutes)) if args.event == "claim" else None
    event = {
        "v": 2,
        "id": str(uuid.uuid4()),
        "ts": iso_utc(now),
        "run": args.run,
        "a": args.actor,
        "e": args.event,
        "t": args.task,
        "f": files,
        "n": args.note,
        "nx": args.next,
        "lease": lease,
    }
    errors = validate_event(event, strict_v2=True)
    if errors:
        raise BridgeError("; ".join(errors))
    with bridge_lock(paths):
        events = read_events(paths)
        existing_errors = event_errors(events)
        if existing_errors:
            raise BridgeError("ledger is invalid; run doctor before writing: " + "; ".join(existing_errors[:3]))
        if args.event == "claim":
            for (run, actor, task, path), existing in active_claims(events).items():
                same_owner = run == args.run and actor == args.actor and task == args.task
                if not same_owner:
                    for requested in files:
                        if path_overlap(path, requested):
                            raise BridgeError(
                                f"claim conflict: {requested} overlaps {path} held by {run}/{actor} "
                                f"for {task} since {existing.get('ts')}"
                            )
        append_event(paths, event)
        refresh_board(paths, events + [canonical(event, len(events))])
    print(f"PASS logged {args.event}: {args.run}/{args.actor} {args.task}")
    return 0


def command_tail(paths: dict[str, Path], count: int) -> int:
    if count < 0:
        raise BridgeError("tail count must be non-negative")
    lines = paths["ledger"].read_text(encoding="utf-8").splitlines() if paths["ledger"].exists() else []
    print("\n".join(lines[-count:] if count else []))
    return 0


def command_claims(paths: dict[str, Path]) -> int:
    claims = active_claims(read_events(paths))
    if not claims:
        print("no active claims")
        return 0
    for (run, actor, task, path), event in sorted(claims.items()):
        print(f"{path}\t{run}/{actor}\t{task}\t{event.get('ts')}\t{event.get('lease') or 'legacy/unbounded'}")
    return 0


def command_board(paths: dict[str, Path]) -> int:
    content = board_text(read_events(paths))
    print(content, end="")
    return 0


def command_compact(paths: dict[str, Path]) -> int:
    with bridge_lock(paths):
        raw = read_raw(paths)
        events = [canonical(item, index) for index, item in enumerate(raw)]
        errors = event_errors(events)
        if errors:
            raise BridgeError("ledger is invalid; doctor before compact: " + "; ".join(errors[:3]))
        total = len(events)
        if total <= COMPACT_THRESHOLD:
            refresh_board(paths, events)
            print(f"SKIP ledger has {total} events; threshold is {COMPACT_THRESHOLD}")
            return 0
        active_indices = {event["_index"] for event in active_claims(events).values()}
        latest_runs: dict[tuple[str, str], dict] = {}
        for event in events:
            if event.get("e") in {"start", "progress", "blocked", "handoff", "done"}:
                latest_runs[(event.get("run"), event.get("t"))] = event
        active_run_indices = {event["_index"] for event in latest_runs.values() if event.get("e") not in TERMINAL}
        blockers: dict[tuple[str, str], dict] = {}
        for event in events:
            key = (event.get("run"), event.get("t"))
            if event.get("e") == "blocked":
                blockers[key] = event
            elif event.get("e") in {"progress", "done"}:
                blockers.pop(key, None)
        blocker_indices = {event["_index"] for event in blockers.values()}
        keep_indices = set(range(max(0, total - COMPACT_KEEP), total)) | active_indices | active_run_indices | blocker_indices
        kept = [raw[index] for index in range(total) if index in keep_indices]
        moved = [raw[index] for index in range(total) if index not in keep_indices]
        if moved:
            existing_lines = paths["archive"].read_text(encoding="utf-8").splitlines() if paths["archive"].exists() else []
            identities: set[str] = set()
            for line in existing_lines:
                try:
                    archived = json.loads(line)
                    identities.add(event_identity(archived))
                except json.JSONDecodeError as exc:
                    raise BridgeError(f"invalid archive JSON: {exc.msg}") from exc
            appended: list[str] = []
            for item in moved:
                clean = {key: value for key, value in item.items() if key != "_line"}
                identity = event_identity(clean)
                if identity not in identities:
                    appended.append(json.dumps(clean, ensure_ascii=False, separators=(",", ":")))
                    identities.add(identity)
            archive_content = "\n".join(existing_lines + appended)
            if archive_content:
                archive_content += "\n"
            atomic_write(paths["archive"], archive_content)
        ledger_content = "".join(
            json.dumps({key: value for key, value in item.items() if key != "_line"}, ensure_ascii=False, separators=(",", ":")) + "\n"
            for item in kept
        )
        atomic_write(paths["ledger"], ledger_content)
        refresh_board(paths, [canonical(item, index) for index, item in enumerate(kept)])
    print(f"PASS compacted ledger: archived {len(moved)}, retained {len(kept)} including active claims")
    return 0


def event_identity(event: dict) -> str:
    if event.get("v") == 2 and event.get("id"):
        return f"v2:{event['id']}"
    content = json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "legacy:" + hashlib.sha256(content).hexdigest()


def command_doctor(paths: dict[str, Path]) -> int:
    events = read_events(paths)
    errors = event_errors(events)
    expected_board = board_text(events)
    actual_board = paths["board"].read_text(encoding="utf-8") if paths["board"].exists() else ""
    if actual_board != expected_board:
        errors.append("board drift: run bridge init or board to regenerate it")
    if errors:
        for error in errors:
            print(f"FAIL {error}", file=sys.stderr)
        return 1
    legacy = sum(1 for event in events if event.get("v") == 1)
    print(f"PASS bridge doctor: {len(events)} events, {len(active_claims(events))} active claims, {legacy} legacy events")
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help="repository root")
    sub = result.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    sub.add_parser("board")
    tail = sub.add_parser("tail")
    tail.add_argument("count", type=int, nargs="?", default=15)
    sub.add_parser("claims")
    sub.add_parser("compact")
    sub.add_parser("doctor")
    log = sub.add_parser("log")
    log.add_argument("run")
    log.add_argument("actor")
    log.add_argument("event", choices=sorted(EVENTS))
    log.add_argument("task")
    log.add_argument("note")
    log.add_argument("files", nargs="?", default="")
    log.add_argument("next", nargs="?", default="")
    log.add_argument("lease_minutes", nargs="?", type=int, default=DEFAULT_LEASE_MINUTES)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    paths = bridge_paths(args.root)
    try:
        if args.command == "init":
            return command_init(paths)
        if args.command == "board":
            return command_board(paths)
        if args.command == "tail":
            return command_tail(paths, args.count)
        if args.command == "claims":
            return command_claims(paths)
        if args.command == "compact":
            return command_compact(paths)
        if args.command == "doctor":
            return command_doctor(paths)
        if args.command == "log":
            return command_log(paths, args)
        raise BridgeError(f"unsupported command: {args.command}")
    except (BridgeError, OSError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
