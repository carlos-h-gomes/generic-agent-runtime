#!/usr/bin/env python3
"""Validate or execute a bounded defensive HTTP contract plan."""

from __future__ import annotations

import argparse
from datetime import timezone
from pathlib import Path
import sys
import urllib.error
import urllib.request
from urllib.parse import unquote, urljoin, urlsplit

from harnesslib.guardrails import (
    GuardrailError,
    current_utc,
    load_json_object,
    normalize_origin,
    origin_is_loopback,
    parse_datetime,
    path_is_allowed,
    resolve_addresses,
)
from harnesslib.reporting import CheckReport
import schema_lite


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
SECRET_HEADERS = {"authorization", "cookie", "proxy-authorization", "x-api-key"}
FORBIDDEN_HEADERS = SECRET_HEADERS | {"content-length", "host", "transfer-encoding"}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


def decoded_safe_path(path: str, scenario_id: str) -> str:
    decoded = path
    for _ in range(3):
        next_value = unquote(decoded)
        if next_value == decoded:
            break
        decoded = next_value
    raw_slashes = path.count("/")
    decoded_slashes = decoded.count("/")
    unsafe_segments = any(segment in {".", ".."} for segment in decoded.split("/"))
    if (
        decoded.startswith("//")
        or "\\" in decoded
        or "?" in decoded
        or "#" in decoded
        or raw_slashes != decoded_slashes
        or unsafe_segments
        or any(ord(char) < 32 for char in decoded)
    ):
        raise GuardrailError(
            f"scenario {scenario_id} path has ambiguous encoded delimiters or traversal"
        )
    return decoded


def load_and_validate(root: Path, path: Path, schema_name: str) -> dict:
    value = load_json_object(path)
    schema = load_json_object(root / "schemas" / schema_name)
    schema_lite.check_schema(schema)
    schema_lite.validate(value, schema)
    return value


def canonical_plan(plan: dict) -> str:
    origin = normalize_origin(plan.get("target_origin"))
    if plan.get("target_origin") != origin:
        raise GuardrailError(f"target origin must be canonical: {origin}")
    if plan.get("max_requests", 0) < len(plan.get("scenarios", [])):
        raise GuardrailError("plan max_requests is below the number of scenarios")
    ids: set[str] = set()
    for scenario in plan.get("scenarios", []):
        scenario_id = scenario["id"]
        if scenario_id in ids:
            raise GuardrailError(f"duplicate scenario id: {scenario_id}")
        ids.add(scenario_id)
        path = scenario["path"]
        if (
            not path.startswith("/")
            or path.startswith("//")
            or "\\" in path
            or "?" in path
            or "#" in path
            or any(ord(char) < 32 for char in path)
        ):
            raise GuardrailError(
                f"scenario {scenario_id} path must be a single-origin absolute path"
            )
        decoded_safe_path(path, scenario_id)
        method = scenario["method"]
        headers = scenario.get("headers", {})
        unsafe_headers = sorted(name for name in headers if name.casefold() in FORBIDDEN_HEADERS)
        if unsafe_headers:
            raise GuardrailError(
                f"scenario {scenario_id} embeds forbidden/secret header(s): {', '.join(unsafe_headers)}"
            )
        for name, value in headers.items():
            if "\r" in name or "\n" in name or "\r" in value or "\n" in value:
                raise GuardrailError(f"scenario {scenario_id} contains header line breaks")
        if method != "POST" and scenario.get("body") not in (None, ""):
            raise GuardrailError(f"scenario {scenario_id} attaches a body to {method}")
        if method == "POST" and scenario.get("body") is None:
            raise GuardrailError(f"scenario {scenario_id} POST requires an explicit inert body")
    return origin


def authorized_scope(root: Path, scope_path: Path, origin: str, plan: dict) -> dict:
    scope = load_and_validate(root, scope_path, "authorized-target.schema.json")
    scoped_origin = normalize_origin(scope.get("target_origin"))
    if scope.get("target_origin") != scoped_origin or scoped_origin != origin:
        raise GuardrailError("authorization target origin does not exactly match the canonical plan origin")
    now = current_utc()
    valid_from = parse_datetime(scope.get("valid_from"), "valid_from")
    expires = parse_datetime(scope.get("expires_at"), "expires_at")
    if not (valid_from <= now <= expires):
        raise GuardrailError(
            f"authorization is not active at {now.astimezone(timezone.utc).isoformat()}"
        )
    if scope.get("destructive_actions_allowed") is not False:
        raise GuardrailError("destructive actions must remain prohibited")
    if plan["max_requests"] > scope["max_requests"]:
        raise GuardrailError("plan request budget exceeds authorization")
    for scenario in plan["scenarios"]:
        if scenario["method"] not in scope["allowed_methods"]:
            raise GuardrailError(f"scenario {scenario['id']} method exceeds authorization")
        decoded_path = decoded_safe_path(scenario["path"], scenario["id"])
        if not path_is_allowed(decoded_path, scope["allowed_path_prefixes"]):
            raise GuardrailError(f"scenario {scenario['id']} path exceeds authorization")
    return scope


