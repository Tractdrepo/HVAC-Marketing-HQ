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
TAGLINE = "Rank · Book · Repeat"
DOMAIN = "hvacmarketinghq.com"
EMAIL = "hello@" + DOMAIN
CALL_LINK = "https://calendar.app.google/bm89Bh3ot8oEk3VA9"  # Google Calendar booking page (Logan, Oct 14)
TURNSTILE_SITEKEY = "0x4AAAAAAFW5gSyWKqCFU_8y"  # Cloudflare Turnstile site key (public); secret is TURNSTILE_SECRET in Vercel
# Founder video bubble (bottom-left). Logan records a 60-90s face-on intro; see video-script.md.
FOUNDER_NAME = "Logan"
FOUNDER_VIDEO = None                  # e.g. "video/founder.mp4" once recorded (also add a poster: "video/founder.jpg")
FOUNDER_POSTER = None
DEMO_PHONE = None                     # demo line for missed-call text-back, e.g. "+12545550123"; block hidden until set
LEGAL_UPDATED = "October 14, 2026"   # "Last updated" on Privacy and Terms
NOINDEX = True                       # stays on until forms are tested and Logan says push
AREA = "Texas"                        # launch market; copy says "starting in Texas"

# Plans: four tiers with a monthly/annual toggle (annual = 20% off). Prices confirmed by Logan Oct 12, 2026.
ANNUAL_DISCOUNT = 0.20
PLAN_PRICE_FOR_CALC = 799            # break-even calculator default, editable by the visitor
PLANS = [
    {
        "name": "Starter", "monthly": 499, "build": 1995, "scope": "5 pages · 1 city", "stage": "1 to 2 trucks",
        "for": "A fast site and a complete Google profile, with every missed call texted back.",
        "items": ["5-page site on our HVAC build", "Missed-call text-back in 60 seconds", "Review requests after every job", "Google profile setup", "Shared inbox app", "HQ Command Center dashboard"],
    },
    {
        "name": "Growth", "monthly": 799, "build": 2495, "featured": True, "scope": "12 pages · 3 cities", "stage": "3 to 8 trucks",
        "for": "The full Rank, Book, Repeat system for an owner-run shop.",
        "items": ["Everything in Starter", "12 pages, including 3 city pages", "Google profile managed, posting the job photos you text us", "Estimate follow-up until booked or lost", "Review replies and AI web chat", "Win-back texts to past customers each season", "1 new article a month"],
    },
    {
        "name": "Dominate", "monthly": 1299, "build": 2995, "scope": "25 pages · 10 cities", "stage": "8+ trucks or a wide area",
        "for": "For shops covering a wide area that want the map in every town they serve.",
        "items": ["Everything in Growth", "25 pages, including 10 city pages", "Full spring and fall tune-up campaigns, text and email", "ServiceTitan, Housecall Pro or Jobber hookup", "Competitor and map spam watch", "Directory listings managed"],
    },
    {
        "name": "Multi-location", "monthly": 2499, "build": 4500, "scope": "Up to 10 locations", "stage": "several branches or brands",
        "for": "One flat price for shops with several branches or brands.",
        "items": ["Everything in Dominate", "Up to 10 locations", "A profile, pages and number for each", "Monthly AI performance report", "Priority support"],
    },
]
# Lighthouse scores measured on this site's own home page (mobile). Update after each measurement.
LIGHTHOUSE = {"scores": [("Performance", 99), ("Accessibility", 100), ("Best practices", 96), ("SEO", 100)],
              "note": "This site, measured with Google Lighthouse on a simulated 4G phone, Oct 11, 2026. Main content shows in 2.0 seconds on that phone and 0.4 seconds on desktop."}

LIGHTHOUSE_LCP_DESKTOP = "0.4s"

ADDONS = [
    ("Google Ads management (ad spend billed to you, no markup)", "$299/mo"),
    ("Local Services Ads management", "$299/mo"),
    ("Facebook and Instagram ads", "$299/mo"),
    ("AI phone answering, after hours and during the rush", "$299/mo"),
    ("Extra page", "$[X] each"),
    ("Directory listings sync", "$[X]/mo"),
    ("Extra tracked phone number", "$[X]/mo"),
    ("Campaigns beyond the included allowance", "At cost"),
]

# ---- Link handling ---------------------------------------------------------------
PREVIEW = False
BUILD_DATE = __import__("datetime").date.today().isoformat()


def call_link():
    return CALL_LINK or f"mailto:{EMAIL}?subject=15-minute%20call"


# Page key -> folder URL. Pages are built under short keys; ROUTES gives each its public address.
ROUTES = {}


def route(key):
    return ROUTES.get(key, key)


def u(path):
    """Link to a page. path is a page key like "" (home), "plans", "local-seo"."""
    if PREVIEW:
        return "/" + (route(path) or "index") + ".html"
    return "/" + route(path)


def a(path):
    """Link to a static asset at the site root."""
    return "/" + path


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
OFFERINGS = [("website", "HVAC websites", "Fast sites built to book service calls"), ("app", "Lead system", "Text-back, inbox and follow-up in one app")]
# Services menu, grouped the way owners think about it. Slugs point at OFFERINGS or SERVICES.
SERVICE_GROUPS = [
    ("Your website", "web", ["website", "hvac-website-redesign", "ai-web-chat"]),
    ("Get found online", "pin", ["local-seo", "google-business-profile", "ai-search"]),
    ("Get more calls", "chat", ["missed-call-text-back", "ai-phone-answering", "estimate-follow-up", "app"]),
    ("Paid ads", "search", ["google-ads", "local-services-ads", "facebook-ads"]),
    ("Keep customers coming", "star", ["review-requests", "seasonal-campaigns", "hq-command-center"]),
]
# For HVAC menu order.
NICHE_ORDER = ["hvac-marketing-residential-replacement", "hvac-marketing-light-commercial", "hvac-marketing-ac-repair", "hvac-marketing-heating",
               "hvac-marketing-ductwork-air-quality", "hvac-marketing-installation", "hvac-marketing-new-companies"]


# ---- Shared parts ----------------------------------------------------------------
def svc_info(slug):
    """(name, short line) for any service slug, offering or service page."""
    for k, n, d in OFFERINGS:
        if k == slug:
            return n, d
    x = next(x for x in SERVICES if x["slug"] == slug)
    return x["name"], x["nav"]


def niches_sorted():
    return sorted(NICHES, key=lambda n: NICHE_ORDER.index(n["slug"]) if n["slug"] in NICHE_ORDER else 99)


def header(has_form=True):
    def group(label, body, cls, all_slug, all_label):
        return (f'<div class="nav-group"><button type="button" aria-expanded="false">{label}{ICON["chev"]}</button>'
                f'<div class="nav-menu {cls}">{body}<a class="nav-all" href="{u(all_slug)}">{all_label} <span class="arrow">→</span></a></div></div>')
    cols = ""
    for g, icon, slugs in SERVICE_GROUPS:
        links = "".join(f'<a href="{u(k)}">{esc(svc_info(k)[0])}</a>' for k in slugs)
        cols += f'<div class="mega-col"><p class="mega-h"><i>{ICON[icon]}</i>{esc(g)}</p>{links}</div>'
    niche_links = "".join(f'<a href="{u(n["slug"])}">{esc(n["name"])}<span>{esc(n["nav"])}</span></a>' for n in niches_sorted())
    res = [("hvac-marketing", "HVAC marketing guide", "The whole system on one page"), ("guides", "Guides", "Straight answers, every number sourced")] + ([("blog", "Blog", "Short answers to owners' questions")] if POSTS else []) + [("tools", "Free tools", "Calculators, no email needed"),
           ("compare", "Compare agencies", "Honest side-by-sides, from their own terms"), ("getting-started", "Getting started", "What happens after you sign up"), ("locations", "Locations", "HVAC marketing in your city"), ("about", "About us", "Who we are and how we work")]
    res_links = "".join(f'<a href="{u(k)}">{n}<span>{d}</span></a>' for k, n, d in res)
    rc = "#report-card" if has_form else u("") + "#report-card"
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="site-head">
  <div class="wrap head-row">
    <a class="brand" href="{u('')}">{MARK}<span>{esc(BRAND_SHORT)}<small>{esc(TAGLINE)}</small></span></a>
    <button class="nav-toggle" type="button" aria-label="Menu" aria-expanded="false"><svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" stroke-width="2"/></svg></button>
    <nav class="nav" aria-label="Main">
      {group("Services", f'<div class="mega">{cols}</div>', "nav-mega", "services", "All services")}
      {group("For HVAC", f'<div class="nav-two">{niche_links}</div>', "nav-wide", "hvac-specialties", "See all HVAC specialties")}
      <a class="nav-link" href="{u('plans')}">Pricing</a>
      <a class="nav-link" href="{u('method')}">The method</a>
      {group("Resources", res_links, "", "guides", "All guides")}
      <a class="nav-link" href="{u('contact')}">Contact</a>
      <a class="btn btn-primary btn-small" href="{rc}">Free report card</a>
    </nav>
  </div>
</header>"""


def footer(has_form=True):
    offers = "".join(f'<li><a href="{u(k)}">{esc(svc_info(k)[0])}</a></li>' for _, _, slugs in SERVICE_GROUPS for k in slugs)
    niches = "".join(f'<li><a href="{u(n["slug"])}">{esc(n["name"])}</a></li>' for n in niches_sorted())
    rc = "#report-card" if has_form else u("") + "#report-card"
    return f"""<footer class="site-foot">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <a class="brand" href="{u('')}">{MARK}<span>{esc(BRAND)}<small>{esc(TAGLINE)}</small></span></a>
        <p style="margin-top:16px;max-width:36ch">Websites, Google profiles and lead systems for HVAC companies.</p>
      </div>
      <div><h2 class="foot-h">How it works</h2><ul><li><a href="{u('method')}">The method</a></li><li><a href="{u('plans')}">Pricing</a></li><li><a href="{u('getting-started')}">Getting started</a></li><li><a href="{u('')}#tech">The tech</a></li><li><a href="{u('guides')}">Guides</a></li>{f'<li><a href="{u("blog")}">Blog</a></li>' if POSTS else ''}<li><a href="{u('tools')}">Free tools</a></li><li><a href="{u('guide-hvac-website-checklist')}">Website checklist</a></li></ul></div>
      <div><h2 class="foot-h">Services</h2><ul>{offers}</ul></div>
      <div><h2 class="foot-h">For HVAC</h2><ul>{niches}</ul></div>
      <div><h2 class="foot-h">Locations</h2><ul><li><a href="{u('hvac-marketing-texas')}">Texas</a></li><li><a href="{u('hvac-marketing-houston-tx')}">Houston</a></li><li><a href="{u('hvac-marketing-dallas-tx')}">Dallas</a></li><li><a href="{u('hvac-marketing-austin-tx')}">Austin</a></li><li><a href="{u('hvac-marketing-waco-tx')}">Waco</a></li><li><a href="{u('locations')}">All locations</a></li></ul></div>
      <div><h2 class="foot-h">Company</h2><ul><li><a href="{u('about')}">About</a></li><li><a href="{u('report-card')}">Free report card</a></li><li><a href="{u('contact')}">Contact</a></li><li><a href="{esc(call_link())}">Book a 15-minute call</a></li><li><a href="mailto:{EMAIL}">{EMAIL}</a></li><li><a href="/llms.txt">Info for AI assistants</a></li></ul></div>
    </div>
    <p class="foot-word" aria-hidden="true">{esc(BRAND)}</p>
    <div class="foot-base">
      <span>© <span data-year>2026</span> {esc(BRAND)}. Waco, Texas.</span>
      <span><a href="{u('privacy')}">Privacy</a> · <a href="{u('terms')}">Terms</a></span>
    </div>
  </div>
</footer>"""


def rc_form(trade="HVAC", key=None, lazy_turnstile=False):
    """The four-step report card form. key keeps ids unique when a page has two forms; the pop-up's
    Turnstile renders when the pop-up opens (main.js), since it can't render while hidden."""
    key = key or trade
    if PREVIEW or not TURNSTILE_SITEKEY:
        ts = ""
    else:
        ts = f'<div class="{"cf-turnstile-lazy" if lazy_turnstile else "cf-turnstile"}" data-sitekey="{TURNSTILE_SITEKEY}" data-theme="light"></div>'
    return f"""    <form class="rc-form" novalidate>
      <div class="rc-body">
        <div class="rc-progress" aria-hidden="true"><i class="on"></i><i></i><i></i><i></i></div>
        <input class="hp" type="text" name="company_fax" tabindex="-1" autocomplete="off" aria-hidden="true">
        <input type="hidden" name="trade" value="{esc(trade)}">
        <div class="rc-step on">
          <h3>What's your website?</h3>
          <p class="muted">No website yet? Put your Facebook page or type "none".</p>
          <div class="field"><label for="rc-site-{key}">Website</label><input id="rc-site-{key}" type="text" name="website" placeholder="yourcompany.com" required data-msg="Add your website, or type none." autocomplete="url"></div>
          <div class="rc-nav"><button type="button" class="btn btn-primary" data-next>Next</button></div>
        </div>
        <div class="rc-step">
          <h3>What's the business called?</h3>
          <p class="muted">The name on your Google profile, so we grade the right one.</p>
          <div class="field"><label for="rc-biz-{key}">Business name</label><input id="rc-biz-{key}" type="text" name="business" required data-msg="Add your business name." autocomplete="organization"></div>
          <div class="field"><label for="rc-town-{key}">Main town and state</label><input id="rc-town-{key}" type="text" name="town" placeholder="Start typing, like Dallas" required data-msg="Add your main town and state, like Dallas, TX." autocomplete="off" data-towns role="combobox" aria-autocomplete="list" aria-expanded="false" aria-controls="rc-town-{key}-list"><ul class="town-suggest" id="rc-town-{key}-list" role="listbox" hidden></ul></div>
          <div class="rc-nav"><button type="button" class="rc-back">Back</button><button type="button" class="btn btn-primary" data-next>Next</button></div>
        </div>
        <div class="rc-step">
          <h3>Where should we send it?</h3>
          <div class="field"><label for="rc-name-{key}">First name</label><input id="rc-name-{key}" type="text" name="first_name" required data-msg="Add your first name." autocomplete="given-name"></div>
          <div class="field"><label for="rc-email-{key}">Email</label><input id="rc-email-{key}" type="email" name="email" required data-msg="Add a valid email." autocomplete="email"></div>
          <div class="rc-nav"><button type="button" class="rc-back">Back</button><button type="button" class="btn btn-primary" data-next>Next</button></div>
        </div>
        <div class="rc-step">
          <h3>Last one: your phone</h3>
          <p class="muted">Only used if you ask us to text you. We don't cold call.</p>
          <div class="field"><label for="rc-phone-{key}">Mobile phone</label><input id="rc-phone-{key}" type="tel" name="phone" required data-msg="Add a phone number." autocomplete="tel" pattern="[0-9()+.\\- ]{{10,}}"></div>
          <label class="consent"><input type="checkbox" name="sms_consent" value="yes"><span>Text me about my report card. Message and data rates may apply. Message frequency varies. Reply STOP to opt out, HELP for help. Consent is not a condition of purchase. See our <a href="{u('privacy')}">Privacy Policy</a> and <a href="{u('terms')}">Terms</a>.</span></label>
          {ts}
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
    </form>"""


