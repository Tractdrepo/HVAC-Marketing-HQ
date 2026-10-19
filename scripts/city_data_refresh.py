#!/usr/bin/env python3
"""Monthly refresh of the data behind the city pages (locations/hvac-marketing-<city>-<st>).

Each city page reads three files, all written by hand-run pulls until now (no fetch script existed):

  data/places/<state>/<city>.json  "<City> on Google" block. Google Places API (New) Text Search for
                                   "HVAC contractor in <City>, <ST>": shop count (max 60), median rating,
                                   median review count, share with a website, top 5 by reviews.
                                   The page says "Refreshed monthly".             -> source "places"
  data/search/<state>/<city>.json  "What <City> types into Google". Google Ads search volume via
                                   DataForSEO for the same 5 keywords per city.   -> source "search"
  data/census/<state>/<city>.json  "<City> homes". Census ACS 5-year estimates.   -> source "census"

Every file carries its own "pulled" date (YYYY-MM-DD), which the page prints. This script re-pulls the
same keywords/queries/geographies from the same sources, rewrites the file and its "pulled" date, and
leaves a city's file untouched when its source fails (reported at the end). It never invents numbers.

Not refreshed here (hand-gathered, see README-seo-scripts.md): population and climate in
data/texas-cities.json and data/states/*.json (Wikipedia/NOAA), and the TDLR license counts in build.py.

Keys, only from environment variables:
  GOOGLE_PLACES_API_KEY                   places  (SKU: Places API Text Search Enterprise)
  DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD  search  (paid, about $0.09 per live task of up to 1,000 keywords)
  CENSUS_API_KEY                          census  (free)

It never commits or pushes. It prints a summary and `git status --short`; a human or the conductor decides.
"""
import argparse
import base64
import datetime as dt
import json
import math
import os
import statistics
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLACES_URL = "https://places.googleapis.com/v1/places:searchText"
# Only these fields: displayName is Pro; rating, userRatingCount and websiteUri make the request
# "Places API Text Search Enterprise". nextPageToken is free (IDs Only).
PLACES_FIELDS = "places.displayName,places.rating,places.userRatingCount,places.websiteUri,nextPageToken"
DFS_URL = "https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live"
CENSUS_URL = "https://api.census.gov/data/{year}/acs/acs5"
YEAR_BUILT = ["2020 or later", "2010-2019", "2000-2009", "1990-1999", "1980-1989", "1970-1979",
              "1960-1969", "1950-1959", "1940-1949", "1939 or earlier"]
CENSUS_VARS = (["B25001_001E", "B25003_001E", "B25003_002E", "B25035_001E", "B25077_001E", "B25034_001E",
                "B25040_001E", "B25040_002E", "B25040_004E"] + [f"B25034_{i:03d}E" for i in range(2, 12)])
# Published prices, checked Oct 19, 2026 (see README-seo-scripts.md for links)
PLACES_FREE_PER_MONTH, PLACES_PER_1000 = 1000, 35.00
DFS_PER_TASK = 0.09
SOURCES = ("places", "search", "census")
INDENT = {"places": 2, "search": 1, "census": 1}


# ---------- HTTP (stdlib only; tests swap these out) ----------

def http_json(url, body=None, headers=None, timeout=30):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers={"content-type": "application/json", **(headers or {})},
                                 method="POST" if data is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} from {urllib.parse.urlsplit(url).netloc}: {e.read().decode(errors='replace')[:200]}")


# ---------- cities and files ----------

