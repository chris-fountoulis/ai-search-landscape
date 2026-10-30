"""Repository-wide checks that are cheap to run on every commit."""

import json
import os
import unittest

from tests import helpers

TEXT_EXTENSIONS = {".py", ".md", ".yml", ".yaml", ".json", ".csv", ".html", ".cff", ".txt", ""}
SKIP_DIRS = {".git", "__pycache__", "_site", ".venv", "venv"}


def text_files():
    for base, dirs, files in os.walk(helpers.ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if os.path.splitext(name)[1] in TEXT_EXTENSIONS:
                yield os.path.join(base, name)


class HygieneTests(unittest.TestCase):
    def test_no_en_or_em_dashes_anywhere(self):
        offenders = []
        for path in text_files():
            try:
                with open(path, encoding="utf-8") as fh:
                    for lineno, line in enumerate(fh, 1):
                        if "\u2013" in line or "\u2014" in line:
                            offenders.append(f"{os.path.relpath(path, helpers.ROOT)}:{lineno}")
            except UnicodeDecodeError:
                continue
        self.assertEqual(offenders, [], "en or em dashes found")

    def test_json_files_parse(self):
        for path in text_files():
            if path.endswith(".json"):
                with self.subTest(path=path), open(path, encoding="utf-8") as fh:
                    json.load(fh)

    def test_segment_vocab_matches_schema_datasets(self):
        with open(os.path.join(helpers.ROOT, "schema", "vocab", "segments.json"), encoding="utf-8") as fh:
            segments = json.load(fh)
        with open(os.path.join(helpers.ROOT, "schema", "company.schema.json"), encoding="utf-8") as fh:
            schema = json.load(fh)
        self.assertEqual(sorted(segments), sorted(schema["properties"]["dataset"]["enum"]))


if __name__ == "__main__":
    unittest.main()
