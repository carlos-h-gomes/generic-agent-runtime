#!/usr/bin/env python3
"""Static validation for legacy and open, user-selected architecture profiles."""

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


def owning_module(path: Path, modules: list[dict], root: Path) -> str | None:
    matches: list[tuple[int, str]] = []
    for module in modules:
        base = root / module["path"]
        try:
            path.relative_to(base)
        except ValueError:
            continue
        matches.append((len(base.parts), module["id"]))
    return max(matches)[1] if matches else None


def resolve_relative_import(source: Path, specifier: str, root: Path) -> Path | None:
    if not specifier.startswith("."):
        return None
    candidate = (source.parent / specifier).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return Path("__outside__")
    return candidate


def check_open_dependencies(root: Path, modules: list[dict], failures: list[str]) -> None:
    allowed = {module["id"]: set(module["may_depend_on"]) for module in modules}
    for module in modules:
        base = root / module["path"]
        if not base.is_dir():
            continue
        for path in sorted(item for item in base.rglob("*") if item.suffix in {".js", ".jsx", ".ts", ".tsx"}):
            text = path.read_text(encoding="utf-8")
            for specifier in IMPORT_PATTERN.findall(text):
                target_path = resolve_relative_import(path, specifier, root)
                if target_path == Path("__outside__"):
                    failures.append(f"source import escapes project: {path.relative_to(root)} -> {specifier}")
                    continue
                if target_path is None:
                    continue
                target = owning_module(target_path, modules, root)
                if target and target != module["id"] and target not in allowed[module["id"]]:
                    failures.append(
                        f"dependency reversal: {path.relative_to(root)} imports module {target}; "
                        f"{module['id']} may depend on {sorted(allowed[module['id']])}"
                    )
        for path in sorted(base.rglob("*.py")):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except (SyntaxError, UnicodeError) as exc:
                failures.append(f"Python syntax {path.relative_to(root)}: {exc}")
                continue
            for imported in python_imports(tree):
                parts = imported.split(".")
                target = next((item["id"] for item in modules if item["id"] in parts), None)
                if target and target != module["id"] and target not in allowed[module["id"]]:
                    failures.append(
                        f"dependency reversal: {path.relative_to(root)} imports module {target}; "
                        f"{module['id']} may depend on {sorted(allowed[module['id']])}"
                    )


def check_open_entrypoint(root: Path, entrypoint: dict, failures: list[str]) -> bool:
    raw = entrypoint["path"]
    path = root / raw
    if not path.is_file():
        failures.append(f"missing composition root: {raw}")
        return False
    limit = int(entrypoint["max_non_comment_lines"])
    if logical_lines(path) > limit:
        failures.append(f"composition root exceeds {limit} logical lines: {raw}")
    adapter = entrypoint["adapter"]
    allowed = set(entrypoint["allowed_symbols"])
    if adapter == "manual":
        return bool(entrypoint["manual_evidence"])
    text = path.read_text(encoding="utf-8")
    if adapter == "python":
        try:
            tree = ast.parse(text, filename=str(path))
        except (SyntaxError, UnicodeError) as exc:
            failures.append(f"Python syntax {raw}: {exc}")
            return False
        route_methods = {"get", "post", "put", "patch", "delete", "options", "head", "route", "websocket"}
        persistence = {"execute", "executemany", "commit", "rollback", "query", "save", "delete"}
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.name not in allowed:
                failures.append(f"composition root owns undeclared symbol {node.name}: {raw}")
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for decorator in node.decorator_list:
                    target = decorator.func if isinstance(decorator, ast.Call) else decorator
                    if isinstance(target, ast.Attribute) and target.attr.lower() in route_methods:
                        failures.append(f"composition root defines HTTP route {node.name}: {raw}")
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr.lower() in persistence:
                failures.append(f"composition root contains persistence call {node.func.attr}: {raw}")
    else:
        forbidden = re.compile(
            r"\b(fetch\s*\(|axios\b|useState\s*\(|useEffect\s*\(|useReducer\s*\(|"
            r"(?:app|router)\.(?:get|post|put|patch|delete)\s*\(|"
            r"(?:query|execute|commit|rollback|save)\s*\()"
        )
        if forbidden.search(text):
            failures.append(f"composition root contains feature, route, persistence, or transport behavior: {raw}")
        declarations = re.findall(r"(?:function|class)\s+([A-Za-z_$][A-Za-z0-9_$]*)", text)
        for name in declarations:
            if name not in allowed:
                failures.append(f"composition root owns undeclared symbol {name}: {raw}")
    return True