def load_cities(root=ROOT):
    """Every city the site knows: Texas from data/texas-cities.json, the rest from data/states/*.json."""
    out = []
    with open(os.path.join(root, "data", "texas-cities.json")) as f:
        tx = json.load(f)
    for c in tx["cities"]:
        out.append({"state": "texas", "abbr": "TX", "state_name": "Texas", "slug": c["slug"], "name": c["name"]})
    sdir = os.path.join(root, "data", "states")
    for fn in sorted(os.listdir(sdir)) if os.path.isdir(sdir) else []:
        if fn.endswith(".json"):
            with open(os.path.join(sdir, fn)) as f:
                d = json.load(f)
            for c in d["cities"]:
                out.append({"state": d["state"]["slug"], "abbr": d["state"]["abbr"].upper(), "state_name": d["state"]["name"],
                            "slug": c["slug"], "name": c["name"]})
    return out


def data_path(root, source, city):
    return os.path.join(root, "data", source, city["state"], city["slug"] + ".json")


def read_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def write_json(path, source, d):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(d, f, indent=INDENT[source])


def age_days(d, today):
    try:
        return (today - dt.date.fromisoformat(d["pulled"])).days
    except (TypeError, KeyError, ValueError):
        return None


# ---------- places ----------

def places_query(city, existing):
    return (existing or {}).get("query") or f"HVAC contractor in {city['name']}, {city['abbr']}"


def fetch_places(query, key, http=http_json, max_pages=3):
    """Up to 60 results (Google's cap), 20 per page. Returns (places, requests_made)."""
    found, token, calls = [], None, 0
    for _ in range(max_pages):
        body = {"textQuery": query, "pageSize": 20, "languageCode": "en", "regionCode": "US",
                "includePureServiceAreaBusinesses": True}
        if token:
            body["pageToken"] = token
        r = http(PLACES_URL, body, {"X-Goog-Api-Key": key, "X-Goog-FieldMask": PLACES_FIELDS})
        calls += 1
        found += r.get("places", [])
        token = r.get("nextPageToken")
        if not token:
            break
    return found, calls


def summarize_places(query, places, today):
    """The same summary the city pages read. Shops with no reviews count as 0 reviews."""
    if not places:
        raise ValueError("Google returned no shops")
    ratings = [p["rating"] for p in places if p.get("rating") is not None]
    reviews = [p.get("userRatingCount") or 0 for p in places]
    ranked = sorted(places, key=lambda p: -(p.get("userRatingCount") or 0))
    return {"pulled": today.isoformat(), "query": query, "count": len(places),
            "median_rating": round(statistics.median(ratings), 1) if ratings else None,
            "median_reviews": statistics.median(reviews),
            "share_with_website": round(sum(1 for p in places if p.get("websiteUri")) / len(places), 2),
            "top5": [[(p.get("displayName") or {}).get("text", ""), p.get("rating"), p.get("userRatingCount") or 0] for p in ranked[:5]]}


# ---------- search (DataForSEO) ----------

def search_keywords(existing):
    """The keywords already on the page (and the unqualified twins for shared city names). Never new ones."""
    kws = [k["keyword"] for k in existing.get("keywords", [])]
    kws += [k["keyword"] for k in (existing.get("shared_city_name") or {}).get("unqualified", [])]
    return kws


def fetch_search_volumes(keywords, login, password, http=http_json):
    """One live task per 1,000 keywords. Returns ({keyword: result}, tasks)."""
    auth = "Basic " + base64.b64encode(f"{login}:{password}".encode()).decode()
    out, tasks = {}, 0
    uniq = list(dict.fromkeys(keywords))
    for i in range(0, len(uniq), 1000):
        r = http(DFS_URL, [{"keywords": uniq[i:i + 1000], "location_code": 2840, "language_code": "en"}], {"Authorization": auth})
        tasks += 1
        for t in r.get("tasks", []):
            if t.get("status_code") != 20000:
                raise RuntimeError(f"DataForSEO task {t.get('status_code')}: {t.get('status_message')}")
            for row in t.get("result") or []:
                out[row["keyword"].lower()] = row
    return out, tasks


def _kw_row(kw, row):
    return {"keyword": kw, "monthly_searches": row.get("search_volume"),
            "cpc_usd": round(row["cpc"], 2) if row.get("cpc") is not None else None,
            "competition": row.get("competition"),
            "monthly": [[m["year"], m["month"], m["search_volume"]] for m in (row.get("monthly_searches") or [])]}


