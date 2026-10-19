# SEO scripts: Search Console export and city data refresh

Two plain Python scripts (no AI) that run on Logan's Windows PC from the desktop job runner.
Neither one commits or pushes anything.

| Script | When | What it needs | Cost |
| --- | --- | --- | --- |
| `scripts/gsc_export.py` | weekly | a Google service account key file | free |
| `scripts/city_data_refresh.py` | monthly (`--sources places`) | `GOOGLE_PLACES_API_KEY` | about $0 to $17 a month, see below |
| `scripts/city_data_refresh.py --sources search,census` | yearly | DataForSEO login, Census key | about $0.09 a run; Census free |

Tests (mocked, no network): `python3 -m unittest discover -s scripts/tests` (also part of `npm test`).

## One-time setup on Windows (do this once)

You need Python 3.10 or newer. In PowerShell, `py --version` should print it. If it doesn't, install Python
from https://www.python.org/downloads/ and tick "Add python.exe to PATH".

1. Open PowerShell in the repo folder and install the two libraries:
   `py -m pip install -r scripts\requirements.txt`
2. Make a folder for keys outside the repo: `mkdir $HOME\secrets`

### Search Console export (service account, recommended)

Why a service account: the job runs on its own with no browser and no token that expires. The only thing
to guard is one key file, which lives in `$HOME\secrets` and never in the repo (`.gitignore` also blocks
`secrets/`, `gsc-key*.json` and `*service-account*.json`). The other option, an OAuth desktop client,
needs a browser sign-in first and a refresh token that can be revoked or expire, so it is not supported here.

1. Go to https://console.cloud.google.com/ and pick your existing project (the one with the Places key is fine)
   or click the project picker, then **New project**, name it `hmhq-seo`, **Create**.
2. **APIs & Services > Library**, search **Google Search Console API**, click it, **Enable**.
3. **IAM & Admin > Service Accounts > Create service account**. Name: `gsc-export`. Click **Create and continue**,
   skip the roles step, click **Done**.
4. Click the new service account, open the **Keys** tab, **Add key > Create new key > JSON > Create**.
   A `.json` file downloads. Copy the service account email shown on the page (it ends in `iam.gserviceaccount.com`).
   (If Google says key creation is disabled by an organization policy, your project is under a Workspace
   organization; create the project with "No organization", or ask the org admin to lift
   `iam.disableServiceAccountKeyCreation` for that project.)
5. Move the file to `C:\Users\<you>\secrets\gsc-key.json`. Don't put it in the repo, email it or upload it.
6. Go to https://search.google.com/search-console, pick the **hvacmarketinghq.com** property (the Domain one),
   **Settings > Users and permissions > Add user**, paste the service account email, permission **Restricted**, **Add**.
   (Restricted can read all performance data. If you also use the `https://www.hvacmarketinghq.com/` URL-prefix
   property, add the same email there too.)
7. Point the script at the key (once; then open a new PowerShell window):
   `setx GSC_KEY_FILE "$HOME\secrets\gsc-key.json"`
8. Test run:
   `py scripts\gsc_export.py --out $HOME\seo\gsc`
   It prints the date range and row counts and the three CSV paths. A `403 ... sufficient permission` error means
   step 6 isn't done yet (it can take a few minutes to apply) or `--property` points at the wrong property.
9. In the job runner, run weekly: `py C:\path\to\hmhq\scripts\gsc_export.py --out C:\Users\<you>\seo\gsc`

Options: `--property domain` (default, `sc-domain:hvacmarketinghq.com`) or `--property url`
(`https://www.hvacmarketinghq.com/`); `--days 28`; `--lag-days 3` (Search Console data runs about 2 to 3 days
behind, so the window ends 3 days ago); `--min-position 8 --max-position 20`; `--key-file` instead of the env var.

Output, stamped with the run date:
- `gsc-YYYY-MM-DD-queries.csv`: query, clicks, impressions, ctr, position (most clicks first)
- `gsc-YYYY-MM-DD-pages.csv`: page, clicks, impressions, ctr, position
- `gsc-YYYY-MM-DD-positions-8-20.csv`: queries and pages with average position 8 to 20, most impressions first.
  These are on page one's doorstep and are the best candidates for a content or internal-link push.