def rc_modal():
    """Pop-up report card form opened by the hero URL box, so nobody gets thrown to the bottom of the page."""
    return f"""<dialog class="rc-modal" aria-labelledby="rc-modal-h">
  <div class="rc-modal-in">
    <button type="button" class="rc-modal-x" aria-label="Close">×</button>
    <span class="eyebrow">Free report card</span>
    <h2 id="rc-modal-h">Grade your shop in four quick steps</h2>
    <p class="muted">Google profile, reviews, website and listings, graded against the shops near you. No sales call.</p>
    {rc_form(key="modal", lazy_turnstile=True)}
  </div>
</dialog>"""


def report_card(title="Get your free report card", sub=None, trade="HVAC"):
    sub = sub or (f"We grade your Google profile, reviews, website and listings against the {trade if trade.isupper() else trade.lower()} companies "
                  "people find near you. It lands in your inbox in about five minutes. Nobody will call you.")
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
    {rc_form(trade)}
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


def asset_v(name):
    """Cache-busting query for styles.css and main.js, so a deploy shows up without a hard refresh."""
    import hashlib
    try:
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), name), "rb") as f:
            return a(name) + "?v=" + hashlib.sha1(f.read()).hexdigest()[:8]
    except OSError:
        return a(name)


def crumbs_ld(body):
    """BreadcrumbList JSON-LD from the visible crumbs, so Google shows the trail."""
    m = _re.search(r'<div class="crumbs">(.*?)</div>', body)
    if not m:
        return ""
    parts = [x.strip() for x in m.group(1).split(" / ")]
    items = []
    for n, x in enumerate(parts):
        lm = _re.match(r'<a href="([^"]*)">(.*)</a>', x)
        name = _strip(lm.group(2) if lm else x)
        item = {"@type": "ListItem", "position": n + 1, "name": name}
        if lm and not PREVIEW:
            item["item"] = f"https://{DOMAIN}{lm.group(1)}"
        items.append(item)
    return ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items})


def page(path, title, desc, body, extra_head="", has_form=True):
    robots = '<meta name="robots" content="noindex, nofollow">' if NOINDEX else ""
    turnstile = "" if PREVIEW or not TURNSTILE_SITEKEY else '<script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>'
    if len(desc) > 160:  # keep descriptions inside what search results show
        cut = desc[:158]
        desc = cut[:cut.rfind(". ") + 1] if cut.rfind(". ") > 90 else cut[:cut.rfind(" ")].rstrip(",;:") + "..."
    full_title = title if title.endswith(BRAND) else f"{title} | {BRAND}"
    if len(full_title) > 65 and not title.endswith(BRAND):
        full_title = title  # keep long titles from being cut off in Google
    preview_meta = '<meta name="site-preview" content="1">' if PREVIEW else ""
    canon = f"https://{DOMAIN}/{route(path)}"
    social = (f'<link rel="canonical" href="{canon}">\n<meta property="og:type" content="website">\n<meta property="og:site_name" content="{esc(BRAND)}">\n'
              f'<meta property="og:title" content="{esc(full_title)}">\n<meta property="og:description" content="{esc(desc)}">\n'
              f'<meta property="og:url" content="{canon}">\n<meta property="og:image" content="https://{DOMAIN}/og-image.png">\n'
              f'<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n<meta name="twitter:card" content="summary_large_image">')
    extra_head = social + "\n" + crumbs_ld(body) + extra_head
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
<link rel="stylesheet" href="{asset_v('styles.css')}">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="{a('favicon.ico')}" sizes="48x48">
<link rel="icon" href="{a('favicon.svg')}" type="image/svg+xml">
<link rel="apple-touch-icon" href="{a('apple-touch-icon-180.png')}">
{extra_head}
</head>
<body>
{header(has_form)}
<main id="main">
{body}
</main>
{footer(has_form)}
{founder_video(has_form)}
{rc_modal() if "data-url-form" in body else ""}
<script src="{asset_v('main.js')}" defer></script>
{turnstile}
</body>
</html>
"""


def cta_band(text="See where your shop stands before you spend a dollar."):
    return f"""<section class="section tight"><div class="wrap"><div class="cta-band">
  <h2>{esc(text)}</h2><a class="btn" href="#report-card">Get your report card</a>
