# HVAC Marketing HQ site

Static site for Vercel: HTML pages, one `styles.css`, one `main.js`, `vercel.json`, and a serverless `api/lead.js` for the report card form. Built fresh from the transfer pack (sections 1 and 4) and the agency teardown in `research/agency-teardown.md`. No Zero Vacancy files or design.

**Not live.** Nothing is deployed and no repo exists. Pages carry `noindex` and the `X-Robots-Tag` header until Logan says push.

## Editing

All copy, plans and settings live in `tools/build.py`. Edit there, then:

```
python3 tools/build.py                 # rewrite the pages in this folder
python3 tools/build.py --preview DIR   # preview copy with .html links and a dummy form
```

Don't hand-edit the generated `.html` files; the next build overwrites them.

## Pages

HVAC-only positioning. Dark redesign blending WebTonic (look, motion, method diagram) and Websites for HVAC (mockups, pricing toggle), with the report card as the main call to action: the hero and closing website boxes hand off into the 4-step form. Home, The method (Answer, Rank, Repeat), Website, Google & reviews, Lead system, Pricing (4 tiers, monthly/annual toggle at 20% off), Privacy, Terms, 404. `hvac`, `plumbing` and `roofing` pages are still built but not linked (`LIVE_TRADES` in build.py). Fonts are self-hosted in `fonts/`.

Oct 11, 2026, after studying rsgonzales.com: added a terms strip, a "what the report card checks" section with a you/we/you-get steps row, a first-90-days timeline with a we-handle/you-handle split, a "what we won't promise" list, a good-fit/not-a-fit section, a "best for N trucks" line per plan (`stage` in `PLANS`), a "what your plan replaces" block on Pricing, five new FAQs, and `llms.txt` (facts for AI assistants, generated from build.py). We did not copy their testimonials, logo walls, case studies, founder photos or city-page lists, since we have no proof yet.

Lighthouse (mobile, Oct 11, 2026, noindex removed for the run): Performance 99, Accessibility 100, Best practices 96 (only failure: Turnstile blocked in the test sandbox), SEO 100. Re-measure before launch and update `LIGHTHOUSE` in build.py.

Oct 11, 2026 (later): deeper service pages (problem, personas, automations, tracking sample, speed, build timeline, per-page FAQ), a Free report card page with sample screens that mirror what the grader really reports, a founder video bubble (`FOUNDER_VIDEO` in build.py; script in `video-script.md`), and location pages: `locations`, `hvac-marketing-texas` and 20 city pages (`hvac-marketing-<city>-tx`). City facts come from `data/texas-cities.json` (Wikipedia: 2020 Census and climate normals, sources listed per city) and TDLR license counts for McLennan and Bell counties from the prospect sheet. Add a state by adding a data file and pages; never ship a city page without real local facts.

Oct 12, 2026: after crawling websitesforhvac.com and rsgonzales.com (see `research/site-crawl.md`), added Guides (`tools/guides.py`: 5 sourced long-form guides, every number linked to its source), Organization/FAQPage/Article JSON-LD, a generated `sitemap.xml` and `robots.txt` (robots disallows all while `NOINDEX` is on; flip both at launch), and a "What every client agreement includes" section in the Terms so the site's promises match the contract.

## Placeholders to fill before launch

- Brand set: HVAC Marketing HQ, hvacmarketinghq.com (domain purchase, Workspace and DNS still to do)
- Plan prices and build fees (`PLANS`: set `monthly` and `build`; the annual price and savings are computed from `ANNUAL_DISCOUNT`), founding-rate count, add-on prices
- Contract terms (FAQ answer, comparison table row) and what happens if a guarantee is missed
- Review count in the 90-day guarantee
- Money-back guarantee (approved by Logan Oct 11: first month refunded within 30 days of launch): decide whether the build fee is refundable
- Demo line phone number
- Founder video file and poster (`FOUNDER_VIDEO`, `FOUNDER_POSTER`)
- Calendly link (`CALL_LINK`), Turnstile site key
- Privacy and Terms: lawyer review, dates
- Env vars on Vercel: `TURNSTILE_SECRET`, `RESEND_API_KEY`, `LEAD_TO`, `LEAD_FROM`

## Form flow

Four steps (website, business name, first name and email, phone with optional SMS consent) post to `/api/lead`, which checks a honeypot, rate-limits per IP, verifies Turnstile and emails the lead via Resend. Automatic report card generation is not built yet; this only delivers the request.

## Launch

Remove `NOINDEX` in build.py and the `X-Robots-Tag` header in vercel.json, add a sitemap and Search Console, and add analytics only once the privacy page covers it.

Oct 12, 2026 (Finish the website thread): switched to a light theme (white background, same cool-blue and heat-orange glows; the old dark stylesheet is in git history), named the dashboard HQ Command Center, added win-back texts to Growth, added a sourced Scorpion alternatives guide, three Who we help pages (tools/niches.py) and set prices.
