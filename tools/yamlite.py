"""A strict, dependency-free loader and dumper for the YAML subset used in data/.

Every record in this repository is a small YAML document. Full YAML is a large
language with surprising implicit typing (``no`` becomes ``False``, ``2026-10``
can become a date, ``1e3`` a float). Rather than depend on PyYAML and fight
those rules, the dataset uses a deliberately small subset that is still valid
YAML, so any YAML library can read the files:

* block mappings with lowercase ``snake_case`` keys, indented by two spaces
* block sequences of scalars (``- "https://..."``)
* scalars: double-quoted strings (JSON escapes), plain strings, integers,
  ``true``, ``false`` and ``null``; the empty flow collections ``[]`` and ``{}``
* full-line comments and trailing comments after a value

Anything else (anchors, tags, flow collections with content, multi-line
strings, tabs, duplicate keys) is rejected with a file and line number.

``dump()`` writes the canonical form: every string double-quoted, keys in the
order given, two-space indentation. ``tools/fmt.py`` rewrites files into that
form and ``tools/validate.py`` reports files that are not canonical.
"""

import json
import re

__all__ = ["YamlError", "loads", "load", "dumps", "dump"]

_KEY_RE = re.compile(r"^([a-z][a-z0-9_]*):(?:[ ]+(.*))?$")
_INT_RE = re.compile(r"^-?(?:0|[1-9][0-9]*)$")
_PLAIN_FORBIDDEN_START = set("!&*|>'%@`{[]},?:#\"")


class YamlError(ValueError):
    """Raised when a document is outside the supported subset."""

    def __init__(self, message, line=None, source=None):
        self.line = line
        self.source = source
        where = ""
        if source:
            where += str(source)
        if line is not None:
            where += (":" if where else "line ") + str(line)
        super().__init__(f"{where}: {message}" if where else message)


def _strip_comment(text, lineno, source):
    """Return ``text`` without a trailing comment, respecting double quotes."""
    if text.startswith('"'):
        # Find the closing quote, honouring backslash escapes.
        i = 1
        while i < len(text):
            ch = text[i]
            if ch == "\\":
                i += 2
                continue
            if ch == '"':
                rest = text[i + 1:]
                stripped = rest.strip()
                if stripped and not stripped.startswith("#"):
                    raise YamlError("unexpected text after quoted string", lineno, source)
                if stripped.startswith("#") and not rest.startswith((" ", "\t")):
                    raise YamlError("a comment needs a space before '#'", lineno, source)
                return text[: i + 1]
            i += 1
        raise YamlError("unterminated double-quoted string", lineno, source)
    idx = text.find(" #")
    if idx >= 0:
        text = text[:idx]
    return text.rstrip()


def _scalar(text, lineno, source):
    if text == "":
        return None
    if text.startswith('"'):
        try:
            value = json.loads(text)
        except ValueError as exc:
            raise YamlError(f"invalid double-quoted string ({exc})", lineno, source)
        if not isinstance(value, str):
            raise YamlError("invalid double-quoted string", lineno, source)
        return value
    if text == "[]":
        return []
    if text == "{}":
        return {}
    if text in ("null", "~"):
        return None
    if text == "true":
        return True
    if text == "false":
        return False
    if _INT_RE.match(text):
        return int(text)
    if text[0] in _PLAIN_FORBIDDEN_START or text[0] in "-" and text[:2] == "- ":
        raise YamlError(f"unsupported value {text!r}: quote it with double quotes", lineno, source)
    if ": " in text or text.endswith(":"):
        raise YamlError(f"unsupported value {text!r}: quote it with double quotes", lineno, source)
    if text.lower() in ("yes", "no", "on", "off", "true", "false", "null"):
        raise YamlError(f"ambiguous value {text!r}: quote it or use true/false/null", lineno, source)
    if re.match(r"^[-+]?(\.[0-9]|[0-9])[0-9_.eE+:-]*$", text):
        raise YamlError(f"ambiguous number-like value {text!r}: quote it", lineno, source)
    return text


def _tokenize(text, source):
    lines = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        if "\t" in raw[: len(raw) - len(raw.lstrip())]:
            raise YamlError("tabs are not allowed for indentation", lineno, source)
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped in ("---", "..."):
            raise YamlError("document markers are not supported", lineno, source)
        indent = len(raw) - len(raw.lstrip(" "))
        if indent % 2:
            raise YamlError("indentation must be a multiple of two spaces", lineno, source)
        lines.append((lineno, indent, raw.rstrip()[indent:]))
    return lines