def summarize_search(existing, volumes, today):
    d = json.loads(json.dumps(existing))  # copy; keeps source, location, note and key order
    missing = [k for k in search_keywords(existing) if k.lower() not in volumes]
    if missing:
        raise ValueError(f"no data for {', '.join(missing)}")
    d["pulled"] = today.isoformat()
    d["keywords"] = [_kw_row(k["keyword"], volumes[k["keyword"].lower()]) for k in existing.get("keywords", [])]
    with_vol = [k for k in d["keywords"] if k["monthly_searches"]]
    top = max(with_vol, key=lambda k: k["monthly_searches"]) if with_vol else None
    d["top_keyword"] = top["keyword"] if top else None
    d["top_monthly_searches"] = top["monthly_searches"] if top else None
    cpcs = [k["cpc_usd"] for k in d["keywords"] if k["cpc_usd"] is not None]
    d["max_cpc_usd"] = max(cpcs) if cpcs else None
    if d.get("shared_city_name"):
        d["shared_city_name"]["unqualified"] = [
            {k: v for k, v in _kw_row(u["keyword"], volumes[u["keyword"].lower()]).items() if k in ("keyword", "monthly_searches", "cpc_usd")}
            for u in d["shared_city_name"].get("unqualified", [])]
    return d


# ---------- census ----------

def _num(v):
    try:
        n = float(v)
    except (TypeError, ValueError):
        return None
    return None if n < 0 else n  # the API uses large negative numbers for "not available"


def fetch_census(geo, year, key, http=http_json):
    q = urllib.parse.urlencode({"get": ",".join(["NAME"] + CENSUS_VARS), "for": f"place:{geo[2:]}", "in": f"state:{geo[:2]}", "key": key})
    rows = http(CENSUS_URL.format(year=year) + "?" + q)
    if not rows or len(rows) < 2:
        raise ValueError("Census returned no row")
    return dict(zip(rows[0], rows[1]))


def summarize_census(existing, row, year, today):
    v = {k: _num(row.get(k)) for k in CENSUS_VARS}
    if not v["B25003_001E"]:
        raise ValueError("Census row has no household count")
    built = [[label, int(v[f"B25034_{i + 2:03d}E"] or 0)] for i, label in enumerate(YEAR_BUILT)]
    total_built = v["B25034_001E"] or sum(n for _, n in built)
    heat_total = v["B25040_001E"]
    d = dict(existing)
    d.update({
        "pulled": today.isoformat(),
        "source": f"U.S. Census Bureau, American Community Survey {year - 4}-{year} 5-year estimates",
        "census_place": row.get("NAME", existing.get("census_place")),
        "median_year_built": int(v["B25035_001E"]) if v["B25035_001E"] else None,
        "households": int(v["B25003_001E"]),
        "owner_occupied": int(v["B25003_002E"] or 0),
        "owner_occupied_share": round((v["B25003_002E"] or 0) / v["B25003_001E"], 3),
        "housing_units": int(v["B25001_001E"] or 0),
        "median_home_value": int(v["B25077_001E"]) if v["B25077_001E"] else None,
        "share_built_before_2000": round(sum(n for _, n in built[3:]) / total_built, 3) if total_built else None,
        "year_built": built,
        "heating_fuel_share": {"utility_gas": round((v["B25040_002E"] or 0) / heat_total, 3),
                               "electricity": round((v["B25040_004E"] or 0) / heat_total, 3)} if heat_total else existing.get("heating_fuel_share"),
    })
    return d


# ---------- run ----------

