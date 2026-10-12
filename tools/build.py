#!/usr/bin/env python3
"""Builds the static site's HTML pages.

Edit copy and settings here, then run:
    python3 tools/build.py              # writes pages into the site folder (production links)
    python3 tools/build.py --preview DIR  # writes a preview copy with .html links and a dummy form

Shared header, footer and report card form live in one place so the pages stay in step.
"""
import html
import os
import shutil
import sys

# ---- Settings (placeholders until Logan decides) --------------------------------
BRAND = "HVAC Marketing HQ"
BRAND_SHORT = "HVAC Marketing HQ"
TAGLINE = "Answer · Rank · Repeat"
DOMAIN = "hvacmarketinghq.com"
EMAIL = "hello@" + DOMAIN
CALL_LINK = None                       # Calendly (later GHL) booking link; until set, "Book a call" opens an email
TURNSTILE_SITEKEY = None               # Cloudflare Turnstile site key; widget is skipped until set
# Founder video bubble (bottom-left). Logan records a 60-90s face-on intro; see video-script.md.
FOUNDER_NAME = "Logan"
FOUNDER_VIDEO = None                  # e.g. "video/founder.mp4" once recorded (also add a poster: "video/founder.jpg")
FOUNDER_POSTER = None
DEMO_PHONE = None                     # demo line for missed-call text-back, e.g. "+12545550123"; block hidden until set
LEGAL_UPDATED = "October 12, 2026"   # "Last updated" on Privacy and Terms
NOINDEX = True                       # stays on until forms are tested and Logan says push
AREA = "Texas"                        # launch market; copy says "starting in Texas"

# Plans: four tiers with a monthly/annual toggle (annual = 20% off). Prices are Logan's call, so they stay
# None (shown as $X) until he picks. Draft ladder in the statewide plan: 499/899/1499/2499 monthly, builds 1995/2495/2995/4500.
ANNUAL_DISCOUNT = 0.20
PLAN_PRICE_FOR_CALC = 899            # break-even calculator default, editable by the visitor
PLANS = [
    {
        "name": "Starter", "monthly": None, "build": None, "scope": "5 pages · 1 city", "stage": "1 to 2 trucks",
        "for": "A fast site and a complete Google profile, with every missed call texted back.",
        "items": ["5-page site on our HVAC build", "Missed-call text-back in 60 seconds", "Review requests after every job", "Google profile setup", "Shared inbox app", "Live dashboard"],
    },
    {
        "name": "Growth", "monthly": None, "build": None, "featured": True, "scope": "12 pages · 3 cities", "stage": "3 to 8 trucks",
        "for": "The full Answer, Rank, Repeat system for an owner-run shop.",
        "items": ["Everything in Starter", "12 pages, including 3 city pages", "Google profile managed, weekly job photos", "Estimate follow-up until booked or lost", "Review replies and AI web chat", "1 new article a month"],
    },
    {
        "name": "Dominate", "monthly": None, "build": None, "scope": "25 pages · 10 cities", "stage": "8+ trucks or a wide area",
        "for": "For shops covering a wide area that want the map in every town they serve.",
        "items": ["Everything in Growth", "25 pages, including 10 city pages", "Spring and fall tune-up campaigns", "ServiceTitan, Housecall Pro or Jobber hookup", "Competitor and map spam watch", "Directory listings managed"],
    },
    {
        "name": "Multi-location", "monthly": None, "build": None, "scope": "Up to 10 locations", "stage": "several branches or brands",
        "for": "One flat price for shops with several branches or brands.",
        "items": ["Everything in Dominate", "Up to 10 locations", "A profile, pages and number for each", "Monthly AI performance report", "Priority support"],
    },
]
# Lighthouse scores measured on this site's own home page (mobile). Update after each measurement.
LIGHTHOUSE = {"scores": [("Performance", 99), ("Accessibility", 100), ("Best practices", 96), ("SEO", 100)],
              "note": "This site, measured with Google Lighthouse on a simulated 4G phone, Oct 11, 2026. Main content shows in 2.0 seconds on that phone and 0.4 seconds on desktop."}

LIGHTHOUSE_LCP_DESKTOP = "0.4s"

ADDONS = [
    ("AI phone answering, after hours and during the rush", "$[X]/mo"),
    ("Extra page", "$[X] each"),
    ("Directory listings sync", "$[X]/mo"),
    ("Extra tracked phone number", "$[X]/mo"),
    ("Campaigns beyond the included allowance", "At cost"),
]

# ---- Link handling ---------------------------------------------------------------
PREVIEW = False


def call_link():
    return CALL_LINK or f"mailto:{EMAIL}?subject=15-minute%20call"


def u(path):
    """Link to a page. path is like "" (home), "hvac", "plans"."""
    if PREVIEW:
        return (path or "index") + ".html"
    return "/" + path


def a(path):
    """Link to a static asset at the site root."""
    return path if PREVIEW else "/" + path


def esc(s):
    return html.escape(s, quote=True)


# ---- Icons -----------------------------------------------------------------------
ICON = {
    "chev": '<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2 4l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>',
    "search": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2"/><path d="M20 20l-4-4" stroke="currentColor" stroke-width="2"/></svg>',
    "phone": '<svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 005 5L15 13l5 2v4a2 2 0 01-2 2A16 16 0 013 6a2 2 0 012-2z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>',
    "web": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="4" width="18" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M3 9h18" stroke="currentColor" stroke-width="2"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 22s7-6.5 7-12a7 7 0 10-14 0c0 5.5 7 12 7 12z" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="10" r="2.5" fill="currentColor"/></svg>',
    "star": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l2.8 5.8 6.2.9-4.5 4.4 1 6.2L12 17.4 6.5 20.3l1-6.2L3 9.7l6.2-.9z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>',
    "chat": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v11H9l-5 4z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>',
    "cal": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M3 10h18M8 3v4M16 3v4" stroke="currentColor" stroke-width="2"/></svg>',
    "loop": '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path d="M4 12a8 8 0 0114-5M20 12a8 8 0 01-14 5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M18 3v4h-4M6 21v-4h4" fill="none" stroke="currentColor" stroke-width="2"/></svg>',
    "chart": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 20V10M10 20V4M16 20v-7M22 20H2" fill="none" stroke="currentColor" stroke-width="2"/></svg>',
    "list": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 6h13M8 12h13M8 18h13M3 6h1M3 12h1M3 18h1" stroke="currentColor" stroke-width="2"/></svg>',
}

MARK = ('<svg class="brand-mark" viewBox="0 0 32 32" aria-hidden="true">'
        '<defs><linearGradient id="mk" x1="0" x2="1"><stop offset="0" stop-color="#47b8ff"/><stop offset="1" stop-color="#ff6a2b"/></linearGradient></defs>'
        '<rect width="32" height="32" rx="9" fill="#101826" stroke="rgba(255,255,255,.14)"/>'
        '<path d="M8 21l8-11 8 11" fill="none" stroke="url(#mk)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
        '<circle cx="16" cy="23" r="2" fill="#eef2f7"/></svg>')

ALL_TRADES = [("hvac", "HVAC", "Heating and air"), ("plumbing", "Plumbing", "Plumbers and drain"), ("roofing", "Roofing", "Roofers and storm work")]
# Trades shown in the nav and on the home page. Roofing is built but parked (see research/trade-choice.md).
LIVE_TRADES = []                     # HVAC-only positioning: the home page is the HVAC page
TRADES = [t for t in ALL_TRADES if t[0] in LIVE_TRADES]
OFFERINGS = [("website", "Website", "Fast, built to book service calls"), ("marketing", "Google & reviews", "Profile, reviews, listings"), ("app", "Lead system", "Text-back, inbox, follow-up")]


# ---- Shared parts ----------------------------------------------------------------
def header(has_form=True):
    def menu(label, items):
        links = "".join(f'<a href="{u(k)}">{n}<span>{d}</span></a>' for k, n, d in items)
        return (f'<div class="nav-group"><button type="button" aria-expanded="false">{label}{ICON["chev"]}</button>'
                f'<div class="nav-menu">{links}</div></div>')
    rc = "#report-card" if has_form else u("") + "#report-card"
    return f"""<a class="skip" href="#main">Skip to content</a>
<div class="announce"><a href="{u('plans')}"><span class="pill">Now open</span><b>Taking founding HVAC clients in Texas.</b> <span class="muted">See founding pricing →</span></a></div>
<header class="site-head">
  <div class="wrap head-row">
    <a class="brand" href="{u('')}">{MARK}<span>{esc(BRAND_SHORT)}<small>{esc(TAGLINE)}</small></span></a>
    <button class="nav-toggle" type="button" aria-label="Menu" aria-expanded="false"><svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" stroke-width="2"/></svg></button>
    <nav class="nav" aria-label="Main">
      <a class="nav-link" href="{u('method')}">The method</a>
      {menu("Services", OFFERINGS)}
      {menu("Who we help", [(n["slug"], n["name"], n["nav"]) for n in NICHES])}
      <a class="nav-link" href="{u('plans')}">Pricing</a>
      <a class="nav-link" href="{u('guides')}">Guides</a>
      <a class="btn btn-primary btn-small" href="{rc}">Free report card</a>
    </nav>
  </div>
</header>"""


def footer(has_form=True):
    offers = "".join(f'<li><a href="{u(k)}">{n}</a></li>' for k, n, _ in OFFERINGS)
    niches = "".join(f'<li><a href="{u(n["slug"])}">{esc(n["name"])}</a></li>' for n in NICHES)
    rc = "#report-card" if has_form else u("") + "#report-card"
    return f"""<footer class="site-foot">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <a class="brand" href="{u('')}">{MARK}<span>{esc(BRAND)}<small>{esc(TAGLINE)}</small></span></a>
        <p style="margin-top:16px;max-width:36ch">Websites, Google profiles and lead systems for HVAC companies. Starting in {esc(AREA)}.</p>
      </div>
      <div><h2 class="foot-h">How it works</h2><ul><li><a href="{u('method')}">The method</a></li><li><a href="{u('plans')}">Pricing</a></li><li><a href="{u('')}#tech">The tech</a></li><li><a href="{u('guides')}">Guides</a></li><li><a href="{u('guide-hvac-website-checklist')}">Website checklist</a></li></ul></div>
      <div><h2 class="foot-h">Services</h2><ul>{offers}</ul><h2 class="foot-h" style="margin-top:18px">Who we help</h2><ul>{niches}</ul></div>
      <div><h2 class="foot-h">Locations</h2><ul><li><a href="{u('hvac-marketing-texas')}">Texas</a></li><li><a href="{u('hvac-marketing-houston-tx')}">Houston</a></li><li><a href="{u('hvac-marketing-dallas-tx')}">Dallas</a></li><li><a href="{u('hvac-marketing-austin-tx')}">Austin</a></li><li><a href="{u('hvac-marketing-waco-tx')}">Waco</a></li><li><a href="{u('locations')}">All locations</a></li></ul></div>
      <div><h2 class="foot-h">Company</h2><ul><li><a href="{u('report-card')}">Free report card</a></li><li><a href="{esc(call_link())}">Book a 15-minute call</a></li><li><a href="mailto:{EMAIL}">{EMAIL}</a></li><li><a href="{'llms.txt' if PREVIEW else '/llms.txt'}">Info for AI assistants</a></li></ul></div>
    </div>
    <p class="foot-word" aria-hidden="true">{esc(BRAND)}</p>
    <div class="foot-base">
      <span>© <span data-year>2026</span> {esc(BRAND)}. Waco, Texas.</span>
      <span><a href="{u('privacy')}">Privacy</a> · <a href="{u('terms')}">Terms</a></span>
    </div>
  </div>
</footer>"""


def report_card(title="Get your free report card", sub=None, trade="HVAC"):
    sub = sub or (f"We grade your Google profile, reviews, website and listings against the {trade if trade.isupper() else trade.lower()} companies "
                  "people find near you. It lands in your inbox in about five minutes. Nobody will call you.")
    turnstile = "" if PREVIEW or not TURNSTILE_SITEKEY else f'<div class="cf-turnstile" data-sitekey="{TURNSTILE_SITEKEY}" data-theme="dark"></div>'
    return f"""<section class="section" id="report-card">
  <div class="wrap"><div class="rc-wrap reveal"><div class="rc">
    <div>
      <span class="eyebrow">Free report card</span>
      <h2>{esc(title)}</h2>
      <p class="lede">{esc(sub)}</p>
      <div class="grades" aria-hidden="true">
        <div class="grade blur"><span>Google profile</span><b class="g-b">B</b></div>
        <div class="grade blur"><span>Reviews</span><b class="g-c">C</b></div>
        <div class="grade blur"><span>Website</span><b class="g-d">D</b></div>
        <div class="grade blur"><span>Listings</span><b class="g-c">C</b></div>
      </div>
      <p class="muted" style="margin-top:18px;font-size:.92rem">Graded only on what anyone can see in public. You get the grades and what to fix first.</p>
    </div>
    <form class="rc-form" novalidate>
      <div class="rc-body">
        <div class="rc-progress" aria-hidden="true"><i class="on"></i><i></i><i></i><i></i></div>
        <input class="hp" type="text" name="company_fax" tabindex="-1" autocomplete="off" aria-hidden="true">
        <input type="hidden" name="trade" value="{esc(trade)}">
        <div class="rc-step on">
          <h3>What's your website?</h3>
          <p class="muted">No website yet? Put your Facebook page or type "none".</p>
          <div class="field"><label for="rc-site-{trade}">Website</label><input id="rc-site-{trade}" type="text" name="website" placeholder="yourcompany.com" required data-msg="Add your website, or type none." autocomplete="url"></div>
          <div class="rc-nav"><button type="button" class="btn btn-primary" data-next>Next</button></div>
        </div>
        <div class="rc-step">
          <h3>What's the business called?</h3>
          <p class="muted">The name on your Google profile, so we grade the right one.</p>
          <div class="field"><label for="rc-biz-{trade}">Business name</label><input id="rc-biz-{trade}" type="text" name="business" required data-msg="Add your business name." autocomplete="organization"></div>
          <div class="field"><label for="rc-town-{trade}">Main town you serve</label><input id="rc-town-{trade}" type="text" name="town" placeholder="Waco"></div>
          <div class="rc-nav"><button type="button" class="rc-back">Back</button><button type="button" class="btn btn-primary" data-next>Next</button></div>
        </div>
        <div class="rc-step">
          <h3>Where should we send it?</h3>
          <div class="field"><label for="rc-name-{trade}">First name</label><input id="rc-name-{trade}" type="text" name="first_name" required data-msg="Add your first name." autocomplete="given-name"></div>
          <div class="field"><label for="rc-email-{trade}">Email</label><input id="rc-email-{trade}" type="email" name="email" required data-msg="Add a valid email." autocomplete="email"></div>
          <div class="rc-nav"><button type="button" class="rc-back">Back</button><button type="button" class="btn btn-primary" data-next>Next</button></div>
        </div>
        <div class="rc-step">
          <h3>Last one: your phone</h3>
          <p class="muted">Only used if you ask us to text you. We don't cold call.</p>
          <div class="field"><label for="rc-phone-{trade}">Mobile phone</label><input id="rc-phone-{trade}" type="tel" name="phone" required data-msg="Add a phone number." autocomplete="tel" pattern="[0-9()+.\\- ]{{10,}}"></div>
          <label class="consent"><input type="checkbox" name="sms_consent" value="yes"><span>Text me about my report card. Message and data rates may apply. Message frequency varies. Reply STOP to opt out, HELP for help. Consent is not a condition of purchase. See our <a href="{u('privacy')}">Privacy Policy</a> and <a href="{u('terms')}">Terms</a>.</span></label>
          {turnstile}
          <div class="rc-nav"><button type="button" class="rc-back">Back</button><button type="submit" class="btn btn-primary">Send my report card</button></div>
        </div>
        <p class="rc-error" role="alert"></p>
      </div>
      <div class="rc-done" role="status">
        <div class="ok">✓</div>
        <h3>It's on the way</h3>
        <p class="muted">Check your inbox in about five minutes. If it's not there, look in spam for an email from {esc(BRAND_SHORT)}.</p>
      </div>
      <p class="rc-call">Rather talk it through? <a href="{esc(call_link())}">Book a 15-minute call</a></p>
    </form>
  </div></div></div>
</section>"""


