#!/usr/bin/env python3
"""Static validation for the mandatory extensible Python/React architecture."""

from __future__ import annotations

import argparse
import ast
import json
import posixpath
from pathlib import Path, PurePosixPath
import re
import sys


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
IMPORT_PATTERN = re.compile(
    r"(?:^|\n)\s*(?:import\s+(?:type\s+)?[^'\";]+?\s+from\s+|import\s*)['\"]([^'\"]+)['\"]",
    re.MULTILINE,
)


def load_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def logical_lines(path: Path) -> int:
    return sum(
        1
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith(("#", "//", "/*", "*"))
    )


def python_imports(tree: ast.AST) -> set[str]:
    result: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            result.add(node.module)
    return result


def mentions_layer(name: str, layer: str) -> bool:
    parts = name.replace("\\", ".").split(".")
    return layer in parts


def check_python(root: Path, policy: dict, failures: list[str]) -> None:
    backend = policy["backend"]
    app_root = root / backend["app_root"]
    forbidden_imports = {
        "controllers": {"models", "repositories"},
        "services": {"controllers"},
        "models": {"controllers", "services", "repositories"},
        "schemas": {"controllers", "services", "repositories"},
        "repositories": {"controllers", "services"},
    }
    for layer, blocked in forbidden_imports.items():
        for path in sorted((app_root / layer).rglob("*.py")):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except (SyntaxError, UnicodeError) as exc:
                failures.append(f"Python syntax {path.relative_to(root)}: {exc}")
                continue
            imports = python_imports(tree)
            for target in blocked:
                if any(mentions_layer(name, target) for name in imports):
                    failures.append(f"backend dependency reversal: {path.relative_to(root)} imports {target}")

    limit = int(policy["entrypoint_limits"]["max_non_comment_lines"])
    found = 0
    route_methods = {"get", "post", "put", "patch", "delete", "options", "head", "route", "websocket"}
    for raw in backend["entrypoints"]:
        path = root / raw
        if not path.is_file():
            continue
        found += 1
        if logical_lines(path) > limit:
            failures.append(f"backend entrypoint exceeds {limit} logical lines: {raw}")
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeError) as exc:
            failures.append(f"Python syntax {raw}: {exc}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                failures.append(f"backend entrypoint defines class {node.name}: {raw}")
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name not in {"create_app", "main", "lifespan"}:
                failures.append(f"backend entrypoint owns non-composition function {node.name}: {raw}")
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        decorator = decorator.func
                    if isinstance(decorator, ast.Attribute) and decorator.attr.lower() in route_methods:
                        failures.append(f"backend entrypoint defines HTTP route {node.name}: {raw}")
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {"execute", "executemany", "commit", "rollback", "query"}:
                failures.append(f"backend entrypoint contains persistence call {node.func.attr}: {raw}")
    if not found:
        failures.append("no declared backend composition entrypoint exists")


def source_layer(relative: Path) -> str | None:
    parts = relative.parts
    return parts[0] if parts else None


def target_layer(source: Path, specifier: str, src_root: Path) -> str | None:
    if not specifier.startswith("."):
        return None
    source_relative = source.relative_to(src_root).as_posix()
    normalized = posixpath.normpath(posixpath.join(posixpath.dirname(source_relative), specifier))
    if normalized.startswith("../") or normalized == "..":
        return "__outside__"
    parts = PurePosixPath(normalized).parts
    return parts[0] if parts else None


def check_frontend(root: Path, policy: dict, failures: list[str]) -> None:
    frontend = policy["frontend"]
    src_root = root / frontend["source_root"]
    forbidden = {
        "api": {"components", "context", "hooks", "pages", "services"},
        "assets": {"api", "components", "context", "hooks", "pages", "services"},
        "components": {"api", "pages", "services"},
        "data": {"api", "components", "context", "hooks", "pages", "services"},
        "services": {"components", "context", "hooks", "pages"},
        "utils": {"api", "components", "context", "hooks", "pages", "services"},
    }
    for path in sorted(item for item in src_root.rglob("*") if item.suffix in {".js", ".jsx", ".ts", ".tsx"}):
        relative = path.relative_to(src_root)
        layer = source_layer(relative)
        text = path.read_text(encoding="utf-8")
        for specifier in IMPORT_PATTERN.findall(text):
            target = target_layer(path, specifier, src_root)
            if target == "__outside__":
                failures.append(f"frontend source import escapes src: {path.relative_to(root)} -> {specifier}")
            elif layer in forbidden and target in forbidden[layer]:
                failures.append(f"frontend dependency reversal: {path.relative_to(root)} imports {target}")
        if layer == "utils" and re.search(r"(?:from\s+['\"]react['\"]|require\(['\"]react['\"]\))", text):
            failures.append(f"frontend utils must remain React-free: {path.relative_to(root)}")

    limit = int(policy["entrypoint_limits"]["max_non_comment_lines"])
    found = 0
    forbidden_signals = re.compile(r"\b(fetch\s*\(|axios\b|useState\s*\(|useEffect\s*\(|useReducer\s*\()")
    for raw in frontend["entrypoints"]:
        path = root / raw
        if not path.is_file():
            continue
        found += 1
        text = path.read_text(encoding="utf-8")
        if logical_lines(path) > limit:
            failures.append(f"frontend entrypoint exceeds {limit} logical lines: {raw}")
        if forbidden_signals.search(text):
            failures.append(f"frontend entrypoint contains feature or transport behavior: {raw}")
        declarations = re.findall(r"(?:function|class)\s+([A-Z][A-Za-z0-9_]*)", text)
        allowed = {"App"} if path.name.startswith("App.") else set()
        for name in declarations:
            if name not in allowed:
                failures.append(f"frontend entrypoint defines reusable component {name}: {raw}")
    if not found:
        failures.append("no declared frontend composition entrypoint exists")


def check_extensions(root: Path, policy: dict, failures: list[str]) -> None:
    authorities = [root / policy["extensions"]["authority"], root / policy["contracts"]["directory_map"]]
    authority_text = "\n".join(path.read_text(encoding="utf-8") for path in authorities if path.is_file())
    expected = {Path(path).name for path in policy["backend"]["required_directories"]}
    backend_root = root / policy["backend"]["app_root"]
    if backend_root.is_dir():
        for path in sorted(item for item in backend_root.iterdir() if item.is_dir() and not item.name.startswith((".", "__"))):
            if path.name not in expected and f"`{path.relative_to(root).as_posix()}/`" not in authority_text:
                failures.append(f"undocumented backend architectural extension: {path.relative_to(root)}")
    expected = {Path(path).name for path in policy["frontend"]["required_directories"] if Path(path).parent.name == "src"}
    frontend_root = root / policy["frontend"]["source_root"]
    if frontend_root.is_dir():
        for path in sorted(item for item in frontend_root.iterdir() if item.is_dir() and not item.name.startswith(".")):
            if path.name not in expected and f"`{path.relative_to(root).as_posix()}/`" not in authority_text:
                failures.append(f"undocumented frontend architectural extension: {path.relative_to(root)}")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    result.add_argument("--policy", type=Path, default=Path("docs/ai/architecture-policy.json"))
    result.add_argument("--profile", choices=("dev", "ci", "release"), default="ci")
    return result


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    root = arguments.root.resolve()
    policy_path = arguments.policy if arguments.policy.is_absolute() else root / arguments.policy
    application_detected = (root / "backend").exists() or (root / "frontend").exists()
    if not application_detected:
        print("NOT_APPLICABLE architecture: no application boundary detected")
        return 0
    if not policy_path.is_file():
        print("INCOMPLETE architecture: docs/ai/architecture-policy.json is missing")
        return 3
    try:
        policy = load_object(policy_path)
        if policy.get("schema_version") != "1.0" or policy.get("profile") != "python-react-hybrid":
            raise ValueError("unsupported architecture policy")
        failures: list[str] = []
        for raw in [*policy["backend"]["required_directories"], *policy["frontend"]["required_directories"]]:
            if not (root / raw).is_dir():
                failures.append(f"missing required directory: {raw}")
        check_python(root, policy, failures)
        check_frontend(root, policy, failures)
        check_extensions(root, policy, failures)
        if arguments.profile == "release" and not (root / policy["contracts"]["api"]).is_file():
            failures.append(f"release API contract is missing: {policy['contracts']['api']}")
        if failures:
            for failure in failures[:100]:
                print(f"FAIL architecture: {failure}")
            if len(failures) > 100:
                print(f"FAIL architecture: {len(failures) - 100} additional failures omitted")
            return 1
        print("PASS architecture: hybrid boundaries, minimum topology, dependencies, extensions, and entrypoints")
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"FAIL architecture: invalid policy or source: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
