"""Guards the redirects in vercel.json and the crawl signals Google reads.

Fails on any redirect chain or loop, any destination page that doesn't exist, internal links or sitemap
URLs that land on a redirect, an apex (non-www) URL where www is canonical, and a site-wide robots block.
Search Console flagged a redirect error on Oct 15, 2026; these tests keep that class of bug from coming back.
"""
import glob
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WWW = "https://www.hvacmarketinghq.com"
APEX = re.compile(r"https?://hvacmarketinghq\.com")


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8", errors="ignore") as f:
        return f.read()


def load_redirects():
    return json.loads(read("vercel.json"))["redirects"]


def norm(path):
    """Vercel has trailingSlash false and cleanUrls true: /a/ and /a.html both end at /a."""
    path = path.split("#")[0].split("?")[0]
    if path.endswith(".html"):
        path = path[:-5]
    return path.rstrip("/") or "/"


def page_exists(path):
    path = norm(path)
    if path == "/":
        return os.path.exists(os.path.join(ROOT, "index.html"))
    rel = path.lstrip("/")
    return any(os.path.exists(os.path.join(ROOT, rel + ext)) for ext in (".html", "/index.html", ""))


def problems(redirects, exists=page_exists):
    """Every reason the redirect list is not 'one hop to a live page'. Empty list means clean."""
    out, by_src = [], {}
    for r in redirects:
        src = r["source"]
        if any(ch in src for ch in ":(*"):
            out.append(f"pattern source not checked by this test, add support first: {src}")
            continue
        if norm(src) in by_src:
            out.append(f"duplicate source: {src}")
        by_src[norm(src)] = r["destination"]
    for src, dest in by_src.items():
        if dest.startswith(WWW + "/") or dest == WWW:
            dest = dest[len(WWW):] or "/"  # absolute www is the same site; check it as a path
        elif APEX.match(dest):
            out.append(f"{src} -> {dest}: apex destination adds a 308 hop, use the path")
            continue
        elif not dest.startswith("/"):
            continue  # off-site (calendar etc.)
        if norm(dest) == src:
            out.append(f"{src} -> {dest}: redirects to itself")
        elif norm(dest) in by_src:
            seen, d = [src], norm(dest)
            while d in by_src and d not in seen:
                seen.append(d)
                d = norm(by_src[d]) if by_src[d].startswith("/") else by_src[d]
            kind = "loop" if d in seen else "chain"
            out.append(f"redirect {kind}: {' -> '.join(seen + [d])}")
        elif not exists(dest):
            out.append(f"{src} -> {dest}: destination page does not exist")
        if exists(src) and os.path.exists(os.path.join(ROOT, src.lstrip("/") + ".html")):
            out.append(f"{src}: a built page sits under this redirect and can never be reached")
    return out


class CheckerCatchesBadRedirects(unittest.TestCase):
    def r(self, *pairs):
        return [{"source": s, "destination": d, "permanent": True} for s, d in pairs]

    def test_loop(self):
        p = problems(self.r(("/hvac-google-ads", "/services/google-ads"), ("/services/google-ads", "/hvac-google-ads")), lambda _: True)
        self.assertTrue(any("loop" in x for x in p), p)

    def test_chain(self):
        p = problems(self.r(("/a", "/b"), ("/b", "/c")), lambda x: x == "/c")
        self.assertTrue(any("chain" in x for x in p), p)

    def test_missing_destination(self):
        p = problems(self.r(("/a", "/nope")), lambda _: False)
        self.assertTrue(any("does not exist" in x for x in p), p)

    def test_apex_destination(self):
        p = problems(self.r(("/a", "https://hvacmarketinghq.com/b")), lambda _: True)
        self.assertTrue(any("apex" in x for x in p), p)

    def test_clean(self):
        self.assertEqual(problems(self.r(("/a", "/b"), ("/book", "https://calendar.google.com/x")), lambda x: x == "/b"), [])


class VercelJson(unittest.TestCase):
    def test_every_redirect_is_one_hop_to_a_live_page(self):
        reds = load_redirects()
        self.assertGreater(len(reds), 200)
        self.assertEqual(problems(reds), [])

    def test_book_short_link_is_kept_and_temporary(self):
        book = [r for r in load_redirects() if r["source"] == "/book"]
        self.assertEqual(len(book), 1, "/book is linked from the report email (api/lead.js); keep it")
        self.assertFalse(book[0]["permanent"])


def built_html():
    for f in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True):
        rel = os.path.relpath(f, ROOT)
        if not rel.startswith(("node_modules", "client-kit", "api", "scripts", "tools")):
            yield rel, read(rel)