def estimate(cities, root, sources):
    lines = []
    if "places" in sources:
        calls = 0
        for c in cities:
            d = read_json(data_path(root, "places", c))
            calls += min(3, max(1, math.ceil(((d or {}).get("count") or 60) / 20)))
        billable = max(0, calls - PLACES_FREE_PER_MONTH)
        lines.append(f"places: about {calls} Text Search Enterprise requests. Free for the first {PLACES_FREE_PER_MONTH:,} a month "
                     f"(shared with the report card grader's searches); ${calls * PLACES_PER_1000 / 1000:.2f} if none of the free cap is left, "
                     f"${billable * PLACES_PER_1000 / 1000:.2f} if all of it is.")
    if "search" in sources:
        kws = sum(len(search_keywords(read_json(data_path(root, "search", c)) or {})) for c in cities)
        tasks = math.ceil(kws / 1000) if kws else 0
        lines.append(f"search: {kws} keywords in {tasks} DataForSEO live task(s), about ${tasks * DFS_PER_TASK:.2f}.")
    if "census" in sources:
        lines.append(f"census: {len(cities)} requests, free.")
    return lines


def refresh(cities, root, sources, today, env, http=http_json, acs_year=2024, log=print):
    """Refresh each source for each city. Returns {"updated": {src: [..]}, "failed": {src: [(city, reason)]}, "calls": {..}}."""
    res = {"updated": {s: [] for s in sources}, "failed": {s: [] for s in sources}, "calls": {s: 0 for s in sources}}
    label = lambda c: f"{c['state']}/{c['slug']}"

    if "places" in sources:
        key = env.get("GOOGLE_PLACES_API_KEY")
        for c in cities:
            if not key:
                res["failed"]["places"].append((label(c), "GOOGLE_PLACES_API_KEY not set"))
                continue
            path = data_path(root, "places", c)
            old = read_json(path)
            q = places_query(c, old)
            try:
                found, n = fetch_places(q, key, http)
                res["calls"]["places"] += n
                write_json(path, "places", summarize_places(q, found, today))
                res["updated"]["places"].append(label(c))
            except Exception as e:
                res["failed"]["places"].append((label(c), str(e)))

    if "search" in sources:
        login, pw = env.get("DATAFORSEO_LOGIN"), env.get("DATAFORSEO_PASSWORD")
        olds = {label(c): read_json(data_path(root, "search", c)) for c in cities}
        todo = [c for c in cities if olds[label(c)]]
        for c in cities:
            if not olds[label(c)]:
                res["failed"]["search"].append((label(c), "no existing search file (keywords are chosen by hand first)"))
        volumes, err = {}, None
        if todo and not (login and pw):
            err = "DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD not set"
        elif todo:
            try:
                volumes, res["calls"]["search"] = fetch_search_volumes([k for c in todo for k in search_keywords(olds[label(c)])], login, pw, http)
            except Exception as e:
                err = str(e)
        for c in todo:
            if err:
                res["failed"]["search"].append((label(c), err))
                continue
            try:
                write_json(data_path(root, "search", c), "search", summarize_search(olds[label(c)], volumes, today))
                res["updated"]["search"].append(label(c))
            except Exception as e:
                res["failed"]["search"].append((label(c), str(e)))

    if "census" in sources:
        key = env.get("CENSUS_API_KEY")
        for c in cities:
            path = data_path(root, "census", c)
            old = read_json(path)
            if not old or not old.get("geo"):
                res["failed"]["census"].append((label(c), "no existing census file with a geo id"))
                continue
            if not key:
                res["failed"]["census"].append((label(c), "CENSUS_API_KEY not set"))
                continue
            try:
                row = fetch_census(old["geo"], acs_year, key, http)
                res["calls"]["census"] += 1
                write_json(path, "census", summarize_census(old, row, acs_year, today))
                res["updated"]["census"].append(label(c))
            except Exception as e:
                res["failed"]["census"].append((label(c), str(e)))
    return res