def demo_line():
    if not DEMO_PHONE:
        return ""
    d = DEMO_PHONE[-10:]
    return f'<div class="demo-line"><div><b>Try it yourself.</b> Call our demo line, let it ring out and hang up. Watch for the text.</div><a class="btn btn-ghost btn-small" href="tel:{DEMO_PHONE}">({d[:3]}) {d[3:6]}-{d[6:]}</a></div>'


def founder_video(has_form=True):
    if not FOUNDER_VIDEO and not PREVIEW:
        return ""  # live site: no empty video bubble until Logan records one
    if FOUNDER_VIDEO:
        poster = f' poster="{a(FOUNDER_POSTER)}"' if FOUNDER_POSTER else ""
        media = f'<video src="{a(FOUNDER_VIDEO)}"{poster} controls playsinline preload="none"></video>'
        thumb = f'<img src="{a(FOUNDER_POSTER)}" alt="" width="72" height="72">' if FOUNDER_POSTER else '<span class="fv-play" aria-hidden="true"></span>'
    else:
        media = '<div class="fv-empty"><span class="fv-play" aria-hidden="true"></span><p><b>Founder intro video</b><br>A 60-second hello from Logan goes here.</p><span class="tbd">Video TBD</span></div>'
        thumb = '<span class="fv-play" aria-hidden="true"></span>'
    return f"""<div class="fv" data-fv>
  <button type="button" class="fv-bubble" aria-haspopup="dialog" aria-label="Watch a 60-second hello from {esc(FOUNDER_NAME)}, the founder">{thumb}<span class="fv-label"><b>Hi, I'm {esc(FOUNDER_NAME)}</b>60-second hello</span></button>
  <button type="button" class="fv-x" aria-label="Hide video">×</button>
  <dialog class="fv-dialog" aria-label="Founder video"><button type="button" class="fv-close" aria-label="Close">×</button>{media}
    <a class="btn btn-primary btn-small" href="{'' if has_form else u('')}#report-card" data-fv-cta>Get my free report card</a></dialog>
</div>"""


def page(path, title, desc, body, extra_head="", has_form=True):
    robots = '<meta name="robots" content="noindex, nofollow">' if NOINDEX else ""
    turnstile = "" if PREVIEW or not TURNSTILE_SITEKEY else '<script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>'
    full_title = title if title.endswith(BRAND) else f"{title} | {BRAND}"
    preview_meta = '<meta name="site-preview" content="1">' if PREVIEW else ""
    return f"""<!doctype html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
{robots}
{preview_meta}
<link rel="preload" href="{a('fonts/Archivo-600-800.woff2')}" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{a('fonts/IBMPlexSans-400.woff2')}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{a('styles.css')}">
<meta name="theme-color" content="#070b12">
<link rel="icon" href="{a('favicon.svg')}" type="image/svg+xml">
{extra_head}
</head>
<body>
{header(has_form)}
<main id="main">
{body}
</main>
{footer(has_form)}
{founder_video(has_form)}
<script src="{a('main.js')}" defer></script>
{turnstile}
</body>
</html>
"""


def cta_band(text="See where your shop stands before you spend a dollar."):
    return f"""<section class="section tight"><div class="wrap"><div class="cta-band">
  <h2>{esc(text)}</h2><a class="btn" href="#report-card">Get your report card</a>
</div></div></section>"""


def demo():
    return f"""<div class="demo" aria-label="How a service call gets booked">
  <div class="demo-steps">
    <button type="button">Found on Google</button>
    <button type="button">Missed call texted back</button>
    <button type="button">Service call booked</button>
    <button type="button">Review asked for</button>
  </div>
  <div class="phone"><div class="screen">
    <div class="screen-bar"><span>4:52</span><span>●●● 5G</span></div>
    <div class="scene">
      <div class="search-box">{ICON["search"]}<span>ac repair near me</span></div>
      <div class="map"><i class="pin" style="left:18%;top:30%"></i><i class="pin" style="left:70%;top:58%"></i><i class="pin you" style="left:46%;top:36%"></i><i class="pin" style="left:80%;top:20%"></i></div>
      <div class="result you"><b>Your Shop Heating &amp; Air</b><span class="stars">★★★★★</span> <span class="faint">Open 24 hours · Book online</span></div>
      <div class="result dim"><b>Another AC Company</b><span class="faint">Closes 5 PM</span></div>
      <div class="result dim"><b>Big Franchise Air</b><span class="faint">Website</span></div>
    </div>
    <div class="scene">
      <div class="call-card"><div class="ring">{ICON["phone"]}</div><b>(254) 555-0142</b><small>Missed call · 4:52 PM</small></div>
      <div class="bubble out">Hi, this is Your Shop Heating &amp; Air. Sorry we missed your call. What's going on with your system?</div>
      <div class="bubble-meta">Sent automatically · 0:08</div>
      <div class="bubble in">AC is running but blowing warm air. House is 84.</div>
      <div class="bubble out">We can get a tech out tomorrow morning. Want the 8 to 10 window?</div>
    </div>
    <div class="scene">
      <div class="bubble in">Yes please, 8 to 10 works</div>
      <div class="booked">
        <span class="tag">Service call booked</span>
        <dl><dt>When</dt><dd>Tomorrow, 8 to 10 AM</dd><dt>Job</dt><dd>AC not cooling</dd><dt>Where</dt><dd>Woodway, TX</dd><dt>Tech</dt><dd>Assigned</dd></dl>
      </div>
      <div class="bubble out" style="margin-top:12px">You're booked. We'll text when your tech is on the way.</div>
    </div>
    <div class="scene">
      <div class="bubble out">Thanks for choosing Your Shop Heating &amp; Air. Would you leave us a quick review? It helps a lot.</div>
      <div class="bubble-meta">Sent when the job was marked done</div>
      <div class="review-card"><span class="stars">★★★★★</span><br>Texted me back in seconds and had it fixed by 10. Great tech.<div class="reply"><b>Reply from the owner:</b> Thank you! Glad we got you cool again.</div></div>
    </div>
  </div></div>
  <p class="demo-caption">Illustration of the system. Your name, your number, your customers.</p>
</div>"""


METHOD = [
    ("Answer", "Every call answered, even when you can't.", [
        "Missed-call text-back in 60 seconds, guaranteed",
        "One shared inbox for calls, texts, chats and forms",
        "AI web chat that captures the lead after hours",
        "Estimate follow-up until the job is booked or lost",
        "Optional AI phone answering during the rush",
    ], "Nobody calls the next shop because you were in an attic."),
    ("Rank", "Show up first when someone searches.", [
        "A fast site built around the jobs you want",
        "A page for each service and each town you really serve",
        "Google profile complete, active and posting job photos",
        "Directory listings kept consistent",
        "Map spam reported on fake competitor listings",
    ], "More of the right homeowners find you, not a franchise."),
    ("Repeat", "Turn every job into the next one.", [
        "Review request after every finished job",
        "A reply to every review, in your voice",
        "Spring and fall tune-up campaigns to past customers",
        "Maintenance plan reminders before plans lapse",
        "A live dashboard and a quarterly re-grade",
    ], "Reviews and repeat customers compound every month."),
]


def method_summary():
    cards = []
    for n, (name, line, items, close) in enumerate(METHOD):
        lis = "".join(f"<li>{esc(x)}</li>" for x in items[:3])
        cards.append(f'<div class="phase"><span class="phase-n">0{n+1}</span><h3>{name}</h3><p class="phase-line">{esc(line)}</p><ul class="ticks">{lis}</ul></div>')
    return f'<div class="phases">{"".join(cards)}</div><p style="margin-top:24px"><a class="btn btn-ghost" href="{u("method")}">See the full method</a></p>'


def dashboard():
    rows = [("Missed calls texted back", "38", "of 38"), ("Average reply time", "0:09", "minutes"), ("Booked from texts", "14", "jobs"), ("New Google reviews", "11", "this month")]
    tiles = "".join(f'<div class="dash-tile"><span>{a_}</span><b>{b}</b><small>{c}</small></div>' for a_, b, c in rows)
    bars = [3, 5, 4, 7, 6, 9, 8, 11, 10, 12, 9, 14]
    mx = max(bars)
    chart = "".join(f'<i style="height:{int(h / mx * 100)}%"></i>' for h in bars)
    feed = [("4:52 PM", "Missed call · texted back in 0:08", "go"), ("4:55 PM", "Reply: AC blowing warm air", ""), ("5:02 PM", "Service call booked · Tue 8 to 10 AM", "go"), ("Yesterday", "New 5-star review · replied", "")]
    items = "".join(f'<li class="{c}"><span>{t}</span>{esc(x)}</li>' for t, x, c in feed)
    return f"""<div class="dash" aria-label="Sample dashboard">
  <div class="dash-head"><b>Your Shop Heating &amp; Air</b><span class="live">Live</span><span class="dash-sample">Sample data</span></div>
  <div class="dash-tiles">{tiles}</div>
  <div class="dash-body">
    <div class="dash-chart"><p>Booked jobs from the system, by week</p><div class="bars">{chart}</div></div>
    <ul class="dash-feed">{items}</ul>
  </div>
</div>"""


def tech():
    scores = LIGHTHOUSE
    rings = "".join(f'<div class="score"><svg viewBox="0 0 36 36" aria-hidden="true"><circle cx="18" cy="18" r="15.9" class="trk"/><circle cx="18" cy="18" r="15.9" class="val" stroke-dasharray="{v} 100"/></svg><b>{v}</b><span>{k}</span></div>' for k, v in scores["scores"])
    stack = [
        ("Static pages on a global edge network", "No WordPress, no page builder, no plugins to patch. Pages are pre-built and served close to the visitor."),
        ("Built for Google from the start", "LocalBusiness schema, clean service and city pages, Core Web Vitals in the green."),
        ("Tracking you can trust", "Tracked phone numbers by source, form tracking and a live dashboard, not a monthly PDF."),
        ("Plugs into your software", "Booking and job-done triggers for ServiceTitan, Housecall Pro and Jobber, or our calendar if you don't use one."),
        ("Secure by default", "HTTPS everywhere, strict security headers and bot protection on every form."),
        ("No lock-in", "You own the domain, the content and the leads. Leave tomorrow and take everything."),
    ]
    items = "".join(f'<div class="stack-item"><h3>{esc(h)}</h3><p>{esc(t)}</p></div>' for h, t in stack)
    return f"""<div class="tech">
  <div class="tech-scores">
    <div class="scores">{rings}</div>
    <p class="note">{esc(scores['note'])}</p>
  </div>
  <div class="stack">{items}</div>
</div>"""


def ownership():
    left = ["Your domain, registered in your name", "Your Google profile and every review on it", "Your site files and content", "Your customer list and every lead"]
    right = ["A live dashboard you can open anytime", "Prices on the website, not after a sales call", "Month to month [TBD], no long contract", "Your number ported back if you leave"]
    l = "".join(f"<li>{esc(x)}</li>" for x in left)
    r = "".join(f"<li>{esc(x)}</li>" for x in right)
    return f"""<div class="grid two">
  <div class="card"><h3>You own</h3><ul class="ticks">{l}</ul></div>
  <div class="card"><h3>You can see</h3><ul class="ticks">{r}</ul></div>
</div>"""


def url_form(btn="Grade my site", note="Free report card in your inbox in about 5 minutes. Nobody calls you."):
    return f"""<form class="url-form" data-url-form novalidate>
  <label><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18" fill="none" stroke="currentColor" stroke-width="2"/></svg>
  <span class="sr-only">Your website</span><input type="text" name="website" placeholder="yourcompany.com" autocomplete="url" inputmode="url"></label>
  <button class="btn btn-primary" type="submit">{esc(btn)} <span class="arrow">→</span></button>
</form>
<p class="url-note">{esc(note)}</p>"""


def hero_visual():
    rows = [("Google profile", "B", "b", 78), ("Reviews", "C", "c", 61), ("Website", "D", "d", 44), ("Listings", "C", "c", 58)]
    g = "".join(f'<div class="g-row"><span>{n}</span><b class="g-{c}">{l}</b><div class="g-bar"><i class="bar-{c}" style="width:{w}%"></i></div></div>' for n, l, c, w in rows)
    return f"""<div class="stack-vis" aria-label="Sample report card">
  <div class="float f2"><span class="ic">{ICON["pin"]}</span><div><b>#1 in the map pack</b><span>"ac repair near me"</span></div></div>
  <div class="rc-sample">
    <div class="rc-sample-head"><div><small>HVAC report card</small><b>Your Shop Heating &amp; Air</b><br><span class="muted" style="font-size:.84rem">Compared with the top shops near you</span></div><div class="overall">C</div></div>
    {g}
    <div class="fix"><b>Fix first:</b> no service pages for AC repair or installs, and no way to book online.</div>
  </div>
  <div class="float f1"><span class="ic">{ICON["chat"]}</span><div><b>Missed call texted back</b><span>in 0:08 · booked for Tue 8 AM</span></div></div>
  <span class="sample-tag">Sample</span>
</div>"""


