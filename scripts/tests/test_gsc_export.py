import csv
import datetime as dt
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import gsc_export as g  # noqa: E402


class Resp:
    def __init__(self, status, body):
        self.status_code, self._body, self.text = status, body, str(body)

    def json(self):
        return self._body


class FakeSession:
    """Answers searchAnalytics.query like the real API: rows for the asked dimension, paged by startRow."""
    def __init__(self, data, fail_first=0):
        self.data, self.calls, self.fail_first = data, [], fail_first

    def post(self, url, json=None, timeout=None):
        self.calls.append((url, json))
        if self.fail_first:
            self.fail_first -= 1
            return Resp(429, {"error": "quota"})
        rows = self.data[json["dimensions"][0]]
        return Resp(200, {"rows": rows[json["startRow"]:json["startRow"] + json["rowLimit"]]})


def row(key, clicks, impr, pos):
    return {"keys": [key], "clicks": clicks, "impressions": impr, "ctr": clicks / impr, "position": pos}


DATA = {"query": [row("hvac marketing", 5, 100, 4.2), row("hvac seo", 1, 300, 9.5), row("hvac website design", 0, 50, 19.9),
                  row("hvac leads", 0, 20, 31.0)],
        "page": [row("https://www.hvacmarketinghq.com/", 6, 400, 7.9), row("https://www.hvacmarketinghq.com/hvac-seo", 1, 200, 12.0)]}


class GscExportTest(unittest.TestCase):
    def test_property_flag(self):
        self.assertEqual(g.resolve_property("domain"), "sc-domain:hvacmarketinghq.com")
        self.assertEqual(g.resolve_property("url"), "https://www.hvacmarketinghq.com/")
        self.assertEqual(g.resolve_property("sc-domain:example.com"), "sc-domain:example.com")

    def test_date_range(self):
        s, e = g.date_range(28, 3, dt.date(2026, 10, 19))
        self.assertEqual((s, e), (dt.date(2026, 9, 19), dt.date(2026, 10, 16)))

    def test_query_pages_and_encodes_site(self):
        sess = FakeSession(DATA)
        rows = g.query(sess, "sc-domain:hvacmarketinghq.com", dt.date(2026, 9, 1), dt.date(2026, 9, 28), "query", row_limit=3)
        self.assertEqual(len(rows), 4)
        self.assertEqual([c[1]["startRow"] for c in sess.calls], [0, 3])
        self.assertIn("/sites/sc-domain%3Ahvacmarketinghq.com/searchAnalytics/query", sess.calls[0][0])
        self.assertEqual(sess.calls[0][1]["startDate"], "2026-09-01")

    def test_retries_quota_then_succeeds(self):
        g.time.sleep, real = (lambda s: None), g.time.sleep
        try:
            sess = FakeSession(DATA, fail_first=1)
            self.assertEqual(len(g.query(sess, "x", dt.date(2026, 9, 1), dt.date(2026, 9, 2), "page")), 2)
        finally:
            g.time.sleep = real

    def test_error_raises(self):
        class Bad:
            def post(self, *a, **k):
                return Resp(403, {"error": "User does not have sufficient permission"})
        with self.assertRaises(RuntimeError):
            g.query(Bad(), "x", dt.date(2026, 9, 1), dt.date(2026, 9, 2), "query")

    def test_striking_distance(self):
        q = [{"query": r["keys"][0], **{k: r[k] for k in ("clicks", "impressions", "ctr", "position")}} for r in DATA["query"]]
        p = [{"page": r["keys"][0], **{k: r[k] for k in ("clicks", "impressions", "ctr", "position")}} for r in DATA["page"]]
        out = g.striking_distance(q, p)
        self.assertEqual([(r["type"], r["key"]) for r in out],
                         [("query", "hvac seo"), ("page", "https://www.hvacmarketinghq.com/hvac-seo"), ("query", "hvac website design")])

    def test_run_writes_three_csvs(self):
        with tempfile.TemporaryDirectory() as d:
            r = g.run(FakeSession(DATA), "sc-domain:hvacmarketinghq.com", d, today=dt.date(2026, 10, 19))
            self.assertEqual(sorted(os.listdir(d)), ["gsc-2026-10-19-pages.csv", "gsc-2026-10-19-positions-8-20.csv", "gsc-2026-10-19-queries.csv"])
            with open(r["paths"]["queries"], newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(list(rows[0].keys()), ["query", "clicks", "impressions", "ctr", "position"])
            self.assertEqual(rows[0]["query"], "hvac marketing")
            self.assertEqual(rows[0]["ctr"], "0.0500")
            with open(r["paths"]["positions-8-20"], newline="") as f:
                self.assertEqual(len(list(csv.DictReader(f))), 3)

    def test_main_needs_key_file(self):
        os.environ.pop("GSC_KEY_FILE", None)
        with self.assertRaises(SystemExit):
            g.main(["--key-file", ""])
        with self.assertRaises(SystemExit):
            g.main(["--key-file", "/nonexistent/key.json"])


if __name__ == "__main__":
    unittest.main()