def _parse_block(lines, pos, indent, source):
    lineno, ind, content = lines[pos]
    if ind != indent:
        raise YamlError("unexpected indentation", lineno, source)
    if content.startswith("- ") or content == "-":
        return _parse_list(lines, pos, indent, source)
    return _parse_map(lines, pos, indent, source)


def _parse_list(lines, pos, indent, source):
    out = []
    while pos < len(lines):
        lineno, ind, content = lines[pos]
        if ind < indent:
            break
        if ind > indent:
            raise YamlError("unexpected indentation inside a list", lineno, source)
        if not (content.startswith("- ") or content == "-"):
            raise YamlError("expected a list item ('- value')", lineno, source)
        item = content[2:].strip() if content != "-" else ""
        if item == "":
            raise YamlError("empty list items and nested lists are not supported", lineno, source)
        if _KEY_RE.match(item) and not item.startswith('"'):
            raise YamlError("lists of mappings are not supported", lineno, source)
        out.append(_scalar(_strip_comment(item, lineno, source), lineno, source))
        pos += 1
    return out, pos


def _parse_map(lines, pos, indent, source):
    out = {}
    while pos < len(lines):
        lineno, ind, content = lines[pos]
        if ind < indent:
            break
        if ind > indent:
            raise YamlError("unexpected indentation", lineno, source)
        m = _KEY_RE.match(content)
        if not m:
            if content.startswith("- "):
                raise YamlError("list item where a key was expected", lineno, source)
            raise YamlError("expected 'key: value' with a lowercase snake_case key", lineno, source)
        key, rest = m.group(1), m.group(2)
        if key in out:
            raise YamlError(f"duplicate key {key!r}", lineno, source)
        pos += 1
        rest = _strip_comment(rest, lineno, source) if rest else ""
        if rest == "":
            if pos < len(lines) and lines[pos][1] > indent:
                if lines[pos][1] != indent + 2:
                    raise YamlError("nested blocks must be indented by two spaces", lines[pos][0], source)
                value, pos = _parse_block(lines, pos, indent + 2, source)
            else:
                value = None
        else:
            value = _scalar(rest, lineno, source)
            if pos < len(lines) and lines[pos][1] > indent:
                raise YamlError("unexpected indentation after a value", lines[pos][0], source)
        out[key] = value
    return out, pos


def loads(text, source=None):
    """Parse ``text`` and return a dict. Raises :class:`YamlError`."""
    if text.startswith("﻿"):
        raise YamlError("byte order marks are not allowed", 1, source)
    lines = _tokenize(text, source)
    if not lines:
        return {}
    if lines[0][1] != 0:
        raise YamlError("the document must start at column 0", lines[0][0], source)
    if lines[0][2].startswith("- "):
        raise YamlError("the top level must be a mapping", lines[0][0], source)
    value, pos = _parse_map(lines, 0, 0, source)
    if pos != len(lines):
        raise YamlError("unexpected content", lines[pos][0], source)
    return value


def load(path):
    with open(path, encoding="utf-8") as fh:
        return loads(fh.read(), source=str(path))


def _dump_scalar(value):
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    raise TypeError(f"unsupported value type {type(value).__name__}")


def _dump_map(data, indent, out):
    pad = " " * indent
    for key, value in data.items():
        if not isinstance(key, str) or not _KEY_RE.match(key + ":"):
            raise ValueError(f"invalid key {key!r}")
        if isinstance(value, dict):
            if not value:
                out.append(f"{pad}{key}: {{}}")
            else:
                out.append(f"{pad}{key}:")
                _dump_map(value, indent + 2, out)
        elif isinstance(value, list):
            if not value:
                out.append(f"{pad}{key}: []")
            else:
                out.append(f"{pad}{key}:")
                for item in value:
                    if isinstance(item, (dict, list)):
                        raise ValueError("lists may only contain scalars")
                    out.append(f"{pad}  - {_dump_scalar(item)}")
        else:
            out.append(f"{pad}{key}: {_dump_scalar(value)}")


def dumps(data, header=None):
    """Return ``data`` (a dict) in canonical form, with an optional comment header."""
    out = []
    if header:
        for line in header.splitlines():
            out.append(("# " + line).rstrip())
    _dump_map(data, 0, out)
    return "\n".join(out) + "\n"


def dump(data, path, header=None):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(dumps(data, header=header))