def prepare_execution(root: Path, plan: dict, scope_path: Path | None) -> tuple[str, dict]:
    origin = canonical_plan(plan)
    loopback = origin_is_loopback(origin)
    methods = {scenario["method"] for scenario in plan["scenarios"]}
    if loopback and methods.issubset(SAFE_METHODS) and scope_path is None:
        return origin, {
            "target_origin": origin,
            "allowed_methods": sorted(SAFE_METHODS),
            "allowed_path_prefixes": ["/"],
            "max_requests": plan["max_requests"],
            "max_response_bytes": 262144,
            "request_timeout_seconds": 5,
            "scope_id": "implicit-loopback-safe-methods",
        }
    if scope_path is None:
        reason = "POST requires explicit scope" if "POST" in methods else "non-loopback execution requires explicit scope"
        raise GuardrailError(reason)
    return origin, authorized_scope(root, scope_path, origin, plan)


def execute(root: Path, plan: dict, scope_path: Path | None, report: CheckReport) -> None:
    origin, scope = prepare_execution(root, plan, scope_path)
    initial_addresses = resolve_addresses(origin)
    opener = urllib.request.build_opener(NoRedirect())
    request_count = 0
    for scenario in plan["scenarios"]:
        if request_count >= min(plan["max_requests"], scope["max_requests"]):
            report.failed("request budget exhausted before all scenarios completed")
            return
        current_addresses = resolve_addresses(origin)
        if current_addresses != initial_addresses:
            report.failed(f"target address set changed during execution; stopped before {scenario['id']}")
            return
        if all(address.is_loopback for address in initial_addresses) is False and scope_path is None:
            report.failed("target is no longer loopback and has no explicit scope")
            return

        url = urljoin(origin + "/", scenario["path"].lstrip("/"))
        parsed_url = urlsplit(url)
        request_origin = normalize_origin(
            f"{parsed_url.scheme}://{parsed_url.netloc}"
        )
        if request_origin != origin:
            report.failed(f"{scenario['id']}: constructed URL escaped the authorized origin")
            return
        headers = {
            "User-Agent": "GenericAgentRuntime-Safe-Assurance/6.0",
            "Accept": "text/html,application/json;q=0.9,*/*;q=0.1",
            **scenario.get("headers", {}),
        }
        body_text = scenario.get("body")
        body = body_text.encode("utf-8") if isinstance(body_text, str) else None
        request = urllib.request.Request(url, data=body, headers=headers, method=scenario["method"])
        request_count += 1
        try:
            response = opener.open(request, timeout=scope["request_timeout_seconds"])
        except urllib.error.HTTPError as exc:
            response = exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            report.failed(f"{scenario['id']}: request failed without response ({type(exc).__name__})")
            return

        with response:
            status = response.status
            response_headers = {name.casefold(): value for name, value in response.headers.items()}
            limit = min(scope["max_response_bytes"], 1_048_576)
            body_bytes = response.read(limit + 1)
        if len(body_bytes) > limit:
            report.failed(f"{scenario['id']}: response exceeded {limit} bytes")
            return
        if status not in scenario["expected_status"]:
            report.failed(f"{scenario['id']}: status {status} not in expected set")
            return
        missing = [
            name
            for name in scenario["required_headers"]
            if name.casefold() not in response_headers
        ]
        if missing:
            report.failed(f"{scenario['id']}: missing required header(s) {', '.join(missing)}")
            return
        text = body_bytes.decode("utf-8", errors="replace")
        exposed = [marker for marker in scenario["forbidden_body_markers"] if marker in text]
        if exposed:
            report.failed(f"{scenario['id']}: forbidden response marker detected (marker names withheld)")
            return
        report.passed(f"{scenario['id']}: bounded response contract passed")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("command", choices=("plan", "execute"))
    result.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    result.add_argument("--plan", type=Path, required=True)
    result.add_argument("--scope", type=Path)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = args.root.resolve()
    report = CheckReport("adversarial_lab")
    try:
        plan_path = args.plan if args.plan.is_absolute() else root / args.plan
        plan = load_and_validate(root, plan_path.resolve(), "security-test-plan.schema.json")
        origin = canonical_plan(plan)
        report.passed(
            f"plan {plan['plan_id']} is schema-valid: {len(plan['scenarios'])} scenario(s), "
            f"budget {plan['max_requests']}, target {origin}"
        )
        if args.command == "plan":
            for scenario in plan["scenarios"]:
                print(
                    f"PLAN {scenario['id']} method={scenario['method']} "
                    f"path={scenario['path']} side_effect_free=true"
                )
            report.na("plan mode performed no network request")
        else:
            scope_path = None
            if args.scope:
                scope_path = args.scope if args.scope.is_absolute() else root / args.scope
                scope_path = scope_path.resolve()
            execute(root, plan, scope_path, report)
    except (GuardrailError, schema_lite.SchemaValidationError, OSError, KeyError, TypeError) as exc:
        print(f"FAIL invalid or unauthorized adversarial test plan: {exc}", file=sys.stderr)
        return 2
    return report.emit()


if __name__ == "__main__":
    raise SystemExit(main())