def works_with():
    names = ["Google Business Profile", "ServiceTitan", "Housecall Pro", "Jobber", "Google Calendar"]
    return '<div class="works"><div class="wrap works-row"><span>Works with</span>' + "".join(f"<b>{n}</b>" for n in names) + "</div></div>"


def pillars():
    cal = "".join(f'<i class="{c}"></i>' for c in ["", "on", "on2", "on", "", "on", "", "on2", "on", "on", "on", "on2", "on", "", "on", "on", "on2", "on", "on", "on", "on"])
    return f"""<div class="pillars">
  <div class="pillar reveal"><div class="vis"><div class="speed-bar"><i></i></div><span class="big" style="margin-top:22px">{LIGHTHOUSE_LCP_DESKTOP}</span><small>this site, desktop load</small></div><h3>Fast</h3><p>Pre-built pages that open almost instantly on a phone, so nobody bounces to the next shop.</p></div>
  <div class="pillar reveal"><div class="vis"><div class="rank-pin"><div class="you"><b>1</b> Your Shop Heating &amp; Air</div><div><b>2</b> Another AC Company</div><div><b>3</b> Big Franchise Air</div></div></div><h3>Found</h3><p>Service pages, town pages and a Google profile that's complete, active and full of fresh reviews.</p></div>
  <div class="pillar reveal"><div class="vis"><div class="cal-vis">{cal}</div></div><h3>Booked</h3><p>Every missed call texted back in 60 seconds, every estimate followed up, every finished job asked for a review.</p></div>
</div>"""


def pains_grid():
    items = [
        ("Calls go to voicemail", "Your techs are in an attic and the office is on another line. The homeowner calls the next shop."),
        ("Quotes go cold", "A $9,000 replacement needs follow-up. Nobody has time, so whoever calls back wins."),
        ("Reviews trickle in", "Happy customers rarely review unless asked. The shop asking every time climbs the map."),
        ("Your agency sends a PDF", "You can't see what you're paying for, and leaving means losing your site."),
    ]
    cards = "".join(f'<div class="pain reveal"><div class="x">✕</div><h3>{esc(h)}</h3><p>{esc(t)}</p></div>' for h, t in items)
    return f'<div class="pains grid4">{cards}</div>'


def method_block():
    # Three arcs around a center, one per phase; JS lights them in turn.
    import math
    cx = cy = 200; r = 150
    cols = ["#47b8ff", "#9b8cff", "#ff6a2b"]
    arcs, nodes = [], []
    for i in range(3):
        a0 = math.radians(-90 + i * 120 + 8); a1 = math.radians(-90 + (i + 1) * 120 - 8)
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0); x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        arcs.append(f'<path class="arc" data-phase="{i}" stroke="{cols[i]}" d="M{x0:.1f} {y0:.1f} A{r} {r} 0 0 1 {x1:.1f} {y1:.1f}"/>')
        am = math.radians(-90 + i * 120 + 60)
        nx, ny = cx + r * math.cos(am), cy + r * math.sin(am)
        nodes.append(f'<g class="node" data-phase="{i}"><circle cx="{nx:.1f}" cy="{ny:.1f}" r="40"/><text x="{nx:.1f}" y="{ny + 5:.1f}">{METHOD[i][0]}</text></g>')
    svg = f"""<svg viewBox="0 0 400 400" role="img" aria-label="Answer, Rank and Repeat form one loop around your schedule">
  <circle class="ring" cx="200" cy="200" r="{r}"/><circle class="ring" cx="200" cy="200" r="96"/>
  {''.join(arcs)}{''.join(nodes)}
  <text class="center-t" x="200" y="190">EVERY DAY</text><text class="center-b" x="200" y="218">Full schedule</text>
</svg>"""
    phases = []
    for n, (name, line, items, close) in enumerate(METHOD):
        lis = "".join(f"<li>{esc(x)}</li>" for x in items[:4])
        phases.append(f'<div class="phase" data-phase="{n}"><div class="phase-top"><span class="phase-n">0{n+1}</span><h3>{name}</h3></div><p class="phase-line">{esc(line)}</p><ul class="ticks">{lis}</ul></div>')
    return f'<div class="method" data-method><div class="method-dia reveal">{svg}</div><div class="phase-list">{"".join(phases)}</div></div>'


def mappack():
    return f"""<div class="mappack">
  <div class="q">{ICON["search"]}<span>ac repair near me</span></div>
  <div class="mp-map"><i class="mp-pin" style="left:20%;top:34%"></i><i class="mp-pin you" style="left:48%;top:30%"></i><i class="mp-pin" style="left:74%;top:55%"></i></div>
  <div class="mp-item you"><div><b>Your Shop Heating &amp; Air</b><span class="stars">★★★★★</span> <span class="sub">Open 24 hours</span></div><span class="rank">#1</span></div>
  <div class="mp-item"><div><b>Another AC Company</b><span class="sub">Closes 5 PM</span></div></div>
</div>"""


def bento():
    return f"""<div class="bento">
  <div class="tile b-2 b-tall reveal"><div><span class="tile-label">Answer</span><h3>Missed-call text-back</h3><p>Every call you miss gets a text in seconds, with your name on it.</p></div>{demo()}</div>
  <div class="tile b-2 reveal"><div><span class="tile-label">Rank</span><h3>Top of the map pack</h3><p>A complete, active Google profile and real town pages.</p></div><div class="mock">{mappack()}</div></div>
  <div class="tile b-2 reveal"><div><span class="tile-label">Answer</span><h3>AI web chat</h3><p>Answers questions and captures the lead after hours.</p></div><div class="mock chat"><div class="chat-head"><i></i>Your Shop assistant</div><div class="msg user">Do you do weekend AC repair?</div><div class="msg bot">Yes, Saturdays 8 to 4. Want me to book a time? What's your address?</div></div></div>
  <div class="tile b-4 reveal"><div><span class="tile-label">Repeat</span><h3>Your live dashboard</h3><p>Calls, texts, booked jobs and reviews, updated as they happen. No monthly PDF.</p></div><div class="mock">{dashboard()}</div></div>
  <div class="tile b-3 reveal"><div><span class="tile-label">Repeat</span><h3>Reviews on autopilot</h3><p>A request after every finished job, and a reply to every review.</p></div><div class="mock review"><div class="req"><span class="tag">Sent</span>Review request · job marked done 2:14 PM</div><span class="stars">★★★★★</span> Texted me back in seconds and had it fixed by 10.<div class="reply"><b>Owner reply:</b> Thank you! Glad we got you cool again.</div></div></div>
  <div class="tile b-3 reveal"><div><span class="tile-label">Repeat</span><h3>Seasonal campaigns</h3><p>Spring and fall tune-up texts to past customers, and maintenance plan reminders before they lapse.</p></div><div class="mock chat"><div class="msg bot">Hi Maria, it's Your Shop Heating &amp; Air. Summer's coming. Book your AC tune-up this month? Reply YES and we'll find a time.</div><div class="msg user">YES</div></div></div>
</div>"""


def process():
    steps = [
        ("Report card", "Get your grades by email in about five minutes. Free, and nobody calls you."),
        ("15-minute walkthrough", "If you want, we go over your weakest grade and what we'd fix first."),
        ("14-day build", "We set up your site, Google profile and lead system on our proven template."),
        ("Go live", "Your line forwards through the system and every missed call starts getting texted back."),
        ("Monthly statement", "Calls, texts, booked jobs and new reviews, on one page each month."),
    ]
    items = "".join(f'<li class="step reveal"><span class="num">0{n+1}</span><h3>{t}</h3><p>{d}</p></li>' for n, (t, d) in enumerate(steps))
    return f'<ol class="steps">{items}</ol>'


def loop():
    stops = [
        ("Found on Google", "A complete Google profile and a site built around the jobs you want put you in the map results."),
        ("Missed call texted back", "Every call you can't pick up gets a text in seconds, so the customer doesn't call the next shop."),
        ("Service call booked", "Replies, follow-up and booking happen in one inbox your office and techs can all see."),
        ("Review asked for", "When the job is done, the customer gets a review request. More reviews, higher on the map."),
    ]
    items = "".join(f'<div class="loop-stop"><span class="num">0{n+1}</span><h3>{t}</h3><p>{d}</p></div>' for n, (t, d) in enumerate(stops))
    return f"""<div class="loop">
  <svg class="loop-track" preserveAspectRatio="none" aria-hidden="true"><rect x="1%" y="34" width="98%" height="calc(100% - 50px)" rx="18"/></svg>
  {items}
  <div class="loop-back">{ICON["loop"]} New reviews feed back into being found</div>
</div>"""


def calculator(ticket=350, job=9000, job_label="system replacement"):
    return f"""<div class="calc">
  <div>
    <div class="field"><label for="c-plan">Monthly plan price</label><div class="money"><input id="c-plan" type="text" inputmode="decimal" name="plan" value="{PLAN_PRICE_FOR_CALC:,}"></div><div class="hint">Placeholder until plans are final. Change it to try any number.</div></div>
    <div class="field"><label for="c-ticket">Your average service call ticket</label><div class="money"><input id="c-ticket" type="text" inputmode="decimal" name="ticket" value="{ticket}"></div></div>
    <div class="field"><label for="c-job">Your average {esc(job_label)}</label><div class="money"><input id="c-job" type="text" inputmode="decimal" name="job" value="{job:,}"></div></div>
    <div class="field"><label for="c-lead">What you pay per bought lead (Angi, Thumbtack and similar)</label><div class="money"><input id="c-lead" type="text" inputmode="decimal" name="lead" value="75"></div></div>
    <div class="field"><label for="c-margin">Your gross margin</label><select id="c-margin" name="margin"><option value="30">30%</option><option value="40">40%</option><option value="50" selected>50%</option><option value="60">60%</option></select></div>
  </div>
  <div class="calc-out" aria-live="polite">
    <div class="row"><span class="big" data-out="calls">–</span><p>extra service calls a month pay for the plan</p></div>
    <div class="row"><span class="big" data-out="jobs">–</span><p>{esc(job_label)}s a month pay for it, on their own</p></div>
    <div class="row"><span class="big" data-out="leads">–</span><p>bought leads cost the same, and those are shared with other shops</p></div>
    <p style="font-size:.85rem">Your numbers, your margin. This is math, not a promise of results.</p>
  </div>
</div>"""


def money(n):
    return "$X" if n is None else f"${n:,.0f}"


def plans_cards():
    out = []
    for p in PLANS:
        feat = " featured" if p.get("featured") else ""
        flag = '<span class="flag">Most shops start here</span>' if p.get("featured") else ""
        m = p["monthly"]
        annual = None if m is None else round(m * (1 - ANNUAL_DISCOUNT))
        save = "Save $X/yr" if m is None else f"Save ${(m - annual) * 12:,.0f}/yr"
        items = "".join(f"<li>{esc(x)}</li>" for x in p["items"])
        tbd = ' <span class="tbd">TBD</span>' if m is None else ""
        out.append(f"""<div class="plan{feat}">{flag}
  <h3>{p['name']}</h3>
  <p class="scope">{esc(p['scope'])}</p>
  <p class="stage">Best for {esc(p['stage'])}</p>
  <div class="price"><span data-monthly="{money(m)}" data-annual="{money(annual)}">{money(annual)}</span><small> /month</small>{tbd}</div>
  <p class="billing"><span class="when-annual">Billed yearly · <b>{save}</b></span><span class="when-monthly">Billed monthly, cancel anytime</span></p>
  <p class="for">{esc(p['for'])}</p>
  <ul class="ticks">{items}</ul>
  <div class="build">One-time build: {money(p['build'])}</div>
  <a class="btn {'btn-primary' if feat else 'btn-ghost'}" href="#report-card">Get started</a>
</div>""")
    toggle = f"""<div class="bill-toggle" role="group" aria-label="Billing">
  <button type="button" data-bill="monthly" aria-pressed="false">Monthly</button>
  <button type="button" data-bill="annual" aria-pressed="true">Annual <span class="save">Save {int(ANNUAL_DISCOUNT*100)}%</span></button>
</div>"""
    return f'<div class="pricing" data-billing="annual"><h2 class="sr-only">Plans</h2>{toggle}<div class="plans">' + "".join(out) + "</div></div>"


def plans_teaser():
    cards = "".join(f'<a class="card teaser" href="{u("plans")}"><h3>{p["name"]}</h3><p class="scope">{esc(p["scope"])}</p><b>from {money(None if p["monthly"] is None else round(p["monthly"]*(1-ANNUAL_DISCOUNT)))}/mo</b></a>' for p in PLANS)
    return f'<div class="grid four">{cards}</div>'


def compare():
    rows = [
        ("Contract", "Often 12 months", "Month to month [TBD]"),
        ("Reporting", "A monthly PDF", "A live dashboard you can check anytime"),
        ("Who owns the website", "Sometimes the agency", "You, always"),
        ("Time to launch", "Varies, often months", "14 days, guaranteed"),
        ("Missed-call text-back", "Add-on, if offered", "In every plan, 60 seconds guaranteed"),
        ("Pricing", "Quoted after a sales call", "On this page, monthly or annual"),
        ("If it's not working", "Locked in until the term ends", "First month back within 30 days"),
        ("What they promise", "Page-one rankings, guaranteed", "Only what we control, in writing"),
        ("Who you talk to", "An account manager with dozens of clients", "A small team that only works with HVAC"),
    ]
    body = "".join(f"<tr><th scope=\"row\">{esc(a_)}</th><td>{esc(b)}</td><td>{esc(c)}</td></tr>" for a_, b, c in rows)
    return f'''<div class="compare"><h3>Compared with a typical agency</h3>
  <div class="table-wrap"><table><thead><tr><th></th><th>Typical agency</th><th>{esc(BRAND_SHORT)}</th></tr></thead><tbody>{body}</tbody></table></div></div>'''


def addons():
    rows = "".join(f'<div class="addon"><span>{esc(n)}</span><b>{esc(p)}</b></div>' for n, p in ADDONS)
    return f'<div class="addons"><h3>One-time and optional</h3><div class="addons-list">{rows}</div></div>'


def promise():
    return """<div class="promise">
  <div class="card reveal"><span class="big">60 seconds</span><p>Every missed call gets a text back within 60 seconds.</p></div>
  <div class="card"><span class="big">14 days</span><p>Your new site is live within 14 days of getting your content.</p></div>
  <div class="card"><span class="big">[N] reviews</span><p>An agreed number of new Google reviews in your first 90 days.</p></div>
</div>
<div class="moneyback reveal"><span class="big">30 days</span><div><h3>Money-back guarantee</h3><p>Not happy in your first 30 days after launch? Tell us and we refund your first month. No form to fill out, no argument. <span class="tbd">Build fee terms TBD</span></p></div></div>
{demo_line()}
<div class="wont reveal"><h3>What we won't promise</h3><p class="muted">Anyone who guarantees these is guessing. We'd rather tell you now.</p><ul class="crosses">
  <li>A #1 ranking on Google</li><li>A set number of jobs or calls</li><li>That ChatGPT will recommend you</li><li>A fixed cost per lead</li></ul></div>
<p class="promise-note">We only guarantee what we control. <span class="tbd">What happens if we miss: TBD</span></p>"""


