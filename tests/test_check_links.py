import os
import socket
import tempfile
import unittest
import urllib.error

from tests import helpers  # noqa: F401
from tests.fixtures import TempRepo, record
import check_links


class FakeClock:
    def __init__(self):
        self.now = 0.0
        self.slept = []

    def clock(self):
        return self.now

    def sleep(self, seconds):
        self.slept.append(round(seconds, 3))
        self.now += seconds


class CheckLinksTests(unittest.TestCase):
    def test_classify(self):
        self.assertEqual(check_links.classify(200), "ok")
        self.assertEqual(check_links.classify(301), "ok")
        self.assertEqual(check_links.classify(404), "broken")
        self.assertEqual(check_links.classify(403), "blocked")
        self.assertEqual(check_links.classify(999), "blocked")
        self.assertEqual(check_links.classify(500), "error")
        self.assertEqual(check_links.classify(None, socket.gaierror("x")), "broken")
        err = urllib.error.URLError(socket.gaierror(8, "nodename nor servname provided"))
        self.assertEqual(check_links.classify(None, err), "broken")
        self.assertEqual(check_links.classify(None, TimeoutError("timed out")), "error")

    def test_head_then_get_fallback(self):
        calls = []

        def fetcher(url, method, timeout):
            calls.append(method)
            return (405, url) if method == "HEAD" else (200, url)

        clock = FakeClock()
        checker = check_links.Checker(fetcher=fetcher, per_host_delay=1.5, sleep=clock.sleep, clock=clock.clock)
        res = checker.check("https://a.example/x")
        self.assertEqual(calls, ["HEAD", "GET"])
        self.assertEqual(res["outcome"], "ok")
        self.assertEqual(res["method"], "GET")
        self.assertEqual(clock.slept, [1.5])  # second request to the same host waited its turn

    def test_dns_failure_stops_early(self):
        calls = []

        def fetcher(url, method, timeout):
            calls.append(method)
            raise urllib.error.URLError(socket.gaierror(-2, "Name or service not known"))

        res = check_links.Checker(fetcher=fetcher, per_host_delay=0).check("https://gone.example")
        self.assertEqual(res["outcome"], "broken")
        self.assertEqual(calls, ["HEAD"])

    def test_collect_and_report(self):
        repo = TempRepo()
        try:
            repo.write(record())
            refs = check_links.collect(repo.root)
            self.assertIn("https://acme.example", refs)
            self.assertEqual(refs["https://acme.example/about"], ["ai-search/acme-search: sources[0]"])

            def fetcher(url, method, timeout):
                return (404, url) if url.endswith("/pricing") else (200, url)

            checker = check_links.Checker(fetcher=fetcher, per_host_delay=0)
            results = check_links.run(refs, checker, workers=2)
            md = check_links.report_md(results, "2026-11-02 06:00")
            self.assertIn("| broken | 1 |", md)
            self.assertIn("https://acme.example/pricing | 404 | ai-search/acme-search: sources[2]", md)
            self.assertNotIn("## Blocked", md)
        finally:
            repo.cleanup()

    def test_main_writes_report_and_exit_codes(self):
        repo = TempRepo()
        repo.write(record())
        out = tempfile.mkdtemp()
        original = check_links.fetch
        check_links.fetch = lambda url, method, timeout: (404, url)
        try:
            import contextlib
            import io
            report = os.path.join(out, "r.md")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(check_links.main(["--root", repo.root, "--report", report,
                                                   "--per-host-delay", "0"]), 0)
                self.assertEqual(check_links.main(["--root", repo.root, "--report", report,
                                                   "--per-host-delay", "0", "--fail-on-broken"]), 1)
            self.assertTrue(os.path.exists(report))
        finally:
            check_links.fetch = original
            repo.cleanup()


if __name__ == "__main__":
    unittest.main()
