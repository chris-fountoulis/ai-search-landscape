import json
import os
import unittest

from tests import helpers
import schemalite
from schemalite import SchemaError

SCHEMA_PATH = os.path.join(helpers.ROOT, "schema", "company.schema.json")


def minimal(**extra):
    record = {
        "name": "Acme Search",
        "slug": "acme-search",
        "dataset": "ai-search",
        "company": "Acme Search",
        "website": "acme.example",
        "segment": "geo-tracking",
        "status": "active",
        "sources": ["https://acme.example/about"],
        "last_verified": "2026-10-26",
    }
    record.update(extra)
    return record


class CompanySchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(SCHEMA_PATH, encoding="utf-8") as fh:
            cls.schema = json.load(fh)

    def errors(self, record):
        return schemalite.validate(record, self.schema)

    def test_minimal_record_is_valid(self):
        self.assertEqual(self.errors(minimal()), [])

    def test_full_record_is_valid(self):
        record = minimal(
            hq={"city": "Berlin", "country": "DE"},
            founded={"year": 2024, "source": "https://acme.example/about"},
            funding={
                "total_usd": 21000000,
                "latest_round": {"name": "Series A", "date": "2025-11", "amount_usd": 21000000},
                "source": "https://news.example/acme-raises",
            },
            pricing={"as_listed_by_vendor": "$95 to $495", "source": "https://acme.example/pricing"},
        )
        self.assertEqual(self.errors(record), [])

    def test_missing_required_and_unknown_field(self):
        record = minimal(revenue_usd=5)
        del record["sources"]
        errs = self.errors(record)
        self.assertTrue(any("sources: required" in e for e in errs))
        self.assertTrue(any("revenue_usd: unknown field" in e for e in errs))

    def test_number_block_requires_source(self):
        errs = self.errors(minimal(founded={"year": 2024}))
        self.assertTrue(any("founded/source" in e for e in errs))
        errs = self.errors(minimal(funding={"total_usd": 5}))
        self.assertTrue(any("funding/source" in e for e in errs))

    def test_formats(self):
        errs = self.errors(minimal(
            slug="Acme_Search", website="https://acme.example", last_verified="2026-13-01",
            hq={"country": "Germany"}, sources=["ftp://x", "ftp://x"],
        ))
        joined = "\n".join(errs)
        for part in ("slug", "website", "last_verified", "hq/country", "sources/0", "duplicate"):
            self.assertIn(part, joined)

    def test_booleans_are_not_integers(self):
        errs = self.errors(minimal(founded={"year": True, "source": "https://a.example"}))
        self.assertTrue(any("founded/year: expected integer" in e for e in errs))


class ValidatorTests(unittest.TestCase):
    def test_unsupported_keyword_is_an_error(self):
        with self.assertRaises(SchemaError):
            schemalite.validate({}, {"type": "object", "oneOf": []})

    def test_enum_and_bounds(self):
        schema = {"type": "integer", "minimum": 1, "maximum": 3}
        self.assertEqual(schemalite.validate(2, schema), [])
        self.assertEqual(len(schemalite.validate(4, schema)), 1)
        self.assertEqual(len(schemalite.validate("a", {"enum": ["b"]})), 1)


if __name__ == "__main__":
    unittest.main()