Cost: none. "All use of Google Search Console API is free of charge. However, it is subject to usage limits."
(https://developers.google.com/webmaster-tools/pricing; limits at https://developers.google.com/webmaster-tools/limits).
This script makes 2 to 4 requests a week, far under the limits.

### City data refresh

Where the city-page data comes from today (checked Oct 19, 2026). There was no fetch script in the repo;
the files were written by one-off pulls on Oct 14 and 15, 2026. Each file has its own `"pulled"` date,
which the page prints ("pulled 2026-10-14"):

| Block on the city page | File | Source | Page promises |
| --- | --- | --- | --- |
| "<City> on Google" (shop count, median rating/reviews, website share, top 5) | `data/places/<state>/<city>.json` | Google Places API (New) Text Search, query `HVAC contractor in <City>, <ST>` | "Refreshed monthly" |
| "What <City> types into Google" | `data/search/<state>/<city>.json` | Google Ads search volume via DataForSEO, the same 5 keywords per city | yearly (build.py) |
| "<City> homes" | `data/census/<state>/<city>.json` | Census ACS 2020-2024 5-year, by Census place id (`geo`) | yearly; next vintage (2021-2025) usually comes out in December |

Not refreshable automatically (hand-gathered, left as is): population and climate in `data/texas-cities.json`
and `data/states/*.json` (from Wikipedia and NOAA normals, which only change every 10 years), the TDLR license
counts (`TDLR_COUNTY` in build.py, from the prospect sheet), and which keywords each city tracks (chosen once; the
script re-pulls those same keywords and never picks new ones). A city with no search or census file is reported,
not filled in.

The script re-pulls the same queries, keywords and Census places, rewrites the file and its `"pulled"` date, and
leaves a city's file untouched when its source fails (listed under "untouched" in the summary). It then flags
stale data (places older than 30 days, search/census older than 400 days), optionally rebuilds (`--build`), and
prints `git status --short`. It exits 2 if anything failed, so the job runner can tell. It never commits.

Two notes on the places numbers: the original pull's exact method isn't recorded, so this script uses the same
query and the obvious math (Python's median over all results, shops with no reviews count as 0 reviews, top 5
by review count) and includes service-area businesses, like the report card does. Expect small shifts on the
first run that come from method, not the market.

Keys (environment variables only; never in the repo):
1. **Google Places**: `setx GOOGLE_PLACES_API_KEY "<key>"`. Use the same key the report card uses (Vercel
   project env var `GOOGLE_PLACES_API_KEY`) or create one in Google Cloud: **APIs & Services > Credentials >
   Create credentials > API key**, then **Edit > API restrictions > Places API (New)**. Places API (New) must be
   enabled on the project and billing turned on.
2. **DataForSEO** (only for the yearly search refresh): `setx DATAFORSEO_LOGIN "<login>"` and
   `setx DATAFORSEO_PASSWORD "<api password>"` (the API password from https://app.dataforseo.com/api-access, not
   the site password).
3. **Census** (only for the yearly census refresh): get a free key at https://api.census.gov/data/key_signup.html,
   click the activation link in the email, then `setx CENSUS_API_KEY "<key>"`. The Census API now requires a key
   on every query (https://www.census.gov/data/developers/guidance/api-user-guide.Query_Limits.html).

Test runs:
- `py scripts\city_data_refresh.py --estimate --sources places,search,census` (calls nothing, prints request counts and cost)
- `py scripts\city_data_refresh.py --check` (calls nothing, lists stale or missing data)
- `py scripts\city_data_refresh.py --cities waco` (one city, about 3 Places requests)
- Monthly job: `py scripts\city_data_refresh.py --sources places --build`
- Yearly (after the ACS release in December): `py scripts\city_data_refresh.py --sources search,census --acs-year 2025 --build`
  (then update the "2020-2024" caption in `housing_block` in tools/build.py; the script reminds you).

Costs (published prices, checked Oct 19, 2026):
- **Places**: the field mask is `displayName, rating, userRatingCount, websiteUri`, which bills as
  **Places API Text Search Enterprise** (SKU E967-44BC-B44D): first 1,000 requests a month free, then $35.00 per
  1,000 (https://developers.google.com/maps/billing-and-pricing/pricing; which fields trigger which SKU:
  https://developers.google.com/maps/documentation/places/web-service/text-search). One city is 1 to 3 requests
  (20 shops a page, 60 max). All 166 cities today is about 468 requests: **$0 if it fits in the 1,000 free**,
  at most about **$16.38** if the free cap is already used up. The report card's ranking searches use the same
  SKU and share the same free 1,000, so a busy report card month can push part of the refresh into paid usage.
- **DataForSEO search volume**: live mode, $0.09 per task of up to 1,000 keywords
  (https://dataforseo.com/pricing/keywords-data/google-ads). All 890 keywords fit in one task: **about $0.09 a run**.
- **Census ACS**: free (key required, no charge).
