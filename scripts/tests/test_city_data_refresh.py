import datetime as dt
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import city_data_refresh as m  # noqa: E402

TODAY = dt.date(2026, 11, 20)
OLD_PLACES = {"pulled": "2026-10-14", "query": "HVAC contractor in Birmingham, AL", "count": 59, "median_rating": 4.9,
              "median_reviews": 130, "share_with_website": 0.71, "top5": [["OnTime Service", 4.9, 8995]]}
OLD_SEARCH = {"pulled": "2026-10-15", "source": "Google Ads search volume via DataForSEO", "location": "United States", "language": "en",
              "note": "n", "keywords": [{"keyword": "ac repair birmingham", "monthly_searches": 390, "cpc_usd": 76.3, "competition": "LOW", "monthly": []},
                                        {"keyword": "hvac repair birmingham", "monthly_searches": 170, "cpc_usd": 37.1, "competition": "LOW", "monthly": []}],
              "top_keyword": "ac repair birmingham", "top_monthly_searches": 390, "max_cpc_usd": 76.3}
OLD_CENSUS = {"pulled": "2026-10-15", "source": "U.S. Census Bureau, American Community Survey 2020-2024 5-year estimates",
              "census_place": "Birmingham city, Alabama", "geo": "0107000", "households": 1}
# Birmingham's real ACS 2020-2024 figures as stored in data/census/alabama/birmingham.json
BHAM_ROW = {"NAME": "Birmingham city, Alabama", "B25001_001E": "109349", "B25003_001E": "88788", "B25003_002E": "40402",
            "B25035_001E": "1965", "B25077_001E": "158800", "B25034_001E": "109349", "B25040_001E": "88788",
            "B25040_002E": str(round(0.432 * 88788)), "B25040_004E": str(round(0.543 * 88788)),
            **{f"B25034_{i + 2:03d}E": str(n) for i, n in enumerate([844, 7294, 6704, 6361, 9806, 15238, 16332, 18434, 8347, 19989])}}


def place(name, rating, reviews, web=True):
    p = {"displayName": {"text": name}}
    if rating is not None:
        p.update(rating=rating, userRatingCount=reviews)
    if web:
        p["websiteUri"] = "https://example.com"
    return p


class FakeHttp:
    def __init__(self, fail_query=None):
        self.calls, self.fail_query = [], fail_query

    def __call__(self, url, body=None, headers=None):
        self.calls.append((url, body, headers))
        if url == m.PLACES_URL:
            if self.fail_query and self.fail_query in body["textQuery"]:
                raise RuntimeError("HTTP 403 from places.googleapis.com: API key not valid")
            if "pageToken" not in body:
                return {"places": [place(f"Shop {i}", 4.8, 100 + i) for i in range(20)], "nextPageToken": "t2"}
            return {"places": [place("Big Shop", 4.9, 9000), place("New Shop", None, None, web=False)]}
        if url == m.DFS_URL:
            kws = body[0]["keywords"]
            return {"tasks": [{"status_code": 20000, "result": [
                {"keyword": k, "search_volume": 500 if k.startswith("hvac") else 400, "cpc": 50.123, "competition": "LOW",
                 "monthly_searches": [{"year": 2026, "month": 10, "search_volume": 600}]} for k in kws]}]}
        if url.startswith("https://api.census.gov/"):
            return [list(BHAM_ROW.keys()) + ["state", "place"], list(BHAM_ROW.values()) + ["01", "07000"]]
        raise AssertionError(url)


class CityRefreshTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.root, "data", "states"))
        with open(os.path.join(self.root, "data", "texas-cities.json"), "w") as f:
            json.dump({"texas": {"population_2020": 1}, "cities": [{"slug": "waco", "name": "Waco"}]}, f)
        with open(os.path.join(self.root, "data", "states", "alabama.json"), "w") as f:
            json.dump({"state": {"name": "Alabama", "abbr": "al", "slug": "alabama"}, "cities": [{"slug": "birmingham", "name": "Birmingham"}]}, f)
        for src, d in (("places", OLD_PLACES), ("search", OLD_SEARCH), ("census", OLD_CENSUS)):
            os.makedirs(os.path.join(self.root, "data", src, "alabama"))
            with open(os.path.join(self.root, "data", src, "alabama", "birmingham.json"), "w") as f:
                json.dump(d, f, indent=m.INDENT[src])
        self.cities = m.load_cities(self.root)
        self.bham = [c for c in self.cities if c["slug"] == "birmingham"]

    def tearDown(self):
        shutil.rmtree(self.root)

    def read(self, src, state="alabama", slug="birmingham"):
        return m.read_json(os.path.join(self.root, "data", src, state, slug + ".json"))

    def test_load_cities(self):
        self.assertEqual([(c["state"], c["abbr"], c["slug"]) for c in self.cities], [("texas", "TX", "waco"), ("alabama", "AL", "birmingham")])

    def test_places_refresh(self):
        http = FakeHttp()
        res = m.refresh(self.bham, self.root, ["places"], TODAY, {"GOOGLE_PLACES_API_KEY": "k"}, http)
        self.assertEqual(res["updated"]["places"], ["alabama/birmingham"])
        self.assertEqual(res["calls"]["places"], 2)
        d = self.read("places")
        self.assertEqual(d["pulled"], "2026-11-20")
        self.assertEqual(d["query"], "HVAC contractor in Birmingham, AL")  # same query as before
        self.assertEqual(d["count"], 22)
        self.assertEqual(d["top5"][0], ["Big Shop", 4.9, 9000])
        self.assertEqual(d["median_rating"], 4.8)
        self.assertEqual(d["share_with_website"], round(21 / 22, 2))
        self.assertEqual(list(d.keys()), list(OLD_PLACES.keys()))
        self.assertEqual(http.calls[1][1]["pageToken"], "t2")
        self.assertIn("places.rating", http.calls[0][2]["X-Goog-FieldMask"])
        self.assertEqual(http.calls[0][2]["X-Goog-Api-Key"], "k")

    def test_places_failure_leaves_file_untouched(self):
        before = open(os.path.join(self.root, "data", "places", "alabama", "birmingham.json")).read()
        res = m.refresh(self.bham, self.root, ["places"], TODAY, {"GOOGLE_PLACES_API_KEY": "k"}, FakeHttp(fail_query="Birmingham"))
        self.assertEqual(res["updated"]["places"], [])
        self.assertIn("403", res["failed"]["places"][0][1])
        self.assertEqual(open(os.path.join(self.root, "data", "places", "alabama", "birmingham.json")).read(), before)

    def test_no_key_is_reported_not_called(self):
        http = FakeHttp()
        res = m.refresh(self.bham, self.root, ["places", "search", "census"], TODAY, {}, http)
        self.assertEqual(http.calls, [])
        self.assertTrue(all(res["failed"][s] for s in ("places", "search", "census")))
        self.assertEqual(self.read("places"), OLD_PLACES)

    def test_new_city_query(self):
        waco = [c for c in self.cities if c["slug"] == "waco"]
        m.refresh(waco, self.root, ["places"], TODAY, {"GOOGLE_PLACES_API_KEY": "k"}, FakeHttp())
        self.assertEqual(self.read("places", "texas", "waco")["query"], "HVAC contractor in Waco, TX")

    def test_search_refresh_same_keywords(self):
        http = FakeHttp()
        res = m.refresh(self.bham, self.root, ["search"], TODAY, {"DATAFORSEO_LOGIN": "u", "DATAFORSEO_PASSWORD": "p"}, http)
        self.assertEqual(res["calls"]["search"], 1)
        self.assertEqual(http.calls[0][1][0]["keywords"], ["ac repair birmingham", "hvac repair birmingham"])
        d = self.read("search")
        self.assertEqual(d["top_keyword"], "hvac repair birmingham")
        self.assertEqual(d["top_monthly_searches"], 500)
        self.assertEqual(d["max_cpc_usd"], 50.12)
        self.assertEqual(d["keywords"][0]["monthly"], [[2026, 10, 600]])
        self.assertEqual(d["note"], "n")

    def test_census_matches_stored_birmingham(self):
        m.refresh(self.bham, self.root, ["census"], TODAY, {"CENSUS_API_KEY": "c"}, FakeHttp())
        d = self.read("census")
        self.assertEqual((d["households"], d["owner_occupied_share"], d["share_built_before_2000"], d["median_year_built"]), (88788, 0.455, 0.864, 1965))
        self.assertEqual(d["heating_fuel_share"], {"utility_gas": 0.432, "electricity": 0.543})
        self.assertEqual(d["year_built"][-1], ["1939 or earlier", 19989])
        self.assertEqual(d["geo"], "0107000")

    def test_staleness(self):
        st = m.staleness(self.cities, self.root, TODAY)
        self.assertEqual(st["places"], [("texas/waco", "missing"), ("alabama/birmingham", "37 days old")])
        self.assertEqual(st["census"], [("texas/waco", "missing")])

    def test_estimate(self):
        lines = m.estimate(self.bham, self.root, ["places", "search"])
        self.assertIn("about 3 Text Search Enterprise requests", lines[0])
        self.assertIn("2 keywords in 1 DataForSEO live task", lines[1])


if __name__ == "__main__":
    unittest.main()