def terms_strip():
    items = ["30-day money-back guarantee", "Prices on the website", "You own your site and domain", "Billing starts at launch"]
    return '<ul class="terms-strip">' + "".join(f"<li>{esc(x)}</li>" for x in items) + "</ul>"


RC_CHECKS = [
    ("pin", "Google profile", "Is it complete, active and in the right categories? Where do you show up on the map against the shops near you?"),
    ("star", "Reviews", "How many, how recent and how often you reply, next to the shops that outrank you."),
    ("web", "Website", "Speed on a phone, a tap-to-call button, service pages for the jobs you want, and a way to book."),
    ("list", "Listings", "Whether your name, address and phone match across the directories Google and AI tools read."),
]


def rc_learn():
    cards = "".join(f'<div class="card reveal"><div class="icon">{ICON.get(i, ICON["pin"])}</div><h3>{t}</h3><p>{esc(d)}</p></div>' for i, t, d in RC_CHECKS)
    return f'<div class="grid four">{cards}</div>'


def rc_how():
    steps = [
        ("You", "Type your website", "Under a minute. Four quick questions, no credit card."),
        ("We", "Compare you locally", "Your profile, reviews, site and listings next to the HVAC shops people find near you."),
        ("You get", "Grades and a fix-first list", "In your inbox in about five minutes, in plain English."),
        ("You", "Decide what's next", "Fix it yourself, or have us do it. The report card is yours to keep either way."),
    ]
    items = "".join(f'<li class="how reveal"><span class="who">{w}</span><h3>{t}</h3><p>{d}</p></li>' for w, t, d in steps)
    return f'<ol class="how-list">{items}</ol>'


FIRST_90 = [
    ("Day 1", "Kickoff", "A 30-minute call on your services, towns, busy season and the jobs you want more of."),
    ("Day 3", "Access", "We walk you through sharing your domain, Google profile and phone line. No passwords over email."),
    ("Day 14", "Live", "Site launched, Google profile cleaned up, missed-call text-back and review requests running."),
    ("Day 30", "First statement", "Calls, texts, booked jobs and new reviews on one page. We fix what's leaking."),
    ("Day 60", "Rank", "Town pages and steady reviews start moving you up the map. We show you where."),
    ("Day 90", "Review", "We go over what's booking, what isn't, and agree the plan for the next 90 days."),
]


def first_90():
    items = "".join(f'<li class="tl reveal"><span class="day">{d}</span><h3>{t}</h3><p>{esc(x)}</p></li>' for d, t, x in FIRST_90)
    return f'<ol class="timeline">{items}</ol>'


def roles_split():
    we = ["Your website: copy, design, build and hosting", "Your Google profile, photos and listings", "Text-back, follow-up and review requests", "Your dashboard and monthly statement"]
    you = ["One kickoff call and quick answers", "Access to your domain, Google profile and phone line", "Job photos now and then, from your phone", "Answering the texts and booking the work"]
    l = "".join(f"<li>{esc(x)}</li>" for x in we)
    r = "".join(f"<li>{esc(x)}</li>" for x in you)
    return f"""<div class="grid two" style="margin-top:22px">
  <div class="card"><h3>We handle</h3><ul class="ticks">{l}</ul></div>
  <div class="card"><h3>You handle</h3><ul class="ticks">{r}</ul></div>
</div>"""


def fit():
    good = ["You do good work and want more of the right jobs", "You miss calls when the crew is busy", "You want to own your marketing, not rent leads", "You'll answer the texts and book the work"]
    bad = ["You can't take on more work right now", "You only want Google Ads managed", "You want a one-time site and nothing after", "You want someone to promise #1 on Google"]
    l = "".join(f"<li>{esc(x)}</li>" for x in good)
    r = "".join(f"<li>{esc(x)}</li>" for x in bad)
    return f"""<div class="grid two fit">
  <div class="card reveal"><h3>A good fit if</h3><ul class="ticks">{l}</ul></div>
  <div class="card reveal"><h3>Not a fit if</h3><ul class="crosses">{r}</ul></div>
</div>
<p class="muted" style="margin-top:16px;font-size:.92rem">If a smaller plan fits your shop better, we'll say so on the call.</p>"""


def replaces():
    tools = [("Website builder and hosting", "Website"), ("Call tracking", "Answer"), ("Texting app", "Answer"), ("Online booking", "Answer"), ("Review software", "Repeat"), ("Reporting", "Repeat")]
    rows = "".join(f'<li><span>{esc(t)}</span><b>{esc(k)}</b></li>' for t, k in tools)
    return f"""<div class="replaces">
  <div><span class="eyebrow">One login instead of six</span><h2>What your plan replaces.</h2><p class="lede">Most shops pay for these separately and still can't see what's booking. Every plan runs them as one system, set up and managed for you.</p></div>
  <ul class="replace-list">{rows}</ul>
</div>"""


def faq(items):
    rows = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(ans)}</p></details>" for q, ans in items)
    return f'<div class="faq">{rows}</div>'


COMMON_FAQ = [
    ("I got burned by an agency before. Why is this different?", "Because you can check it. Prices are on this page, you own your site, domain and reviews, and you can open your dashboard anytime to see calls, texts and booked jobs. If it isn't working, you'll see it before we tell you."),
    ("Is there a money-back guarantee?", "Yes. If you're not happy in your first 30 days after launch, tell us and we refund your first month. You keep your domain, Google profile and reviews either way."),
    ("What do I have to do?", "One kickoff call, sharing access to your domain, Google profile and phone line, approving your site before it goes live, and answering the texts. We do the rest."),
    ("Do I own my website?", "Yes. Your domain, Google profile, reviews and site content are yours. If you leave, we hand over the site files and help move your number. It's written into the agreement."),
    ("How long is the contract?", "Plan terms are being finalized. Ask us on a 15-minute call and we'll walk you through them."),
    ("What if I already have a website I like?", "Keep it. We can add the booking form and lead system to your current site, and the build fee is lower or waived."),
    ("Do I have to change my phone number?", "No. You forward your existing line through the system, so customers keep calling the number they already know. We walk you through it during setup."),
    ("Does it work with ServiceTitan, Housecall Pro or Jobber?", "Yes. Booking can go straight to your field-service software, or into our calendar if you don't use one. Review requests can trigger when a job is marked done."),
    ("Who owns my website, Google profile and reviews?", "You do. Your domain, Google profile and reviews always stay yours, even if you leave."),
    ("Do I have to manage the software?", "No. You and your office use one inbox app on your phones, and you can check the live dashboard anytime. We build and run everything behind it."),
    ("Do you run Google Ads or Local Services Ads?", "Not yet. We start with the foundation that makes ads pay off: answered calls, a site that books and a strong Google profile. Ads management is coming as an add-on."),
    ("How many Google reviews do I need?", "There's no magic number. Steady, recent reviews beat a big pile of old ones, which is why every plan asks every finished job for one."),
    ("Can you get my shop recommended by ChatGPT?", "We build what AI tools read: a complete Google profile, consistent listings, clear service pages and recent reviews. Nobody can honestly guarantee an AI answer, and we won't."),
    ("What if we can't handle more calls yet?", "Tell us on the call. We'd rather wait, or start with text-back only, than send you work your crew can't get to."),
    ("Who will I talk to?", "A small team that only works with HVAC companies. You get a direct line, not a ticket queue."),
    ("What's the build fee for?", "Building your site, setting up your Google profile, forwarding your line through the text-back system and importing your past customers. Monthly billing starts when you go live, not when you sign."),
]


# ---- Location pages ------------------------------------------------------------------
# Facts come from data/texas-cities.json (Wikipedia: 2020 Census population, NOAA climate normals as shown there)
# and the CenTex prospect sheet (active TDLR A/C contractor licenses by county, Oct 2026). Every page says
# something true and specific about its city; no copy-and-paste doorway pages.
import json
_DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "texas-cities.json")
with open(_DATA) as _f:
    _TX = json.load(_f)
CITIES = _TX["cities"]
TX_POP = _TX["texas"]["population_2020"]
# Businesses holding an active TDLR A/C contractor license, merged by company (prospects/centex-prospects.xlsx, Oct 11, 2026)
TDLR_COUNTY = {"McLennan County": 156, "Bell County": 161}


def city_path(c):
    return f"hvac-marketing-{c['slug']}-tx"


def fnum(n):
    return f"{n:,.0f}" if n is not None else "–"


def deg(n):
    return "–" if n is None else (f"{n:.0f}°F" if float(n).is_integer() else f"{n}°F")


def city_insights(c):
    out = []
    hot, days = c["july_high_f"] or 0, c.get("days_90_plus")
    cold = c["jan_low_f"] if c["jan_low_f"] is not None else 40
    k = (c.get("koppen") or "").lower()
    if days and days >= 100:
        out.append(("A cooling season most of the year", f"{c['name']} averages about {days:.0f} days a year at 90°F or hotter. AC repair and replacement pages lead your site, and every missed call in the summer surge gets a text back."))
    elif hot >= 96:
        out.append(("Summers that break AC units", f"July highs average {deg(hot)} in {c['name']}. The hottest weeks bring the most calls and the most missed ones, so text-back and fast booking matter most then."))
    else:
        out.append(("A long, busy summer", f"July highs average {deg(hot)} in {c['name']}. We build AC repair and replacement pages first and time tune-up texts for spring."))
    if cold <= 33:
        out.append(("A real heating season", f"January lows average {deg(cold)}. Furnace and heat pump pages earn their keep here, and fall tune-up campaigns fill the schedule before the first cold snap."))
    else:
        out.append(("Mild winters, steady heat pump work", f"January lows average {deg(cold)}. Heat pump repair and installs carry the cooler months, with fewer emergency heating calls."))
    if "cfa" in k or "humid" in k:
        out.append(("Humidity sells comfort", "Humid air makes homes feel warmer than the thermostat says. Pages for dehumidifiers, indoor air quality and duct work bring higher-value jobs."))
    elif "bs" in k or "bw" in k or "arid" in k or "desert" in k:
        out.append(("Dry air and dust", "Dust works filters and outdoor units hard. Maintenance plan pages and filter reminders keep customers coming back between breakdowns."))
    if c["population_2020"] and c["population_2020"] >= 500000:
        out.append(("A crowded map", f"With {fnum(c['population_2020'])} people in the city alone, you won't win every search from one address. A page for each part of town you serve helps you show up beyond your shop's neighborhood."))
    else:
        out.append(("Reviews decide it", "In a market this size, homeowners often pick between a handful of shops by star rating and how recent the reviews are. Steady review requests after every job are the fastest lever."))
    return out


def city_page(c):
    facts = [("Population", fnum(c["population_2020"]), "2020 Census"), ("Average July high", deg(c["july_high_f"]), "daily max"), ("Average January low", deg(c["jan_low_f"]), "daily min")]
    if c.get("days_90_plus"):
        facts.append(("Days at 90°F+", f"{c['days_90_plus']:.0f}", "per year"))
    elif c.get("record_high_f"):
        facts.append(("Record high", deg(c["record_high_f"]), "all time"))
    fact_html = "".join(f'<div class="cfact"><span>{a_}</span><b>{b}</b><small>{c_}</small></div>' for a_, b, c_ in facts)
    station = f"{c['climate_station']}, {c['climate_period']}" if c.get("climate_station") and c.get("climate_period") else (c.get("climate_station") or "local weather records")
    ins = "".join(f'<div class="card reveal"><h3>{esc(h)}</h3><p>{esc(t)}</p></div>' for h, t in city_insights(c))
    towns = "".join(f"<li>{esc(t)}</li>" for t in c["nearby"])
    lic = TDLR_COUNTY.get(c["county"])
    lic_html = f'<p class="clic"><b>{lic}</b> businesses hold an active Texas A/C contractor license in {esc(c["county"])} (TDLR records, Oct 2026). That\'s who you\'re up against on the map.</p>' if lic else ""
    others = [o for o in CITIES if o["slug"] != c["slug"]]
    near = "".join(f'<a href="{u(city_path(o))}">{esc(o["name"])}</a>' for o in others)
    body = f"""<section class="page-head city-head"><div class="wrap">
  <div class="crumbs"><a href="{u('')}">Home</a> / <a href="{u('locations')}">Locations</a> / <a href="{u('hvac-marketing-texas')}">Texas</a> / {esc(c['name'])}</div>
  <span class="eyebrow">{esc(c['county'])} · {esc(c['metro'])}</span>
  <h1 style="max-width:20ch">HVAC marketing in {esc(c['name'])}, Texas.</h1>
  <p class="lede">When it's {round(c['july_high_f'])}° in July, a {esc(c['name'])} homeowner with a dead AC calls the first shop that shows up and answers. We make sure that's you: a fast site, a Google profile that's actually run, and every missed call texted back in 60 seconds.</p>
  {url_form()}
</div></section>
<section class="section" style="padding-top:12px"><div class="wrap">
  <div class="cfacts reveal">{fact_html}</div>
  <p class="csrc">Population: 2020 U.S. Census. Climate: {esc(station)} normals. Both as published on Wikipedia.</p>
</div></section>
<section class="section alt"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">{esc(c['name'])} market</span><h2>What {esc(c['name'])}'s weather means for your marketing.</h2><p class="lede">{esc(c['one_fact'])}</p></div>
  <div class="grid two">{ins}</div>
  {lic_html}
</div></section>
<section class="section"><div class="wrap split">
  <div><span class="eyebrow">Service areas</span><h2>A page for every town you really serve.</h2><p class="lede">Google shows the shops closest to the person searching. Real town pages, with your work and reviews from that town, stretch your reach past your own zip code.</p></div>
  <div class="card"><h3>Around {esc(c['name'])}</h3><ul class="ticks town-list">{towns}</ul><p class="muted" style="font-size:.9rem">We only build pages for towns you actually take calls in.</p></div>
</div></section>
<section class="section alt"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">The method</span><h2>Answer. Rank. Repeat.</h2><p class="lede">The same three jobs, run for {esc(c['name'])} shops every day.</p></div>
  {method_block()}
</div></section>
{report_card(f"How does your shop stack up in {c['name']}?")}
<section class="section"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Texas</span><h2>Other Texas markets</h2></div>
  <div class="city-links">{near}</div>
</div></section>
"""
    return page(city_path(c), f"HVAC marketing in {c['name']}, TX", f"Websites, Google profiles and missed-call text-back for {c['name']}, Texas HVAC companies. July highs average {deg(c['july_high_f'])}; here's what that means for your marketing.", body)


