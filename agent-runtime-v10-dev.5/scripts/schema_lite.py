#!/usr/bin/env python3
"""Self-contained validator for the JSON Schema keyword subset used by Harness contracts."""

from __future__ import annotations

from datetime import date, datetime
import json
import math
import re
from typing import Any
from urllib.parse import urlsplit


class SchemaValidationError(ValueError):
    pass


def _json_equal(left: Any, right: Any) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    return left == right


def _matches_type(instance: Any, expected: str) -> bool:
    return {
        "null": instance is None,
        "boolean": isinstance(instance, bool),
        "object": isinstance(instance, dict),
        "array": isinstance(instance, list),
        "string": isinstance(instance, str),
        "integer": isinstance(instance, int) and not isinstance(instance, bool),
        "number": isinstance(instance, (int, float))
        and not isinstance(instance, bool)
        and not (isinstance(instance, float) and (math.isnan(instance) or math.isinf(instance))),
    }.get(expected, False)


def _resolve(root: dict, reference: str) -> Any:
    if not reference.startswith("#/"):
        raise SchemaValidationError(f"only local JSON pointers are supported: {reference}")
    value: Any = root
    for raw in reference[2:].split("/"):
        key = raw.replace("~1", "/").replace("~0", "~")
        if not isinstance(value, dict) or key not in value:
            raise SchemaValidationError(f"unresolved schema reference: {reference}")
        value = value[key]
    return value


def _format_ok(value: str, format_name: str) -> bool:
    try:
        if format_name == "date":
            date.fromisoformat(value)
            return True
        if format_name == "date-time":
            normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
            parsed = datetime.fromisoformat(normalized)
            return parsed.tzinfo is not None
        if format_name == "uri":
            parsed = urlsplit(value)
            return bool(parsed.scheme and (parsed.netloc or parsed.scheme in {"urn", "file"}))
    except (ValueError, OverflowError):
        return False
    return True


def is_valid(instance: Any, schema: Any, root: dict | None = None) -> bool:
    try:
        validate(instance, schema, root=root)
        return True
    except SchemaValidationError:
        return False


def validate(instance: Any, schema: Any, *, root: dict | None = None, path: str = "$") -> None:
    if isinstance(schema, bool):
        if not schema:
            raise SchemaValidationError(f"{path}: rejected by false schema")
        return
    if not isinstance(schema, dict):
        raise SchemaValidationError(f"{path}: schema must be an object or boolean")
    root = schema if root is None else root

    if "$ref" in schema:
        validate(instance, _resolve(root, schema["$ref"]), root=root, path=path)
        return

    for item in schema.get("allOf", []):
        validate(instance, item, root=root, path=path)
    if "anyOf" in schema and not any(is_valid(instance, item, root) for item in schema["anyOf"]):
        raise SchemaValidationError(f"{path}: no anyOf branch matched")
    if "oneOf" in schema and sum(is_valid(instance, item, root) for item in schema["oneOf"]) != 1:
        raise SchemaValidationError(f"{path}: exactly one oneOf branch must match")
    if "not" in schema and is_valid(instance, schema["not"], root):
        raise SchemaValidationError(f"{path}: instance matched a forbidden schema")
    if "if" in schema:
        branch = schema.get("then") if is_valid(instance, schema["if"], root) else schema.get("else")
        if branch is not None:
            validate(instance, branch, root=root, path=path)

    if "const" in schema and not _json_equal(instance, schema["const"]):
        raise SchemaValidationError(f"{path}: value does not match const")
    if "enum" in schema and not any(_json_equal(instance, item) for item in schema["enum"]):
        raise SchemaValidationError(f"{path}: value is not in enum")

    expected = schema.get("type")
    if expected is not None:
        choices = [expected] if isinstance(expected, str) else expected
        if not isinstance(choices, list) or not all(isinstance(item, str) for item in choices):
            raise SchemaValidationError(f"{path}: invalid schema type declaration")
        if not any(_matches_type(instance, item) for item in choices):
            raise SchemaValidationError(f"{path}: expected type {choices}")

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for name in required:
            if name not in instance:
                raise SchemaValidationError(f"{path}: missing required property {name!r}")
        properties = schema.get("properties", {})
        if properties and not isinstance(properties, dict):
            raise SchemaValidationError(f"{path}: invalid properties schema")
        for name, value in instance.items():
            child_path = f"{path}.{name}"
            if name in properties:
                validate(value, properties[name], root=root, path=child_path)
            else:
                additional = schema.get("additionalProperties", True)
                if additional is False:
                    raise SchemaValidationError(f"{path}: unexpected property {name!r}")
                if isinstance(additional, dict):
                    validate(value, additional, root=root, path=child_path)
        if "minProperties" in schema and len(instance) < schema["minProperties"]:
            raise SchemaValidationError(f"{path}: too few properties")
        if "maxProperties" in schema and len(instance) > schema["maxProperties"]:
            raise SchemaValidationError(f"{path}: too many properties")

    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            raise SchemaValidationError(f"{path}: too few items")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            raise SchemaValidationError(f"{path}: too many items")
        if schema.get("uniqueItems"):
            normalized = [json.dumps(item, sort_keys=True, separators=(",", ":")) for item in instance]
            if len(normalized) != len(set(normalized)):
                raise SchemaValidationError(f"{path}: array items must be unique")
        if "items" in schema:
            for index, value in enumerate(instance):
                validate(value, schema["items"], root=root, path=f"{path}[{index}]")
        if "contains" in schema and not any(is_valid(value, schema["contains"], root) for value in instance):
            raise SchemaValidationError(f"{path}: array does not contain a required match")

    if isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0):
            raise SchemaValidationError(f"{path}: string is too short")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            raise SchemaValidationError(f"{path}: string is too long")
        if "pattern" in schema:
            try:
                matched = re.search(schema["pattern"], instance)
            except re.error as exc:
                raise SchemaValidationError(f"{path}: invalid schema pattern: {exc}") from exc
            if not matched:
                raise SchemaValidationError(f"{path}: string does not match pattern")
        if "format" in schema and not _format_ok(instance, schema["format"]):
            raise SchemaValidationError(f"{path}: invalid {schema['format']} format")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            raise SchemaValidationError(f"{path}: number is below minimum")
        if "maximum" in schema and instance > schema["maximum"]:
            raise SchemaValidationError(f"{path}: number is above maximum")


def check_schema(schema: dict) -> None:
    """Check local references and the keyword shapes relied on by this validator."""

    if not isinstance(schema, dict):
        raise SchemaValidationError("schema root must be an object")

    def walk(value: Any, path: str) -> None:
        if isinstance(value, dict):
            if "$ref" in value:
                if not isinstance(value["$ref"], str):
                    raise SchemaValidationError(f"{path}.$ref must be a string")
                _resolve(schema, value["$ref"])
            if "type" in value:
                declared = value["type"]
                if not isinstance(declared, (str, list)):
                    raise SchemaValidationError(f"{path}.type has invalid shape")
            for key, child in value.items():
                walk(child, f"{path}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{path}[{index}]")

    walk(schema, "$")