</div></div></section>"""


def next_step(title="Know where your shop stands.", sub="The free report card grades your Google profile, reviews, website and listings against the shops near you, so you know what to fix first."):
    """Closing navy band for pages without the inline form (guides, posts): one primary action, one fallback."""
    return f"""<section class="section dark next-step"><div class="wrap"><div class="ns">
  <div><span class="eyebrow">Your next step</span><h2>{esc(title)}</h2><p class="lede">{esc(sub)}</p>
    <div class="ns-actions"><a class="btn btn-primary" href="{u('report-card')}">Get my free report card <span class="arrow">→</span></a><a class="btn btn-ghost" href="{esc(call_link())}">Book a 15-minute call</a></div></div>
  <ul class="ns-list"><li><b>Grades</b>Google profile, reviews, website and listings</li><li><b>Time</b>In your inbox in about five minutes</li><li><b>Cost</b>Free. Nobody calls you.</li></ul>
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
    ("Rank", "Show up first when someone searches.", [
        "A fast site built around the jobs you want",
        "A page for each service and each town you really serve",
        "Google profile complete, active and posting the job photos you send",
        "Directory listings kept consistent",
        "Map spam reported on fake competitor listings",
    ], "More of the right homeowners find you, not a franchise."),
    ("Book", "Every call answered and booked, even when you can't pick up.", [
        "Missed-call text-back in 60 seconds, guaranteed",
        "One shared inbox for calls, texts, chats and forms",
        "AI web chat that captures the lead after hours",
        "Estimate follow-up until the job is booked or lost",
        "Optional AI phone answering during the rush",
    ], "Nobody calls the next shop because you were in an attic."),
    ("Repeat", "Turn every job into the next one.", [
        "Review request after every finished job",
        "A reply to every review, in your voice",
        "Spring and fall tune-up campaigns to past customers",
        "Maintenance plan reminders before plans lapse",
        "Your HQ Command Center dashboard and a quarterly re-grade",
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
  <div class="dash-head"><b>HQ Command Center · Your Shop Heating &amp; Air</b><span class="live">Live</span><span class="dash-sample">Sample data</span></div>
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
    right = ["An HQ Command Center dashboard you can open anytime", "Prices on the website, not after a sales call", "Month to month, no long contract", "Your number ported back if you leave"]
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
    svg = f"""<svg viewBox="0 0 400 400" role="img" aria-label="Rank, Book and Repeat form one loop around your schedule">
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
  <div class="tile b-2 b-tall reveal"><div><span class="tile-label">Book</span><h3>Missed-call text-back</h3><p>Every call you miss gets a text in seconds, with your name on it.</p></div>{demo()}</div>
  <div class="tile b-2 reveal"><div><span class="tile-label">Rank</span><h3>Top of the map pack</h3><p>A complete, active Google profile and real town pages.</p></div><div class="mock">{mappack()}</div></div>
  <div class="tile b-2 reveal"><div><span class="tile-label">Book</span><h3>AI web chat</h3><p>Answers questions and captures the lead after hours.</p></div><div class="mock chat"><div class="chat-head"><i></i>Your Shop assistant</div><div class="msg user">Do you do weekend AC repair?</div><div class="msg bot">Yes, Saturdays 8 to 4. Want me to book a time? What's your address?</div></div></div>
  <div class="tile b-4 reveal"><div><span class="tile-label">Repeat</span><h3>HQ Command Center</h3><p>Calls, texts, booked jobs and reviews, updated as they happen. No monthly PDF.</p></div><div class="mock">{dashboard()}</div></div>
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
    <div class="field"><label for="c-plan">Monthly plan price</label><div class="money"><input id="c-plan" type="text" inputmode="decimal" name="plan" value="{PLAN_PRICE_FOR_CALC:,}"></div><div class="hint">Our Growth plan. Change it to try any number.</div></div>
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
        ("Price", "Often $2,500+ a month, quoted after a sales call", "Software fees plus your own evenings", "$499 to $2,499 a month, on this site"),
        ("Contract", "Often 12 months", "Monthly software subscriptions", "Month to month"),
        ("Who owns the website", "Sometimes the agency, or you rebuild when you leave", "You", "You, always"),
        ("Missed-call text-back", "Add-on, if offered", "If you set it up yourself", "In every plan, 60 seconds guaranteed"),
        ("Reporting", "A monthly PDF", "Whatever you have time to check", "HQ Command Center, live anytime"),
        ("Time to launch", "Varies, often months", "Whenever you get to it", "14 days, guaranteed"),
        ("If it's not working", "Locked in until the term ends", "Cancel the tools", "First month back within 30 days"),
        ("What they promise", "Often page-one rankings", "Nothing", "Only what we control, in writing"),
        ("Who does the work", "An account manager with dozens of clients", "You", "A small team that only works with HVAC"),
    ]
    body = "".join(f"<tr><th scope=\"row\">{esc(a_)}</th><td>{esc(b)}</td><td>{esc(c)}</td><td>{esc(d)}</td></tr>" for a_, b, c, d in rows)
    return f'''<div class="compare"><h3>Compared with a big agency, or doing it yourself</h3>
  <div class="table-wrap"><table><thead><tr><th></th><th>Big agency</th><th>Do it yourself</th><th>{esc(BRAND_SHORT)}</th></tr></thead><tbody>{body}</tbody></table></div>
  <p class="muted" style="font-size:.85rem;margin-top:10px">Agency prices and terms from their own published pages, Oct 2026. See our <a href="{u('guide-hvac-marketing-cost')}">cost guide</a> and <a href="{u('guide-scorpion-alternative-hvac')}">Scorpion guide</a>.</p></div>'''


def report_vs_track():
    rows = [("Impressions and clicks", "Calls answered and missed"), ("\"Leads\"", "Missed calls texted back, and how many replied"),
            ("Website visits", "Booked jobs from calls, texts and chat"), ("Keyword reports", "Where you show up on the map for your real searches"),
            ("A monthly PDF", "New reviews, and your replies"), ("Activity, \"we posted 4 times\"", "What's working, what isn't, and what we're changing")]
    body = "".join(f"<tr><td>{esc(a_)}</td><td><b>{esc(b)}</b></td></tr>" for a_, b in rows)
    return f'''<div class="compare"><h3>What most agencies report vs what we track</h3>
  <div class="table-wrap"><table><thead><tr><th>Most agencies report</th><th>Your HQ Command Center shows</th></tr></thead><tbody>{body}</tbody></table></div></div>'''


def missed_call_calc():
    return """<div class="calc mcalc">
  <div>
    <div class="field"><label for="m-calls">Calls you miss in a week</label><input id="m-calls" type="text" inputmode="decimal" name="calls" value="5"><div class="hint">Busy season, after hours and while you're on a job. Guess if you don't know.</div></div>
    <div class="field"><label for="m-job">Average value of a job from a new caller</label><div class="money"><input id="m-job" type="text" inputmode="decimal" name="job" value="1,200"></div><div class="hint">Mix of repairs and the odd replacement.</div></div>
    <div class="field"><label for="m-close">Share of those callers you'd normally book</label><select id="m-close" name="close"><option value="20">20%</option><option value="30" selected>30%</option><option value="40">40%</option><option value="50">50%</option></select></div>
  </div>
  <div class="calc-out" aria-live="polite">
    <div class="row"><span class="big" data-out="week">–</span><p>in jobs at risk each week from missed calls</p></div>
    <div class="row"><span class="big" data-out="month">–</span><p>at risk each month</p></div>
    <div class="row"><span class="big" data-out="year">–</span><p>at risk each year</p></div>
    <p style="font-size:.85rem">Missed calls x job value x the share you'd book. Your numbers; this is math, not a promise of results.</p>
  </div>
</div>"""


def addons():
    rows = "".join(f'<div class="addon"><span>{esc(n)}</span><b>{esc(p)}</b></div>' for n, p in ADDONS)
    return f'<div class="addons"><h3>One-time and optional</h3><div class="addons-list">{rows}</div></div>'


def promise():
    return f"""<div class="promise">
  <div class="card reveal"><span class="big">60 seconds</span><p>Every missed call gets a text back within 60 seconds.</p></div>
  <div class="card"><span class="big">14 days</span><p>Your new site is live within 14 days of getting your content.</p></div>
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
    bad = ["You can't take on more work right now", "You want ads with no one answering the calls they bring", "You want a one-time site and nothing after", "You want someone to promise #1 on Google"]
    l = "".join(f"<li>{esc(x)}</li>" for x in good)
    r = "".join(f"<li>{esc(x)}</li>" for x in bad)
    return f"""<div class="grid two fit">
  <div class="card reveal"><h3>A good fit if</h3><ul class="ticks">{l}</ul></div>
  <div class="card reveal"><h3>Not a fit if</h3><ul class="crosses">{r}</ul></div>
</div>
<p class="muted" style="margin-top:16px;font-size:.92rem">If a smaller plan fits your shop better, we'll say so on the call.</p>"""


def replaces():
    tools = [("Website builder and hosting", "Website"), ("Call tracking", "Book"), ("Texting app", "Book"), ("Online booking", "Book"), ("Review software", "Repeat"), ("Reporting", "Repeat")]
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
    ("Do I have to manage the software?", "No. You and your office use one inbox app on your phones, and you can check your HQ Command Center dashboard anytime. We build and run everything behind it."),
    ("Do you run Google Ads or Local Services Ads?", "Yes, as an add-on to any plan: Google Ads, Local Services Ads and Facebook ads. Your ad spend is billed by Google or Meta to your own account and never marked up, and every call from an ad is tracked to a booked job."),
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
# Every other state lives in data/states/<slug>.json: {"state": {name, abbr, slug, population_2020, source_url}, "cities": [...]}
STATES = [{"name": "Texas", "abbr": "TX", "slug": "texas", "population_2020": TX_POP, "cities": CITIES}]
_SDIR = os.path.join(os.path.dirname(_DATA), "states")
for _fn in sorted(os.listdir(_SDIR)) if os.path.isdir(_SDIR) else []:
    if _fn.endswith(".json"):
        with open(os.path.join(_SDIR, _fn)) as _f:
            _d = json.load(_f)
        STATES.append(dict(_d["state"], abbr=_d["state"]["abbr"].upper(), cities=_d["cities"]))
for _st in STATES:
    # A city page needs its own climate numbers; cities whose article has none wait for map data.
    _st["cities"] = [c for c in _st["cities"] if c.get("july_high_f") is not None and c.get("jan_low_f") is not None]
    for _c in _st["cities"]:
        _c["_st"] = _st
STATES = [st for st in STATES if st["cities"]]
CITIES = STATES[0]["cities"]
ALL_CITIES = [c for st in STATES for c in st["cities"]]
# Businesses holding an active TDLR A/C contractor license, merged by company (prospects/centex-prospects.xlsx, Oct 11, 2026)
TDLR_COUNTY = {"McLennan County": 156, "Bell County": 161}


def city_path(c):
    return f"hvac-marketing-{c['slug']}-{c['_st']['abbr'].lower()}"


def place(c):
    st = c["_st"]
    return st["name"] if st["abbr"] == "DC" else f"{c['name']}, {st['name']}"


def state_key(st):
    return f"hvac-marketing-{st['slug']}"


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
    elif hot >= 85:
        out.append(("A long, busy summer", f"July highs average {deg(hot)} in {c['name']}. We build AC repair and replacement pages first and time tune-up texts for spring."))
    else:
        out.append(("A short cooling season", f"July highs average {deg(hot)} in {c['name']}, so AC calls bunch into a few hot weeks. Heat pump, furnace and air quality pages carry the rest of the year, and early-summer tune-up texts catch the rush."))
    if cold <= 33:
        out.append(("A real heating season", f"January lows average {deg(cold)}. Furnace and heat pump pages earn their keep here, and fall tune-up campaigns fill the schedule before the first cold snap."))
    else:
        out.append(("Mild winters, steady heat pump work", f"January lows average {deg(cold)}. Heat pump repair and installs carry the cooler months, with fewer emergency heating calls."))
    if "cfa" in k or "humid" in k or "tropical" in k:
        out.append(("Humidity sells comfort", "Humid air makes homes feel warmer than the thermostat says. Pages for dehumidifiers, indoor air quality and duct work bring higher-value jobs."))
    elif "bs" in k or "bw" in k or "arid" in k or "desert" in k:
        out.append(("Dry air and dust", "Dust works filters and outdoor units hard. Maintenance plan pages and filter reminders keep customers coming back between breakdowns."))
    if c["population_2020"] and c["population_2020"] >= 500000:
        out.append(("A crowded map", f"With {fnum(c['population_2020'])} people in the city alone, you won't win every search from one address. A page for each part of town you serve helps you show up beyond your shop's neighborhood."))
    else:
        out.append(("Reviews decide it", "In a market this size, homeowners often pick between a handful of shops by star rating and how recent the reviews are. Steady review requests after every job are the fastest lever."))
    return out


def an(word):
    return "an" if word[:1].upper() in "AEIOU" else "a"


def city_hook(c):
    hot, cold = c["july_high_f"], c["jan_low_f"]
    if hot >= 85:
        return f"When it's {round(hot)}° in July, {an(c['name'])} {esc(c['name'])} homeowner with a dead AC calls the first shop that shows up and answers."
    if cold <= 32:
        return f"When January lows sit near {round(cold)}°, {an(c['name'])} {esc(c['name'])} homeowner with no heat calls the first shop that shows up and answers."
    return f"Summers stay mild in {esc(c['name'])}, so heat pumps, tune-ups and the first hot week decide the year. Homeowners call the first shop that shows up and answers."


def places_data(c):
    """Google Maps snapshot for a city, written by the city map data pull (data/places/<state>/<city>.json). Refreshed within 30 days."""
    p_ = os.path.join(os.path.dirname(_DATA), "places", c["_st"]["slug"], c["slug"] + ".json")
    try:
        with open(p_) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def market_block(c):
    d = places_data(c)
    # Under 20 results means Google stopped the search early; the numbers would mislead, so skip the block.
    if not d or (d.get("count") or 0) < 20:
        return ""
    n_ = d["count"]
    stats = [("HVAC shops Google shows", f"{n_}+" if n_ >= 60 else fnum(n_), "for one city search"),
             ("Median rating", f'{d["median_rating"]:.1f}★' if d.get("median_rating") is not None else "–", "of those shops"),
             ("Median review count", fnum(d.get("median_reviews")), "of those shops")]
    if d.get("share_with_website") is not None:
        stats.append(("Have a website", f'{round(d["share_with_website"] * 100) if d["share_with_website"] <= 1 else round(d["share_with_website"])}%', "linked on Google"))
    st_html = "".join(f'<div class="cfact"><span>{a_}</span><b>{b}</b><small>{c_}</small></div>' for a_, b, c_ in stats)
    rows = "".join(f'<tr><td>{n + 1}</td><td>{esc(t[0])}</td><td>{f"{t[1]:.1f}" if t[1] is not None else "–"}</td><td>{fnum(t[2])}</td></tr>' for n, t in enumerate(d.get("top5", [])[:5]))
    table = f'<table class="mtable"><thead><tr><th>#</th><th>Shop</th><th>Rating</th><th>Reviews</th></tr></thead><tbody>{rows}</tbody></table>' if rows else ""
    top = d.get("top5") or []
    gap = f"The most-reviewed shop has {fnum(top[0][2])} reviews; the median shop has {fnum(d.get('median_reviews'))}. That gap is what review requests close." if top and d.get("median_reviews") is not None else ""
    return f"""<section class="section dark"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">{esc(c['name'])} on Google</span><h2>The {esc(c['name'])} HVAC map, in numbers.</h2><p class="lede">What a homeowner sees when they search for HVAC help in {esc(c['name'])}. {esc(gap)}</p></div>
  <div class="cfacts reveal">{st_html}</div>
  <h3 style="margin-top:34px">Most-reviewed HVAC shops around {esc(c['name'])}</h3>
  {table}
  <p class="csrc">Data from Google, pulled {esc(d.get("pulled", ""))}. Search: "{esc(d.get("query", ""))}". Refreshed monthly. Google includes shops from nearby towns. Listed for context only; these shops are not our clients.</p>
</div></section>"""


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
    st = c["_st"]
    lic = TDLR_COUNTY.get(c["county"]) if st["abbr"] == "TX" else None
    lic_html = f'<p class="clic"><b>{lic}</b> businesses hold an active Texas A/C contractor license in {esc(c["county"])} (TDLR records, Oct 2026). That\'s who you\'re up against on the map.</p>' if lic else ""
    others = [o for o in st["cities"] if o["slug"] != c["slug"]]
    near = "".join(f'<a href="{u(city_path(o))}">{esc(o["name"])}</a>' for o in others)
    other_html = f"""<div class="more-row"><h3>Other {esc(st['name'])} markets</h3><div class="city-links">{near}</div></div>""" if others else ""
    mk = market_block(c)
    body = f"""<section class="page-head city-head"><div class="wrap">
  <div class="crumbs"><a href="{u('')}">Home</a> / <a href="{u('locations')}">Locations</a> / {"" if st["abbr"] == "DC" else f'<a href="{u(state_key(st))}">{esc(st["name"])}</a> / '}{esc(c['name'])}</div>
  <span class="eyebrow">{esc(c['county'])} · {esc(c['metro'])}</span>
  <h1 style="max-width:20ch">HVAC marketing in {esc(place(c).rstrip('.'))}.</h1>
  <p class="lede">{city_hook(c)} We make sure that's you: a fast site, a Google profile that's actually run, and every missed call texted back in 60 seconds.</p>
  {url_form()}
</div></section>
<section class="section" style="padding-top:12px"><div class="wrap">
  <div class="cfacts reveal">{fact_html}</div>
  <p class="csrc">Population: 2020 U.S. Census. Climate: {esc(station)}{" normals" if c.get("climate_period") else ""}. Both as published on Wikipedia.</p>
</div></section>
{mk}
<section class="section {"alt" if mk else "dark"}"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">{esc(c['name'])} market</span><h2>What {esc(c['name'])}'s weather means for your marketing.</h2><p class="lede">{esc(c['one_fact'])}</p></div>
  <div class="grid two">{ins}</div>
  {lic_html}
</div></section>
<section class="section"><div class="wrap split">
  <div><span class="eyebrow">Service areas</span><h2>A page for every town you really serve.</h2><p class="lede">Google shows the shops closest to the person searching. Real town pages, with your work and reviews from that town, stretch your reach past your own zip code.</p></div>
  <div class="card"><h3>Around {esc(c['name'])}</h3><ul class="ticks town-list">{towns}</ul><p class="muted" style="font-size:.9rem">We only build pages for towns you actually take calls in.</p></div>
</div></section>
{local_links(c['name'], other_html)}
{report_card(f"How does your shop stack up in {c['name']}?")}"""
    return page(city_path(c), f"HVAC marketing in {c['name']}, {st['abbr']}", f"Websites, Google profiles and missed-call text-back for {place(c)} HVAC companies. July highs average {deg(c['july_high_f'])}; here's what that means for your marketing.", body)


def local_links(where, more=""):
    svc = ["website", "local-seo", "google-business-profile", "missed-call-text-back", "google-ads", "local-services-ads"]
    svc_h = "".join(f'<a href="{u(k)}">{esc(svc_info(k)[0])}</a>' for k in svc)
    reads = [(guide_path("google-map-pack-hvac"), "How HVAC shops get into the map pack"), (guide_path("hvac-seo-what-moves-rankings"), "HVAC SEO: what moves rankings"),
             ("tools/missed-call-cost-calculator", "Missed call cost calculator"), ("tools/lsa-cost-calculator", "Local Services Ads cost calculator"), ("plans", "Plans and pricing")]
    rd = "".join(f'<li><a href="{u(k)}">{esc(t)}</a></li>' for k, t in reads if k in ROUTES or k == "plans")
    return f"""<section class="section alt"><div class="wrap"><div class="split">
  <div><span class="eyebrow">For {esc(where)} shops</span><h2>What we run for you.</h2><p class="lede">The same system on every plan: Rank, Book, Repeat. <a class="more" href="{u('method')}">How it works →</a></p><div class="city-links" style="margin-top:18px">{svc_h}</div></div>
  <div class="card"><h3>Read before you hire anyone</h3><ul class="ticks">{rd}</ul></div>
</div>{more}</div></section>"""


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
<section class="section dark"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">Why Texas is different</span><h2>Heat, freezes and crowded maps.</h2></div>
  <div class="grid three">
    <div class="card reveal"><h3>One state, very different weather</h3><p>July highs average {deg(hottest['july_high_f'])} in {esc(hottest['name'])}, while January lows average {deg(coldest['jan_low_f'])} in {esc(coldest['name'])}. Your site should talk about the weather your customers actually live with.</p></div>
    <div class="card reveal"><h3>Freezes happen too</h3><p>The February 2021 winter storm showed how fast heating calls can pile up in a state built for cooling. Heat pump and furnace pages pay off even here.</p></div>
    <div class="card reveal"><h3>Built for Texas rules</h3><p>Texting customers is set up the right way: carrier registration and opt-outs on every message. And we never cold text or cold call, in line with Texas law.</p></div>
  </div>
</div></section>
<section class="section"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">Texas markets</span><h2>Pick your city.</h2><p class="lede">Each page shows that market's weather and what it means for your marketing.</p></div>
  <div class="city-grid">{city_cards(CITIES)}</div>
</div></section>
{local_links("Texas")}
{report_card("See how your shop stacks up in your Texas town.")}
"""
    return page("hvac-marketing-texas", "HVAC marketing in Texas", "Websites, Google profiles and missed-call text-back for Texas HVAC contractors, from Houston to El Paso.", body)


def state_page(st):
    cs = st["cities"]
    hottest = max(cs, key=lambda c: c["july_high_f"] or 0)
    coldest = min(cs, key=lambda c: c["jan_low_f"] if c["jan_low_f"] is not None else 99)
    big = max(cs, key=lambda c: c["population_2020"] or 0)
    n = st["name"]
    if len(cs) > 1:
        weather_card = f'<div class="card reveal"><h3>Different weather, city to city</h3><p>July highs average {deg(hottest["july_high_f"])} in {esc(hottest["name"])}, while January lows average {deg(coldest["jan_low_f"])} in {esc(coldest["name"])}. Your site should talk about the weather your customers actually live with.</p></div>'
    else:
        weather_card = f'<div class="card reveal"><h3>Weather that drives the calls</h3><p>July highs average {deg(big["july_high_f"])} and January lows {deg(big["jan_low_f"])} in {esc(big["name"])}. Your site should talk about the weather your customers actually live with.</p></div>'
    body = f"""<section class="page-head"><div class="wrap">
  <div class="crumbs"><a href="{u('')}">Home</a> / <a href="{u('locations')}">Locations</a> / {esc(n)}</div>
  <span class="eyebrow">{esc(n)} · {len(cs)} markets</span>
  <h1 style="max-width:20ch">HVAC marketing for {esc(n)} contractors.</h1>
  <p class="lede">{fnum(st['population_2020'])} people live in {esc(n)}, and each market has its own weather and its own map to win. We build the same system for every shop here: a fast site, a Google profile that's actually run, and every missed call texted back.</p>
  {url_form()}
</div></section>
<section class="section dark"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">{esc(n)} up close</span><h2>What {esc(n)} means for your marketing.</h2></div>
  <div class="grid three">
    {weather_card}
    <div class="card reveal"><h3>Big markets, crowded maps</h3><p>{esc(big['name'])} alone has {fnum(big['population_2020'])} people. In a market that size, a page for each part of town you serve helps you show up past your own neighborhood.</p></div>
    <div class="card reveal"><h3>Texting done right</h3><p>Every text we send for you is set up the right way: carrier registration and an opt-out on every message. We never cold text or cold call homeowners.</p></div>
  </div>
</div></section>
<section class="section"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">{esc(n)} markets</span><h2>Pick your city.</h2><p class="lede">Each page shows that market's weather and what it means for your marketing.</p></div>
  <div class="city-grid">{city_cards(cs)}</div>
</div></section>
{local_links(n)}
{report_card(f"See how your shop stacks up in your {n} town.")}
"""
    names = [c["name"] for c in sorted(cs, key=lambda c: -(c["population_2020"] or 0))]
    return page(state_key(st), f"HVAC marketing in {n}", f"Websites, Google profiles and missed-call text-back for {n} HVAC contractors in " + (f"{', '.join(names[:-1])} and {names[-1]}." if len(names) > 1 else f"{names[0]}."), body)


def locations_page():
    blocks = "".join(f"""<div class="loc-state reveal"><div><h2><a href="{u(state_key(st))}">{esc(st['name'])}</a></h2><p class="muted">{len(st['cities'])} markets · {fnum(st['population_2020'])} people</p></div>
  <div class="city-grid">{city_cards(st['cities'])}</div></div>
  """ for st in STATES)
    body = f"""<section class="page-head"><div class="wrap">
  <div class="crumbs"><a href="{u('')}">Home</a> / Locations</div>
  <span class="eyebrow">Markets</span>
  <h1 style="max-width:20ch">HVAC marketing, built in Texas, for shops everywhere.</h1>
  <p class="lede">Everything we do works from anywhere: your site, your Google profile and your lead system. We started in Texas and add local market pages state by state. {len(ALL_CITIES)} markets in {len(STATES)} states so far.</p>
  {url_form()}
</div></section>
<section class="section" style="padding-top:12px"><div class="wrap">
  {blocks}<div class="loc-next reveal"><h3>Don't see your state?</h3><p>We work with HVAC companies in any state. Local market pages for more states are on the way; the report card works for any town today.</p><a class="btn btn-ghost btn-small" href="#report-card">Grade my shop</a></div>
</div></section>
{report_card()}
"""
    return page("locations", "HVAC marketing locations", f"HVAC marketing for contractors across the U.S.: {len(ALL_CITIES)} markets in {', '.join(st['name'] for st in STATES[:-1])} and {STATES[-1]['name']}." if len(STATES) > 1 else "HVAC marketing for contractors across the U.S., starting with Texas markets from Houston to El Paso.", body)


BAND = [("houston", "TX"), ("dallas", "TX"), ("san-antonio", "TX"), ("austin", "TX"), ("waco", "TX"), ("phoenix", "AZ"), ("tucson", "AZ"),
        ("atlanta", "GA"), ("savannah", "GA"), ("charlotte", "NC"), ("raleigh", "NC"), ("tampa", "FL"), ("orlando", "FL"), ("jacksonville", "FL")]


def locations_band():
    top = [c for k in BAND for c in ALL_CITIES if (c["slug"], c["_st"]["abbr"]) == k]
    chips = "".join(f'<a href="{u(city_path(c))}">{esc(c["name"])}</a>' for c in top)
    return f"""<section class="section"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">Coast to coast</span><h2>HVAC marketing, market by market.</h2><p class="lede">A page for each market, built on real census and climate data.</p></div>
  <div class="city-links">{chips}<a class="all" href="{u('locations')}">All locations →</a></div>
</div></section>"""


# ---- Guides ---------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guides import GUIDES, UPDATED as GUIDES_UPDATED, AUTHOR as GUIDES_AUTHOR
from vs_guides import VS_GUIDES
GUIDES = GUIDES + VS_GUIDES
try:
    from posts import POSTS, UPDATED as POSTS_UPDATED
except ImportError:
    POSTS = []
POST_SLUGS = {p_["slug"] for p_ in POSTS}
from niches import NICHES
from services import SERVICES
from free_tools import NEW_TOOLS, gcalc_widget
import re as _re


def guide_path(slug):
    return ("post-" if slug in POST_SLUGS else "guide-") + slug


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
        tr = "".join("<tr>" + "".join(f"<td>{_links(x)}</td>" for x in r) + "</tr>" for r in rows)
        return f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'
    if kind == "note":
        return f'<p class="g-note">{_links(b[1])}</p>'
    if kind == "cta":
        return f'<div class="g-cta"><div><b>See how your shop stacks up.</b><p>Free report card: your Google profile, reviews, website and listings graded against the shops near you.</p></div><a class="btn btn-primary" href="{u("report-card")}">Get my report card <span class="arrow">→</span></a></div>'
    return ""


def author_box():
    return f"""<aside class="author-box"><img src="{a('img/logan-320.webp')}" width="96" height="96" alt="Logan, founder of HVAC Marketing HQ" loading="lazy">
  <div><b>Logan</b><span>Founder, {esc(BRAND)} · Waco, Texas</span><p>{esc(BRAND)} works only with HVAC companies. Questions about this guide? <a href="{u('contact')}">Get in touch</a>.</p></div></aside>"""


def byline(updated=None):
    return f'<p class="g-meta g-by"><img src="{a("img/logan-320.webp")}" width="28" height="28" alt="">By {esc(GUIDES_AUTHOR)} · Updated {updated or GUIDES_UPDATED}</p>'


def guide_page(g):
    toc = "".join(f'<li><a href="#s{n}">{esc(h)}</a></li>' for n, (h, _) in enumerate(g["sections"]))
    secs = "".join(f'<h2 id="s{n}">{esc(h)}</h2>' + "".join(guide_block(b) for b in blocks) for n, (h, blocks) in enumerate(g["sections"]))
    take = "".join(f"<li>{esc(t)}</li>" for t in g["takeaways"])
    src = "".join(f'<li><a href="{esc(url)}" rel="noopener">{esc(lbl)}</a></li>' for lbl, url in g["sources"])
    is_post = g["slug"] in POST_SLUGS
    rel = [x for x in GUIDES + POSTS if x["slug"] in g["related"] and x["slug"] != g["slug"]]
    rel_html = "".join(f'<a class="card guide-card" href="{u(guide_path(x["slug"]))}"><span class="eyebrow">{x["read"]} min read</span><h3>{esc(x["title"])}</h3><p>{esc(x["desc"])}</p></a>' for x in rel)
    body = f"""<section class="page-head"><div class="wrap g-wrap">
  <div class="crumbs"><a href="{u('')}">Home</a> / <a href="{u('blog' if is_post else 'guides')}">{'Blog' if is_post else 'Guides'}</a> / {esc(g['short'])}</div>
  <span class="eyebrow">{'Blog' if is_post else 'Guide'} · {g['read']} min read</span>
  <h1>{esc(g['title'])}</h1>
  <p class="lede">{esc(g['desc'])}</p>
  {byline(POSTS_UPDATED if is_post else None)}
</div></section>
<section class="section" style="padding-top:0"><div class="wrap g-wrap">
  <div class="g-take"><h2>Key takeaways</h2><ul class="ticks">{take}</ul></div>
  <nav class="g-toc" aria-label="In this guide"><b>In this guide</b><ol>{toc}</ol></nav>
  <article class="g-body">{secs}
    <h2>Questions</h2>{faq(g['faq'])}
    <h2>Sources</h2><ul class="g-src">{src}</ul>
    {author_box()}
  </article>
</div></section>
<section class="section alt"><div class="wrap"><div class="keep">
  <div><span class="eyebrow">Keep reading</span><h2>Related reading</h2>{rel_html}</div>
  {guide_links(g["slug"])}
</div></div></section>
{next_step()}
"""
    art = ld({"@context": "https://schema.org", "@type": "Article", "headline": g["title"], "description": g["desc"],
              "author": {"@type": "Person", "name": GUIDES_AUTHOR.split(",")[0], "jobTitle": "Founder", "image": f"https://{DOMAIN}/img/logan-320.jpg", "worksFor": {"@type": "Organization", "name": BRAND}}, "publisher": {"@type": "Organization", "name": BRAND},
              "dateModified": g.get("date", "2026-10-12"), "mainEntityOfPage": f"https://{DOMAIN}/{route(guide_path(g['slug']))}"})
    return page(guide_path(g["slug"]), g["title"], g["desc"], body, extra_head=art + faq_ld(g["faq"]), has_form=False)


def niche_page(n):
    setup = "".join(f'<div class="card reveal"><h3>{esc(h)}</h3><p>{esc(t)}</p></div>' for h, t in n["setup"])
    others = "".join(f'<a href="{u(o["slug"])}">{esc(o["name"])}</a>' for o in niches_sorted() if o["slug"] != n["slug"])
    ticket, job, label = n["calc"]
    body = f"""<section class="page-head"><div class="wrap">
  <div class="crumbs"><a href="{u('')}">Home</a> / <a href="{u('hvac-specialties')}">For HVAC</a> / {esc(n['name'])}</div>
  <span class="eyebrow">For HVAC · {esc(n['name'])}</span>
  <h1 style="max-width:22ch">{esc(n['h1'])}</h1>
  <p class="lede">{esc(n['lede'])}</p>
  {url_form()}
</div></section>
<section class="section dark"><div class="wrap">{deep_problem("Where shops like yours lose jobs.", n["pains"])}</div></section>
<section class="section"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">What we set up</span><h2>Built for how your customers really pick a shop.</h2><p class="lede">All of it runs on the same method: Rank, Book, Repeat. <a class="more" href="{u('method')}">How it works →</a></p></div>
  <div class="grid three">{setup}</div>
</div></section>
<section class="section alt"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">Break-even</span><h2>Check the math for your shop.</h2></div>
  {calculator(ticket, job, label)}
</div></section>
<section class="section"><div class="wrap g-wrap">
  <div class="section-head"><span class="eyebrow">Questions</span><h2>Common questions</h2></div>
  {faq(n['faq'])}
  <div class="more-row"><h3>Other HVAC specialties</h3><div class="city-links">{others}</div></div>
</div></section>
{report_card()}
"""
    return page(n["slug"], n["title"], n["desc"], body, extra_head=faq_ld(n["faq"]))


SERVICE_POSTS = {
    "google-ads": ["how-much-to-spend-on-google-ads-hvac", "google-ads-vs-local-services-ads-hvac"],
    "local-services-ads": ["google-local-services-ads-hvac", "google-ads-vs-local-services-ads-hvac"],
    "facebook-ads": ["facebook-ads-for-hvac"],
    "local-seo": ["hvac-seo-what-moves-rankings"],
    "google-business-profile": ["hvac-seo-what-moves-rankings"],
    "review-requests": ["get-more-google-reviews-hvac"],
    "hvac-website-redesign": ["hvac-website-design"],
    "missed-call-text-back": ["hvac-lead-generation-bought-vs-owned"],
    "estimate-follow-up": ["hvac-lead-generation-bought-vs-owned"],
}


def service_page(sv):
    pains = deep_problem(sv.get("pains_h", "Where the calls leak."), sv["pains"])
    steps = "".join(f'<li class="flow-step reveal"><span class="n">{n+1}</span><h3>{esc(a_)}</h3><p>{esc(b)}</p></li>' for n, (a_, b) in enumerate(sv["steps"]))
    inc = "".join(f"<li>{esc(x)}</li>" for x in sv["includes"])
    grp = next(g for g in SERVICE_GROUPS if sv["slug"] in g[2])
    rel = [k for k in grp[2] if k != sv["slug"]] + [k for g in SERVICE_GROUPS if g is not grp for k in g[2][:1]]
    others = "".join(f'<a href="{u(k)}">{esc(svc_info(k)[0])}</a>' for k in rel[:6])
    g = next((x for x in GUIDES if x["slug"] == sv.get("guide")), None)
    extra = [(guide_path(p_["slug"]), p_["title"]) for p_ in POSTS if p_["slug"] in SERVICE_POSTS.get(sv["slug"], [])]
    extra += [("tools/" + t["slug"], t["title"]) for t in TOOLS if t["service"] == sv["slug"]]
    if g:
        extra.insert(0, (guide_path(g["slug"]), g["title"]))
    guide = ('<ul class="read-more">' + "".join(f'<li><a href="{u(k)}">{esc(t)}</a></li>' for k, t in extra) + "</ul>") if extra else ""
    calc = f"""<section class="section alt"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">The math</span><h2>What missed calls cost you.</h2><p class="lede">Put in your own numbers.</p></div>
  {missed_call_calc()}
</div></section>""" if sv.get("calc") else ""
    body = f"""<section class="page-head"><div class="wrap">
  <div class="crumbs"><a href="{u('')}">Home</a> / <a href="{u('services')}">Services</a> / {esc(sv['name'])}</div>
  <span class="eyebrow">{esc(sv['name'])}</span>
  <h1 style="max-width:22ch">{esc(sv['h1'])}</h1>
  <p class="lede">{esc(sv['lede'])}</p>
  {url_form()}
</div></section>
<section class="section dark"><div class="wrap">{pains}</div></section>
<section class="section"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">How it works</span><h2>Set up for you. Running on day one.</h2></div>
  <ol class="flow">{steps}</ol>
</div></section>
{calc}
<section class="section{"" if calc else " alt"}"><div class="wrap"><div class="split">
  <div><span class="eyebrow">What's included</span><h2>What you get.</h2><p class="lede">{esc(sv['plan'])}</p><a class="more" href="{u('plans')}">Compare plans →</a>{guide}</div>
  <div class="card"><ul class="ticks">{inc}</ul></div>
</div>{fit_block(sv["slug"], inner=True)}</div></section>
<section class="section{" alt" if calc else ""}"><div class="wrap g-wrap">
  <div class="section-head"><span class="eyebrow">Questions</span><h2>Common questions</h2></div>
  {faq(sv['faq'])}
  <div class="more-row"><h3>The rest of the system</h3><div class="city-links">{others}<a class="all" href="{u('services')}">All services →</a></div></div>
</div></section>
{report_card()}
"""
    svc = ld({"@context": "https://schema.org", "@type": "Service", "name": sv["title"], "description": sv["desc"], "serviceType": sv["name"],
              "provider": {"@type": "ProfessionalService", "name": BRAND, "url": f"https://{DOMAIN}/"}, "areaServed": "US", "audience": {"@type": "BusinessAudience", "name": "HVAC contractors"}})
    return page(sv["slug"], sv["title"], sv["desc"], body, extra_head=svc + faq_ld(sv["faq"]))


GETTING_STARTED_FAQ = [
    ("Why do you cost less than Scorpion or the big agencies?", "We only do HVAC, ads are an add-on you only pay for if you want them, and we don't do photo or video shoots. Every client gets the same proven system, set up for their shop, instead of a custom project. That keeps our costs, and your price, down."),
    ("What happens if I leave?", "Your website, domain, Google profile, reviews and phone number are yours. We hand over the site and your data, and your number is ported back to you."),
    ("Will I actually get more calls?", "We can't promise a number, and nobody honest can. We guarantee what we control: missed calls texted back in 60 seconds, review requests after every job, and launch in 14 days. Your HQ Command Center shows what's working."),
    ("How much of my time does it take?", "One kickoff call, sharing access, and a review of your site before launch. After that, answering the texts and booking the work, which you're doing already."),
    ("Is there a sales call?", "Only if you want one. Prices and plans are on the site. The report card is free and nobody calls you."),
]


def getting_started_page():
    body = f"""<section class="page-head"><div class="wrap">
  <div class="crumbs"><a href="{u('')}">Home</a> / Getting started</div>
  <span class="eyebrow">Getting started</span>
  <h1 style="max-width:20ch">What happens after you sign up.</h1>
  <p class="lede">No mystery and no long onboarding. Here's exactly what happens, what we do and what we need from you.</p>
</div></section>
<section class="section" style="padding-top:12px"><div class="wrap">
  {terms_strip()}
  <div class="section-head reveal" style="margin-top:32px"><span class="eyebrow">The first 90 days</span><h2>Live in 14 days. A plan for the next 90.</h2></div>
  {first_90()}
</div></section>
<section class="section alt"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">Who does what</span><h2>We do the work. You run the jobs.</h2></div>
  {roles_split()}
</div></section>
<section class="section"><div class="wrap">{compare()}</div></section>
<section class="section alt"><div class="wrap">{report_vs_track()}</div></section>
<section class="section"><div class="wrap g-wrap">
  <div class="section-head"><span class="eyebrow">Questions</span><h2>The questions owners ask first</h2></div>
  {faq(GETTING_STARTED_FAQ)}
</div></section>
{report_card("Start with your free report card")}
"""
    return page("getting-started", "What happens after you sign up", "Exactly what happens after an HVAC shop signs up with HVAC Marketing HQ: the 14-day build, the first 90 days, who does what, and what happens if you leave.", body, extra_head=faq_ld(GETTING_STARTED_FAQ))


def services_overview():
    cols = ""
    for g, icon, slugs in SERVICE_GROUPS:
        links = "".join(f'<li><a href="{u(k)}"><b>{esc(svc_info(k)[0])}</b><span>{esc(svc_info(k)[1])}</span></a></li>' for k in slugs)
        cols += f'<div class="card svc-group reveal"><div class="icon">{ICON[icon]}</div><h3>{esc(g)}</h3><ul>{links}</ul></div>'
    return f"""<section class="section"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">What we do</span><h2>Everything an HVAC shop needs to get found and booked.</h2><p class="lede">Twelve services, one system, run for you. No ad management and no photo shoots, so the price stays fair.</p></div>
  <div class="grid two svc-groups">{cols}</div>
  <p style="margin-top:24px"><a class="more" href="{u('services')}">See all services →</a></p>
</div></section>"""


def services_hub():
    body = f"""<section class="page-head"><div class="wrap">
  <div class="crumbs"><a href="{u('')}">Home</a> / Services</div>
  <span class="eyebrow">Services</span>
  <h1 style="max-width:20ch">HVAC marketing services, run for you.</h1>
  <p class="lede">Your website, your Google profile and your lead system, built once and run every day. Every plan includes the core of each. Higher plans add more pages, more towns and more of our time.</p>
</div></section>
{services_overview().replace('<section class="section">', '<section class="section" style="padding-top:12px">', 1)}
<section class="section alt"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">How it fits together</span><h2>Rank. Book. Repeat.</h2></div>
  {method_block()}
</div></section>
{report_card()}
"""
    return page("services", "HVAC Digital Marketing Services", "HVAC digital marketing services: websites, SEO, Google Business Profile, Google Ads, Local Services Ads, Facebook ads, missed-call text-back, AI phone answering and review requests, run for you.", body)


def specialties_hub():
    cards = "".join(f'<a class="card guide-card reveal" href="{u(n["slug"])}"><span class="eyebrow">For HVAC</span><h3>{esc(n["name"])}</h3><p>{esc(n["desc"])}</p></a>' for n in niches_sorted())
    body = f"""<section class="page-head"><div class="wrap">
  <div class="crumbs"><a href="{u('')}">Home</a> / For HVAC</div>
  <span class="eyebrow">For HVAC</span>
  <h1 style="max-width:20ch">Marketing for every kind of HVAC work.</h1>
  <p class="lede">We only work with HVAC companies, so every page we build speaks to the job your customer needs done. Pick the work you want more of.</p>
</div></section>
<section class="section" style="padding-top:12px"><div class="wrap">
  <h2 class="sr-only">HVAC specialties</h2>
  <div class="grid two">{cards}</div>
</div></section>
{report_card()}
"""
    return page("hvac-specialties", "Marketing for every kind of HVAC company", "HVAC marketing by specialty: residential, commercial, AC repair, heating, ductwork and air quality, installs and replacement, and new HVAC companies.", body)


FIT = {
    "google-ads": (["You want calls this week, not just next season", "You can answer the calls ads bring", "You want to see which ads book jobs"], ["Nobody answers the phone during the day", "You want ads with no tracking"]),
    "local-services-ads": (["You can pass Google's license, insurance and background checks", "You answer most calls live", "You'd rather pay per lead than per click"], ["You can't get verified in your state", "You can't answer leads quickly"]),
    "facebook-ads": (["You sell tune-ups or maintenance plans", "You have your own job photos", "You want past site visitors to see you again"], ["You only want emergency repair calls", "You won't follow up on form leads"]),
    "ai-phone-answering": (["Calls ring out on busy days", "You get after-hours calls", "A live answering service costs too much"], ["You never want a bot talking to customers", "Someone always answers live, every hour"]),
    "missed-call-text-back": (["You miss calls when the crew is on jobs", "Callers rarely leave voicemails", "You get after-hours calls"], ["Someone always answers live, every hour", "You don't want to reply to texts"]),
    "review-requests": (["You finish jobs but rarely ask for reviews", "A nearby shop has far more reviews than you", "You want reviews coming in every week"], ["You want to pick who gets asked (Google doesn't allow it)", "You'd rather buy reviews (it gets profiles suspended)"]),
    "google-business-profile": (["Your profile is missing services, photos or hours", "You don't show up on the map in towns you serve", "Nobody has touched the profile in months"], ["You don't serve customers in person", "You want a fake address in another town"]),
    "local-seo": (["You want to show up in more towns", "Your site has one page for all services", "You'd rather own rankings than rent ads"], ["You need calls this week and nothing else", "You only want ads managed"]),
    "ai-web-chat": (["Visitors come to your site at night", "Your office gets the same questions all day", "You want leads captured after hours"], ["You never want a bot talking to customers", "Your site gets almost no visitors yet"]),
    "ai-search": (["Customers ask ChatGPT or Google AI for recommendations", "You want plain facts about your shop easy to find", "You're building a site anyway"], ["You want guarantees about AI answers (nobody can give them)"]),
    "hvac-website-redesign": (["Your site is slow or hard to use on a phone", "You can't change it without calling someone", "It has no page per service or town"], ["Your site already books calls and ranks well", "You want a one-time site with nothing after"]),
    "estimate-follow-up": (["You send quotes that go quiet", "Nobody owns follow-up in your shop", "Replacement quotes are a big share of your revenue"], ["You close nearly every quote on the spot", "You'd rather not text customers at all"]),
    "seasonal-campaigns": (["You have a list of past customers", "Spring and fall are slow", "You sell maintenance plans"], ["You're booked solid all year", "You don't have customer contact info yet"]),
    "hq-command-center": (["You want to see calls and booked jobs, not clicks", "You've never known what your marketing brings in", "You want to check it on your phone"], ["You already track every call to a booked job yourself"]),
}


def fit_block(slug, inner=False):
    if slug not in FIT:
        return ""
    yes, no = FIT[slug]
    y = "".join(f"<li>{esc(x)}</li>" for x in yes)
    n_ = "".join(f"<li>{esc(x)}</li>" for x in no)
    if inner:  # sits under "What you get" in the same band instead of its own white section
        return f"""<div style="margin-top:56px"><div class="section-head reveal" style="margin-bottom:28px"><span class="eyebrow">Straight answer</span><h2>Is it worth it for your shop?</h2></div>
  <div class="grid two fit"><div class="card fit-yes"><h3>Worth it if</h3><ul class="ticks">{y}</ul></div><div class="card fit-no"><h3>Skip it if</h3><ul class="crosses">{n_}</ul></div></div></div>"""
    return f"""<section class="section"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">Straight answer</span><h2>Is it worth it for your shop?</h2></div>
  <div class="grid two fit"><div class="card fit-yes"><h3>Worth it if</h3><ul class="ticks">{y}</ul></div><div class="card fit-no"><h3>Skip it if</h3><ul class="crosses">{n_}</ul></div></div>
</div></section>"""


# Guides link up to the services and specialties they support.
GUIDE_LINKS = {
    "google-map-pack-hvac": ["google-business-profile", "local-seo", "review-requests"],
    "google-reviews-hvac": ["review-requests", "google-business-profile", "seasonal-campaigns"],
    "missed-call-text-back-hvac": ["missed-call-text-back", "ai-web-chat", "estimate-follow-up"],
    "hvac-website-checklist": ["website", "hvac-website-redesign", "local-seo"],
    "hvac-marketing-cost": ["hq-command-center", "local-seo", "missed-call-text-back"],
    "scorpion-alternative-hvac": ["website", "hq-command-center", "hvac-website-redesign"],
    "questions-to-ask-hvac-marketing-agency": ["hq-command-center", "website", "local-seo"],
    "websites-for-hvac-alternative": ["website", "missed-call-text-back", "hq-command-center"],
    "rs-gonzales-alternative": ["local-seo", "google-business-profile", "hq-command-center"],
    "hook-agency-alternative-hvac": ["local-seo", "website", "hq-command-center"],
    "footbridge-media-alternative-hvac": ["website", "missed-call-text-back", "review-requests"],
}
COMPARE_SLUGS = ["scorpion-alternative-hvac", "websites-for-hvac-alternative", "rs-gonzales-alternative", "hook-agency-alternative-hvac", "footbridge-media-alternative-hvac"]


def compare_hub():
    cards = "".join(f'<a class="card guide-card reveal" href="{u(guide_path(g["slug"]))}"><span class="eyebrow">Comparison</span><h3>{esc(g["title"])}</h3><p>{esc(g["desc"])}</p></a>' for slug in COMPARE_SLUGS for g in GUIDES if g["slug"] == slug)
    body = f"""<section class="page-head"><div class="wrap">
  <div class="crumbs"><a href="{u('')}">Home</a> / Compare agencies</div>
  <span class="eyebrow">Compare</span>
  <h1 style="max-width:22ch">How we compare with other HVAC marketing companies.</h1>
  <p class="lede">Honest side-by-sides built from each company's own published prices and terms, with the date we read them. Where they do something better, we say so.</p>
</div></section>
<section class="section" style="padding-top:12px"><div class="wrap">
  <h2 class="sr-only">Comparisons</h2>
  <div class="grid two">{cards}</div>
  <div style="margin-top:32px">{compare()}</div>
</div></section>
{report_card()}
"""
    return page("compare", "Compare HVAC marketing companies", "Honest comparisons of HVAC Marketing HQ with Scorpion, Websites for HVAC, RS Gonzales, Hook Agency and Footbridge Media, from their own published prices and terms.", body)


def guide_links(slug):
    keys = GUIDE_LINKS.get(slug, [])
    if not keys:
        return ""
    cards = "".join(f'<li><a href="{u(k)}"><b>{esc(svc_info(k)[0])}</b><span>{esc(svc_info(k)[1])}</span></a></li>' for k in keys)
    return f"""<div><span class="eyebrow">Put it to work</span><h2>We can run this for you</h2><ul class="link-list">{cards}</ul></div>"""


TOOLS = [
    {"slug": "missed-call-cost-calculator", "name": "Missed call cost calculator", "line": "What missed calls cost your shop in a year",
     "title": "Missed call cost calculator for HVAC companies",
     "desc": "Free calculator: see what missed calls cost your HVAC company each week, month and year. Put in your own numbers. No email needed.",
     "lede": "Put in how many calls you miss, what a new customer's job is usually worth and how many of them you'd normally book. The math runs in your browser and nothing is sent anywhere.",
     "formula": ["Weekly cost = calls missed a week x average job value x the share you'd book", "Monthly = weekly x 52 / 12", "Yearly = weekly x 52"],
     "improve": [("Text back every missed call", "A text in about a minute keeps the caller talking to you instead of the next shop."), ("Share the inbox", "Calls, texts and chats in one app, so whoever's free can reply."), ("Cover after hours", "AI web chat takes the address and the problem at night, so you can call back first thing.")],
     "service": "missed-call-text-back", "guide": "missed-call-text-back-hvac"},
    {"slug": "hvac-marketing-break-even-calculator", "name": "Marketing break-even calculator", "line": "How many jobs pay for a marketing plan",
     "title": "HVAC marketing break-even calculator",
     "desc": "Free calculator: how many extra service calls or system replacements an HVAC company needs each month to pay for a marketing plan. Your numbers, no email needed.",
     "lede": "Any marketing spend should pay for itself. Put in the monthly price, your average ticket and your margin to see how many extra jobs cover it. Change the plan price to test any agency's quote.",
     "formula": ["Service calls to break even = monthly price / (average ticket x gross margin), rounded up", "Replacements to break even = monthly price / (average replacement x gross margin)", "Bought leads for the same money = monthly price / price per lead"],
     "improve": [("Track booked jobs, not clicks", "You can only check the math if you can see which calls became jobs."), ("Follow up on quotes", "One extra replacement a month changes the math more than any number of clicks."), ("Ask every customer for a review", "More reviews help more of the calls you already get turn into jobs.")],
     "service": "hq-command-center", "guide": "hvac-marketing-cost"},
    {"slug": "google-review-gap-calculator", "name": "Review gap calculator", "line": "How long to catch the top shop's reviews",
     "title": "Google review gap calculator for HVAC companies",
     "desc": "Free calculator: how many months it takes your HVAC company to catch a competitor's Google review count, based on your jobs a month and how many customers leave a review.",
     "lede": "Homeowners compare review counts on the map. Put in your count, the top shop's count, your jobs a month and how many customers leave a review to see how long it takes to catch up.",
     "formula": ["Reviews a month = finished jobs a month x share who leave a review", "Months to catch up = (their reviews - your reviews) / (your reviews a month - their reviews a month)", "If they add reviews as fast as you, you never catch up, so the tool says so"],
     "improve": [("Ask after every job", "A text right after the job, while the customer is happy, gets far more reviews than asking now and then."), ("Ask everyone", "Google's rules say don't pick and choose who gets asked. Asking everyone is also how the count grows."), ("Reply to every review", "Replies show the next homeowner that a real owner is paying attention.")],
     "service": "review-requests", "guide": "google-reviews-hvac"},
]


TOOLS = TOOLS + NEW_TOOLS


def review_gap_calc():
    return """<div class="calc rcalc">
  <div>
    <div class="field"><label for="r-you">Your Google reviews today</label><input id="r-you" type="text" inputmode="decimal" name="you" value="40"></div>
    <div class="field"><label for="r-them">The top shop near you</label><input id="r-them" type="text" inputmode="decimal" name="them" value="400"></div>
    <div class="field"><label for="r-jobs">Jobs you finish a month</label><input id="r-jobs" type="text" inputmode="decimal" name="jobs" value="150"></div>
    <div class="field"><label for="r-rate">Share of customers who leave a review</label><select id="r-rate" name="rate"><option value="5">5%</option><option value="10">10%</option><option value="15" selected>15%</option><option value="20">20%</option><option value="30">30%</option></select><div class="hint">A guess. Change it to match your shop.</div></div>
    <div class="field"><label for="r-their">Reviews the top shop adds a month</label><input id="r-their" type="text" inputmode="decimal" name="their" value="6"><div class="hint">Count their reviews from the last 30 days on Google.</div></div>
  </div>
  <div class="calc-out" aria-live="polite">
    <div class="row"><span class="big" data-out="mine">–</span><p>new reviews a month for you</p></div>
    <div class="row"><span class="big" data-out="months">–</span><p>months to catch the top shop</p></div>
    <p style="font-size:.85rem">Your numbers; this is math, not a promise of results.</p>
  </div>
</div>"""


def tool_widget(slug):
    nt = next((t for t in NEW_TOOLS if t["slug"] == slug), None)
    if nt:
        return gcalc_widget(nt)
    if slug == "missed-call-cost-calculator":
        return missed_call_calc()
    if slug == "hvac-marketing-break-even-calculator":
        return calculator()
    return review_gap_calc()


def related_tools(t, n=4):
    grp = next((ks for _, ks in TOOL_GROUPS if t["slug"] in ks), [])
    order = [k for k in grp if k != t["slug"]] + [k for _, ks in TOOL_GROUPS for k in ks if k not in grp]
    tb = {x["slug"]: x for x in TOOLS}
    return [tb[k] for k in order if k in tb][:n]


def tool_page(t):
    formula = "".join(f"<li>{esc(x)}</li>" for x in t["formula"])
    improve = "".join(f'<div class="card reveal"><h3>{esc(h)}</h3><p>{esc(p_)}</p></div>' for h, p_ in t["improve"])
    others = "".join(f'<a href="{u("tools/" + o["slug"])}">{esc(o["name"])}</a>' for o in related_tools(t))
    g = next(x for x in GUIDES if x["slug"] == t["guide"])
    sn, sd = svc_info(t["service"])
    body = f"""<section class="page-head"><div class="wrap">
  <div class="crumbs"><a href="{u('')}">Home</a> / <a href="{u('tools')}">Free tools</a> / {esc(t['name'])}</div>
  <span class="eyebrow">Free tool · No email needed</span>
  <h1 style="max-width:22ch">{esc(t['title'])}</h1>
  <p class="lede">{esc(t['lede'])}</p>
</div></section>
<section class="section" style="padding-top:12px"><div class="wrap">
  <h2 class="sr-only">Calculator</h2>
  {tool_widget(t['slug'])}
</div></section>
<section class="section alt"><div class="wrap split">
  <div><span class="eyebrow">The math</span><h2>How it's worked out.</h2><p class="lede">No hidden numbers. Here's every step.</p></div>
  <div class="card"><ul class="ticks">{formula}</ul></div>
</div></section>
<section class="section"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">Improve the number</span><h2>Three ways to move it.</h2></div>
  <div class="grid three">{improve}</div>
  <p style="margin-top:22px"><a class="more" href="{u(t['service'])}">{esc(sn)}: {esc(sd)} →</a><br><a class="more" href="{u(guide_path(g['slug']))}">Read the guide: {esc(g['title'])} →</a></p>
  <div class="more-row"><h3>More free calculators</h3><div class="city-links">{others}<a class="all" href="{u('tools')}">All tools →</a></div></div>
</div></section>
{report_card("Got your number? See what is behind it.")}
"""
    app_ld = ld({"@context": "https://schema.org", "@type": "WebApplication", "name": t["title"], "description": t["desc"], "applicationCategory": "BusinessApplication",
                 "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, "provider": {"@type": "Organization", "name": BRAND}})
    if any(x["slug"] == t["slug"] for x in NEW_TOOLS):
        app_ld += f'<script src="{asset_v("gcalc.js")}" defer></script>'
    return page("tools/" + t["slug"], t["title"], t["desc"], body, extra_head=app_ld)


TOOL_GROUPS = [
    ("Ads and lead costs", ["hvac-cost-per-lead-calculator", "google-ads-budget-calculator-hvac", "lsa-cost-calculator", "hvac-marketing-budget-calculator", "hvac-marketing-break-even-calculator", "hvac-seo-roi-calculator"]),
    ("Calls and booking", ["missed-call-cost-calculator", "after-hours-call-calculator", "hvac-close-rate-calculator", "hvac-estimate-follow-up-calculator"]),
    ("Customers and reviews", ["google-review-gap-calculator", "hvac-maintenance-plan-calculator", "hvac-customer-lifetime-value-calculator"]),
]


def tools_hub():
    tb = {t["slug"]: t for t in TOOLS}
    cards = "".join(f'<div class="section-head" style="margin-top:28px"><h2>{esc(g)}</h2></div><div class="grid three">' + "".join(
        f'<a class="card guide-card reveal" href="{u("tools/" + tb[k]["slug"])}"><span class="eyebrow">Free tool</span><h3>{esc(tb[k]["name"])}</h3><p>{esc(tb[k]["line"])}</p></a>' for k in ks if k in tb) + "</div>" for g, ks in TOOL_GROUPS)
    body = f"""<section class="page-head"><div class="wrap">
  <div class="crumbs"><a href="{u('')}">Home</a> / Free tools</div>
  <span class="eyebrow">Free tools</span>
  <h1 style="max-width:20ch">Free calculators for HVAC owners.</h1>
  <p class="lede">Check the math on ads, missed calls, marketing spend and reviews with your own numbers. No email, no sign-up, and nothing you type leaves your browser.</p>
</div></section>
<section class="section" style="padding-top:12px"><div class="wrap">
  <h2 class="sr-only">All tools</h2>
  {cards}
</div></section>
{report_card("Want the full picture? Get your report card")}
"""
    return page("tools", "Free calculators for HVAC companies", f"{len(TOOLS)} free, no-sign-up calculators for HVAC owners: cost per lead, Google Ads and LSA budgets, missed calls, close rate, maintenance plans, reviews and more.", body)


def contact_page():
    body = f"""<section class="page-head"><div class="wrap">
  <div class="crumbs"><a href="{u('')}">Home</a> / Contact</div>
  <span class="eyebrow">Contact</span>
  <h1 style="max-width:20ch">Talk to a person who only does HVAC.</h1>
  <p class="lede">Ask a question, book a short call, or start with the free report card. No pressure and no long sales process.</p>
</div></section>
<section class="section" style="padding-top:12px"><div class="wrap">
  <h2 class="sr-only">Ways to reach us</h2>
  <div class="grid three">
    <div class="card reveal"><div class="icon">{ICON['chat']}</div><h3>Email us</h3><p>Questions about plans, your site or how it works.</p><p><a href="mailto:{EMAIL}">{EMAIL}</a></p></div>
    <div class="card reveal"><div class="icon">{ICON['cal']}</div><h3>Book a 15-minute call</h3><p>A quick look at your shop and whether we're a fit.</p><p><a href="{esc(call_link())}">Pick a time →</a></p></div>
    <div class="card reveal"><div class="icon">{ICON['chart']}</div><h3>Get your report card</h3><p>See where you stand on Google before you talk to anyone.</p><p><a href="#report-card">Start here →</a></p></div>
  </div>
</div></section>
<section class="section alt"><div class="wrap split">
  <div><span class="eyebrow">What to expect</span><h2>What happens when you reach out.</h2></div>
  <div class="card"><ul class="ticks"><li>A real person reads every message. No call center.</li><li>No sales sequence. If we're not a fit, we'll say so.</li><li>Prices are on the site, so the call is about your shop, not a quote.</li><li>Nothing is signed on the first call.</li></ul></div>
</div></section>
{report_card()}
"""
    return page("contact", "Contact", "Contact HVAC Marketing HQ: email, book a 15-minute call, or get a free report card on how your HVAC company shows up on Google.", body)


def about_page():
    beliefs = [
        ("HVAC only", "One trade means we know the jobs, the seasons and the searches. Every page, script and campaign is built for heating and cooling work."),
        ("You own everything", "Your domain, site content, Google profile, reviews, ad accounts and customer list are in your name. Leave anytime and take it all."),
        ("Prices on the site", "Plan prices are published on the site. The call is about your shop, not a quote."),
        ("Booked jobs, not clicks", "We judge our work by calls answered and jobs booked, on a dashboard you can check yourself."),
    ]
    cards = "".join(f'<div class="card reveal"><h3>{esc(h)}</h3><p>{esc(t)}</p></div>' for h, t in beliefs)
    body = f"""<section class="page-head"><div class="wrap about-head">
  <div>
    <div class="crumbs"><a href="{u('')}">Home</a> / About</div>
    <span class="eyebrow">About {esc(BRAND)}</span>
    <h1 style="max-width:18ch">Built for the HVAC shops that do the work.</h1>
    <p class="lede">{esc(BRAND)} is a marketing company for HVAC contractors, and only HVAC contractors. We're based in Waco, Texas, and work with shops anywhere in the U.S.</p>
  </div>
  <figure class="about-photo"><img src="{a('img/logan-portrait-600.webp')}" width="600" height="900" alt="Logan, founder of {esc(BRAND)}" loading="eager"><figcaption><b>Logan</b><span>Founder</span></figcaption></figure>
</div></section>
<section class="section"><div class="wrap g-wrap">
  <span class="eyebrow">A note from the founder</span>
  <h2>Why I started {esc(BRAND)}.</h2>
  <div class="about-note">
    <p>Most HVAC owners I talk to are great at the work and stuck with marketing that doesn't add up. They're paying for a site they don't own, leads they share with three other shops, or a report full of clicks that never turned into a job.</p>
    <p>I started {esc(BRAND)} to do it the other way. One trade. Prices on the site. A fast website, a Google profile that's actually run, every missed call texted back, and reviews coming in after every job, all in your name, all tracked to booked jobs.</p>
    <p>If we're not the right fit for your shop, I'll tell you. If we are, you'll always know exactly what you're paying for and what it's bringing in.</p>
    <p class="about-sign">Logan<br><span>Founder, {esc(BRAND)}</span></p>
  </div>
</div></section>
<section class="section dark"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">What we believe</span><h2>How we work.</h2></div>
  <div class="grid two">{cards}</div>
</div></section>
<section class="section"><div class="wrap split">
  <div><span class="eyebrow">The facts</span><h2>{esc(BRAND)} at a glance.</h2></div>
  <div class="card"><ul class="ticks"><li>HVAC contractors only, residential and light commercial</li><li>Based in Waco, Texas, serving shops across the U.S.</li><li>The method: <a href="{u('method')}">Rank, Book, Repeat</a></li><li>Published <a href="{u('plans')}">pricing</a>, with a 30-day money-back guarantee</li><li>Email: <a href="mailto:{EMAIL}">{EMAIL}</a></li></ul></div>
</div></section>
{report_card()}
"""
    ld_ = ld({"@context": "https://schema.org", "@type": "AboutPage", "name": f"About {BRAND}", "url": f"https://{DOMAIN}/about",
              "mainEntity": {"@type": "Organization", "name": BRAND, "url": f"https://{DOMAIN}/", "email": EMAIL, "address": {"@type": "PostalAddress", "addressLocality": "Waco", "addressRegion": "TX", "addressCountry": "US"},
                             "founder": {"@type": "Person", "name": "Logan", "jobTitle": "Founder", "image": f"https://{DOMAIN}/img/logan-320.jpg"}}})
    return page("about", f"About {BRAND}", f"About {BRAND}: an HVAC-only marketing company based in Waco, Texas. Meet the founder and how we work.", body, extra_head=ld_)


PATH_STEPS = [
    ("search", "Rank", "Searches on Google", "A homeowner with a hot house types \"ac repair near me\" on their phone."),
    ("pin", "Rank", "Picks from the map", "Three shops show up. Stars, reviews, photos and hours decide who gets the call."),
    ("phone", "Book", "Calls or chats", "They tap call. After hours, they ask your site's chat instead."),
    ("chat", "Book", "Gets a text if you miss it", "Busy on a job? A text from your number goes out within 60 seconds."),
    ("cal", "Book", "Books the job", "Whoever's free replies from the shared inbox and gets it on the schedule."),
    ("star", "Repeat", "Leaves a review", "A text after the job asks for a review, and that review helps win the next search."),
]


def homeowner_path():
    steps = "".join(f'<li class="path-step reveal" data-ph="{ph.lower()}"><span class="path-ic">{ICON[ic]}</span><span class="path-ph">{ph}</span><h3>{esc(h)}</h3><p>{esc(t)}</p></li>' for ic, ph, h, t in PATH_STEPS)
    return f"""<section class="section" id="method"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">How a homeowner picks a shop</span><h2>From a broken AC to a booked job, in six steps.</h2><p class="lede">Ranking gets you to step two. We run all six: Rank, Book, Repeat.</p></div>
  <ol class="path">{steps}</ol>
  <p style="margin-top:30px"><a class="btn btn-ghost" href="{u('method')}">See the full method <span class="arrow">→</span></a></p>
</div></section>"""


PILLAR_FAQ = [
    ("What is HVAC marketing?", "Everything that gets a homeowner or business to call your shop instead of the next one: showing up on Google and the map, a website that turns visits into calls, answering and following up fast, and turning finished jobs into reviews and repeat work."),
    ("What's the best marketing for an HVAC company?", "For most owner-run shops, a complete Google Business Profile, steady reviews and a fast site with a page per service and town come first, because that's where homeowners pick a shop. Answering every call matters just as much, since a lead you don't answer is wasted."),
    ("How long does HVAC SEO take to work?", "It depends on your town, your competition and where you start, so nobody can honestly promise a date. Profile fixes and review growth can show up within weeks; new pages ranking usually takes months. Be wary of anyone who guarantees page one."),
    ("Should I run Google Ads or do SEO?", "Ads bring calls as long as you pay; SEO and your map listing keep working after you stop. Many shops do both. We run both: ads as an add-on, on top of the parts you own, like your site, your profile, your reviews and your follow-up."),
    ("Are Google Local Services Ads worth it for HVAC?", "They can be, since you pay per lead and the Google Verified badge shows at the top. Your reviews and how fast you answer affect how often they show, so the basics we run help there too."),
    ("How do I get more HVAC maintenance plan sign-ups?", "Ask on every job, put the plan on its own page, and remind past customers before each season. We send the reminders; your techs make the ask."),
    ("How do I market heating in a warm state?", "Heat pumps run in both seasons and cold snaps bring a rush of calls. Have heating pages and your profile ready before the first cold front, not during it."),
    ("Should I market indoor air quality and ductwork?", "Yes, if you do the work. People search for the symptom, like a hot room or dusty vents, so pages that explain the problem plainly bring in calls that turn into bigger jobs."),
    ("Do you work with ServiceTitan, Housecall Pro or Jobber?", "Yes. On our Dominate plan we connect them so booked jobs and customers flow into your dashboard and campaigns."),
    ("Should I put financing on my website?", "If you offer it, put it on the replacement pages where people decide. Hiding it in the footer doesn't help anyone."),
    ("Does commercial HVAC need different marketing?", "Partly. Property managers want proof you can handle it: license, insurance, service area and response times, on pages written for them, separate from your residential pages."),
    ("How much should an HVAC company spend on marketing?", "There's no single right number. Work out how many extra jobs pay for the spend with our free break-even calculator, and compare published prices in our cost guide."),
]


def pillar_page():
    svc = lambda keys: "".join(f'<li><a href="{u(k)}"><b>{esc(svc_info(k)[0])}</b></a> {esc(svc_info(k)[1])}</li>' for k in keys)
    gd = lambda slugs: "".join(f'<li><a href="{u(guide_path(x["slug"]))}">{esc(x["title"])}</a></li>' for x in GUIDES if x["slug"] in slugs)
    spec = "".join(f'<a class="card guide-card" href="{u(n["slug"])}"><span class="eyebrow">For HVAC</span><h3>{esc(n["name"])}</h3><p>{esc(n["nav"])}</p></a>' for n in niches_sorted())
    cities = "".join(f'<p><b><a href="{u(state_key(st))}">{esc(st["name"])}</a>:</b> ' + " · ".join(f'<a href="{u(city_path(c))}">{esc(c["name"])}</a>' for c in st["cities"]) + "</p>" for st in STATES)
    tools_ = "".join(f'<li><a href="{u("tools/" + t["slug"])}">{esc(t["name"])}</a>: {esc(t["line"])}</li>' for t in TOOLS)
    toc = [("s-what", "What HVAC marketing is"), ("s-rank", "Rank: get found first"), ("s-book", "Book: answer and follow up"), ("s-repeat", "Repeat: reviews and past customers"),
           ("s-cost", "What it costs"), ("s-spec", "By specialty"), ("s-loc", "By location"), ("s-faq", "Questions")]
    toc_html = "".join(f'<li><a href="#{a_}">{esc(b)}</a></li>' for a_, b in toc)
    body = f"""<section class="page-head"><div class="wrap g-wrap">
  <div class="crumbs"><a href="{u('')}">Home</a> / HVAC marketing</div>
  <span class="eyebrow">The complete guide</span>
  <h1>HVAC marketing: how owner-run shops get found and booked</h1>
  <p class="lede">Everything that decides whether a homeowner calls your shop or the next one, in plain words, with a link to the detail on each part.</p>
  {byline()}
</div></section>
<section class="section" style="padding-top:0"><div class="wrap g-wrap">
  <div class="g-take"><h2>The short version</h2><ul class="ticks"><li>Homeowners pick from the map, so your Google profile and reviews matter most.</li><li>A lead you don't answer is wasted, so answering and following up are marketing too.</li><li>Past customers are the cheapest jobs you'll ever book. Remind them before each season.</li><li>Own everything: your site, domain, profile, reviews and customer list.</li></ul></div>
  <nav class="g-toc" aria-label="In this guide"><b>In this guide</b><ol>{toc_html}</ol></nav>
  <article class="g-body">
    <h2 id="s-what">What HVAC marketing is</h2>
    <p>HVAC marketing is three jobs that feed each other. <b>Rank</b>: show up first when someone nearby searches. <b>Book</b>: answer every call, text and chat, and follow up until the job is on the schedule. <b>Repeat</b>: turn every finished job into a review and the next visit. Most agencies sell one of the three. A shop needs all of them working together.</p>
    <h2 id="s-rank">Rank: get found first</h2>
    <p>When the AC quits, a lot of homeowners search on their phone and pick from the shops on the map. Google ranks those on distance, relevance and prominence. You can't move your shop, but you control the other two.</p>
    <ul class="ticks">{svc(["google-business-profile", "local-seo", "website", "ai-search"])}</ul>
    <p>Read more:</p><ul>{gd(["google-map-pack-hvac", "hvac-website-checklist"])}</ul>
    <h2 id="s-book">Book: answer and follow up</h2>
    <p>Ranking only matters if someone answers. Many callers who hit voicemail just call the next shop. Quotes go quiet when nobody follows up.</p>
    <ul class="ticks">{svc(["missed-call-text-back", "ai-web-chat", "estimate-follow-up", "app"])}</ul>
    <p>Read more:</p><ul>{gd(["missed-call-text-back-hvac"])}</ul>
    <h2 id="s-repeat">Repeat: reviews and past customers</h2>
    <p>Fresh reviews help you rank and help the next homeowner pick you. Past customers already trust you; they just need a reminder before the season turns.</p>
    <ul class="ticks">{svc(["review-requests", "seasonal-campaigns", "hq-command-center"])}</ul>
    <p>Read more:</p><ul>{gd(["google-reviews-hvac"])}</ul>
    <h2 id="s-cost">What it costs</h2>
    <p>Prices range from a few hundred dollars a month for a template site to several thousand for a big agency, plus ad spend. Whatever you pay, check how many extra jobs cover it.</p>
    <ul>{tools_}</ul>
    <p>Read more:</p><ul>{gd(["hvac-marketing-cost", "questions-to-ask-hvac-marketing-agency", "scorpion-alternative-hvac"])}</ul>
    <p>Our own prices are on the <a href="{u('plans')}">plans page</a>.</p>
  </article>
</div></section>
<section class="section alt" id="s-spec"><div class="wrap">
  <div class="section-head"><span class="eyebrow">By specialty</span><h2>Marketing for the work you want more of</h2></div>
  <div class="grid three">{spec}</div>
</div></section>
<section class="section" id="s-loc"><div class="wrap g-wrap">
  <div class="section-head"><span class="eyebrow">By location</span><h2>HVAC marketing by state</h2><p class="lede">Each page uses real local numbers: population and climate, plus licensed contractors where the state publishes them. Pick a state or a city:</p></div>
  <div class="city-links-by-state">{cities}</div>
</div></section>
<section class="section alt" id="s-faq"><div class="wrap g-wrap">
  <div class="section-head"><span class="eyebrow">Questions</span><h2>HVAC marketing questions owners ask</h2></div>
  {faq(PILLAR_FAQ)}
  {author_box()}
</div></section>
{report_card()}
"""
    art = ld({"@context": "https://schema.org", "@type": "Article", "headline": "HVAC marketing: how owner-run shops get found and booked",
              "author": {"@type": "Person", "name": GUIDES_AUTHOR.split(",")[0], "jobTitle": "Founder", "image": f"https://{DOMAIN}/img/logan-320.jpg", "worksFor": {"@type": "Organization", "name": BRAND}}, "publisher": {"@type": "Organization", "name": BRAND}, "dateModified": BUILD_DATE})
    return page("hvac-marketing", "HVAC Marketing: The Complete Guide for Owner-Run Shops", "HVAC marketing explained: how to get found on Google and the map, answer and book every call, and turn jobs into reviews and repeat work. With costs, tools and FAQs.", body, extra_head=art + faq_ld(PILLAR_FAQ))


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


def blog_page():
    cards = "".join(f'<a class="card guide-card reveal" href="{u(guide_path(g["slug"]))}"><span class="eyebrow">{g["read"]} min read</span><h3>{esc(g["title"])}</h3><p>{esc(g["desc"])}</p></a>' for g in POSTS)
    body = f"""<section class="page-head"><div class="wrap">
  <div class="crumbs"><a href="{u('')}">Home</a> / Blog</div>
  <span class="eyebrow">Blog</span>
  <h1 style="max-width:20ch">HVAC marketing, one question at a time.</h1>
  <p class="lede">Short, sourced answers to the questions HVAC owners ask about ads, SEO, reviews and leads. For the deep dives, see our <a href="{u('guides')}">guides</a>.</p>
</div></section>
<section class="section" style="padding-top:12px"><div class="wrap">
  <h2 class="sr-only">All posts</h2>
  <div class="grid two">{cards}</div>
</div></section>
{report_card("Rather have it checked for you?")}
"""
    return page("blog", "HVAC Marketing Blog", "Short, sourced posts for HVAC owners on Google Ads, Local Services Ads, SEO, reviews, websites and lead generation.", body)


def towns_json():
    """Town suggestions for the report card form: our city pages first (biggest first), then their
    nearby towns, then every US place in data/us-cities.csv (kelvins/US-Cities-Database, MIT)."""
    import csv
    out, seen = [], set()
    def add(t):
        if t.lower() not in seen:
            seen.add(t.lower()); out.append(t)
    with open(os.path.join(os.path.dirname(_DATA), "us-cities.csv"), newline="") as f:
        places = sorted({(r["CITY"], r["STATE_CODE"]) for r in csv.DictReader(f) if r["CITY"] and r["STATE_CODE"]})
    real = {f"{c}, {st}".lower() for c, st in places}
    big = sorted(ALL_CITIES, key=lambda c: -(c.get("population_2020") or 0))
    big_names = {c["name"].lower(): c["_st"]["abbr"] for c in big}
    for c in big:
        add(f'{c["name"]}, {c["_st"]["abbr"]}')
    for c in big:
        st = c["_st"]["abbr"]
        for n in c.get("nearby") or []:
            # "Nearby" can cross a state line (Jersey City next to New York), so keep only real towns in this state.
            if f"{n}, {st}".lower() in real and big_names.get(n.lower(), st) == st:
                add(f"{n}, {st}")
    for c, st in places:
        add(f"{c}, {st}")
    return json.dumps(out, separators=(",", ":"))


def sitemap_xml(paths):
    urls = "".join(f"<url><loc>https://{DOMAIN}/{p_}</loc><lastmod>{BUILD_DATE}</lastmod></url>" for p_ in paths)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n'


# ---- Pages -----------------------------------------------------------------------
def home():
    body = f"""<section class="hero"><div class="hero-grid-bg" aria-hidden="true"></div><div class="wrap hero-grid">
  <div>
    <span class="chip-top"><i>❄</i>Built only for HVAC contractors</span>
    <h1>Rank higher. <span class="grad">Book every call.</span></h1>
    <p class="lede">We build your website, run your Google profile and text back every missed call in 60 seconds, guaranteed. Start with a free report card on how you stack up locally.</p>
    {url_form()}
    <div class="hero-points"><span>Live in 14 days</span><span>We run it for you</span><span>You own everything</span></div>
    <p class="hero-alt">Rather talk first? <a href="{esc(call_link())}">Book a 15-minute call</a></p>
  </div>
  {hero_visual()}
</div></section>
<div class="wrap terms-wrap">{terms_strip()}</div>

<section class="section dark"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">Sounds familiar?</span><h2>The phone rings when you can't answer it.</h2><p class="lede">Most shops don't lose jobs to a better competitor. They lose them to voicemail, slow follow-up and a Google profile nobody runs.</p></div>
  {pains_grid()}
</div></section>

{homeowner_path()}

<section class="section alt"><div class="wrap">
  <div class="section-head center reveal"><span class="eyebrow">What runs behind it</span><h2>One system. Every piece working.</h2><p class="lede">Your site, your Google profile and your lead system, built once and run for you. Your office just answers the texts.</p></div>
  {bento()}
  <p style="margin-top:30px;text-align:center"><a class="btn btn-ghost" href="{u('services')}">See all twelve services <span class="arrow">→</span></a></p>
</div></section>

<section class="section" id="tech"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">The tech</span><h2>Built fast, on purpose.</h2><p class="lede">A slow site loses the homeowner before the page loads. Here's this site's own score from Google's test.</p></div>
  {tech()}
</div></section>

<section class="section dark"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">Guarantees</span><h2>We guarantee what we control.</h2></div>
  {promise()}
  <div style="margin-top:28px">{ownership()}</div>
</div></section>

<section class="section" id="pricing"><div class="wrap">
  <div class="section-head center reveal"><span class="eyebrow">Pricing</span><h2>Pick a plan. Go live in 14 days.</h2><p class="lede">Every plan texts back every missed call. Monthly billing starts at launch, not at signing.</p></div>
  {plans_cards()}
  <p style="margin-top:24px;text-align:center"><a class="more" href="{u('plans')}">Compare plans side by side, with add-ons →</a></p>
</div></section>

<section class="section alt"><div class="wrap" style="max-width:900px">
  <div class="section-head reveal"><span class="eyebrow">Questions</span><h2>Straight answers.</h2></div>
  {faq(COMMON_FAQ[:6])}
  <p style="margin-top:22px"><a class="more" href="{u('plans')}#faq">All pricing and contract questions →</a> · <a class="more" href="{u('getting-started')}">What happens after you sign up →</a> · <a class="more" href="{u('guides')}">Guides, with sources →</a></p>
</div></section>

{locations_band().replace('<section class="section">', '<section class="section tight">', 1)}

{report_card("See where you stand before you spend a dollar.")}
"""
    return page("", f"Web Design & SEO for HVAC Businesses | {BRAND}",
                "Websites, Google profiles and missed-call text-back for HVAC companies. Every missed call texted back in 60 seconds, guaranteed.", body,
                extra_head=org_ld() + faq_ld(COMMON_FAQ[:6]))


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
  <h1>Rank. Book. Repeat.</h1>
  <p class="lede">Most agencies sell you a website, or ads, or software. We run the three jobs that actually fill an HVAC schedule, as one system, on every plan.</p>
</div></section>
<section class="section" style="padding-top:0"><div class="wrap"><h2 class="sr-only">The three phases</h2>{method_block()}</div></section>
{"".join(phases)}
<section class="section"><div class="wrap split">
  <div><span class="eyebrow">Every plan</span><h2>Watch it work in your HQ Command Center.</h2><p class="lede">Calls, texts, booked jobs and reviews, updated as they happen.</p></div>
  {dashboard()}
</div></section>
<section class="section alt"><div class="wrap">
  <div class="section-head"><span class="eyebrow">Your first 90 days</span><h2>What happens after you sign.</h2></div>
  {first_90()}
  {roles_split()}
</div></section>
{report_card("See where you stand on all three.")}
"""
    return page("method", "The method: Rank, Book, Repeat", "How we rank you on Google, answer and book every call, and turn every job into the next one.", body)


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
        "title": "Website", "seo_title": "HVAC Web Design: Websites Built to Book Calls", "h1": "HVAC web design built to book service calls.",
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
        "list": ["We ask every customer for a review and never filter out unhappy ones (Google doesn't allow it)", "Map spam reports on fake competitor listings", "Call tracking by source", "Google Ads, Local Services Ads and Facebook ads available as add-ons", "No promises of rankings, only of the work"],
    },
    "app": {
        "title": "Lead system", "seo_title": "HVAC Lead Generation System: Every Lead in One Inbox", "h1": "Every call, text and form in one inbox.",
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
            ("Do you run Google Ads or Local Services Ads?", "Yes, as an add-on to any plan. Ads work best once calls are answered and your profile is strong, and every plan already covers that part."),
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
    def sec(inner, cls=None):
        nonlocal alt
        if cls is None:
            cls = "section alt" if alt else "section"
            alt = not alt
        out.append(f'<section class="{cls}"><div class="wrap">{inner}</div></section>')
    if "problem" in d: sec(deep_problem(*d["problem"]), "section dark")
    if "personas" in d: sec(deep_personas(*d["personas"]))
    if "auto" in d: sec(deep_auto(*d["auto"]))
    if "flow" in d: sec(deep_flow(*d["flow"]))
    if "ai" in d: sec(deep_ai(*d["ai"]))
    if "attribution" in d: sec(deep_attr(*d["attribution"]))
    if d.get("replaces"): sec(replaces())
    if d.get("speed"): sec('<div class="section-head reveal"><span class="eyebrow">Speed</span><h2>Slow sites lose jobs.</h2><p class="lede">This is how our own site scores on Google\'s test. Yours is built the same way.</p></div>' + tech())
    if "timeline" in d: sec(deep_timeline(*d["timeline"]))
    if d.get("faq"):  # questions sit above the closing report card, keeping the band rhythm
        sec(f'<div style="max-width:900px;margin:0 auto"><div class="section-head"><span class="eyebrow">Questions</span><h2>{OFFER_CONTENT[key]["title"]} questions</h2></div>{faq(d["faq"])}</div>')
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
  <div class="crumbs"><a href="{u('')}">Home</a> / <a href="{u('services')}">Services</a> / {o['title']}</div>
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
"""
    items = OFFER_DEEP.get(key, {}).get("faq")
    return page(key, o.get("seo_title", f"{_strip(o['title'])} for HVAC companies"), o["lede"], body, extra_head=faq_ld(items) if items else "")


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
  <div class="split" style="margin-top:80px">
  <div><span class="eyebrow">After the report card</span><h2>You've got the grades. Now what?</h2><p class="lede">Some owners fix it themselves, and the report shows exactly where to start. Others hand it to us. Either way, it's yours to keep.</p></div>
  <div class="card"><ul class="ticks"><li>Graded only on what anyone can see in public</li><li>The same facts always give the same grade</li><li>Plain English, no jargon</li><li>Re-grade anytime to see what changed</li></ul><a class="more" href="{esc(call_link())}">Rather talk it through? Book a 15-minute call →</a></div>
  </div>
</div></section>
{report_card()}
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
  <p class="muted" style="margin-top:18px;font-size:.9rem">Rate lock: the first 25 shops keep the annual price on monthly billing, locked for as long as they stay. Normal texting, calling and AI use is included; large campaigns beyond your plan are billed at cost. <span class="tbd">Terms TBD</span></p>
  {addons()}
</div></section>
<section class="section alt"><div class="wrap">{replaces()}</div></section>
<section class="section"><div class="wrap">
  {compare()}
  <div style="margin-top:28px">{report_vs_track()}</div>
  <p style="margin-top:18px"><a class="more" href="{u('getting-started')}">What happens after you sign up →</a></p>
</div></section>
<section class="section dark"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">Guarantees</span><h2>We guarantee what we control.</h2></div>
  {promise()}
</div></section>
<section class="section"><div class="wrap">
  <div class="section-head reveal"><span class="eyebrow">Is this for you?</span><h2>Who we work with, and who we don't.</h2></div>
  {fit()}
  <div class="section-head reveal" style="margin-top:72px"><span class="eyebrow">Break-even</span><h2>Check the math for your shop.</h2></div>
  {calculator()}
</div></section>
<section class="section alt" id="faq"><div class="wrap" style="max-width:860px">
  <div class="section-head"><span class="eyebrow">Questions</span><h2>Pricing questions</h2></div>
  {faq(COMMON_FAQ)}
</div></section>
{report_card("Not sure which plan? Start with the report card.")}
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
<p>We use service providers to run this site and our services, such as hosting (Vercel), email delivery (Resend), spam protection (Cloudflare), our CRM and messaging platform, and scheduling tools. To build report cards we send your business name, town and website (never your own name, email or phone) to Google for business lookups and site speed tests and to Anthropic for AI that checks listings and writes part of the report. They only use your information to provide services to us. We do not sell your personal information.</p>
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
<li><b>Money-back guarantee:</b> if you're not happy in the first 30 days after launch, tell us and we refund your first month's fee.</li>
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
    city_names = "; ".join(f"{st['name']}: " + ", ".join(c["name"] for c in st["cities"]) for st in STATES)
    guide_names = "; ".join(g["title"] for g in GUIDES)
    # Plain facts for AI assistants (the "Answer" in our own method). Only states what the site states.
    plans = []
    for p in PLANS:
        price = "price not published yet" if p["monthly"] is None else f"${p['monthly']:,}/month, or 20% less billed yearly"
        plans.append(f"- {p['name']} ({p['scope']}; best for {p['stage']}): {price}")
    methods = "\n".join(f"- {n}: {line} " + "; ".join(items) + "." for n, line, items, _ in METHOD)
    return f"""# {BRAND}

> {BRAND} builds websites, runs Google Business Profiles and sets up missed-call text-back and review requests for HVAC contractors. HVAC only, serving HVAC companies nationally.

## Quick facts
- Website: https://{DOMAIN}
- Email: {EMAIL}
- Who it serves: residential and light commercial HVAC contractors
- Main offer: a free report card that grades an HVAC company's Google profile, reviews, website and listings against nearby competitors
- Guarantees: every missed call texted back within 60 seconds; new site live within 14 days of receiving content; first month refunded if the client is unhappy in the first 30 days after launch
- Paid ads: Google Ads, Local Services Ads and Facebook/Instagram ads managed as add-ons to any plan at $299/month each (AI phone answering also $299/month); ad spend billed by the platform to the client, never marked up
- Does not promise: #1 rankings, a set number of jobs, a fixed cost per lead, or AI assistant recommendations
- Ownership: the client owns their domain, website content, Google profile and reviews

## Method: Rank, Book, Repeat
{methods}

## Plans
{chr(10).join(plans)}

## Good fit
HVAC shops that do good work, miss calls when the crew is busy, and want to own their marketing rather than rent leads.

## Not a fit
Shops that can't take on more work, want ads with nobody answering the calls, or want a one-time website with nothing after.

## Pages
- Home: https://{DOMAIN}/
- The method: https://{DOMAIN}/method
- Pricing: https://{DOMAIN}/plans ({'; '.join(f"{p_['name']} ${p_['monthly']:,}/mo" for p_ in PLANS)}, 20% off annual)
- Free report card: https://{DOMAIN}/report-card
- Guides: https://{DOMAIN}/guides ({guide_names})
- Locations: https://{DOMAIN}/locations ({city_names})
"""


NICHE_URL = {"hvac-marketing-residential-replacement": "residential", "hvac-marketing-light-commercial": "commercial"}
OFFER_URL = {"website": "hvac-websites", "app": "lead-system"}
OLD_REDIRECTS = {"examples": "", "marketing": "google-business-profile", "hvac": "", "plumbing": "", "roofing": ""}  # pages removed Oct 13


def build_routes():
    ROUTES.clear()
    for k, slug in OFFER_URL.items():
        ROUTES[k] = f"services/{slug}"
    for sv in SERVICES:
        ROUTES[sv["slug"]] = f"services/{sv['slug']}"
    ROUTES["hvac-specialties"] = "for-hvac"
    for n in NICHES:
        ROUTES[n["slug"]] = "for-hvac/" + NICHE_URL.get(n["slug"], n["slug"].removeprefix("hvac-marketing-"))
    for g in GUIDES:
        ROUTES[guide_path(g["slug"])] = f"guides/{g['slug']}"
    for g in POSTS:
        ROUTES[guide_path(g["slug"])] = f"blog/{g['slug']}"
    ROUTES["tools"] = "free-tools"  # /tools is the build script folder, kept off the live site
    for t in TOOLS:
        ROUTES["tools/" + t["slug"]] = "free-tools/" + t["slug"]
    for st in STATES:
        ROUTES[state_key(st)] = f"locations/{st['slug']}"
        for c in st["cities"]:
            ROUTES[city_path(c)] = f"locations/{st['slug']}/{c['slug']}"


def write_redirects(site_dir):
    """Old flat URLs point to the folder URLs, so links shared before Oct 13 keep working."""
    p_ = os.path.join(site_dir, "vercel.json")
    with open(p_) as f:
        cfg = json.load(f)
    reds = [{"source": "/" + old, "destination": "/" + new, "permanent": True} for old, new in ROUTES.items() if not old.startswith("tools")]
    reds += [{"source": "/" + old, "destination": "/" + route(new), "permanent": True} for old, new in OLD_REDIRECTS.items()]
    # One short link on our own domain for the report email; the calendar can change without touching the email.
    reds.append({"source": "/book", "destination": call_link(), "permanent": False})
    cfg["redirects"] = reds
    with open(p_, "w") as f:
        f.write(json.dumps(cfg, indent=2) + "\n")


def your_report_page():
    """Personal results page linked from the report card email. One job: book the call.
    No menu or footer links; the report itself is read from the link by your-report.js."""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Your HVAC report card | {esc(BRAND)}</title>
<meta name="robots" content="noindex, nofollow">
<meta name="referrer" content="no-referrer">
<link rel="preload" href="{a('fonts/Archivo-600-800.woff2')}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{asset_v('styles.css')}">
<link rel="icon" href="{a('favicon.svg')}" type="image/svg+xml">
</head>
<body class="yr-page">
<header class="yr-top"><div class="wrap"><span class="brand">{MARK}<span>{esc(BRAND_SHORT)}<small>{esc(TAGLINE)}</small></span></span><a class="btn btn-primary btn-small" href="{esc(call_link())}">Book a call</a></div></header>
<main id="yr" data-book="{esc(call_link())}"><noscript><div class="wrap" style="padding:60px 0"><h1>Your report card</h1><p>Turn on JavaScript to see your report, or <a href="{esc(call_link())}">book a 15-minute call</a> and we'll walk you through it.</p></div></noscript></main>
<footer class="yr-foot"><div class="wrap">© 2026 {esc(BRAND)}. This report is for you; anyone with the link can open it.</div></footer>
<script src="{asset_v('your-report.js')}" defer></script>
</body>
</html>
"""


def build(out_dir):
    build_routes()
    pages = {"index": home(), "report-card": report_card_page(), "method": method_page(), "plans": plans_page(), "privacy": legal_page("privacy"), "terms": legal_page("terms"), "404": not_found()}
    for k, _, _ in TRADES:
        pages[k] = trade_page(k)
    for k, _, _ in OFFERINGS:
        pages[k] = offer_page(k)
    pages["guides"] = guides_page()
    for g in GUIDES:
        pages[guide_path(g["slug"])] = guide_page(g)
    if POSTS:
        pages["blog"] = blog_page()
        for g in POSTS:
            pages[guide_path(g["slug"])] = guide_page(g)
    for n in NICHES:
        pages[n["slug"]] = niche_page(n)
    for sv in SERVICES:
        pages[sv["slug"]] = service_page(sv)
    pages["getting-started"] = getting_started_page()
    pages["services"] = services_hub()
    pages["tools"] = tools_hub()
    for t in TOOLS:
        pages["tools/" + t["slug"]] = tool_page(t)
    pages["contact"] = contact_page()
    pages["about"] = about_page()
    pages["your-report"] = your_report_page()
    pages["hvac-marketing"] = pillar_page()
    pages["compare"] = compare_hub()
    pages["hvac-specialties"] = specialties_hub()
    pages["locations"] = locations_page()
    for st in STATES:
        pages[state_key(st)] = texas_page() if st["abbr"] == "TX" else state_page(st)
        for c in st["cities"]:
            pages[city_path(c)] = city_page(c)
    os.makedirs(out_dir, exist_ok=True)
    for name, content in pages.items():
        dest = os.path.join(out_dir, route(name) + ".html")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if route(name) != name and os.path.exists(os.path.join(out_dir, name + ".html")):
            os.remove(os.path.join(out_dir, name + ".html"))  # old flat file, now redirected
        with open(dest, "w") as f:
            f.write(content)
    with open(os.path.join(out_dir, "llms.txt"), "w") as f:
        f.write(llms_txt())
    with open(os.path.join(out_dir, "towns.json"), "w") as f:
        f.write(towns_json())
    skip = {"404", "hvac", "plumbing", "roofing", "your-report"}
    paths = ["" if n == "index" else route(n) for n in pages if n not in skip]
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
        for asset in ("styles.css", "main.js", "gcalc.js", "your-report.js", "favicon.svg", "favicon.ico", "apple-touch-icon-180.png", "og-image.png"):
            shutil.copy(os.path.join(site, asset), os.path.join(out, asset))
        shutil.copytree(os.path.join(site, "fonts"), os.path.join(out, "fonts"), dirs_exist_ok=True)
        shutil.copytree(os.path.join(site, "img"), os.path.join(out, "img"), dirs_exist_ok=True)
    else:
        names = build(site)
        write_redirects(site)
    print("Wrote:", ", ".join(n + ".html" for n in names))