def city_cards(cities):
    return "".join(f'<a class="city-card" href="{u(city_path(c))}"><b>{esc(c["name"])}</b><span>{deg(c["july_high_f"])} July high · pop. {fnum(c["population_2020"])}</span></a>' for c in cities)


def texas_page():
    hottest = max(CITIES, key=lambda c: c["july_high_f"] or 0)
    coldest = min(CITIES, key=lambda c: c["jan_low_f"] if c["jan_low_f"] is not None else 99)
    body = f"""<section class="page-head"><div class="wrap">
  <div class="crumbs"><a href="{u('')}">Home</a> / <a href="{u('locations')}">Locations</a> / Texas</div>
  <span class="eyebrow">Texas · Where we started</span>
  <h1 style="max-width:20ch">HVAC marketing for Texas contractors.</h1>
  <p class="lede">{fnum(TX_POP)} Texans, and summer runs half the year. We're based in Waco and built this for Texas heat first: every missed call texted back, a fast site and a Google profile that wins the map.</p>
  {url_form()}
</div></section>
<section class="section" style="padding-top:12px"><div class="wrap">
  <h2 class="sr-only">Why Texas is different</h2>
  <div class="grid three">
    <div class="card reveal"><h3>One state, very different weather</h3><p>July highs average {deg(hottest['july_high_f'])} in {esc(hottest['name'])}, while January lows average {deg(coldest['jan_low_f'])} in {esc(coldest['name'])}. Your site should talk about the weather your customers actually live with.</p></div>
    <div class="card reveal"><h3>Freezes happen too</h3><p>The February 2021 winter storm showed how fast heating calls can pile up in a state built for cooling. Heat pump and furnace pages pay off even here.</p></div>
    <div class="card reveal"><h3>Built for Texas rules</h3><p>Texting customers is set up the right way: carrier registration and opt-outs on every message. And we never cold text or cold call, in line with Texas law.</p></div>
  </div>
</div></section>
<section class="section alt"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">Texas markets</span><h2>Pick your city.</h2><p class="lede">Each page shows that market's weather and what it means for your marketing.</p></div>
  <div class="city-grid">{city_cards(CITIES)}</div>
</div></section>
{report_card("See how your shop stacks up in your Texas town.")}
"""
    return page("hvac-marketing-texas", "HVAC marketing in Texas", "Websites, Google profiles and missed-call text-back for Texas HVAC contractors, from Houston to El Paso.", body)


def locations_page():
    body = f"""<section class="page-head"><div class="wrap">
  <div class="crumbs"><a href="{u('')}">Home</a> / Locations</div>
  <span class="eyebrow">Coast to coast</span>
  <h1 style="max-width:20ch">HVAC marketing, built in Texas, for shops everywhere.</h1>
  <p class="lede">Everything we do works from anywhere: your site, your Google profile and your lead system. We started in Texas and add local market pages state by state.</p>
  {url_form()}
</div></section>
<section class="section" style="padding-top:12px"><div class="wrap">
  <div class="loc-state reveal"><div><span class="eyebrow">Live now</span><h2><a href="{u('hvac-marketing-texas')}">Texas</a></h2><p class="muted">{len(CITIES)} markets · {fnum(TX_POP)} people</p></div>
  <div class="city-grid">{city_cards(CITIES)}</div></div>
  <div class="loc-next reveal"><h3>Outside Texas?</h3><p>We already work with HVAC companies in any state. Local market pages for your state are on the way; the report card works for any town today.</p><a class="btn btn-ghost btn-small" href="#report-card">Grade my shop</a></div>
</div></section>
{report_card()}
"""
    return page("locations", "HVAC marketing locations", "HVAC marketing for contractors across the U.S., starting with Texas markets from Houston to El Paso.", body)


def locations_band():
    top = [c for c in CITIES if c["slug"] in ("houston", "dallas", "san-antonio", "austin", "fort-worth", "el-paso", "waco", "killeen", "temple", "lubbock", "corpus-christi", "college-station")]
    chips = "".join(f'<a href="{u(city_path(c))}">{esc(c["name"])}</a>' for c in top)
    return f"""<section class="section"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">Coast to coast</span><h2>Built in Texas. Working everywhere.</h2><p class="lede">Local market pages for every city we serve, starting in Texas.</p></div>
  <div class="city-links">{chips}<a class="all" href="{u('locations')}">All locations →</a></div>
</div></section>"""


# ---- Guides ---------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guides import GUIDES, UPDATED as GUIDES_UPDATED, AUTHOR as GUIDES_AUTHOR
from niches import NICHES
import re as _re


def guide_path(slug):
    return "guide-" + slug


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace("</", "<\\/") + "</script>"


def _strip(html):
    return _re.sub(r"<[^>]+>", "", html).replace("&amp;", "&")


def faq_ld(items):
    return ld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a_}} for q, a_ in items]})


def org_ld():
    return ld({"@context": "https://schema.org", "@type": "ProfessionalService", "name": BRAND, "url": f"https://{DOMAIN}/",
               "email": EMAIL, "description": "Websites, Google Business Profile management, missed-call text-back and review requests for HVAC contractors.",
               "address": {"@type": "PostalAddress", "addressLocality": "Waco", "addressRegion": "TX", "addressCountry": "US"},
               "areaServed": "US", "slogan": TAGLINE})


def _links(text):
    return _re.sub(r"\{u:([a-z0-9-]*)\}", lambda m: u(m.group(1)), text)


def guide_block(b):
    kind = b[0]
    if kind == "p":
        return f"<p>{_links(b[1])}</p>"
    if kind in ("ul", "ol"):
        cls = ' class="ticks"' if kind == "ul" else ""
        return f"<{kind}{cls}>" + "".join(f"<li>{_links(x)}</li>" for x in b[1]) + f"</{kind}>"
    if kind == "table":
        head, *rows = b[1]
        th = "".join(f"<th>{x}</th>" for x in head)
        tr = "".join("<tr>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>" for r in rows)
        return f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'
    if kind == "note":
        return f'<p class="g-note">{_links(b[1])}</p>'
    if kind == "cta":
        return f'<div class="g-cta"><div><b>See how your shop stacks up.</b><p>Free report card: your Google profile, reviews, website and listings graded against the shops near you.</p></div><a class="btn btn-primary" href="{u("report-card")}">Get my report card <span class="arrow">→</span></a></div>'
    return ""


def guide_page(g):
    toc = "".join(f'<li><a href="#s{n}">{esc(h)}</a></li>' for n, (h, _) in enumerate(g["sections"]))
    secs = "".join(f'<h2 id="s{n}">{esc(h)}</h2>' + "".join(guide_block(b) for b in blocks) for n, (h, blocks) in enumerate(g["sections"]))
    take = "".join(f"<li>{esc(t)}</li>" for t in g["takeaways"])
    src = "".join(f'<li><a href="{esc(url)}" rel="noopener">{esc(lbl)}</a></li>' for lbl, url in g["sources"])
    rel = [x for x in GUIDES if x["slug"] in g["related"]]
    rel_html = "".join(f'<a class="card guide-card" href="{u(guide_path(x["slug"]))}"><span class="eyebrow">{x["read"]} min read</span><h3>{esc(x["title"])}</h3><p>{esc(x["desc"])}</p></a>' for x in rel)
    body = f"""<section class="page-head"><div class="wrap g-wrap">
  <div class="crumbs"><a href="{u('')}">Home</a> / <a href="{u('guides')}">Guides</a> / {esc(g['short'])}</div>
  <span class="eyebrow">Guide · {g['read']} min read</span>
  <h1>{esc(g['title'])}</h1>
  <p class="lede">{esc(g['desc'])}</p>
  <p class="g-meta">By {esc(GUIDES_AUTHOR)} · Updated {GUIDES_UPDATED}</p>
</div></section>
<section class="section" style="padding-top:0"><div class="wrap g-wrap">
  <div class="g-take"><h2>Key takeaways</h2><ul class="ticks">{take}</ul></div>
  <nav class="g-toc" aria-label="In this guide"><b>In this guide</b><ol>{toc}</ol></nav>
  <article class="g-body">{secs}
    <h2>Questions</h2>{faq(g['faq'])}
    <h2>Sources</h2><ul class="g-src">{src}</ul>
  </article>
</div></section>
<section class="section alt"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Keep reading</span><h2>Related guides</h2></div>
  <div class="grid two">{rel_html}</div>
</div></section>
"""
    art = ld({"@context": "https://schema.org", "@type": "Article", "headline": g["title"], "description": g["desc"],
              "author": {"@type": "Person", "name": GUIDES_AUTHOR.split(",")[0]}, "publisher": {"@type": "Organization", "name": BRAND},
              "dateModified": "2026-10-12", "mainEntityOfPage": f"https://{DOMAIN}/{guide_path(g['slug'])}"})
    return page(guide_path(g["slug"]), g["title"], g["desc"], body, extra_head=art + faq_ld(g["faq"]), has_form=False)


def niche_page(n):
    setup = "".join(f'<div class="card reveal"><h3>{esc(h)}</h3><p>{esc(t)}</p></div>' for h, t in n["setup"])
    others = "".join(f'<a class="card guide-card" href="{u(o["slug"])}"><span class="eyebrow">Who we help</span><h3>{esc(o["name"])}</h3><p>{esc(o["nav"])}</p></a>' for o in NICHES if o["slug"] != n["slug"])
    ticket, job, label = n["calc"]
    body = f"""<section class="page-head"><div class="wrap">
  <div class="crumbs"><a href="{u('')}">Home</a> / Who we help / {esc(n['name'])}</div>
  <span class="eyebrow">Who we help · {esc(n['name'])}</span>
  <h1 style="max-width:22ch">{esc(n['h1'])}</h1>
  <p class="lede">{esc(n['lede'])}</p>
  {url_form()}
</div></section>
<section class="section"><div class="wrap">{deep_problem("Where shops like yours lose jobs.", n["pains"])}</div></section>
<section class="section alt"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">What we set up</span><h2>Built for how your customers really pick a shop.</h2></div>
  <div class="grid three">{setup}</div>
</div></section>
<section class="section"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">The method</span><h2>Answer. Rank. Repeat.</h2></div>
  {method_block()}
</div></section>
<section class="section alt"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">Break-even</span><h2>Check the math for your shop.</h2></div>
  {calculator(ticket, job, label)}
</div></section>
<section class="section"><div class="wrap g-wrap">
  <div class="section-head"><span class="eyebrow">Questions</span><h2>Common questions</h2></div>
  {faq(n['faq'])}
</div></section>
{report_card()}
<section class="section"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Who we help</span><h2>Other kinds of HVAC shops</h2></div>
  <div class="grid two">{others}</div>
</div></section>
"""
    return page(n["slug"], n["title"], n["desc"], body, extra_head=faq_ld(n["faq"]))


def guides_page():
    cards = "".join(f'<a class="card guide-card reveal" href="{u(guide_path(g["slug"]))}"><span class="eyebrow">{g["read"]} min read</span><h3>{esc(g["title"])}</h3><p>{esc(g["desc"])}</p></a>' for g in GUIDES)
    body = f"""<section class="page-head"><div class="wrap">
  <div class="crumbs"><a href="{u('')}">Home</a> / Guides</div>
  <span class="eyebrow">Guides</span>
  <h1 style="max-width:20ch">Straight answers for HVAC owners.</h1>
  <p class="lede">How the map works, how to get reviews the right way, what marketing really costs. Every number has a source. No email needed to read any of it.</p>
</div></section>
<section class="section" style="padding-top:12px"><div class="wrap">
  <h2 class="sr-only">All guides</h2>
  <div class="grid two">{cards}</div>
</div></section>
{report_card("Rather have it checked for you?")}
"""
    return page("guides", "Guides for HVAC owners", "Sourced, plain-English guides on Google rankings, reviews, websites, texting rules and marketing costs for HVAC companies.", body)


def sitemap_xml(paths):
    urls = "".join(f"<url><loc>https://{DOMAIN}/{p_}</loc><lastmod>2026-10-12</lastmod></url>" for p_ in paths)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n'


