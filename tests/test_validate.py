import contextlib
import io
import os
import unittest

from tests import helpers  # noqa: F401
from tests.fixtures import TempRepo, record
import common
import validate


class ValidateTests(unittest.TestCase):
    def setUp(self):
        self.repo = TempRepo()

    def tearDown(self):
        self.repo.cleanup()

    def failures(self, **kwargs):
        return validate.run(self.repo.root, **kwargs)

    def only_errors(self):
        result = self.failures()
        return [e for errs in result.values() for e in errs]

    def test_valid_record_passes(self):
        self.repo.write(record())
        self.assertEqual(self.failures(), {})

    def test_slug_and_dataset_must_match_location(self):
        self.repo.write(record(), filename="other-name.yaml")
        self.repo.write(record(slug="beta", name="Beta", dataset="ai-agents", segment="builders"),
                        filename="beta.yaml")
        os.replace(os.path.join(self.repo.root, "data", "ai-agents", "beta.yaml"),
                   os.path.join(self.repo.root, "data", "ai-search", "beta.yaml"))
        errs = "\n".join(self.only_errors())
        self.assertIn("file is named other-name.yaml", errs)
        self.assertIn("the file is in data/ai-search/", errs)

    def test_vocabularies(self):
        self.repo.write(record(segment="seo-stuff", hq={"country": "XX"}, status="sleeping",
                               pricing={"as_listed_by_vendor": "custom", "model": "per seat"}))
        errs = "\n".join(self.only_errors())
        self.assertIn("segment: 'seo-stuff'", errs)
        self.assertIn("hq/country: 'XX'", errs)
        self.assertIn("status: 'sleeping'", errs)
        self.assertIn("pricing/model: only used in the ai-agents dataset", errs)

    def test_field_sources_must_be_listed(self):
        self.repo.write(record(sources=["https://acme.example/about"]))
        errs = "\n".join(self.only_errors())
        self.assertIn("funding.source: https://news.example/acme-raises must also be listed", errs)
        self.assertIn("pricing.source", errs)

    def test_hq_and_round_sources_must_be_listed(self):
        self.repo.write(record(
            hq={"city": "Berlin", "country": "DE", "source": "https://acme.example/imprint"},
            funding={"total_usd": 21000000, "source": "https://news.example/acme-raises",
                     "latest_round": {"name": "Series A", "source": "https://news.example/acme-series-a"}}))
        errs = "\n".join(self.only_errors())
        self.assertIn("hq.source: https://acme.example/imprint must also be listed", errs)
        self.assertIn("funding.latest_round.source: https://news.example/acme-series-a must also be listed", errs)

    def test_price_with_number_needs_source(self):
        self.repo.write(record(pricing={"as_listed_by_vendor": "from $49"}))
        self.assertIn("pricing: a price with a number needs pricing.source", self.only_errors())

    def test_custom_price_needs_no_source(self):
        self.repo.write(record(pricing={"as_listed_by_vendor": "custom"}))
        self.assertEqual(self.failures(), {})

    def test_bad_urls(self):
        rec = record()
        rec["sources"] = rec["sources"] + ["https://localhost/x", "https://exa mple.com"]
        self.repo.write(rec)
        errs = "\n".join(self.only_errors())
        self.assertIn("sources/3: URL host 'localhost'", errs)
        self.assertIn("sources/4", errs)

    def test_status_consistency(self):
        self.repo.write(record(status="acquired"))
        self.repo.write(record(slug="b", name="B", website="b.example",
                               acquisition={"acquirer": "Bigco", "source": "https://acme.example/about"}))
        errs = "\n".join(self.only_errors())
        self.assertIn("status: acquired needs an acquisition block", errs)
        self.assertIn("acquisition: set status to acquired", errs)

    def test_public_company_has_no_total(self):
        self.repo.write(record(public_company=True))
        self.assertTrue(any("public companies carry no funding total" in e for e in self.only_errors()))

    def test_dash_ban(self):
        self.repo.write(record(hq={"city": "Berlin \u2014 Mitte", "country": "DE"}))
        self.assertTrue(any("U+2014" in e for e in self.only_errors()))

    def test_duplicates_within_dataset(self):
        self.repo.write(record())
        self.repo.write(record(slug="acme-search-2"))
        errs = "\n".join(self.only_errors())
        self.assertIn("name: 'Acme Search' is already used", errs)

    def test_canonical_form(self):
        rec = record()
        text = common.canonical_text(rec, self.repo.schema)
        self.repo.write(rec, raw=text.replace('"Berlin"', "Berlin"))
        self.assertIn("not in canonical form: run python3 tools/fmt.py", self.only_errors())
        self.assertEqual(self.failures(format_check=False), {})

    def test_yaml_errors_are_reported(self):
        self.repo.write(record(), raw="name: yes\n")
        self.assertTrue(any(e.startswith("YAML:") for e in self.only_errors()))

    def test_main_exit_codes(self):
        self.repo.write(record())
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(validate.main(["--root", self.repo.root]), 0)
            self.repo.write(record(segment="nope"))
            self.assertEqual(validate.main(["--root", self.repo.root]), 1)


if __name__ == "__main__":
    unittest.main()
