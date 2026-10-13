# Site to-do list

Owner: the "Finish the website" thread. Order set by Logan, Oct 12, 2026: finish the website design first, then go all-in on SEO. SEO is essential, not optional.

## 1. Website design (now)
- [ ] Logan reviews the white theme and flags any page that looks off
- [ ] About page: Logan's story (4 to 5 sentences)
- [ ] Report card form working: RESEND_API_KEY, LEAD_TO, LEAD_FROM in Vercel (Logan)
- [ ] Booking link (Google Calendar booking page or Calendly) and demo phone number (Logan)
- [ ] Contract terms: month to month, review count, build fee refund, missed-guarantee remedy, add-on prices (Logan, defaults proposed)
- [ ] Founder video (Logan, whenever recorded)
- [x] Removed new-company wording, the Works-with strip and the duplicate Fast/Found/Booked section (Oct 13)
- [x] Light theme, prices, niche pages, HQ Command Center, Scorpion guide, photo wording (Oct 12)

## 1b. Gaps vs competitors (from research/crawls/, Oct 12)
Funnel
- [ ] Report card actually delivers itself: wire grader/ to /api/lead so the report emails in minutes, as the site promises. Today the form only emails us. Needs Resend + Google Places + Anthropic keys (Logan); use a cheap model to keep token spend low
- [ ] Self-serve sign-up: a "Start now" button per plan to a Stripe checkout plus a click-to-sign agreement, so a shop can buy without a call (Footbridge does this). Needs Stripe account and final contract terms (Logan)
- [ ] Booking calendar on the site (Logan's link)
- [x] Missed-call cost calculator (Hook's math: $7,500 install x 30% close = $2,250 per missed call), interactive, ungated
- [ ] Add trucks and "biggest bottleneck" to the report card form to pre-qualify
- [ ] Live demo: demo line for text-back (Logan's number) and the AI web chat running on our own site
- [ ] Referral offer for clients, later a trade group partner rate (Nexstar, CertainPath members). Needs Logan's terms
Pages and structure
- [x] Split services into one page per product, each aimed at its own search: Missed-call text-back, Review requests, Google Business Profile, Local SEO, AI web chat, AI search (AEO), HVAC websites
- [x] "What happens after you sign up" page: day-by-day timeline, objections answered (why cheaper than Scorpion, what if I leave, will I get more calls)
- [x] Comparison table on home and pricing: us vs big agencies vs DIY, plus "what agencies report vs what we track"
- [x] "7 questions to ask any HVAC marketing agency" guide, answered for ourselves (RYNO lists them and never answers)
- [ ] "Slow season" section: tune-ups, maintenance plans, win-back texts
- [ ] About page (Logan's story); reviews and case-study pages once we have founding clients, every quote linked to its public Google review
Rule: never imply years in business, clients served or results. Examples page and mockups removed Oct 13 at Logan's call. Real client work goes up only after we have it, with the shop's permission.
Skip at our price: photo and video shoots, podcasts, books, webinars, gated courses, paid ad management

## 2. SEO (essential, right after design)
- [ ] Turn indexing on: drop NOINDEX in build.py and the X-Robots-Tag header in vercel.json, robots.txt allows all, submit sitemap in Google Search Console (Logan verifies the domain)
- [ ] National city pages: top 100 to 150 US metros by population, each with real local data (Census population, climate normals, licensed-contractor counts where a state publishes them). Never a city page without real local facts
- [ ] 50 state pages with real state data and links to their city pages
- [ ] Competitor "alternative" pages, sourced from their own published terms (research/crawls/): Footbridge, Hook, RYNO/Blue Corona, Valve+Meter, websitesforhvac, RS Gonzales
- [ ] "Who owns my website?" guide quoting each agency's published terms
- [ ] "What agencies report vs what we track" table and missed-call math on the home or text-back page
- [ ] "What happens after you book" page
- [ ] Google Business Profile for HVAC Marketing HQ
- [ ] Links: trade association directories (ACCA, state ACCA chapters), supplier and distributor partners, HVAC podcasts and trade publications
- [ ] Keep publishing sourced guides; re-run Lighthouse after each big change

## Rules
No invented proof or stats. One source per number. The grading rubric never goes on the site. No photo or video shoots at our pricing: we only post photos the shop texts us.

## Oct 13: menu restructure (modeled on Websites for HVAC)
- [x] Top announce bar removed; Examples page removed (redirects to home); Google & reviews page folded into Google Business Profile (redirect)
- [x] Services mega menu in 4 groups (Your website, Get found online, Get more calls, Keep customers coming) + /services hub
- [x] For HVAC menu (7 specialties) + /hvac-specialties hub; new pages: AC repair, Heating, Ductwork and air quality, Installs and replacement
- [x] New service pages: Website redesign, Estimate follow-up, Tune-up and win-back campaigns, HQ Command Center
- [ ] City pages: add Places competitor count + top-5 table, keyword volume and CPC, Census housing age (see research/crawls/skillmammoth.md). Needs Places key + a keyword source.
