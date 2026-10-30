#!/usr/bin/env python3
"""Validate every record in data/ against the schema and the dataset rules.

Checks, per file:
  * parses as the strict YAML subset (tools/yamlite.py)
  * matches schema/company.schema.json
  * dataset equals its folder and slug equals its file name
  * segment, country, pricing model and status come from schema/vocab/
  * every URL is a well-formed http(s) URL with a real host
  * every number sits in a block with a source, and every field-level source
    is also listed in sources
  * status agrees with the acquisition and closure blocks
  * no en dash or em dash anywhere in the file
  * the file is in canonical form (run tools/fmt.py to fix)
And across files: slugs, names and websites are unique within a dataset.

Exit status 0 when clean, 1 when any error is found.
Usage: python3 tools/validate.py [--root DIR] [--no-format-check]
"""

import argparse
import os
import re
import sys
from collections import defaultdict
from urllib.parse import urlsplit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import common  # noqa: E402
import schemalite  # noqa: E402
import yamlite  # noqa: E402

_HOST_RE = re.compile(r"^(?=.{1,253}$)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$", re.I)
_DIGIT_RE = re.compile(r"[0-9]")


def check_url(url):
    """Return an error message for a malformed URL, or None."""
    if any(ch.isspace() for ch in url):
        return "contains whitespace"
    try:
        parts = urlsplit(url)
    except ValueError as exc:
        return f"cannot be parsed ({exc})"
    if parts.scheme not in ("http", "https"):
        return "must start with http:// or https://"
    host = parts.hostname or ""
    if not _HOST_RE.match(host):
        return f"host {host!r} is not a valid domain name"
    if parts.username or parts.password:
        return "must not contain credentials"
    return None


def field_sources(record):
    """Yield (path, url) for every field-level source in a record."""
    for block in ("founded", "funding", "acquisition", "closure", "pricing"):
        value = record.get(block)
        if isinstance(value, dict) and isinstance(value.get("source"), str):
            yield block + ".source", value["source"]


def check_record(record, dataset, path, schema, vocab):
    """Return a list of error strings for one parsed record."""
    errors = list(schemalite.validate(record, schema))
    if not isinstance(record, dict):
        return errors
    slug = os.path.splitext(os.path.basename(path))[0]

    if record.get("dataset") != dataset:
        errors.append(f"dataset: is {record.get('dataset')!r} but the file is in data/{dataset}/")
    if record.get("slug") != slug:
        errors.append(f"slug: is {record.get('slug')!r} but the file is named {slug}.yaml")

    segment = record.get("segment")
    allowed = vocab["segments"].get(dataset, {})
    if segment is not None and segment not in allowed:
        errors.append(f"segment: {segment!r} is not in schema/vocab/segments.json for {dataset} "
                      f"(allowed: {', '.join(allowed)})")
    country = (record.get("hq") or {}).get("country")
    if country is not None and country not in vocab["countries"]:
        errors.append(f"hq/country: {country!r} is not an ISO 3166-1 alpha-2 code in schema/vocab/countries.json")
    model = (record.get("pricing") or {}).get("model")
    if model is not None:
        if dataset != "ai-agents":
            errors.append("pricing/model: only used in the ai-agents dataset")
        elif model not in vocab["pricing_models"]:
            errors.append(f"pricing/model: {model!r} is not in schema/vocab/pricing-models.json")
    status = record.get("status")
    if status is not None and status not in vocab["statuses"]:
        errors.append(f"status: {status!r} is not in schema/vocab/statuses.json")

    # URLs
    for key_path, value in common.iter_strings(record):
        if key_path and (key_path[-1] == "source" or key_path[0] == "sources"):
            problem = check_url(value)
            if problem:
                errors.append(f"{'/'.join(map(str, key_path))}: URL {problem}")

    # Sources for numbers
    sources = record.get("sources") if isinstance(record.get("sources"), list) else []
    for where, url in field_sources(record):
        if url not in sources:
            errors.append(f"{where}: {url} must also be listed in sources")
    pricing = record.get("pricing") or {}
    listed = pricing.get("as_listed_by_vendor")
    if isinstance(listed, str) and _DIGIT_RE.search(listed) and not pricing.get("source"):
        errors.append("pricing: a price with a number needs pricing.source")
    funding = record.get("funding") or {}
    if isinstance(funding, dict):
        if funding.get("bootstrapped") and funding.get("total_usd"):
            errors.append("funding: bootstrapped and a funding total cannot both be set")
        if record.get("public_company") and "total_usd" in funding:
            errors.append("funding/total_usd: public companies carry no funding total (see METHODOLOGY.md)")

    # Status consistency
    if status == "acquired" and "acquisition" not in record:
        errors.append("status: acquired needs an acquisition block with acquirer and source")
    if "acquisition" in record and status not in ("acquired", "closed"):
        errors.append("acquisition: set status to acquired (or closed) when an acquisition block exists")
    if status == "closed" and "closure" not in record:
        errors.append("status: closed needs a closure block with a source")
    if "closure" in record and status != "closed":
        errors.append("closure: only allowed when status is closed")

    return errors


