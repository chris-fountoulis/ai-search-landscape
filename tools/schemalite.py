"""A small JSON Schema (draft 2020-12) validator for the keywords this repo uses.

Supported keywords: type, enum, const, properties, required,
additionalProperties (boolean), minProperties, items, minItems, uniqueItems,
minLength, maxLength, pattern, minimum, maximum, format ("uri" is checked by
pattern only), description/title (ignored) and local $ref to "#/$defs/...".

An unsupported keyword raises SchemaError instead of being silently ignored,
so the schema can never claim a rule the validator does not enforce.
"""

import re

__all__ = ["SchemaError", "validate"]

_KNOWN = {
    "$schema", "$id", "$defs", "$ref", "title", "description", "type", "enum", "const",
    "properties", "required", "additionalProperties", "minProperties", "items",
    "minItems", "uniqueItems", "minLength", "maxLength", "pattern", "minimum",
    "maximum", "format",
}

_TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


class SchemaError(Exception):
    """The schema itself uses something this validator does not support."""


def _resolve(ref, root):
    if not ref.startswith("#/"):
        raise SchemaError(f"only local $ref is supported, got {ref!r}")
    node = root
    for part in ref[2:].split("/"):
        node = node[part]
    return node


def _path(parts):
    return "/".join(str(p) for p in parts) or "(root)"


def _check(value, schema, root, path, errors):
    unknown = set(schema) - _KNOWN
    if unknown:
        raise SchemaError(f"unsupported keywords at {_path(path)}: {sorted(unknown)}")
    if "$ref" in schema:
        _check(value, _resolve(schema["$ref"], root), root, path, errors)

    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_TYPES[t](value) for t in types):
            errors.append(f"{_path(path)}: expected {' or '.join(types)}, got {type(value).__name__}")
            return
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{_path(path)}: {value!r} is not one of {schema['enum']}")
    if "const" in schema and value != schema["const"]:
        errors.append(f"{_path(path)}: must be {schema['const']!r}")

    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{_path(path)}: shorter than {schema['minLength']} characters")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(f"{_path(path)}: longer than {schema['maxLength']} characters")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{_path(path)}: {value!r} does not match the expected format")

    if _TYPES["number"](value):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{_path(path)}: {value} is below the minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{_path(path)}: {value} is above the maximum {schema['maximum']}")

    if isinstance(value, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{_path(path + [key])}: required field is missing")
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in props:
                    errors.append(f"{_path(path + [key])}: unknown field")
        if "minProperties" in schema and len(value) < schema["minProperties"]:
            errors.append(f"{_path(path)}: needs at least {schema['minProperties']} fields")
        for key, sub in props.items():
            if key in value:
                _check(value[key], sub, root, path + [key], errors)

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{_path(path)}: needs at least {schema['minItems']} items")
        if schema.get("uniqueItems"):
            seen = set()
            for i, item in enumerate(value):
                marker = repr(item)
                if marker in seen:
                    errors.append(f"{_path(path + [i])}: duplicate item {item!r}")
                seen.add(marker)
        if "items" in schema:
            for i, item in enumerate(value):
                _check(item, schema["items"], root, path + [i], errors)


def validate(value, schema):
    """Return a list of human-readable error strings (empty when valid)."""
    errors = []
    _check(value, schema, schema, [], errors)
    return errors
