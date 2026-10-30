#!/usr/bin/env python3
"""Rewrite data files into canonical form (quoted strings, schema key order).

Usage:
  python3 tools/fmt.py            rewrite every file under data/ that is not canonical
  python3 tools/fmt.py FILE...    rewrite only the given files
  python3 tools/fmt.py --check    list non-canonical files and exit 1, change nothing
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import common  # noqa: E402
import yamlite  # noqa: E402


def format_file(path, schema, check=False):
    """Return True when the file was (or, with check, would be) changed."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    record = yamlite.loads(text, source=path)
    new = common.canonical_text(record, schema)
    if new == text:
        return False
    if not check:
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(new)
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description="Canonicalise data/*.yaml files.")
    parser.add_argument("files", nargs="*", help="files to format (default: all of data/)")
    parser.add_argument("--check", action="store_true", help="report only, exit 1 if changes are needed")
    parser.add_argument("--root", default=common.ROOT)
    args = parser.parse_args(argv)

    schema = common.load_schema(args.root)
    paths = args.files or [p for _, p in common.record_paths(args.root)]
    changed, failed = [], []
    for path in paths:
        try:
            if format_file(path, schema, check=args.check):
                changed.append(path)
        except yamlite.YamlError as exc:
            failed.append(str(exc))
    for msg in failed:
        print(f"error: {msg}", file=sys.stderr)
    verb = "would reformat" if args.check else "reformatted"
    for path in changed:
        print(f"{verb} {os.path.relpath(path, args.root)}")
    print(f"{len(changed)} file(s) {verb}, {len(paths) - len(changed) - len(failed)} unchanged.")
    if failed or (args.check and changed):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
