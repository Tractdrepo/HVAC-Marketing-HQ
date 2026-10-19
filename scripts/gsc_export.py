#!/usr/bin/env python3
"""Weekly Google Search Console export for hvacmarketinghq.com.

Pulls the last N days (default 28) of Search Analytics data by query and by page, and writes three CSVs
into an output folder, stamped with the run date:

  gsc-YYYY-MM-DD-queries.csv       query, clicks, impressions, ctr, position
  gsc-YYYY-MM-DD-pages.csv         page, clicks, impressions, ctr, position
  gsc-YYYY-MM-DD-positions-8-20.csv  queries and pages with average position 8 to 20 (page two, close to page one)

Auth: a Google Cloud service account JSON key (see README-seo-scripts.md). The key path comes from
--key-file or the GSC_KEY_FILE environment variable. Never commit the key.

The Search Console API is free (https://developers.google.com/webmaster-tools/pricing).
Plain Python, no AI. Needs: pip install -r scripts/requirements.txt
"""
import argparse
import csv
import datetime as dt
import os
import sys
import time
import urllib.parse

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
API = "https://searchconsole.googleapis.com/webmasters/v3/sites/{site}/searchAnalytics/query"
PROPERTIES = {"domain": "sc-domain:hvacmarketinghq.com", "url": "https://www.hvacmarketinghq.com/"}
ROW_LIMIT = 25000  # the API maximum per request


def resolve_property(value):
    """'domain' or 'url' map to the two hvacmarketinghq.com properties; anything else is used as given."""
    return PROPERTIES.get(value, value)


def date_range(days, lag_days, today=None):
    """Search Console data lags a few days, so the window ends lag_days before today and spans `days` days."""
    today = today or dt.date.today()
    end = today - dt.timedelta(days=lag_days)
    start = end - dt.timedelta(days=days - 1)
    return start, end


def make_session(key_file):
    """An authorized requests session from a service account key file."""
    from google.oauth2 import service_account
    from google.auth.transport.requests import AuthorizedSession
    creds = service_account.Credentials.from_service_account_file(key_file, scopes=SCOPES)
    return AuthorizedSession(creds)


def query(session, site, start, end, dimension, row_limit=ROW_LIMIT, max_rows=None, retries=3):
    """All rows for one dimension ('query' or 'page'), paging with startRow. Returns a list of dicts."""
    url = API.format(site=urllib.parse.quote(site, safe=""))
    rows, start_row = [], 0
    while True:
        body = {"startDate": start.isoformat(), "endDate": end.isoformat(), "dimensions": [dimension],
                "rowLimit": row_limit, "startRow": start_row, "dataState": "final"}
        for attempt in range(retries + 1):
            resp = session.post(url, json=body, timeout=60)
            if resp.status_code in (429, 500, 503) and attempt < retries:
                time.sleep(2 ** attempt * 5)
                continue
            break
        if resp.status_code != 200:
            raise RuntimeError(f"Search Console API {resp.status_code} for {dimension}: {resp.text[:300]}")
        page = resp.json().get("rows", [])
        for r in page:
            rows.append({dimension: r["keys"][0], "clicks": r.get("clicks", 0), "impressions": r.get("impressions", 0),
                         "ctr": r.get("ctr", 0.0), "position": r.get("position", 0.0)})
        if len(page) < row_limit or (max_rows and len(rows) >= max_rows):
            return rows[:max_rows] if max_rows else rows
        start_row += row_limit


def striking_distance(queries, pages, low=8.0, high=20.0):
    """Queries and pages with average position between low and high (inclusive), most impressions first."""
    out = [{"type": "query", "key": r["query"], **{k: r[k] for k in ("clicks", "impressions", "ctr", "position")}}
           for r in queries if low <= r["position"] <= high]
    out += [{"type": "page", "key": r["page"], **{k: r[k] for k in ("clicks", "impressions", "ctr", "position")}}
            for r in pages if low <= r["position"] <= high]
    return sorted(out, key=lambda r: (-r["impressions"], r["position"]))


def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({**r, "ctr": f'{r["ctr"]:.4f}', "position": f'{r["position"]:.1f}'})


def run(session, site, out_dir, days=28, lag_days=3, low=8.0, high=20.0, today=None):
    today = today or dt.date.today()
    start, end = date_range(days, lag_days, today)
    queries = query(session, site, start, end, "query")
    pages = query(session, site, start, end, "page")
    os.makedirs(out_dir, exist_ok=True)
    stamp = today.isoformat()
    paths = {name: os.path.join(out_dir, f"gsc-{stamp}-{name}.csv") for name in ("queries", "pages", "positions-8-20")}
    metrics = ["clicks", "impressions", "ctr", "position"]
    write_csv(paths["queries"], sorted(queries, key=lambda r: -r["clicks"]), ["query"] + metrics)
    write_csv(paths["pages"], sorted(pages, key=lambda r: -r["clicks"]), ["page"] + metrics)
    write_csv(paths["positions-8-20"], striking_distance(queries, pages, low, high), ["type", "key"] + metrics)
    return {"site": site, "start": start, "end": end, "queries": len(queries), "pages": len(pages), "paths": paths}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Export Search Console queries and pages to CSV (weekly job).")
    ap.add_argument("--property", default="domain",
                    help="'domain' = sc-domain:hvacmarketinghq.com (default), 'url' = https://www.hvacmarketinghq.com/, or any property string")
    ap.add_argument("--key-file", default=os.environ.get("GSC_KEY_FILE"),
                    help="service account JSON key (default: GSC_KEY_FILE env var)")
    ap.add_argument("--out", default=os.environ.get("GSC_OUT_DIR", "gsc-exports"), help="output folder (default: gsc-exports or GSC_OUT_DIR)")
    ap.add_argument("--days", type=int, default=28, help="days of data (default 28)")
    ap.add_argument("--lag-days", type=int, default=3, help="end the window this many days before today; data is a few days behind (default 3)")
    ap.add_argument("--min-position", type=float, default=8.0)
    ap.add_argument("--max-position", type=float, default=20.0)
    a = ap.parse_args(argv)
    if not a.key_file:
        ap.error("no key file: set GSC_KEY_FILE or pass --key-file (see scripts/README-seo-scripts.md)")
    if not os.path.isfile(a.key_file):
        ap.error(f"key file not found: {a.key_file}")
    site = resolve_property(a.property)
    try:
        r = run(make_session(a.key_file), site, a.out, a.days, a.lag_days, a.min_position, a.max_position)
    except Exception as e:  # one clear line for the job runner's log
        print(f"gsc_export failed: {e}", file=sys.stderr)
        return 1
    print(f"{r['site']}  {r['start']} to {r['end']}: {r['queries']} queries, {r['pages']} pages")
    for p in r["paths"].values():
        print("wrote", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
