"""Paths, vocabularies and record helpers shared by the tools."""

import json
import os
from collections import OrderedDict

import yamlite

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
SCHEMA_DIR = os.path.join(ROOT, "schema")
DIST_DIR = os.path.join(ROOT, "dist")

REPO_SLUG = "chris-fountoulis/ai-search-landscape"
REPO_URL = "https://github.com/" + REPO_SLUG

DATASETS = OrderedDict([
    ("ai-search", {
        "title": "AI Search Optimization Companies",
        "study_url": "https://growthofinfluence.com/ai-search-optimization-companies/",
        "edition": "2026-10",
        "unit": "companies",
    }),
    ("ai-agents", {
        "title": "AI Agent Companies",
        "study_url": "https://growthofinfluence.com/ai-agent-companies/",
        "edition": "2026-10",
        "unit": "products",
    }),
])

HEADER = (
    "AI Search Landscape, by Growth Of Influence. Data licensed CC BY 4.0.\n"
    "Schema: schema/company.schema.json. A missing field means not disclosed, never zero."
)

DASHES = ("\u2013", "\u2014")


def load_json(*parts):
    with open(os.path.join(*parts), encoding="utf-8") as fh:
        return json.load(fh, object_pairs_hook=OrderedDict)


def load_schema(root=ROOT):
    return load_json(root, "schema", "company.schema.json")


def load_vocab(root=ROOT):
    """Return a dict of id sets and label maps for every controlled vocabulary."""
    vocab_dir = os.path.join(root, "schema", "vocab")
    segments = load_json(vocab_dir, "segments.json")
    countries = load_json(vocab_dir, "countries.json")["countries"]
    pricing = load_json(vocab_dir, "pricing-models.json")
    statuses = load_json(vocab_dir, "statuses.json")
    return {
        "segments": {ds: OrderedDict((s["id"], s["label"]) for s in items) for ds, items in segments.items()},
        "countries": OrderedDict((c["code"], c["name"]) for c in countries),
        "regions": {c["code"]: c.get("region") or "Other" for c in countries},
        "pricing_models": OrderedDict((p["id"], p["label"]) for p in pricing),
        "statuses": OrderedDict((s["id"], s["label"]) for s in statuses),
    }


def record_paths(root=ROOT, datasets=None):
    """Yield (dataset, path) for every YAML file under data/, sorted."""
    data_dir = os.path.join(root, "data")
    for dataset in datasets or DATASETS:
        folder = os.path.join(data_dir, dataset)
        if not os.path.isdir(folder):
            continue
        for name in sorted(os.listdir(folder)):
            if name.endswith((".yaml", ".yml")):
                yield dataset, os.path.join(folder, name)


def load_records(root=ROOT, datasets=None):
    """Return {dataset: [record, ...]} sorted by slug. Raises yamlite.YamlError."""
    out = OrderedDict((ds, []) for ds in (datasets or DATASETS))
    for dataset, path in record_paths(root, datasets):
        out[dataset].append(yamlite.load(path))
    for dataset in out:
        out[dataset].sort(key=lambda r: str(r.get("slug", "")))
    return out


def _ordered(value, schema, root_schema):
    if "$ref" in schema:
        ref = schema["$ref"][2:].split("/")
        node = root_schema
        for part in ref:
            node = node[part]
        schema = node
    if isinstance(value, dict) and "properties" in schema:
        props = schema["properties"]
        out = OrderedDict()
        for key in props:
            if key in value:
                out[key] = _ordered(value[key], props[key], root_schema)
        for key in value:  # unknown keys keep their place at the end; validate reports them
            if key not in out:
                out[key] = value[key]
        return out
    return value


def canonical(record, schema):
    """Return ``record`` with keys in schema order, ready for yamlite.dumps."""
    return _ordered(record, schema, schema)


def canonical_text(record, schema):
    return yamlite.dumps(canonical(record, schema), header=HEADER)


def iter_strings(value, path=()):
    """Yield (path, string) for every string inside a record."""
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, sub in value.items():
            for item in iter_strings(sub, path + (key,)):
                yield item
    elif isinstance(value, list):
        for i, sub in enumerate(value):
            for item in iter_strings(sub, path + (i,)):
                yield item


def yaml_url(dataset, slug):
    return f"{REPO_URL}/blob/main/data/{dataset}/{slug}.yaml"