def check_open_profile(root: Path, policy: dict, failures: list[str]) -> bool:
    organization = policy["organization"]
    modules = organization["modules"]
    ids = [module["id"] for module in modules]
    if len(ids) != len(set(ids)):
        failures.append("architecture module ids must be unique")
    known = set(ids)
    for module in modules:
        unknown = set(module["may_depend_on"]) - known
        if unknown or module["id"] in module["may_depend_on"]:
            failures.append(f"invalid dependency declaration for module {module['id']}: {sorted(unknown)}")
        if not (root / module["path"]).is_dir():
            failures.append(f"missing declared module directory: {module['path']}")
    for raw in organization["roots"]:
        if not (root / raw).is_dir():
            failures.append(f"missing architecture root: {raw}")
    check_open_dependencies(root, modules, failures)
    complete = True
    for entrypoint in organization["composition_roots"]:
        if entrypoint["adapter"] == "manual" and not entrypoint["manual_evidence"]:
            complete = False
        if not check_open_entrypoint(root, entrypoint, failures):
            complete = False
    return complete


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
    application_markers = (
        "backend", "frontend", "src", "app", "package.json", "pyproject.toml", "requirements.txt",
        "Pipfile", "pom.xml", "build.gradle", "build.gradle.kts", "go.mod", "Cargo.toml",
        "composer.json", "Gemfile", "Dockerfile", "docker-compose.yml", "compose.yml",
    )
    application_detected = any((root / marker).exists() for marker in application_markers)
    if not application_detected:
        print("NOT_APPLICABLE architecture: no application boundary detected")
        return 0
    adoption_path = root / ".harness" / "adoption-state.json"
    if adoption_path.is_file():
        try:
            adoption = load_object(adoption_path)
            disposition = adoption.get("architecture_disposition")
            posture = adoption.get("application_posture")
            if disposition == "profile_required":
                print(
                    "INCOMPLETE architecture: observed brownfield application requires an "
                    f"evidence-backed project policy (posture={posture})"
                )
                return 3
            if disposition == "migration_required":
                print("INCOMPLETE architecture: a separate approved architecture migration is required")
                return 3
        except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
            print(f"FAIL architecture: invalid adoption state: {exc}", file=sys.stderr)
            return 2
    if not policy_path.is_file():
        print("INCOMPLETE architecture: docs/ai/architecture-policy.json is missing")
        return 3
    try:
        policy = load_object(policy_path)
        failures: list[str] = []
        schema_version = policy.get("schema_version")
        complete = True
        if schema_version == "1.0" and policy.get("profile") == "python-react-hybrid":
            for raw in [*policy["backend"]["required_directories"], *policy["frontend"]["required_directories"]]:
                if not (root / raw).is_dir():
                    failures.append(f"missing required directory: {raw}")
            check_python(root, policy, failures)
            check_frontend(root, policy, failures)
            check_extensions(root, policy, failures)
            if arguments.profile == "release" and not (root / policy["contracts"]["api"]).is_file():
                failures.append(f"release API contract is missing: {policy['contracts']['api']}")
        elif schema_version == "2.0":
            complete = check_open_profile(root, policy, failures)
            if policy.get("status") == "migration_required":
                complete = False
            if policy.get("selection", {}).get("user_decision_status") == "pending":
                complete = False
            if arguments.profile == "release":
                for raw in policy["contracts"]["interfaces"]:
                    if not (root / raw).is_file():
                        failures.append(f"release interface contract is missing: {raw}")
        else:
            raise ValueError("unsupported architecture policy")
        if failures:
            for failure in failures[:100]:
                print(f"FAIL architecture: {failure}")
            if len(failures) > 100:
                print(f"FAIL architecture: {len(failures) - 100} additional failures omitted")
            return 1
        if not complete:
            print("INCOMPLETE architecture: adapter evidence, user decision, or migration closure is required")
            return 3
        print("PASS architecture: declared modules, dependencies, composition roots, contracts, and evidence")
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"FAIL architecture: invalid policy or source: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