def staleness(cities, root, today, max_age=30, yearly_max_age=400):
    """Cities whose data is older than the page promises: places monthly (30 days), search and census yearly."""
    out = {s: [] for s in SOURCES}
    for c in cities:
        for s in SOURCES:
            d = read_json(data_path(root, s, c))
            if d is None:
                out[s].append((f"{c['state']}/{c['slug']}", "missing"))
                continue
            a = age_days(d, today)
            limit = max_age if s == "places" else yearly_max_age
            if a is None or a > limit:
                out[s].append((f"{c['state']}/{c['slug']}", f"{a} days old" if a is not None else "no pulled date"))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Refresh city-page data (Google Places, DataForSEO search volume, Census ACS).")
    ap.add_argument("--sources", default="places", help="comma list of places,search,census (default: places, the monthly one)")
    ap.add_argument("--cities", default="", help="comma list of city slugs or state/slug to limit the run (default: all)")
    ap.add_argument("--limit", type=int, default=0, help="only the first N cities (handy for a test run)")
    ap.add_argument("--acs-year", type=int, default=2024, help="ACS 5-year vintage end year (default 2024 = 2020-2024)")
    ap.add_argument("--max-age-days", type=int, default=30, help="flag places data older than this (default 30)")
    ap.add_argument("--yearly-max-age-days", type=int, default=400, help="flag search/census data older than this (default 400)")
    ap.add_argument("--estimate", action="store_true", help="print the request count and cost, call nothing")
    ap.add_argument("--check", action="store_true", help="only report stale or missing data, call nothing")
    ap.add_argument("--build", action="store_true", help="run python tools/build.py after a refresh that changed something")
    ap.add_argument("--root", default=ROOT, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    sources = [s.strip() for s in a.sources.split(",") if s.strip()]
    bad = [s for s in sources if s not in SOURCES]
    if bad:
        ap.error(f"unknown source(s): {', '.join(bad)}")
    cities = load_cities(a.root)
    if a.cities:
        want = {w.strip() for w in a.cities.split(",") if w.strip()}
        cities = [c for c in cities if c["slug"] in want or f"{c['state']}/{c['slug']}" in want]
    if a.limit:
        cities = cities[:a.limit]
    today = dt.date.today()

    if a.estimate:
        print("\n".join(estimate(cities, a.root, sources)))
        return 0
    failed_any = False
    if not a.check:
        res = refresh(cities, a.root, sources, today, os.environ, acs_year=a.acs_year)
        print(f"Refresh {today.isoformat()} for {len(cities)} cities")
        for s in sources:
            print(f"  {s}: {len(res['updated'][s])} updated, {len(res['failed'][s])} left untouched, {res['calls'][s]} API requests")
            for name, why in res["failed"][s]:
                print(f"    untouched {name}: {why}")
            failed_any = failed_any or bool(res["failed"][s])
        if "census" in sources and a.acs_year != 2024 and any(res["updated"]["census"]):
            print("  note: tools/build.py prints 'ACS 2020-2024'; update that caption for the new vintage.")
        if a.build and any(res["updated"][s] for s in sources):
            b = subprocess.run([sys.executable, os.path.join(a.root, "tools", "build.py")], cwd=a.root, capture_output=True, text=True)
            print("  build:", "ok" if b.returncode == 0 else f"FAILED\n{b.stderr[-1500:]}")
            failed_any = failed_any or b.returncode != 0
    stale = staleness(cities, a.root, today, a.max_age_days, a.yearly_max_age_days)
    print(f"Stale data (places > {a.max_age_days} days, search/census > {a.yearly_max_age_days} days):")
    for s in SOURCES:
        print(f"  {s}: {len(stale[s])}" + ("" if not stale[s] else " -> " + ", ".join(f"{n} ({w})" for n, w in stale[s])))
    g = subprocess.run(["git", "status", "--short"], cwd=a.root, capture_output=True, text=True)
    print("git status --short (nothing committed or pushed):")
    print(g.stdout.rstrip() or "  clean")
    return 2 if failed_any else 0


if __name__ == "__main__":
    sys.exit(main())