class CrawlSignals(unittest.TestCase):
    def test_no_internal_link_or_sitemap_url_hits_a_redirect(self):
        sources = {norm(r["source"]) for r in load_redirects()}
        bad = []
        for rel, html in built_html():
            for h in re.findall(r'href="(/[^"]*)"', html) + re.findall(re.escape(WWW) + r'(/[^"<\s)]*)', html):
                if norm(h) in sources and norm(h) != "/book":
                    bad.append(f"{rel}: {h}")
        sm = read("sitemap.xml")
        for loc in re.findall(r"<loc>([^<]+)</loc>", sm):
            self.assertTrue(loc.startswith(WWW + "/"), loc)
            path = loc[len(WWW):] or "/"
            if norm(path) in sources or not page_exists(path):
                bad.append(f"sitemap: {loc}")
        self.assertEqual(bad, [])

    def test_canonicals_and_links_use_www(self):
        bad = []
        for rel, html in built_html():
            if APEX.search(html):
                bad.append(rel)
            m = re.search(r'<link rel="canonical" href="([^"]+)"', html)
            if m and not m.group(1).startswith(WWW):
                bad.append(f"{rel}: canonical {m.group(1)}")
        for name in ("sitemap.xml", "robots.txt", "llms.txt"):
            if APEX.search(read(name)):
                bad.append(name)
        self.assertEqual(bad, [])

    def test_robots_allows_crawling(self):
        robots = read("robots.txt")
        self.assertNotRegex(robots, r"(?im)^disallow:\s*/\s*$")
        self.assertIn(f"Sitemap: {WWW}/sitemap.xml", robots)


def page_meta():
    """(url path, canonical, noindex) for every built page."""
    out = []
    for rel, html in built_html():
        path = "/" + rel[:-5]
        path = "/" if path == "/index" else path
        m = re.search(r'<link rel="canonical" href="([^"]+)"', html)
        rb = re.search(r'<meta name="robots" content="([^"]+)"', html)
        out.append((path, m.group(1) if m else None, bool(rb and "noindex" in rb.group(1))))
    return out


class SitemapClean(unittest.TestCase):
    """Every sitemap URL is a 200 page (a built file, not a redirect), indexable, and its own canonical."""

    def setUp(self):
        sm = read("sitemap.xml")
        self.entries = re.findall(r"<url><loc>([^<]+)</loc>(?:<lastmod>([^<]+)</lastmod>)?</url>", sm)
        self.urls = {loc[len(WWW):] or "/" for loc, _ in self.entries}
        self.meta = {p: (c, n) for p, c, n in page_meta()}
        self.sources = {norm(r["source"]) for r in load_redirects()}

    def test_sitemap_urls_are_live_indexable_self_canonical(self):
        bad = []
        for path in self.urls:
            if path in self.sources:
                bad.append(f"{path}: redirects")
            elif path not in self.meta:
                bad.append(f"{path}: no page (404)")
            else:
                canon, noindex = self.meta[path]
                if noindex:
                    bad.append(f"{path}: noindex")
                if canon != WWW + path:
                    bad.append(f"{path}: canonical {canon}")
        self.assertEqual(bad, [])

    def test_every_indexable_page_is_in_the_sitemap_and_self_canonical(self):
        bad = []
        for path, (canon, noindex) in self.meta.items():
            if canon and canon != WWW + path:
                bad.append(f"{path}: canonical {canon}")
            if canon and not noindex and path not in self.urls:
                bad.append(f"{path}: indexable but not in sitemap")
        self.assertEqual(bad, [])

    def test_location_urls_have_real_lastmod(self):
        missing = [loc for loc, lm in self.entries if "/locations" in loc and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", lm or "")]
        self.assertEqual(missing, [])

    def test_no_site_wide_noindex_header(self):
        for rule in json.loads(read("vercel.json")).get("headers", []):
            for h in rule["headers"]:
                self.assertNotEqual(h["key"].lower(), "x-robots-tag", rule["source"])

    def test_internal_links_resolve(self):
        sources, bad = self.sources | {"/book"}, set()
        for rel, html in built_html():
            for h in re.findall(r'href="(/[^"]*)"', html):
                p_ = norm(h)
                if p_ in sources or p_.startswith(("/_vercel", "/api/")) or "." in p_.rsplit("/", 1)[-1]:
                    continue
                if not page_exists(p_):
                    bad.add(f"{rel}: {h}")
        self.assertEqual(sorted(bad), [])


if __name__ == "__main__":
    unittest.main()
