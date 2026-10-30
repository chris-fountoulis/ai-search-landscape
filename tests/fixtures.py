"""Build throwaway repository trees for tool tests."""

import os
import shutil
import tempfile

from tests import helpers
import common


def record(**extra):
    base = {
        "name": "Acme Search",
        "slug": "acme-search",
        "dataset": "ai-search",
        "company": "Acme Search",
        "website": "acme.example",
        "segment": "geo-tracking",
        "hq": {"city": "Berlin", "country": "DE"},
        "founded": {"year": 2024, "source": "https://acme.example/about"},
        "status": "active",
        "funding": {"total_usd": 21000000, "latest_round": {"name": "Series A"},
                    "source": "https://news.example/acme-raises"},
        "pricing": {"as_listed_by_vendor": "$95 to $495", "source": "https://acme.example/pricing"},
        "sources": ["https://acme.example/about", "https://news.example/acme-raises",
                    "https://acme.example/pricing"],
        "last_verified": "2026-10-26",
    }
    base.update(extra)
    return {k: v for k, v in base.items() if v is not None}


class TempRepo:
    """A temporary checkout with the real schema/ and a chosen set of records."""

    def __init__(self):
        self.root = tempfile.mkdtemp(prefix="landscape-test-")
        shutil.copytree(os.path.join(helpers.ROOT, "schema"), os.path.join(self.root, "schema"))
        self.schema = common.load_schema(self.root)

    def write(self, rec, raw=None, filename=None):
        folder = os.path.join(self.root, "data", rec.get("dataset", "ai-search"))
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, filename or (rec["slug"] + ".yaml"))
        text = raw if raw is not None else common.canonical_text(rec, self.schema)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        return path

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)


__all__ = ["record", "TempRepo"]
