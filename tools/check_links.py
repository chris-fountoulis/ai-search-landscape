#!/usr/bin/env python3
"""Check every website and source URL in data/ and write a report. Report only.

Each URL is tried with HEAD and, when the server refuses HEAD or answers with
an error, again with GET. Requests carry a browser User-Agent, run on a few
threads, and are spaced per host so no site sees more than one request every
--per-host-delay seconds.

Results are grouped as:
  broken     404, 410, DNS failure, connection refused: the link needs fixing
  error      timeouts, TLS errors and 5xx answers: often temporary, recheck
  blocked    401, 403, 429, 999 and similar bot walls: could not be checked
  ok         2xx (after redirects)

The exit status is 0 even when links are broken, unless --fail-on-broken is
given. The weekly workflow turns the Markdown report into an issue.

Usage:
  python3 tools/check_links.py [--report link-report.md] [--json link-report.json]
                               [--dataset ai-search] [--limit N] [--workers 4]
"""

import argparse
import json
import os
import socket
import ssl
import sys
import threading
import time
import urllib.error
import urllib.request
from collections import OrderedDict, defaultdict
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlsplit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import common  # noqa: E402

USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
BLOCKED_CODES = {401, 403, 406, 429, 451, 503, 999}
BROKEN_CODES = {404, 410}
DNS_MARKERS = ("Name or service not known", "nodename nor servname", "Temporary failure in name resolution",
               "getaddrinfo failed", "No address associated", "Connection refused")


def collect(root=common.ROOT, datasets=None):
    """Return OrderedDict url -> list of 'dataset/slug: field' references."""
    refs = OrderedDict()
    for ds, recs in common.load_records(root, datasets).items():
        for rec in recs:
            where = f"{ds}/{rec['slug']}"
            refs.setdefault("https://" + rec["website"], []).append(f"{where}: website")
            for i, url in enumerate(rec.get("sources", [])):
                refs.setdefault(url, []).append(f"{where}: sources[{i}]")
    return refs


def classify(status, error=None):
    if error is not None:
        text = str(error)
        if isinstance(error, socket.gaierror) or any(marker in text for marker in DNS_MARKERS):
            return "broken"
        return "error"
    if 200 <= status < 400:
        return "ok"
    if status in BROKEN_CODES:
        return "broken"
    if status in BLOCKED_CODES:
        return "blocked"
    if status >= 500:
        return "error"
    return "broken"


def fetch(url, method, timeout):
    """Return (status, final_url). Raises on network errors."""
    req = urllib.request.Request(url, method=method, headers=HEADERS)
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            if method == "GET":
                resp.read(2048)
            return resp.status, resp.geturl()
    except urllib.error.HTTPError as exc:
        return exc.code, url


class Checker:
    def __init__(self, fetcher=None, timeout=20, per_host_delay=2.0, sleep=time.sleep, clock=time.monotonic):
        self.fetcher = fetcher
        self.timeout = timeout
        self.per_host_delay = per_host_delay
        self.sleep = sleep
        self.clock = clock
        self._next = defaultdict(float)
        self._locks = defaultdict(threading.Lock)
        self._guard = threading.Lock()

    def _wait_turn(self, host):
        with self._guard:
            lock = self._locks[host]
        with lock:
            now = self.clock()
            wait = self._next[host] - now
            if wait > 0:
                self.sleep(wait)
            self._next[host] = max(now, self._next[host]) + self.per_host_delay

    def check(self, url):
        host = (urlsplit(url).hostname or "").lower()
        result = {"url": url, "status": None, "method": None, "final_url": None, "error": None}
        for method in ("HEAD", "GET"):
            self._wait_turn(host)
            try:
                status, final = (self.fetcher or fetch)(url, method, self.timeout)
                result.update(status=status, method=method, final_url=final, error=None)
                if classify(status) == "ok":
                    break
            except Exception as exc:  # network errors of every kind are a result, not a crash
                result.update(status=None, method=method, error=f"{type(exc).__name__}: {exc}")
                if classify(None, exc) == "broken":
                    result["outcome"] = "broken"
                    return result
        result["outcome"] = classify(result["status"], result["error"] and Exception(result["error"]))
        return result


def run(refs, checker, workers=4, limit=None):
    urls = list(refs)[:limit] if limit else list(refs)
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        results = list(pool.map(checker.check, urls))
    for res in results:
        res["refs"] = refs[res["url"]]
    return results


def report_md(results, started):
    groups = OrderedDict((k, [r for r in results if r["outcome"] == k]) for k in ("broken", "error", "blocked", "ok"))
    lines = ["# Link check report", "",
             f"Checked {len(results)} unique URL(s) on {started} (UTC).", "",
             "| Outcome | URLs |", "|---|---:|"]
    lines += [f"| {k} | {len(v)} |" for k, v in groups.items()]
    for key, title in (("broken", "Broken (fix or replace the source)"),
                       ("error", "Errors (often temporary, recheck before editing)"),
                       ("blocked", "Blocked by the site (check by hand)")):
        if not groups[key]:
            continue
        lines += ["", f"## {title}", "", "| URL | Result | Used in |", "|---|---|---|"]
        for r in groups[key]:
            what = str(r["status"]) if r["status"] is not None else (r["error"] or "")[:80]
            used = "<br>".join(r["refs"][:5]) + (f"<br>and {len(r['refs']) - 5} more" if len(r["refs"]) > 5 else "")
            lines.append(f"| {r['url']} | {what.replace('|', '/')} | {used} |")
    lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check website and source URLs in data/ (report only).")
    parser.add_argument("--root", default=common.ROOT)
    parser.add_argument("--dataset", choices=list(common.DATASETS), action="append",
                        help="limit to one dataset (repeatable)")
    parser.add_argument("--limit", type=int, help="check only the first N unique URLs")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=float, default=20)
    parser.add_argument("--per-host-delay", type=float, default=2.0, help="seconds between requests to one host")
    parser.add_argument("--report", default="link-report.md", help="Markdown report path")
    parser.add_argument("--json", dest="json_path", help="also write the raw results as JSON")
    parser.add_argument("--fail-on-broken", action="store_true", help="exit 1 when any URL is broken")
    args = parser.parse_args(argv)

    started = time.strftime("%Y-%m-%d %H:%M", time.gmtime())
    refs = collect(args.root, args.dataset)
    checker = Checker(timeout=args.timeout, per_host_delay=args.per_host_delay)
    results = run(refs, checker, workers=args.workers, limit=args.limit)
    with open(args.report, "w", encoding="utf-8") as fh:
        fh.write(report_md(results, started))
    if args.json_path:
        with open(args.json_path, "w", encoding="utf-8") as fh:
            json.dump(results, fh, ensure_ascii=False, indent=1)
    counts = {k: sum(1 for r in results if r["outcome"] == k) for k in ("ok", "blocked", "error", "broken")}
    print(" ".join(f"{k}={v}" for k, v in counts.items()), f"report={args.report}")
    if args.fail_on_broken and counts["broken"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