def check_text(text):
    errors = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for dash in common.DASHES:
            if dash in line:
                errors.append(f"line {lineno}: contains U+{ord(dash):04X} ({'en' if dash == common.DASHES[0] else 'em'} dash); "
                              "use a comma, colon, period or hyphen")
    return errors


def run(root=common.ROOT, format_check=True):
    """Validate the tree at ``root``. Return {relative path: [errors]} for failing files."""
    schema = common.load_schema(root)
    vocab = common.load_vocab(root)
    failures = defaultdict(list)
    seen = defaultdict(dict)  # (dataset, field) -> {value: path}

    for dataset, path in common.record_paths(root):
        rel = os.path.relpath(path, root)
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        failures[rel].extend(check_text(text))
        if path.endswith(".yml"):
            failures[rel].append("use the .yaml extension")
        try:
            record = yamlite.loads(text, source=rel)
        except yamlite.YamlError as exc:
            failures[rel].append(f"YAML: {exc}")
            continue
        failures[rel].extend(check_record(record, dataset, path, schema, vocab))
        if format_check and not failures[rel]:
            if common.canonical_text(record, schema) != text:
                failures[rel].append("not in canonical form: run python3 tools/fmt.py")
        for field in ("slug", "name"):
            value = record.get(field)
            if isinstance(value, str):
                key = value.lower()
                other = seen[(dataset, field)].get(key)
                if other:
                    failures[rel].append(f"{field}: {value!r} is already used by {other}")
                else:
                    seen[(dataset, field)][key] = rel
        site = record.get("website")
        product = record.get("product") or record.get("name")
        if isinstance(site, str):
            key = (site.lower(), str(product).lower())
            other = seen[(dataset, "website")].get(key)
            if other:
                failures[rel].append(f"website: {site} is already used by {other} for the same product")
            else:
                seen[(dataset, "website")][key] = rel

    return {k: v for k, v in failures.items() if v}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--root", default=common.ROOT, help="repository root (default: this checkout)")
    parser.add_argument("--no-format-check", action="store_true", help="skip the canonical form check")
    args = parser.parse_args(argv)

    failures = run(args.root, format_check=not args.no_format_check)
    total = sum(1 for _ in common.record_paths(args.root))
    in_actions = os.environ.get("GITHUB_ACTIONS") == "true"
    for rel, errs in sorted(failures.items()):
        for err in errs:
            if in_actions:
                print(f"::error file={rel}::{err}")
            print(f"{rel}: {err}")
    if failures:
        count = sum(len(v) for v in failures.values())
        print(f"\n{count} error(s) in {len(failures)} of {total} file(s).", file=sys.stderr)
        return 1
    print(f"OK: {total} record(s) valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
