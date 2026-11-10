from __future__ import annotations

from datetime import date, datetime, timezone
import ipaddress
import json
import os
from pathlib import Path
import re
import socket
from typing import Iterable, Mapping
from urllib.parse import urlsplit, urlunsplit


class GuardrailError(ValueError):
    pass


def load_json_object(path: Path, max_bytes: int = 1_048_576) -> dict:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise GuardrailError(f"cannot inspect JSON file {path}: {exc}") from exc
    if size > max_bytes:
        raise GuardrailError(f"JSON file exceeds {max_bytes} bytes: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GuardrailError(f"invalid JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise GuardrailError(f"JSON object required: {path}")
    return value


def parse_date(value: object, field: str) -> date:
    if not isinstance(value, str):
        raise GuardrailError(f"{field} must be an ISO date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise GuardrailError(f"{field} must be an ISO date") from exc


def parse_datetime(value: object, field: str) -> datetime:
    if not isinstance(value, str):
        raise GuardrailError(f"{field} must be an ISO date-time")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise GuardrailError(f"{field} must be an ISO date-time") from exc
    if parsed.tzinfo is None:
        raise GuardrailError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def sanitize_environment(
    source: Mapping[str, str],
    allowed_names: Iterable[str],
    secret_name_pattern: str,
    *,
    allow_secret_names: bool = False,
) -> dict[str, str]:
    allowed = {name.casefold() for name in allowed_names}
    try:
        secret = re.compile(secret_name_pattern)
    except re.error as exc:
        raise GuardrailError(f"invalid secret environment pattern: {exc}") from exc
    result: dict[str, str] = {}
    for name, value in source.items():
        if name.casefold() not in allowed:
            continue
        if not allow_secret_names and secret.search(name):
            continue
        result[name] = value
    result["CI"] = "1"
    return result


def normalize_origin(value: object) -> str:
    if not isinstance(value, str) or len(value) > 500:
        raise GuardrailError("target origin must be a bounded string")
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise GuardrailError("target origin must use http or https with a host")
    if parsed.username or parsed.password:
        raise GuardrailError("target origin must not contain credentials")
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise GuardrailError("target origin must not contain a path, query, or fragment")
    host = parsed.hostname.encode("idna").decode("ascii").lower()
    try:
        port = parsed.port
    except ValueError as exc:
        raise GuardrailError("target origin contains an invalid port") from exc
    default_port = 80 if parsed.scheme == "http" else 443
    netloc = f"[{host}]" if ":" in host else host
    if port is not None and port != default_port:
        netloc = f"{netloc}:{port}"
    return urlunsplit((parsed.scheme, netloc, "", "", ""))


def resolve_addresses(origin: str) -> set[ipaddress.IPv4Address | ipaddress.IPv6Address]:
    parsed = urlsplit(origin)
    assert parsed.hostname
    port = parsed.port or (80 if parsed.scheme == "http" else 443)
    try:
        infos = socket.getaddrinfo(parsed.hostname, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise GuardrailError(f"target host resolution failed: {exc}") from exc
    addresses = {ipaddress.ip_address(info[4][0].split("%", 1)[0]) for info in infos}
    if not addresses:
        raise GuardrailError("target host resolved to no addresses")
    return addresses


def origin_is_loopback(origin: str) -> bool:
    addresses = resolve_addresses(origin)
    return bool(addresses) and all(address.is_loopback for address in addresses)


def path_is_allowed(path: str, prefixes: Iterable[str]) -> bool:
    if not path.startswith("/"):
        return False
    for prefix in prefixes:
        if prefix == "/":
            return True
        if prefix.endswith("/") and path.startswith(prefix):
            return True
        if path == prefix or path.startswith(prefix + "/"):
            return True
    return False


def semver_tuple(value: object) -> tuple[int, int, int] | None:
    if not isinstance(value, str) or not re.fullmatch(r"\d+\.\d+\.\d+", value):
        return None
    return tuple(int(part) for part in value.split("."))  # type: ignore[return-value]


def resolve_under_root(root: Path, relative: str) -> Path:
    if not relative or "\x00" in relative:
        raise GuardrailError("empty or invalid path")
    root = root.resolve()
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise GuardrailError(f"path escapes project root: {relative}") from exc
    return candidate


def sensitive_environment_names(source: Mapping[str, str], pattern: str) -> list[str]:
    try:
        matcher = re.compile(pattern)
    except re.error as exc:
        raise GuardrailError(f"invalid secret environment pattern: {exc}") from exc
    return sorted(name for name in source if matcher.search(name))


def current_utc() -> datetime:
    override = os.environ.get("HARNESS_TEST_NOW")
    return parse_datetime(override, "HARNESS_TEST_NOW") if override else datetime.now(timezone.utc)
