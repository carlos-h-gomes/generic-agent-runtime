"""Bounded evidence readers. Files and statements do not authenticate their author."""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat

class EvidenceError(ValueError):
    pass

def member(root: Path, name: str) -> Path:
    if not isinstance(name, str) or not name or len(name) > 240 or '\\' in name or ':' in name:
        raise EvidenceError('invalid relative evidence path')
    parts = PurePosixPath(name).parts
    if name.startswith('/') or any(p in {'.', '..'} for p in parts):
        raise EvidenceError('evidence path escapes root')
    root = root.resolve(strict=True)
    current = root
    for part in parts:
        current = current / part
        attributes = getattr(current.lstat(), 'st_file_attributes', 0)
        if current.is_symlink() or attributes & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 1024):
            raise EvidenceError('links are not evidence')
    if not current.resolve(strict=True).is_relative_to(root) or not current.is_file():
        raise EvidenceError('evidence must be a file inside root')
    return current

def digest(path: Path) -> str:
    if path.stat().st_size > 8_388_608:
        raise EvidenceError('evidence exceeds byte limit')
    return hashlib.sha256(path.read_bytes()).hexdigest()

def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise EvidenceError('duplicate JSON key')
        result[key] = value
    return result

def load(path: Path) -> dict:
    if path.stat().st_size > 1_048_576:
        raise EvidenceError('JSON exceeds byte limit')
    value = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=pairs,
                       parse_constant=lambda _: (_ for _ in ()).throw(EvidenceError('nonfinite JSON')))
    if not isinstance(value, dict):
        raise EvidenceError('JSON object required')
    return value

def sha(value):
    if not isinstance(value, str) or not re.fullmatch('[a-f0-9]{64}', value):
        raise EvidenceError('lowercase SHA-256 required')
    return value

def fresh(record: dict, now: datetime | None = None):
    now = now or datetime.now(timezone.utc)
    dates = []
    for key in ('observed_at', 'expires_at'):
        value = record.get(key)
        if not isinstance(value, str):
            raise EvidenceError('evidence timestamps required')
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if parsed.tzinfo is None:
            raise EvidenceError('timestamp timezone required')
        dates.append(parsed)
    if not dates[0] <= now < dates[1]:
        raise EvidenceError('expired or future evidence')

def keys(record: dict, required: set, optional: set = frozenset()):
    if not isinstance(record, dict) or not required <= record.keys() or record.keys() - required - optional:
        raise EvidenceError('missing or unknown fields')

def bound(root: Path, record: dict):
    keys(record, {'path', 'sha256'})
    path = member(root, record['path'])
    if digest(path) != sha(record['sha256']):
        raise EvidenceError('evidence digest changed')
    return path
