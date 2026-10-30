import contextlib
import io
import unittest

from tests import helpers  # noqa: F401
from tests.fixtures import TempRepo, record
import common
import fmt


class FmtTests(unittest.TestCase):
    def setUp(self):
        self.repo = TempRepo()

    def tearDown(self):
        self.repo.cleanup()

    def test_rewrites_plain_scalars_and_key_order(self):
        rec = record()
        messy = (
            "slug: acme-search\nname: Acme Search\ndataset: ai-search\ncompany: Acme Search\n"
            "website: acme.example\nsegment: geo-tracking\nstatus: active\n"
            "sources:\n  - https://acme.example/about\nlast_verified: \"2026-10-26\"\n"
        )
        path = self.repo.write(rec, raw=messy)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(fmt.main(["--check", "--root", self.repo.root]), 1)
            self.assertEqual(fmt.main(["--root", self.repo.root]), 0)
            self.assertEqual(fmt.main(["--check", "--root", self.repo.root]), 0)
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        self.assertTrue(text.startswith("# AI Search Landscape"))
        self.assertLess(text.index("name:"), text.index("slug:"))
        self.assertIn('website: "acme.example"', text)
        self.assertEqual(text, common.canonical_text(common.yamlite.loads(text), self.repo.schema))


if __name__ == "__main__":
    unittest.main()