# ---- Pages -----------------------------------------------------------------------
def home():
    body = f"""<section class="hero"><div class="hero-grid-bg" aria-hidden="true"></div><div class="wrap hero-grid">
  <div>
    <span class="chip-top"><i>❄</i>Built only for HVAC contractors</span>
    <h1>Every call answered. <span class="grad">Every job booked.</span></h1>
    <p class="lede">We build your website, run your Google profile and text back every missed call in 60 seconds, guaranteed. Start with a free report card on how you stack up locally.</p>
    {url_form()}
    <div class="hero-points"><span>Live in 14 days</span><span>We run it for you</span><span>You own everything</span></div>
    <p class="hero-alt">Rather talk first? <a href="{esc(call_link())}">Book a 15-minute call</a></p>
  </div>
  {hero_visual()}
</div></section>
{works_with()}
<div class="wrap terms-wrap">{terms_strip()}</div>

<section class="section"><div class="wrap">
  <div class="section-head center reveal"><span class="eyebrow">What you get</span><h2>Fast. Found. Booked.</h2><p class="lede">Three things decide who gets the job when a homeowner's AC quits. We handle all three.</p></div>
  {pillars()}
</div></section>

<section class="section alt"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">Sounds familiar?</span><h2>The phone rings when you can't answer it.</h2></div>
  {pains_grid()}
</div></section>

<section class="section" id="method"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">The method</span><h2>Answer. Rank. Repeat.</h2><p class="lede">Three jobs, run for you every day, on every plan. Each one feeds the next.</p></div>
  {method_block()}
  <p style="margin-top:34px"><a class="btn btn-ghost" href="{u('method')}">See the full method <span class="arrow">→</span></a></p>
</div></section>

<section class="section alt"><div class="wrap">
  <div class="section-head center reveal"><span class="eyebrow">What runs behind it</span><h2>One system. Every piece working.</h2><p class="lede">Your site, your Google profile and your lead system, built once and run for you. Your office just answers the texts.</p></div>
  {bento()}
</div></section>

<section class="section" id="tech"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">The tech</span><h2>Built fast, on purpose.</h2><p class="lede">A slow site loses the homeowner before the page loads. Here's this site's own score from Google's test.</p></div>
  {tech()}
</div></section>

<section class="section alt"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">The free report card</span><h2>Where are you losing calls?</h2><p class="lede">We check the four things that decide who a homeowner calls, and grade you against the HVAC shops people find near you.</p></div>
  {rc_learn()}
  {rc_how()}
</div></section>

{report_card()}

<section class="section alt"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">Your first 90 days</span><h2>Live in 14 days. A plan for the next 90.</h2><p class="lede">No mystery months. Here's what happens, and who does what.</p></div>
  {first_90()}
  {roles_split()}
</div></section>

<section class="section" style="padding-top:24px"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">Guarantees</span><h2>We guarantee what we control.</h2></div>
  {promise()}
  <div style="margin-top:28px">{ownership()}</div>
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">Is this for you?</span><h2>Who we work with, and who we don't.</h2></div>
  {fit()}
</div></section>

<section class="section alt" id="pricing"><div class="wrap">
  <div class="section-head center reveal"><span class="eyebrow">Pricing</span><h2>Pick a plan. Go live in 14 days.</h2><p class="lede">Every plan texts back every missed call. Monthly billing starts at launch, not at signing.</p></div>
  {plans_cards()}
</div></section>

<section class="section"><div class="wrap" style="max-width:900px">
  <div class="section-head reveal"><span class="eyebrow">Questions</span><h2>Straight answers.</h2></div>
  {faq(COMMON_FAQ)}
</div></section>

<section class="section alt"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">Guides</span><h2>Straight answers, with sources.</h2></div>
  <div class="grid three">{"".join(f'<a class="card guide-card reveal" href="{u(guide_path(g["slug"]))}"><span class="eyebrow">{g["read"]} min read</span><h3>{esc(g["title"])}</h3></a>' for g in GUIDES[:3])}</div>
  <p style="margin-top:22px"><a class="btn btn-ghost" href="{u('guides')}">All guides <span class="arrow">→</span></a></p>
</div></section>

{locations_band()}

<section class="section final"><div class="wrap">
  <span class="eyebrow">Free report card</span>
  <h2>See where you stand <span class="grad">before you spend a dollar.</span></h2>
  {url_form("Get my report card")}
  <p class="rc-call">Rather talk? <a href="{esc(call_link())}">Book a 15-minute call</a></p>
</div></section>
"""
    return page("", f"HVAC websites and lead systems | {BRAND}",
                "Websites, Google profiles and missed-call text-back for HVAC companies. Every missed call texted back in 60 seconds, guaranteed.", body,
                extra_head=org_ld() + faq_ld(COMMON_FAQ))


def method_page():
    phases = []
    for n, (name, line, items, close) in enumerate(METHOD):
        lis = "".join(f"<li>{esc(x)}</li>" for x in items)
        alt = " alt" if n == 1 else ""
        phases.append(f"""<section class="section{alt}"><div class="wrap split">
  <div><span class="eyebrow">Phase 0{n+1}</span><h2>{name}.</h2><p class="lede">{esc(line)}</p><p class="phase-close">{esc(close)}</p></div>
  <div class="card"><ul class="ticks">{lis}</ul></div>
</div></section>""")
    body = f"""<section class="page-head"><div class="wrap">
  <div class="crumbs"><a href="{u('')}">Home</a> / The method</div>
  <span class="eyebrow">The method</span>
  <h1>Answer. Rank. Repeat.</h1>
  <p class="lede">Most agencies sell you a website, or ads, or software. We run the three jobs that actually fill an HVAC schedule, as one system, on every plan.</p>
</div></section>
<section class="section" style="padding-top:0"><div class="wrap"><h2 class="sr-only">The three phases</h2>{method_block()}</div></section>
{"".join(phases)}
<section class="section"><div class="wrap split">
  <div><span class="eyebrow">Every plan</span><h2>Watch it work on your live dashboard.</h2><p class="lede">Calls, texts, booked jobs and reviews, updated as they happen.</p></div>
  {dashboard()}
</div></section>
<section class="section alt"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Your first 90 days</span><h2>What happens after you sign.</h2></div>
  {first_90()}
  {roles_split()}
</div></section>
{report_card("See where you stand on all three.")}
"""
    return page("method", "The method: Answer, Rank, Repeat", "How we answer every call, rank you on Google and turn every job into the next one.", body)


TRADE_CONTENT = {
    "hvac": {
        "name": "HVAC", "noun": "HVAC company", "plural": "HVAC companies", "search": "AC repair near me", "ticket": 350, "job": 9000, "job_label": "system replacement",
        "h1": "More booked service calls for Central Texas HVAC companies.",
        "lede": "When it's 104 in July, the homeowner calls three shops and books the first one that answers. We make sure that's you, even when your techs are in an attic.",
        "pains": [
            ("The summer rush outruns your phones", "Calls stack up on the hottest days of the year, exactly when your office can't keep up. Every missed call gets a text back in seconds."),
            ("Tune-up season comes and goes", "Spring and fall are when past customers should hear from you. We run the seasonal tune-up campaign so the schedule fills before the rush."),
            ("Maintenance plans don't renew themselves", "Reminders go out before plans lapse, with a link to renew."),
            ("Big franchises and lead sellers crowd the map", "A complete Google profile, real service-area pages and a steady stream of reviews help a local shop hold its ground."),
            ("Replacement quotes go quiet", "A $9,000 system is a big decision. Estimate follow-up keeps going until the homeowner books or says no, with a financing link if you offer one."),
        ],
        "scenario": "A homeowner in Temple calls at 4:55 on a Friday in August. Your office just closed. Within seconds they get a text from you asking what's wrong. By the time they'd have dialed the next shop, they've picked a Saturday window.",
        "services": ["AC repair", "Heating repair", "System installs and replacements", "Maintenance plans", "Indoor air quality", "Financing"],
    },
    "plumbing": {
        "name": "Plumbing", "noun": "plumbing company", "plural": "plumbing companies", "search": "plumber near me", "ticket": 300, "job": 2500, "job_label": "water heater install",
        "h1": "More booked jobs for Central Texas plumbing companies.",
        "lede": "A burst pipe doesn't wait for business hours. The plumber who answers first gets the job, and usually the customer for life.",
        "pains": [
            ("Emergency calls come at the worst times", "Nights, weekends and while you're under a slab. Every missed call gets a text back, so the homeowner knows help is coming."),
            ("Water heater and repipe quotes stall", "Estimate follow-up keeps going until the job is booked or the customer says no."),
            ("One-time customers never hear from you again", "Seasonal reminders, like before the first freeze, bring past customers back."),
            ("Reviews come in slowly", "A review request goes out after every finished job, and every review gets a reply."),
            ("Your site doesn't list what you actually do", "Drain cleaning, water heaters, slab leaks, sewer lines: each gets its own page, so you show up for the search."),
        ],
        "scenario": "A homeowner in Belton finds water under the kitchen sink at 9 PM and calls you. You're on another job. They get a text back right away, send a photo, and book you for first thing in the morning.",
        "services": ["Emergency plumbing", "Drain cleaning", "Water heaters", "Leak detection", "Sewer and slab work", "Repiping"],
    },
    "roofing": {
        "name": "Roofing", "noun": "roofing company", "plural": "roofing companies", "search": "roofer near me", "ticket": 450, "job": 14000, "job_label": "roof replacement",
        "h1": "More booked inspections for Central Texas roofing companies.",
        "lede": "After a hailstorm, every homeowner on the street calls around at once. The roofer who answers and follows up wins the inspection, and the job.",
        "pains": [
            ("Storm days flood your phones", "When hail hits, calls come in faster than anyone can answer. Every missed call gets a text back with a link to book an inspection."),
            ("Long sales cycles lose people", "Between the inspection, the adjuster and the decision, homeowners drift. Follow-up keeps going until they sign or say no."),
            ("Out-of-town crews look just like you online", "A strong Google profile, real local reviews and service-area pages show you're the roofer who'll still be here next year."),
            ("Estimates need signatures", "Send the estimate, get it signed and share a financing link, all from the same inbox."),
            ("Reviews don't show your work", "Review requests go out after every job, and every review gets a reply."),
        ],
        "scenario": "Hail moves through Hewitt on a Tuesday afternoon. Forty calls come in by evening. Every one you miss gets a text with a link to book an inspection, so your schedule fills without anyone sitting on the phone.",
        "services": ["Roof replacement", "Storm and hail damage", "Roof repair", "Inspections", "Gutters", "Insurance claim help"],
    },
}


def trade_page(key):
    t = TRADE_CONTENT[key]
    pains = "".join(f'<div class="pain"><div><h3>{esc(h)}</h3><p>{esc(p)}</p></div></div>' for h, p in t["pains"])
    services = "".join(f"<li>{esc(s)}</li>" for s in t["services"])
    body = f"""<section class="page-head"><div class="wrap split">
  <div>
    <div class="crumbs"><a href="{u('')}">Home</a> / Trades / {t['name']}</div>
    <span class="eyebrow">For {t['plural']}</span>
    <h1>{esc(t['h1'])}</h1>
    <p class="lede">{esc(t['lede'])}</p>
    <div class="actions" style="display:flex;gap:12px;flex-wrap:wrap;margin-top:26px"><a class="btn btn-primary" href="#report-card">Grade my {t['noun']}</a><a class="btn btn-ghost" href="{u('plans')}">See plans</a></div>
  </div>
  <div class="scenario"><span class="eyebrow">What it looks like</span><p style="margin:0">{esc(t['scenario'])}</p></div>
</div></section>

<section class="section" style="padding-top:24px"><div class="wrap split">
  <div><span class="eyebrow">Where you lose jobs</span><h2>What we fix for {t['plural']}</h2><p class="lede">The same few gaps cost most shops the most work.</p></div>
  <div class="pains">{pains}</div>
</div></section>

<section class="section ink"><div class="wrap split">
  <div>
    <span class="eyebrow">Your website</span>
    <h2>Pages for the jobs you want.</h2>
    <p class="lede">People search for the job, not your name. Each service gets its own page, and each town you really serve gets a page with real local detail, not a copy with the town swapped.</p>
  </div>
  <div class="card"><h3>Typical service pages</h3><ul class="ticks">{services}</ul><p class="muted" style="font-size:.9rem">Plus a page for each town you serve, written from your real work there.</p></div>
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Break-even</span><h2>How many calls pay for it?</h2></div>
  {calculator(t['ticket'], t['job'], t['job_label'])}
</div></section>

{report_card(f"Get your {t['name']} report card", trade=t['name'])}
"""
    return page(key, f"{t['name']} marketing in Central Texas",
                f"Websites, Google profiles and missed-call text-back for {t['plural']} in Central Texas.", body)


OFFER_CONTENT = {
    "website": {
        "title": "Website", "h1": "A website built to book service calls.",
        "lede": "Not a brochure. Every page is built around a job people search for, with a clear way to book on every screen.",
        "cards": [
            ("web", "Service pages", "A page for each service you want more of, written for how homeowners search."),
            ("pin", "Service-area pages", "Pages for the towns you really serve, with real local detail. No copy-and-paste city pages."),
            ("cal", "Book a service call", "A booking form on every page, into our calendar or straight into ServiceTitan, Housecall Pro or Jobber."),
            ("chat", "AI web chat", "Answers common questions and captures the lead after hours."),
            ("chart", "Fast and mobile first", "Most of your visitors are on a phone. The site loads fast and works with one thumb."),
            ("star", "Reviews on the page", "Your real Google reviews shown where people decide."),
        ],
        "list": ["Live within 14 days of getting your content", "Hosting, security and updates included", "Edits each month, written on your plan", "You own your domain"],
    },
    "marketing": {
        "title": "Google &amp; reviews", "h1": "Get found on Google, and stay at the top.",
        "lede": "Most local jobs start with a search and a look at the map. We keep your Google presence complete, active and full of fresh reviews.",
        "cards": [
            ("pin", "Google Business Profile", "Right categories, every service listed, current hours, photos and regular posts."),
            ("star", "Review requests", "Sent automatically when a job is marked done, so asking never depends on remembering."),
            ("chat", "Review replies", "Every review gets a reply, good or bad, in your voice."),
            ("list", "Directory listings", "Your name, address and phone kept the same on Facebook, Yelp, BBB, Angi, Nextdoor and more."),
            ("cal", "Seasonal campaigns", "Tune-up and reminder campaigns to past customers before the busy season."),
            ("chart", "Monthly statement", "Calls, texts, booked jobs and new reviews, in one page each month."),
        ],
        "list": ["We ask every customer for a review and never filter out unhappy ones (Google doesn't allow it)", "Map spam reports on fake competitor listings", "Call tracking by source", "Paid ads available later as an add-on", "No promises of rankings, only of the work"],
    },
    "app": {
        "title": "Lead system", "h1": "Every call, text and form in one inbox.",
        "lede": "The lead system behind it all. It texts back missed calls, follows up on estimates and keeps your whole team on the same page.",
        "cards": [
            ("phone", "Missed-call text-back", "Every call you can't pick up gets a text in seconds, with your name on it."),
            ("chat", "Shared inbox app", "Owner, office and techs see every call, text, chat and form on their phones."),
            ("cal", "Estimate follow-up", "Keeps following up until the job is booked or the customer says no."),
            ("list", "Reminders and on-the-way texts", "Appointment reminders and \"your tech is on the way\" texts."),
            ("star", "E-sign and financing", "Send an estimate, get it signed and share a financing link from the same thread."),
            ("loop", "Maintenance plan reminders", "Customers hear from you before plans lapse."),
        ],
        "list": ["Keep your existing phone number", "Works alongside your field-service software", "Normal texting and calling included", "AI phone answering available as an add-on"],
    },
}


