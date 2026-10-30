import contextlib
import csv
import io
import json
import os
import unittest

from tests import helpers  # noqa: F401
from tests.fixtures import TempRepo, record
import build


def quiet(fn, *args):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(*args)


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.repo = TempRepo()
        self.repo.write(record())
        self.repo.write(record(slug="beta-labs", name="Beta Labs", company="Beta Labs", website="beta.example",
                               hq={"country": "US"}, founded={"year": 2019, "source": "https://acme.example/about"},
                               funding={"total_usd": 5000000, "source": "https://acme.example/about"},
                               pricing={"as_listed_by_vendor": "custom"},
                               status="acquired",
                               acquisition={"acquirer": "Bigco", "date": "2026-06", "date_type": "announced",
                                            "source": "https://acme.example/about"}))
        self.repo.write(record(dataset="ai-agents", segment="builders", slug="gamma-agents", name="Gamma (Agents)",
                               company="Gamma", product="Agents", website="gamma.example",
                               pricing={"as_listed_by_vendor": "$10 to $20 (as listed)", "model": "per seat",
                                        "source": "https://acme.example/pricing"}))
        self.repo.write(record(dataset="ai-agents", segment="builders", slug="lab-agent", name="Lab (Agent)",
                               company="Lab", website="lab.example", model_lab=True,
                               funding={"total_usd": 999000000000, "source": "https://acme.example/about"}))
        with open(os.path.join(self.repo.root, "README.md"), "w", encoding="utf-8") as fh:
            fh.write(f"# Title\n\n{build.README_START}\nold\n{build.README_END}\n\nTail\n")

    def tearDown(self):
        self.repo.cleanup()

    def path(self, rel):
        return os.path.join(self.repo.root, rel)

    def test_money(self):
        self.assertEqual(build.money(335000000), "$335M")
        self.assertEqual(build.money(29120000), "$29.1M")
        self.assertEqual(build.money(2601292000), "$2.60B")
        self.assertEqual(build.money(None), "")

    def test_build_then_check(self):
        self.assertEqual(quiet(build.main, ["--root", self.repo.root, "--check"]), 1)
        self.assertEqual(quiet(build.main, ["--root", self.repo.root]), 0)
        self.assertEqual(quiet(build.main, ["--root", self.repo.root, "--check"]), 0)
        with open(self.path("dist/ai-search.csv"), encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual([r["slug"] for r in rows], ["acme-search", "beta-labs"])
        self.assertEqual(rows[0]["hq_country_name"], "Germany")
        self.assertEqual(rows[0]["region"], "Europe")
        self.assertEqual(rows[1]["acquired_by"], "Bigco")
        self.assertTrue(rows[0]["yaml_url"].endswith("/data/ai-search/acme-search.yaml"))

    def test_json_outputs_are_valid_and_complete(self):
        quiet(build.main, ["--root", self.repo.root])
        with open(self.path("dist/landscape.json"), encoding="utf-8") as fh:
            land = json.load(fh)
        self.assertEqual(land["license"], "CC-BY-4.0")
        self.assertEqual(len(land["records"]), 4)
        self.assertEqual(land["datasets"]["ai-agents"]["count"], 2)
        self.assertEqual(sorted(land["countries"]), ["DE", "US"])
        with open(self.path("dist/ai-agents.json"), encoding="utf-8") as fh:
            agents = json.load(fh)
        self.assertEqual(agents["records"][0]["product"], "Agents")

    def test_stats_exclude_model_labs_and_count_companies_once(self):
        quiet(build.main, ["--root", self.repo.root])
        with open(self.path("STATS.md"), encoding="utf-8") as fh:
            stats = fh.read()
        self.assertIn("$26M across 2 companies", stats)       # 21M + 5M
        self.assertIn("$21M across 1 companies", stats)       # agents: lab excluded
        self.assertIn("| Model labs (outside funding totals) | Lab |", stats)
        self.assertIn("| 2019 | 1 |", stats)

    def test_readme_block_is_replaced_in_place(self):
        quiet(build.main, ["--root", self.repo.root])
        with open(self.path("README.md"), encoding="utf-8") as fh:
            text = fh.read()
        self.assertTrue(text.startswith("# Title\n"))
        self.assertTrue(text.endswith("\n\nTail\n"))
        self.assertNotIn("\nold\n", text)
        self.assertIn("pie showData title AI Search Optimization Companies", text)

    def test_build_refuses_invalid_data(self):
        self.repo.write(record(slug="bad", name="Bad", segment="nope"))
        self.assertEqual(quiet(build.main, ["--root", self.repo.root]), 1)

    def test_site_assembly(self):
        os.makedirs(self.path("site"))
        with open(self.path("site/index.html"), "w") as fh:
            fh.write("<!doctype html>")
        target = self.path("_site")
        quiet(build.main, ["--root", self.repo.root, "--site", target])
        self.assertTrue(os.path.exists(os.path.join(target, "index.html")))
        self.assertTrue(os.path.exists(os.path.join(target, "data", "landscape.json")))
        self.assertTrue(os.path.exists(os.path.join(target, ".nojekyll")))

    def test_deterministic(self):
        first = build.build_outputs(self.repo.root)
        second = build.build_outputs(self.repo.root)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
