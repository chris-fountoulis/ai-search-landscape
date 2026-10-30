import unittest

from tests import helpers  # noqa: F401
import yamlite
from yamlite import YamlError


class LoadTests(unittest.TestCase):
    def test_nested_mapping_and_list(self):
        doc = yamlite.loads(
            "# header comment\n"
            'name: "Acme Search"\n'
            "hq:\n"
            "  city: Berlin\n"
            '  country: "DE"\n'
            "founded:\n"
            "  year: 2023  # trailing comment\n"
            "sources:\n"
            '  - "https://example.com/about"\n'
            "  - https://example.com/news#launch\n"
            "public_company: false\n"
            "note: null\n"
        )
        self.assertEqual(doc["name"], "Acme Search")
        self.assertEqual(doc["hq"], {"city": "Berlin", "country": "DE"})
        self.assertEqual(doc["founded"]["year"], 2023)
        self.assertEqual(doc["sources"][1], "https://example.com/news#launch")
        self.assertIs(doc["public_company"], False)
        self.assertIsNone(doc["note"])

    def test_quoted_escapes_and_hash(self):
        doc = yamlite.loads('price: "from $5 \\"per seat\\" # not a comment"\n')
        self.assertEqual(doc["price"], 'from $5 "per seat" # not a comment')

    def test_empty_collections_and_empty_value(self):
        doc = yamlite.loads("a: []\nb: {}\nc:\n")
        self.assertEqual(doc, {"a": [], "b": {}, "c": None})

    def test_rejects_ambiguous_scalars(self):
        for bad in ("date: 2026-10\n", "flag: yes\n", "n: 1e3\n", "v: 1.5\n", "x: 012\n"):
            with self.subTest(bad=bad):
                with self.assertRaises(YamlError):
                    yamlite.loads(bad)

    def test_rejects_unsupported_syntax(self):
        cases = [
            "a: &anchor 1\n",
            "a: [1, 2]\n",
            "a: |\n  text\n",
            "a: 'single'\n",
            "a:\n\t- x\n",
            "a:\n   b: 1\n",
            "a:\n  - b: 1\n",
            "Name: x\n",
            "a: 1\na: 2\n",
            "---\na: 1\n",
            "a: 1\n  b: 2\n",
            "- a\n",
            'a: "unterminated\n',
            'a: "x" trailing\n',
        ]
        for bad in cases:
            with self.subTest(bad=bad):
                with self.assertRaises(YamlError):
                    yamlite.loads(bad)

    def test_error_carries_line_number(self):
        with self.assertRaises(YamlError) as ctx:
            yamlite.loads("a: 1\nb: 2\nc: yes\n", source="x.yaml")
        self.assertEqual(ctx.exception.line, 3)
        self.assertIn("x.yaml:3", str(ctx.exception))


class DumpTests(unittest.TestCase):
    def test_round_trip_is_canonical(self):
        data = {
            "name": "Acme",
            "hq": {"city": "New York", "country": "US"},
            "funding": {"total_usd": 12000000, "source": "https://example.com/a"},
            "sources": ["https://example.com/a", "https://example.com/b"],
            "public_company": True,
            "empty": [],
        }
        text = yamlite.dumps(data, header="Example header")
        self.assertTrue(text.startswith("# Example header\n"))
        self.assertIn('  city: "New York"\n', text)
        self.assertIn("  total_usd: 12000000\n", text)
        self.assertEqual(yamlite.loads(text), data)
        self.assertEqual(yamlite.dumps(yamlite.loads(text), header="Example header"), text)

    def test_non_ascii_is_kept_readable(self):
        text = yamlite.dumps({"city": "Thessaloníki"})
        self.assertEqual(text, 'city: "Thessaloníki"\n')

    def test_rejects_nested_lists(self):
        with self.assertRaises(ValueError):
            yamlite.dumps({"a": [[1]]})


if __name__ == "__main__":
    unittest.main()