# Extra depth for the three offer pages (after studying rsgonzales.com service pages).
OFFER_DEEP = {
    "website": {
        "problem": ("Why most HVAC websites never make the phone ring", [
            ("Slow on a phone", "Most homeowners search on a phone. If the page takes four seconds, they're already calling the next shop."),
            ("The number is hard to find", "No tap-to-call button at the top of every screen means lost emergency calls."),
            ("One page for everything", "Without a page for AC repair, heating repair and installs, Google has nothing to rank you for."),
            ("Built once, never touched", "Hours change, services change, the site doesn't. Google notices."),
        ]),
        "personas": ("One site, three kinds of customer", "Every HVAC site has to serve three people at once. Ours is built around all three.", [
            ("phone", "The emergency caller", "AC quit at 9 PM in July. They need your number in one tap and an answer even after hours.", ["Tap-to-call on every screen", "Missed calls texted back in seconds", "Open-hours and emergency service up top"]),
            ("star", "The big-install buyer", "Shopping a $9,000 system. They read reviews, compare and want to know you're not going to upsell them.", ["A page for each system type", "Real reviews next to the quote form", "Financing link if you offer it"]),
            ("search", "The researcher", "Wondering if their unit is worth fixing. They'll come back when it's time to buy.", ["Straight answers to common questions", "Repair or replace guidance", "Tune-up and maintenance plan pages"]),
        ]),
        "timeline": ("Your site, live in 14 days", "You send photos and details. We do the rest.", [
            ("Day 1", "Kickoff", "Your services, towns, hours, photos of your trucks and crew."),
            ("Day 4", "Copy", "We write every page around the jobs you want more of."),
            ("Day 8", "Design review", "You see the full site on your phone and tell us what to change."),
            ("Day 12", "Final checks", "Speed, forms, tap-to-call, tracking and Google setup tested."),
            ("Day 14", "Live", "Launched on your domain, with text-back running behind it."),
        ]),
        "speed": True,
        "faq": [
            ("How long does a new site take?", "14 days from when we get your photos and details. Most of that time is us writing and building; your part is one kickoff call and one review."),
            ("Do I own the website?", "Yes. Your domain is registered in your name and the site's content is yours. If you leave, we hand over the files."),
            ("Can I edit it myself?", "You can, but you don't have to. Send us changes by text or email and they're included in your plan."),
            ("Is it WordPress?", "No. It's pre-built static pages on a global network, so there are no plugins to update and nothing to hack. That's why it loads so fast."),
            ("I already have a site I like. Do I need a new one?", "No. We can add the booking form and lead system to your current site, and the build fee is lower or waived."),
            ("Who writes the pages?", "We do, from your kickoff call. You review everything before it goes live."),
            ("How is this different from Wix or a freelancer?", "A builder gives you a template and leaves the rest to you. A freelancer usually builds and leaves. We build it, keep it updated, connect it to text-back and reviews, and show you the results."),
        ],
    },
    "marketing": {
        "problem": ("Why you show up in one part of town and not another", [
            ("Distance", "Google favors shops close to the person searching. You can't move your shop, but town pages and a complete profile stretch your reach."),
            ("Relevance", "The wrong main category or missing services means Google doesn't know you do the job. This is the fastest fix."),
            ("Prominence", "Reviews, how recent they are, how often you reply and how active your profile is. This is where steady work wins."),
            ("Spam listings", "Fake competitor listings crowd the map. We report them."),
        ]),
        "flow": ("Reviews on autopilot", "A steady flow of new reviews beats a big pile of old ones. Here's how every finished job becomes the next one.", [
            ("Job marked done", "In your field software or our app"),
            ("Text goes out", "A short, friendly ask with your name on it"),
            ("Review posted", "One tap to your Google profile"),
            ("We reply", "In your voice, good or bad"),
        ]),
        "ai": ("Show up when they ask AI, too", "More homeowners are asking ChatGPT, Gemini and Google's AI answers who to call. Those tools lean on the same signals the map does.", ["A complete, consistent Google profile", "The same name, address and phone everywhere", "Clear service and town pages they can read", "Recent reviews that mention the work"]),
        "faq": [
            ("How long until I move up the map?", "Profile fixes can help within weeks. Steady movement usually takes three to six months, longer in a big metro. We show you where you rank on your dashboard."),
            ("How many Google reviews do I need?", "There's no magic number. Recent, steady reviews matter more than a big total."),
            ("What do you do about a bad review?", "Reply calmly and professionally, offer to make it right, and keep good reviews coming so one bad one doesn't define you."),
            ("Do you run Google Ads or Local Services Ads?", "Not yet. Ads work better once calls are answered and your profile is strong, so we start there. Ads are coming as an add-on."),
            ("Can you guarantee I'll be #1?", "No, and be careful with anyone who does. We guarantee the work: a complete profile, review requests after every job and a reply to every review."),
        ],
    },
    "app": {
        "problem": ("Where good HVAC leads slip away", [
            ("Calls missed on the job", "Your tech is in an attic and the office is on another line. Voicemail means the next shop wins."),
            ("Leads in five places", "Calls, texts, web forms, Facebook messages and Google chats, all in different apps."),
            ("Slow follow-up", "A quote sent Tuesday and never chased is a job someone else booked Friday."),
            ("No idea what's working", "Without tracking, you can't tell which calls came from Google and which from the truck wrap."),
        ]),
        "auto": ("Always on, even when you're not", [
            ("Missed call", "Text back in under 60 seconds"),
            ("New web lead", "Instant reply and a link to book"),
            ("Appointment booked", "Reminder the day before, on-the-way text"),
            ("Job marked done", "Review request and thank-you"),
            ("Quiet customer", "Tune-up and maintenance plan reminders"),
        ]),
        "attribution": ("See what's booking your jobs", "Every booked job tagged with where it came from, so you know what to keep paying for.", [("Google map pack", 41), ("Website", 23), ("Repeat customers", 18), ("Referrals", 11), ("Other", 7)]),
        "replaces": True,
        "faq": [
            ("Does it replace ServiceTitan, Housecall Pro or Jobber?", "No. It sits in front of them and catches, answers and follows up on leads. Booked jobs can go straight into your field software."),
            ("Do I keep my phone number?", "Yes. You forward your existing line through the system, so customers keep calling the number they know."),
            ("Is texting customers legal?", "Yes, when it's done right. We register your texting with the carriers and every message carries opt-out instructions. That's part of setup."),
            ("Who sets it up?", "We do. You get the app on your phone already set up, with your messages written and your team added."),
            ("What does it cost?", "It's included in every plan. Normal texting and calling are included; large campaigns beyond your plan are billed at cost."),
        ],
    },
}


def deep_problem(h, items):
    cards = "".join(f'<div class="pain reveal"><div class="x">✕</div><h3>{esc(a_)}</h3><p>{esc(b)}</p></div>' for a_, b in items)
    return f'<div class="section-head reveal"><span class="eyebrow">The problem</span><h2>{esc(h)}</h2></div><div class="pains grid4">{cards}</div>'


def deep_personas(h, lede, items):
    cards = "".join(f'<div class="card persona reveal"><div class="icon">{ICON[i]}</div><h3>{esc(t)}</h3><p>{esc(d)}</p><ul class="ticks">' + "".join(f"<li>{esc(x)}</li>" for x in li) + "</ul></div>" for i, t, d, li in items)
    return f'<div class="section-head reveal"><span class="eyebrow">Who it\'s for</span><h2>{esc(h)}</h2><p class="lede">{esc(lede)}</p></div><div class="grid three">{cards}</div>'


def deep_timeline(h, lede, items):
    lis = "".join(f'<li class="tl reveal"><span class="day">{d}</span><h3>{t}</h3><p>{esc(x)}</p></li>' for d, t, x in items)
    return f'<div class="section-head reveal"><span class="eyebrow">The build</span><h2>{esc(h)}</h2><p class="lede">{esc(lede)}</p></div><ol class="timeline t5">{lis}</ol>'


def deep_flow(h, lede, items):
    lis = "".join(f'<li class="flow-step reveal"><span class="n">{n+1}</span><h3>{esc(a_)}</h3><p>{esc(b)}</p></li>' for n, (a_, b) in enumerate(items))
    return f'<div class="section-head reveal"><span class="eyebrow">Repeat</span><h2>{esc(h)}</h2><p class="lede">{esc(lede)}</p></div><ol class="flow">{lis}</ol>'


def deep_ai(h, lede, items):
    lis = "".join(f"<li>{esc(x)}</li>" for x in items)
    return f"""<div class="split"><div><span class="eyebrow">AI search</span><h2>{esc(h)}</h2><p class="lede">{esc(lede)}</p><p class="muted">Nobody can promise an AI tool will recommend you. We build what they read.</p></div>
<div class="card ai-card"><div class="chat"><div class="msg user">Who's a good AC repair company near me?</div><div class="msg bot">A few well-reviewed options nearby: <b>Your Shop Heating &amp; Air</b> (4.9★, open 24 hours)…</div></div><ul class="ticks" style="margin-top:18px">{lis}</ul><span class="sample-tag" style="position:static">Sample</span></div></div>"""


def deep_auto(h, items):
    rows = "".join(f'<li><span class="trig">{esc(a_)}</span><span class="arrow-r" aria-hidden="true">→</span><span class="act">{esc(b)}</span><span class="on">On</span></li>' for a_, b in items)
    return f'<div class="split"><div><span class="eyebrow">Automations</span><h2>{esc(h)}</h2><p class="lede">Set up for you on day one, written in your voice. Your office only steps in when a customer replies.</p></div><div class="auto-panel reveal"><div class="auto-head"><i></i>Automations · Your Shop Heating &amp; Air</div><ul>{rows}</ul></div></div>'


def deep_attr(h, lede, items):
    mx = max(v for _, v in items)
    rows = "".join(f'<li><span>{esc(k)}</span><div class="attr-bar"><i style="width:{int(v / mx * 100)}%"></i></div><b>{v}%</b></li>' for k, v in items)
    return f'<div class="split"><div><span class="eyebrow">Tracking</span><h2>{esc(h)}</h2><p class="lede">{esc(lede)}</p></div><div class="card attr reveal"><p class="attr-t">Booked jobs by source, last 90 days</p><ul>{rows}</ul><span class="dash-sample">Sample data</span></div></div>'


def offer_deep(key):
    d = OFFER_DEEP.get(key, {})
    out = []
    alt = False
    def sec(inner):
        nonlocal alt
        cls = "section alt" if alt else "section"
        alt = not alt
        out.append(f'<section class="{cls}"><div class="wrap">{inner}</div></section>')
    if "problem" in d: sec(deep_problem(*d["problem"]))
    if "personas" in d: sec(deep_personas(*d["personas"]))
    if "auto" in d: sec(deep_auto(*d["auto"]))
    if "flow" in d: sec(deep_flow(*d["flow"]))
    if "ai" in d: sec(deep_ai(*d["ai"]))
    if "attribution" in d: sec(deep_attr(*d["attribution"]))
    if d.get("replaces"): sec(replaces())
    if d.get("speed"): sec('<div class="section-head reveal"><span class="eyebrow">Speed</span><h2>Slow sites lose jobs.</h2><p class="lede">This is how our own site scores on Google\'s test. Yours is built the same way.</p></div>' + tech())
    if "timeline" in d: sec(deep_timeline(*d["timeline"]))
    return "".join(out)


def offer_faq(key):
    items = OFFER_DEEP.get(key, {}).get("faq")
    if not items:
        return ""
    return f'<section class="section"><div class="wrap" style="max-width:900px"><div class="section-head"><span class="eyebrow">Questions</span><h2>{OFFER_CONTENT[key]["title"]} questions</h2></div>{faq(items)}</div></section>'


def offer_page(key):
    o = OFFER_CONTENT[key]
    cards = "".join(f'<div class="card reveal"><div class="icon">{ICON[i]}</div><h3>{esc(h)}</h3><p>{esc(p)}</p></div>' for i, h, p in o["cards"])
    ticks = "".join(f"<li>{esc(x)}</li>" for x in o["list"])
    body = f"""<section class="page-head"><div class="wrap">
  <div class="crumbs"><a href="{u('')}">Home</a> / Offerings / {o['title']}</div>
  <span class="eyebrow">{o['title']}</span>
  <h1 style="max-width:18ch">{esc(o['h1'])}</h1>
  <p class="lede">{esc(o['lede'])}</p>
</div></section>
<section class="section" style="padding-top:12px"><div class="wrap">
  {terms_strip()}
  <h2 class="sr-only">What's included</h2>
  <div class="grid three">{cards}</div>
</div></section>
<section class="section ink"><div class="wrap split">
  <div><span class="eyebrow">Also included</span><h2>The details that matter.</h2><p class="lede">Part of every plan. Higher plans add more of our time, not more software.</p></div>
  <div class="card"><ul class="ticks">{ticks}</ul><a class="more" href="{u('plans')}">Compare plans →</a></div>
</div></section>
{offer_deep(key)}
{report_card()}
{offer_faq(key)}
"""
    items = OFFER_DEEP.get(key, {}).get("faq")
    return page(key, f"{_strip(o['title'])} for HVAC companies", o["lede"], body, extra_head=faq_ld(items) if items else "")


def rc_samples():
    # Mirrors what the grader really reports (grader/hvac-rubric.md). Sample numbers, labeled.
    return """<div class="rcs">
  <div class="rcs-card rcs-wide reveal">
    <div class="rcs-top"><span>Overall</span><span class="sample-tag" style="position:static">Sample</span></div>
    <div class="rcs-grade"><div class="overall">C</div><div><b>Your Shop Heating &amp; Air · Waco, TX</b><p>Your reviews are strong, but your website is holding you back. Start by adding pages for AC repair and installs so Google has something to rank.</p></div></div>
    <div class="rcs-areas"><span>Google profile <b class="g-b">B</b></span><span>Reviews <b class="g-b">B−</b></span><span>Website <b class="g-d">D</b></span><span>Listings <b class="g-c">C</b></span></div>
  </div>
  <div class="rcs-card reveal">
    <div class="rcs-top"><span>Google profile</span><b class="g-b">B</b></div>
    <p class="rcs-sub">Where you show up in two real searches</p>
    <ul class="rcs-rows"><li><span>"HVAC near Waco, TX"</span><b>#7</b></li><li><span>"AC repair Waco, TX"</span><b>#4</b></li><li><span>Photos added by you</span><b>3</b></li><li><span>Main category</span><b class="ok">HVAC contractor</b></li></ul>
    <p class="rcs-fix"><b>Fix first:</b> add at least 10 photos of your crew and jobs.</p>
  </div>
  <div class="rcs-card reveal">
    <div class="rcs-top"><span>Reviews</span><b class="g-b">B−</b></div>
    <p class="rcs-sub">You vs the top 3 shops in your search</p>
    <div class="rcs-vs"><span>Rating</span><div><i style="width:92%"></i><em>4.6</em></div><div class="them"><i style="width:96%"></i><em>4.8</em></div></div>
    <div class="rcs-vs"><span>Reviews</span><div><i style="width:21%"></i><em>64</em></div><div class="them"><i style="width:100%"></i><em>310</em></div></div>
    <p class="rcs-legend"><i></i>You <i class="them"></i>Top 3 average</p>
    <p class="rcs-fix"><b>Fix first:</b> your newest review is 41 days old. Ask after every job.</p>
  </div>
  <div class="rcs-card reveal">
    <div class="rcs-top"><span>Website</span><b class="g-d">D</b></div>
    <p class="rcs-sub">Google's speed test and the pages that bring searches</p>
    <ul class="rcs-rows"><li><span>Speed on a phone</span><b class="bad">38 / 100</b></li><li><span>Service pages found</span><b class="bad">2 of 8</b></li><li><span>Town pages</span><b class="bad">0</b></li><li><span>Tap-to-call number</span><b class="ok">Yes</b></li></ul>
    <p class="rcs-fix"><b>Fix first:</b> add pages for AC repair, installs and maintenance plans.</p>
  </div>
  <div class="rcs-card reveal">
    <div class="rcs-top"><span>Listings</span><b class="g-c">C</b></div>
    <p class="rcs-sub">Directories a web search finds you on</p>
    <div class="rcs-dirs"><span class="ok">Facebook</span><span class="ok">Yelp</span><span class="ok">Angi</span><span>BBB</span><span>Nextdoor</span><span>Thumbtack</span><span>HomeAdvisor</span></div>
    <ul class="rcs-rows"><li><span>Phone matches your site</span><b class="ok">Yes</b></li></ul>
    <p class="rcs-fix"><b>Fix first:</b> claim your BBB and Nextdoor listings.</p>
  </div>
</div>"""


def report_card_page():
    body = f"""<section class="page-head"><div class="wrap">
  <div class="crumbs"><a href="{u('')}">Home</a> / Free report card</div>
  <span class="eyebrow">Free report card</span>
  <h1 style="max-width:20ch">Find out why the phone isn't ringing.</h1>
  <p class="lede">We grade your Google profile, reviews, website and listings against the HVAC shops people find near you. Free, in your inbox in about five minutes, and nobody will call you.</p>
  <p style="margin-top:26px"><a class="btn btn-primary" href="#report-card">Get my report card <span class="arrow">→</span></a> <a class="btn btn-ghost" href="#sample">See a sample</a></p>
</div></section>
<section class="section" style="padding-top:12px"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">What you'll learn</span><h2>Four grades. One list of what to fix first.</h2></div>
  {rc_learn()}
</div></section>
<section class="section alt" id="sample"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">Sample</span><h2>Here's what lands in your inbox.</h2><p class="lede">A real report uses your shop, your town and your competitors. This one is made up so you can see the layout.</p></div>
  {rc_samples()}
</div></section>
<section class="section"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">How it works</span><h2>Under a minute for you.</h2></div>
  {rc_how()}
</div></section>
{report_card()}
<section class="section"><div class="wrap split">
  <div><span class="eyebrow">After the report card</span><h2>You've got the grades. Now what?</h2><p class="lede">Some owners fix it themselves, and the report shows exactly where to start. Others hand it to us. Either way, it's yours to keep.</p></div>
  <div class="card"><ul class="ticks"><li>Graded only on what anyone can see in public</li><li>The same facts always give the same grade</li><li>Plain English, no jargon</li><li>Re-grade anytime to see what changed</li></ul><a class="more" href="{esc(call_link())}">Rather talk it through? Book a 15-minute call →</a></div>
</div></section>
"""
    return page("report-card", "Free HVAC marketing report card", "A free report card grading your HVAC company's Google profile, reviews, website and listings against the shops near you.", body)


def plans_page():
    body = f"""<section class="page-head"><div class="wrap">
  <div class="crumbs"><a href="{u('')}">Home</a> / Pricing</div>
  <span class="eyebrow">Pricing</span>
  <h1>Simple pricing. Pick a plan and go live in 14 days.</h1>
  <p class="lede">Every plan texts back every missed call. Bigger plans add pages, towns and campaigns. Monthly billing starts at launch, not at signing.</p>
</div></section>
<section class="section" style="padding-top:12px"><div class="wrap">
  {terms_strip()}
  {plans_cards()}
  <p class="muted" style="margin-top:18px;font-size:.9rem">Founding rate: the first [N] shops keep the annual price on monthly billing, locked for as long as they stay. Normal texting, calling and AI use is included; large campaigns beyond your plan are billed at cost. <span class="tbd">Prices and terms TBD</span></p>
  {addons()}
</div></section>
<section class="section alt"><div class="wrap">{replaces()}</div></section>
<section class="section" style="padding-bottom:0"><div class="wrap">
  {compare()}
</div></section>
<section class="section" style="padding-top:0"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Is this for you?</span><h2>Who we work with, and who we don't.</h2></div>
  {fit()}
</div></section>
<section class="section" style="padding-top:0"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Guarantees</span><h2>We guarantee what we control.</h2></div>
  {promise()}
</div></section>
<section class="section" style="padding-top:0"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Break-even</span><h2>Check the math for your shop.</h2></div>
  {calculator()}
</div></section>
{report_card("Not sure which plan? Start with the report card.")}
<section class="section"><div class="wrap" style="max-width:860px">
  <div class="section-head"><h2>Pricing questions</h2></div>
  {faq(COMMON_FAQ)}
</div></section>
"""
    return page("plans", "Pricing", "HVAC website, Google profile and missed-call text-back plans, billed monthly or annually.", body, extra_head=faq_ld(COMMON_FAQ))


def legal_page(key):
    if key == "privacy":
        title = "Privacy Policy"
        content = f"""
<p>This policy explains what {esc(BRAND)} ("we", "us") collects through this website and our services, and how we use it. Last updated: {LEGAL_UPDATED}.</p>
<h2>What we collect</h2>
<ul>
<li><b>Information you give us.</b> When you request a report card or contact us: your website, business name, the town you serve, first name, email address and phone number.</li>
<li><b>Public business information.</b> To build your report card we look up public information about your business, such as your Google Business Profile, reviews, website and directory listings.</li>
<li><b>Usage information.</b> Basic technical data such as browser type and pages visited. If we add analytics tools such as Google Analytics, they may set cookies to measure how the site is used.</li>
<li><b>Chat and messages.</b> If we add a web chat, we keep the messages you send so we can reply.</li>
</ul>
<h2>How we use it</h2>
<ul>
<li>To create and email your report card and answer your questions.</li>
<li>To send follow-up emails about your report card. You can unsubscribe at any time.</li>
<li>To text you, only if you checked the box agreeing to receive texts.</li>
<li>To protect the site from spam and abuse (for example with Cloudflare Turnstile).</li>
</ul>
<h2>Text messaging</h2>
<p>If you opt in to text messages, we will text you about your report card and our services. Message frequency varies. Message and data rates may apply. Reply STOP to opt out at any time and HELP for help. <b>We do not sell, rent or share your mobile number or text messaging opt-in data with third parties or affiliates for their marketing purposes.</b> Opt-in data and consent are not shared with any third parties, except service providers that deliver messages on our behalf.</p>
<h2>Who we share it with</h2>
<p>We use service providers to run this site and our services, such as hosting (Vercel), email delivery (Resend), spam protection (Cloudflare), our CRM and messaging platform, and scheduling tools. They only use your information to provide services to us. We do not sell your personal information.</p>
<h2>Client customer data</h2>
<p>When we provide services to a business, we handle that business's customer data only on its instructions, never sell it, and notify the business of any breach as required by law.</p>
<h2>How long we keep it</h2>
<p>We keep report card requests and messages for as long as needed to serve you, then delete them. You can ask us to delete your information at any time.</p>
<h2>Your choices</h2>
<p>You can unsubscribe from emails using the link in any email, reply STOP to any text, or email <a href="mailto:{EMAIL}">{EMAIL}</a> to see, correct or delete your information.</p>
<h2>Contact</h2>
<p>{esc(BRAND)}, Waco, Texas. <a href="mailto:{EMAIL}">{EMAIL}</a></p>"""
    else:
        title = "Terms of Service"
        content = f"""
<p>These terms cover your use of this website and the free report card. Client services are covered by a separate signed service agreement. Last updated: {LEGAL_UPDATED}.</p>
<h2>The report card</h2>
<p>The report card is a free assessment based only on public information about your business. It is an opinion, not a guarantee of any result, ranking or number of jobs.</p>
<h2>Text messaging program</h2>
<ul>
<li><b>Program:</b> {esc(BRAND)} report card and service updates.</li>
<li><b>What you'll get:</b> texts about your report card, scheduling a call and our services.</li>
<li><b>Frequency:</b> message frequency varies.</li>
<li><b>Cost:</b> message and data rates may apply.</li>
<li><b>Opt out:</b> reply STOP at any time. You'll get one final message confirming you're unsubscribed.</li>
<li><b>Help:</b> reply HELP or email <a href="mailto:{EMAIL}">{EMAIL}</a>.</li>
<li>Carriers are not liable for delayed or undelivered messages.</li>
</ul>
<h2>What every client agreement includes</h2>
<p>The promises on this website are written into every client service agreement in the same words:</p>
<ul>
<li><b>Ownership:</b> your domain is registered in your name, and your website content, Google Business Profile, reviews, customer list and leads are yours. If you leave, we hand over the site files and help move your phone number.</li>
<li><b>Money-back guarantee:</b> if you're not happy in the first 30 days after launch, tell us and we refund your first month's fee. [Build fee terms TBD]</li>
<li><b>Text-back:</b> every missed call to your forwarded line gets a text back within 60 seconds while the service is active.</li>
<li><b>Launch:</b> your new site goes live within 14 days of receiving your content.</li>
<li><b>Billing:</b> monthly billing starts when you go live, not when you sign.</li>
</ul>
<h2>Using this site</h2>
<p>Don't misuse the site, submit someone else's information without permission or try to interfere with how it works.</p>
<h2>No warranty</h2>
<p>The site and report card are provided as is. To the extent allowed by law, we are not liable for decisions made based on them.</p>
<h2>Governing law</h2>
<p>These terms are governed by the laws of the State of Texas, with courts in McLennan County, Texas.</p>
<h2>Changes</h2>
<p>We may update these terms. The date at the top shows the latest version.</p>
<h2>Contact</h2>
<p><a href="mailto:{EMAIL}">{EMAIL}</a></p>"""
    body = f"""<section class="page-head"><div class="wrap legal">
  <div class="crumbs"><a href="{u('')}">Home</a> / {title}</div>
  <h1>{title}</h1>
</div></section>
<section class="section" style="padding-top:0"><div class="wrap legal">
  <div class="draft-note">Draft for lawyer review before launch. Written to meet A2P 10DLC texting verification.</div>
  {content}
</div></section>"""
    return page(key, title, f"{title} for {BRAND}.", body, has_form=False)


def not_found():
    body = f"""<section class="page-head"><div class="wrap">
  <span class="eyebrow">404</span><h1>That page isn't here.</h1>
  <p class="lede">Try the home page, or get your free report card.</p>
  <p style="margin-top:22px"><a class="btn btn-primary" href="{u('')}">Go home</a></p>
</div></section>"""
    return page("404", "Page not found", "Page not found.", body, has_form=False)


# ---- Write -----------------------------------------------------------------------
def llms_txt():
    city_names = ", ".join(c["name"] for c in CITIES)
    guide_names = "; ".join(g["title"] for g in GUIDES)
    # Plain facts for AI assistants (the "Answer" in our own method). Only states what the site states.
    plans = []
    for p in PLANS:
        price = "price not published yet" if p["monthly"] is None else f"${p['monthly']:,}/month, or 20% less billed yearly"
        plans.append(f"- {p['name']} ({p['scope']}; best for {p['stage']}): {price}")
    methods = "\n".join(f"- {n}: {line} " + "; ".join(items) + "." for n, line, items, _ in METHOD)
    return f"""# {BRAND}

> {BRAND} builds websites, runs Google Business Profiles and sets up missed-call text-back and review requests for HVAC contractors. HVAC only. Starting in {AREA}, serving HVAC companies nationally.

## Quick facts
- Website: https://{DOMAIN}
- Email: {EMAIL}
- Who it serves: residential and light commercial HVAC contractors
- Main offer: a free report card that grades an HVAC company's Google profile, reviews, website and listings against nearby competitors
- Guarantees: every missed call texted back within 60 seconds; new site live within 14 days of receiving content; first month refunded if the client is unhappy in the first 30 days after launch
- Does not promise: #1 rankings, a set number of jobs, a fixed cost per lead, or AI assistant recommendations
- Ownership: the client owns their domain, website content, Google profile and reviews

## Method: Answer, Rank, Repeat
{methods}

## Plans
{chr(10).join(plans)}

## Good fit
HVAC shops that do good work, miss calls when the crew is busy, and want to own their marketing rather than rent leads.

## Not a fit
Shops that can't take on more work, want only Google Ads management, or want a one-time website with nothing after.

## Pages
- Home: https://{DOMAIN}/
- The method: https://{DOMAIN}/method
- Pricing: https://{DOMAIN}/plans
- Free report card: https://{DOMAIN}/report-card
- Guides: https://{DOMAIN}/guides ({guide_names})
- Locations: https://{DOMAIN}/locations (Texas markets: {city_names})
"""


def build(out_dir):
    pages = {"index": home(), "report-card": report_card_page(), "method": method_page(), "plans": plans_page(), "privacy": legal_page("privacy"), "terms": legal_page("terms"), "404": not_found()}
    for k, _, _ in ALL_TRADES:
        pages[k] = trade_page(k)
    for k, _, _ in OFFERINGS:
        pages[k] = offer_page(k)
    pages["guides"] = guides_page()
    for g in GUIDES:
        pages[guide_path(g["slug"])] = guide_page(g)
    for n in NICHES:
        pages[n["slug"]] = niche_page(n)
    pages["locations"] = locations_page()
    pages["hvac-marketing-texas"] = texas_page()
    for c in CITIES:
        pages[city_path(c)] = city_page(c)
    os.makedirs(out_dir, exist_ok=True)
    for name, content in pages.items():
        with open(os.path.join(out_dir, name + ".html"), "w") as f:
            f.write(content)
    with open(os.path.join(out_dir, "llms.txt"), "w") as f:
        f.write(llms_txt())
    skip = {"404", "hvac", "plumbing", "roofing"}
    paths = ["" if n == "index" else n for n in pages if n not in skip]
    with open(os.path.join(out_dir, "sitemap.xml"), "w") as f:
        f.write(sitemap_xml(sorted(paths, key=lambda x: (x != "", x))))
    with open(os.path.join(out_dir, "robots.txt"), "w") as f:
        f.write(("User-agent: *\nDisallow: /\n" if NOINDEX else "User-agent: *\nAllow: /\n") + f"\nSitemap: https://{DOMAIN}/sitemap.xml\n")
    return sorted(pages)


if __name__ == "__main__":
    site = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if len(sys.argv) > 2 and sys.argv[1] == "--preview":
        PREVIEW = True
        out = sys.argv[2]
        names = build(out)
        for asset in ("styles.css", "main.js", "favicon.svg"):
            shutil.copy(os.path.join(site, asset), os.path.join(out, asset))
        shutil.copytree(os.path.join(site, "fonts"), os.path.join(out, "fonts"), dirs_exist_ok=True)
    else:
        names = build(site)
    print("Wrote:", ", ".join(n + ".html" for n in names))
