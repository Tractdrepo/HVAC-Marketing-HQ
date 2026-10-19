#!/usr/bin/env python3
"""Client site template generator (client-kit). NOT part of the HMHQ marketing site.

Writes a static site for ONE client from ONE config file (client.json):
    python3 client-kit/site-generator/generate.py client-kit/site-generator/clients/practice-hvac-co/client.json
Output goes to client-kit/sites/<slug>/ (or --out DIR). Images come from the client's assets/ folder next to
client.json (or --assets DIR). client-kit/ is in the repo's .vercelignore, so the HMHQ project never deploys any
of this. Deploy the output folder as its OWN Vercel project (client-kit/scripts/deploy-preview.sh).

Everything optional is behind a config value and left out when empty: logo, photos, per-city pages (only for
cities with supplied facts), booking link, Google review link, GA4, call-tracking script, Turnstile, chat widget.

Safety rules baked in (tests enforce them):
- NOINDEX: robots meta noindex,nofollow on every page + X-Robots-Tag header + robots.txt Disallow: / .
- TEST_SITE: visible "TEST SITE - not a real business" banner on every page; phone must be fictional 555-01xx.
- Forms are email-only: no phone input, no SMS opt-in. They post to FORM_ENDPOINT (the form-lead function).
- Chat widget loader only when CHAT_WIDGET_ID is set; HMHQ's own widget id is refused.
- Review link goes straight to Google (no gating page). Non-test sites must use a Google review URL.
- City pages render ONLY the facts given in client.json, verbatim. No facts = no city page.
- Copy lint: no reviews/testimonials/stats/guarantees/"what if we miss" wording in generated pages.
"""
import argparse
import html
import json
import os
import re
import shutil
import sys
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(HERE)
FORM_LEAD_SRC = os.path.join(KIT, "form-lead", "api", "form-lead.js")
HMHQ_WIDGET_ID = "6ad452bad3ae3b035c14772f"  # HMHQ's own GHL widget. Never on a client site.
TEST_BANNER = "TEST SITE – not a real business"
REVIEW_LINK_TEXT = "Leave us a Google review"
FORM_SERVICES = ["Repair", "Tune-Up/Maintenance", "New System Estimate", "Indoor Air Quality", "Other"]
GOOGLE_REVIEW_HOSTS = ("g.page", "search.google.com", "www.google.com", "google.com", "maps.app.goo.gl", "g.co")
CALL_TRACKING_HOSTS = ("leadconnectorhq.com", "msgsndr.com")
TURNSTILE = "https://challenges.cloudflare.com"
# Copy that must never appear on a generated client page (proof, promises, review gating, miss scenarios).
BANNED_COPY = [
    r"testimonial", r"\breviews?\b", r"\bstars?\b", r"\brated\b", r"\d+\s*%", r"guarantee", r"\bpromise",
    r"what if we miss", r"if we miss", r"\bmissed call", r"years of experience", r"\bhappy customers\b",
    r"\b#1\b", r"\bbest\b", r"more calls", r"more jobs", r"rank", r"\btext me\b", r"\bsms\b", r"opt[- ]?in",
    r"how did we do", r"unhappy", r"rate us", r"\bfive[- ]star", r"\btop[- ]rated", r"\baward",
]
# Legal pages must talk about texting, reviews of the policy, etc. They only get the claims/proof checks.
LEGAL_EXEMPT = {r"\breviews?\b", r"\bsms\b", r"opt[- ]?in", r"\btext me\b"}
LEGAL_PAGES = {"privacy.html", "terms.html"}


class ConfigError(ValueError):
    pass


def esc(s):
    return html.escape(str(s), quote=True)


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")


def https_url(u):
    p = urlparse(str(u or ""))
    return p.scheme == "https" and bool(p.netloc)


def host_in(u, hosts):
    h = (urlparse(u).hostname or "").lower()
    return any(h == x or h.endswith("." + x) for x in hosts)


def areas(cfg):
    """service_areas entries are a town name, or {"name": ..., "facts": [...]}."""
    out = []
    for a in cfg["service_areas"]:
        if isinstance(a, str):
            out.append({"name": a, "facts": []})
        else:
            out.append({"name": a["name"], "facts": [str(f).strip() for f in a.get("facts", []) if str(f).strip()]})
    for a in out:
        a["slug"] = slugify(a["name"])
    return out


def load_config(path, assets_dir=None):
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    cfg["_assets_dir"] = assets_dir or os.path.join(os.path.dirname(os.path.abspath(path)), "assets")
    validate(cfg)
    return cfg


def validate(cfg):
    for key in ("slug", "business_name", "phone", "services", "service_areas", "FORM_ENDPOINT"):
        if not cfg.get(key):
            raise ConfigError(f"client.json: '{key}' is required")
    if not re.fullmatch(r"[a-z0-9-]+", cfg["slug"]):
        raise ConfigError("client.json: slug must be lowercase letters, digits and dashes")
    test = bool(cfg.get("TEST_SITE"))
    wid = str(cfg.get("CHAT_WIDGET_ID") or "").strip()
    if wid == HMHQ_WIDGET_ID:
        raise ConfigError("client.json: CHAT_WIDGET_ID is HMHQ's own widget. Use the client's widget id or leave it empty")
    if wid and not re.fullmatch(r"[A-Za-z0-9]+", wid):
        raise ConfigError("client.json: CHAT_WIDGET_ID must be alphanumeric")
    digits = re.sub(r"\D", "", cfg["phone"])
    if len(digits) != 10:
        raise ConfigError("client.json: phone must be a 10-digit US number")
    if test and not re.fullmatch(r"\d{3}55501\d{2}", digits):
        raise ConfigError("client.json: a TEST_SITE must use a fictional 555-01xx phone number")
    if test and not cfg.get("NOINDEX", True):
        raise ConfigError("client.json: a TEST_SITE can never turn NOINDEX off")
    for s in cfg["services"]:
        if s.get("form_value") not in FORM_SERVICES:
            raise ConfigError(f"client.json: service form_value must be one of {FORM_SERVICES}")
    seen = set()
    for a in areas(cfg):
        if not a["slug"] or a["slug"] in seen:
            raise ConfigError(f"client.json: service area '{a['name']}' is empty or duplicated")
        seen.add(a["slug"])
        if any(len(f) > 400 for f in a["facts"]):
            raise ConfigError(f"client.json: a fact for {a['name']} is over 400 characters")
    for key in ("booking_url", "review_url", "call_tracking_script_url"):
        v = str(cfg.get(key) or "").strip()
        if v and not https_url(v):
            raise ConfigError(f"client.json: {key} must be an https:// URL")
    rv = str(cfg.get("review_url") or "").strip()
    if rv and not test and not host_in(rv, GOOGLE_REVIEW_HOSTS):
        raise ConfigError("client.json: review_url must go straight to Google (g.page/r/.../review or search.google.com), no gating page")
    ct = str(cfg.get("call_tracking_script_url") or "").strip()
    if ct and not host_in(ct, CALL_TRACKING_HOSTS):
        raise ConfigError("client.json: call_tracking_script_url must be the GHL number-pool script (leadconnectorhq.com / msgsndr.com)")
    ga = str(cfg.get("ga4_id") or "").strip()
    if ga and not re.fullmatch(r"G-[A-Z0-9]{4,20}", ga):
        raise ConfigError("client.json: ga4_id must look like G-XXXXXXX")
    ts = str(cfg.get("turnstile_site_key") or "").strip()
    if ts and not re.fullmatch(r"[0-9A-Za-z_-]{10,100}", ts):
        raise ConfigError("client.json: turnstile_site_key looks wrong")
    imgs = ([cfg["logo"]] if cfg.get("logo") else []) + list(cfg.get("photos") or [])
    for im in imgs:
        src = str(im.get("src") or "")
        if not re.fullmatch(r"[A-Za-z0-9._-]+\.(svg|png|jpe?g|webp)", src):
            raise ConfigError(f"client.json: image src '{src}' must be a plain file name in assets/")
        if not str(im.get("alt") or "").strip():
            raise ConfigError(f"client.json: image '{src}' needs alt text")
        if not os.path.isfile(os.path.join(cfg["_assets_dir"], src)):
            raise ConfigError(f"client.json: image '{src}' not found in {cfg['_assets_dir']}")


def opt(cfg, key):
    return str(cfg.get(key) or "").strip()


def noindex(cfg):
    return bool(cfg.get("TEST_SITE")) or bool(cfg.get("NOINDEX", True))


def tel(cfg):
    return "+1" + re.sub(r"\D", "", cfg["phone"])


def city_pages(cfg):
    return [a for a in areas(cfg) if a["facts"]]  # no facts = no page, never invented text


# ---------- layout ----------

def nav(cfg):
    links = [("/", "Home"), ("/services", "Services"), ("/service-areas", "Service areas"), ("/contact", "Contact")]
    return "".join(f'<a href="{h}">{esc(t)}</a>' for h, t in links)


def head_scripts(cfg, has_form):
    out = []
    ga = opt(cfg, "ga4_id")
    if ga:
        out.append(f'<script async src="https://www.googletagmanager.com/gtag/js?id={esc(ga)}"></script>')
        out.append('<script src="/ga.js"></script>')
    if has_form and opt(cfg, "turnstile_site_key"):
        out.append(f'<script src="{TURNSTILE}/turnstile/v0/api.js" async defer></script>')
    return "\n".join(out)


def body_scripts(cfg):
    out = ['<script src="/site.js" defer></script>']
    ct = opt(cfg, "call_tracking_script_url")
    if ct:
        out.append(f'<script src="{esc(ct)}" async></script>')
    wid = opt(cfg, "CHAT_WIDGET_ID")
    if wid:  # widget id not known yet = loader skipped
        out.append(f'<script src="https://widgets.leadconnectorhq.com/loader.js" '
                   f'data-resources-url="https://widgets.leadconnectorhq.com/chat-widget/loader.js" '
                   f'data-widget-id="{esc(wid)}" data-source="WEB_USER" defer></script>')
    return "\n".join(out)


def schema(cfg):
    ld = {
        "@context": "https://schema.org",
        "@type": "HVACBusiness",
        "name": cfg["business_name"],
        "telephone": tel(cfg),
        "areaServed": [{"@type": "City", "name": f"{a['name']}, {cfg.get('state', 'TX')}"} for a in areas(cfg)],
    }
    if cfg.get("street_address"):
        ld["address"] = {"@type": "PostalAddress", "streetAddress": cfg["street_address"],
                         "addressLocality": cfg.get("city", ""), "addressRegion": cfg.get("state", "")}
    # No AggregateRating / review markup, ever (self-serving review markup is ineligible).
    return '<script type="application/ld+json">' + json.dumps(ld).replace("</", "<\\/") + "</script>"


def brand(cfg):
    lg = cfg.get("logo")
    if lg:
        return f'<a class="brand" href="/"><img src="/img/{esc(lg["src"])}" alt="{esc(lg["alt"])}" height="40"></a>'
    return f'<a class="brand" href="/">{esc(cfg["business_name"])}</a>'


def review_link(cfg, cls="review-link"):
    rv = opt(cfg, "review_url")
    if not rv:
        return ""
    # Straight to Google, for everyone. No "how did we do" screen, no star picker, no filter.
    return f'<a class="{cls}" href="{esc(rv)}" target="_blank" rel="noopener">{esc(REVIEW_LINK_TEXT)}</a>'


def book_btn(cfg, cls="btn ghost"):
    b = opt(cfg, "booking_url")
    return f'<a class="{cls}" href="{esc(b)}" target="_blank" rel="noopener">Book online</a>' if b else ""


def page(cfg, title, desc, body, has_form=False):
    robots = '<meta name="robots" content="noindex,nofollow">' if noindex(cfg) else ""
    banner = f'<div class="test-banner" role="note">{esc(TEST_BANNER)}</div>' if cfg.get("TEST_SITE") else ""
    name = esc(cfg["business_name"])
    st = esc(cfg.get("state", "TX"))
    foot_lines = [f"<p>{name} · Serving {esc(', '.join(a['name'] for a in areas(cfg)))}, {st}</p>"]
    if cfg.get("street_address"):
        foot_lines.append(f"<p>{esc(cfg['street_address'])}, {esc(cfg.get('city', ''))}, {st}</p>")
    foot_lines.append(f'<p><a href="tel:{tel(cfg)}">{esc(cfg["phone"])}</a></p>')
    if cfg.get("hours"):
        foot_lines.append(f"<p>Hours: {esc(cfg['hours'])}</p>")
    if cfg.get("license"):
        foot_lines.append(f"<p>License: {esc(cfg['license'])}</p>")
    if opt(cfg, "review_url"):
        foot_lines.append(f"<p>{review_link(cfg)}</p>")
    foot_lines.append('<p><a href="/privacy">Privacy</a> · <a href="/terms">Terms</a></p>')
    if cfg.get("TEST_SITE"):
        foot_lines.append(f"<p><strong>{esc(TEST_BANNER)}.</strong> Practice site for internal testing.</p>")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{robots}
<title>{esc(title)} | {name}</title>
<meta name="description" content="{esc(desc)}">
<link rel="stylesheet" href="/styles.css">
{schema(cfg)}
{head_scripts(cfg, has_form)}
</head>
<body>
{banner}
<header class="top"><div class="wrap">{brand(cfg)}<nav>{nav(cfg)}</nav>
<span class="cta">{book_btn(cfg)} <a class="btn call" href="tel:{tel(cfg)}">Call {esc(cfg['phone'])}</a></span></div></header>
<main class="wrap">
{body}
</main>
<footer class="foot"><div class="wrap">
{chr(10).join(foot_lines)}
</div></footer>
{body_scripts(cfg)}
</body>
</html>
"""


def lead_form(cfg):
    opts = "".join(f'<option value="{esc(s)}">{esc(s)}</option>' for s in FORM_SERVICES)
    hidden = "".join(f'<input type="hidden" name="{k}">' for k in
                     ("utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid"))
    ts = opt(cfg, "turnstile_site_key")
    widget = f'<div class="cf-turnstile" data-sitekey="{esc(ts)}" data-theme="light"></div>' if ts else ""
    return f"""<form id="lead-form" class="lead-form" action="{esc(cfg['FORM_ENDPOINT'])}" method="post" novalidate>
<label>Name <input name="name" autocomplete="name" maxlength="100" required></label>
<label>Email <input type="email" name="email" autocomplete="email" maxlength="254" required></label>
<label>Town or ZIP <input name="town_zip" maxlength="100"></label>
<label>Service needed <select name="service">{opts}</select></label>
<label>Message <textarea name="message" rows="4" maxlength="2000"></textarea></label>
<div class="hp" aria-hidden="true"><label>Company fax <input name="company_fax" tabindex="-1" autocomplete="off"></label></div>
{hidden}
{widget}
<button class="btn" type="submit">Send</button>
<p class="form-note">We reply by email. To talk now, call {esc(cfg['phone'])}.</p>
<p class="form-status" role="status" aria-live="polite"></p>
</form>"""


# ---------- legal drafts ----------

def legal_banner():
    return ('<p class="draft-note"><strong>DRAFT – needs lawyer review.</strong> This template has not been reviewed by a '
            'lawyer. Do not launch a client site with it until it has been.</p>')


def privacy_body(cfg):
    n = esc(cfg["business_name"])
    ga = ("<li>Website analytics (Google Analytics 4): pages visited, device and browser, and how you arrived. "
          "Google processes this data under its own terms.</li>") if opt(cfg, "ga4_id") else \
        "<li>Website analytics: none on this site right now. If added, this section will say so first.</li>"
    return f"""<h1>Privacy policy</h1>{legal_banner()}
<p>This policy explains what {n} collects through this website and how it is used.</p>
<h2>What we collect</h2><ul>
<li>Contact form: name, email, town or ZIP, the service you need and your message. We use it to reply to you by email.
This website's form does not ask for a phone number.</li>
<li>Chat widget (if shown): what you type, and a phone number only if you choose to give one there.</li>
{ga}
<li>Spam protection: the form may use Cloudflare Turnstile, which checks the browser to block bots.</li></ul>
<h2>Text messages</h2>
<p>We only send text messages to people who gave their number and agreed to receive texts through the chat widget,
using the separate checkboxes shown there. Message frequency varies. Message and data rates may apply.
Reply STOP to stop texts at any time, and HELP for help. We do not sell or share phone numbers or text consent with
third parties for their marketing.</p>
<h2>Who we share it with</h2>
<p>Service providers that run this website and our customer records (for example website hosting and our CRM),
only to provide our services to you. We do not sell personal information.</p>
<h2>Your choices</h2>
<p>To see, correct or delete your information, use the contact form or call {esc(cfg['phone'])}.</p>
<p>Last updated: [DATE – fill in at launch]</p>"""


def terms_body(cfg):
    n = esc(cfg["business_name"])
    return f"""<h1>Terms of use</h1>{legal_banner()}
<p>These terms cover use of the {n} website.</p>
<h2>Information on this site</h2>
<p>Service descriptions are general information. Prices, availability and the work needed are confirmed only after
we look at your system.</p>
<h2>Booking and requests</h2>
<p>Sending the form or booking online is a request. An appointment is set once we confirm it with you.</p>
<h2>Text messages</h2>
<p>If you agree to receive texts through the chat widget, reply STOP to end them at any time. See the Privacy policy.</p>
<h2>Licensing</h2><p>{esc(cfg.get('license', '[license number]'))}</p>
<h2>Contact</h2><p>Use the contact form or call {esc(cfg['phone'])}.</p>
<p>Last updated: [DATE – fill in at launch]</p>"""


# ---------- pages ----------

def pages(cfg):
    name = cfg["business_name"]
    st = esc(cfg.get("state", "TX"))
    svc_cards = "".join(f'<div class="card"><h3>{esc(s["name"])}</h3><p>{esc(s["blurb"])}</p></div>' for s in cfg["services"])
    with_page = {a["slug"] for a in city_pages(cfg)}

    def area_item(a):
        label = f"{esc(a['name'])}, {st}"
        return f'<li><a href="/areas/{a["slug"]}">{label}</a></li>' if a["slug"] in with_page else f"<li>{label}</li>"
    area_list = "".join(area_item(a) for a in areas(cfg))
    photos = cfg.get("photos") or []
    gallery = ""
    if photos:
        figs = "".join(
            f'<figure><img src="/img/{esc(p["src"])}" alt="{esc(p["alt"])}" loading="lazy">'
            + (f'<figcaption>{esc(p["caption"])}</figcaption>' if p.get("caption") else "") + "</figure>" for p in photos)
        gallery = f'<section><h2>Our work</h2><div class="gallery">{figs}</div></section>'
    book = book_btn(cfg, "btn")
    out = {}
    out["index.html"] = page(cfg, "Heating and air conditioning", cfg.get("tagline", ""), f"""
<section class="hero"><h1>{esc(name)}</h1><p>{esc(cfg.get('tagline', ''))}</p>
<p><a class="btn" href="/contact">Request service</a> {book} <a class="btn ghost" href="tel:{tel(cfg)}">Call {esc(cfg['phone'])}</a></p></section>
{gallery}
<section><h2>Services</h2><div class="grid">{svc_cards}</div></section>
<section><h2>Where we work</h2><ul class="areas">{area_list}</ul></section>""")
    out["services.html"] = page(cfg, "Services", f"Heating and cooling services from {name}.", f"""
<h1>Services</h1><div class="grid">{svc_cards}</div>
<p><a class="btn" href="/contact">Request service</a> {book}</p>""")
    out["service-areas.html"] = page(cfg, "Service areas", f"Towns served by {name}.", f"""
<h1>Service areas</h1><p>We work in these towns:</p><ul class="areas">{area_list}</ul>""")
    for a in city_pages(cfg):
        facts = "".join(f"<li>{esc(f)}</li>" for f in a["facts"])  # verbatim from client.json, nothing added
        out[f"areas/{a['slug']}.html"] = page(cfg, f"HVAC service in {a['name']}, {cfg.get('state', 'TX')}",
                                              f"Heating and cooling service in {a['name']} from {name}.", f"""
<h1>Heating and air conditioning in {esc(a['name'])}, {st}</h1>
<section><h2>Local notes</h2><ul class="facts">{facts}</ul></section>
<section><h2>Services in {esc(a['name'])}</h2><div class="grid">{svc_cards}</div></section>
<p><a class="btn" href="/contact">Request service</a> {book}</p>""")
    rv = review_link(cfg, "btn ghost")
    out["contact.html"] = page(cfg, "Contact", f"Request service from {name}.", f"""
<h1>Request service</h1>{lead_form(cfg)}
{f'<p>Prefer to pick a time yourself? {book}</p>' if book else ''}
{f'<p>Already a customer? {rv}</p>' if rv else ''}""", has_form=True)
    out["privacy.html"] = page(cfg, "Privacy", f"Privacy policy for {name}.", privacy_body(cfg))
    out["terms.html"] = page(cfg, "Terms", f"Terms of use for {name}.", terms_body(cfg))
    out["404.html"] = page(cfg, "Page not found", "Page not found.", """
<h1>Page not found</h1><p><a href="/">Go to the home page</a></p>""")
    return out


CSS = """*{box-sizing:border-box}body{margin:0;font:16px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:#1b1f24}
.wrap{max-width:960px;margin:0 auto;padding:0 16px}.test-banner{background:#b00020;color:#fff;text-align:center;font-weight:700;padding:8px 12px}
.top .wrap{display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between;padding:12px 16px}
.brand{font-weight:700;color:inherit;text-decoration:none}.brand img{display:block}nav a{margin-right:12px;color:inherit}
.btn{display:inline-block;background:var(--accent);color:#fff;border:0;border-radius:6px;padding:10px 16px;text-decoration:none;font:inherit;cursor:pointer}
.btn.ghost{background:transparent;color:var(--accent);border:2px solid var(--accent)}.hero{padding:32px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}.card{border:1px solid #d0d7de;border-radius:8px;padding:16px}
.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}.gallery img{width:100%;height:auto;border-radius:8px}
.lead-form{display:grid;gap:12px;max-width:520px}.lead-form label{display:grid;gap:4px}.lead-form input,.lead-form select,.lead-form textarea{font:inherit;padding:8px;border:1px solid #8c959f;border-radius:6px}
.hp{position:absolute;left:-10000px;width:1px;height:1px;overflow:hidden}.foot{margin-top:48px;background:#f6f8fa;padding:24px 0;font-size:14px}
.draft-note{background:#fff8c5;border:1px solid #d4a72c;padding:12px;border-radius:6px}
"""

JS = r"""// Client site JS: keep UTMs/gclid from the landing URL in hidden fields, send the lead form as JSON,
// and fire GA4 key events (generate_lead, click_to_call) only if GA4 is on the page.
(function () {
  var keys = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid"];
  var q = new URLSearchParams(location.search);
  keys.forEach(function (k) {
    var v = q.get(k) || sessionStorage.getItem(k);
    if (q.get(k)) sessionStorage.setItem(k, v);
    document.querySelectorAll('input[name="' + k + '"]').forEach(function (el) { if (v) el.value = v; });
  });
  var ev = function (name) { if (typeof window.gtag === "function") window.gtag("event", name); };
  document.querySelectorAll('a[href^="tel:"]').forEach(function (a) { a.addEventListener("click", function () { ev("click_to_call"); }); });
  var form = document.getElementById("lead-form");
  if (!form) return;
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var status = form.querySelector(".form-status");
    var data = {};
    new FormData(form).forEach(function (v, k) { data[k] = v; });
    status.textContent = "Sending...";
    var resetCheck = function () { if (window.turnstile && form.querySelector(".cf-turnstile")) window.turnstile.reset(); };
    fetch(form.getAttribute("action"), { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) })
      .then(function (r) { return r.json().catch(function () { return { ok: false }; }); })
      .then(function (j) {
        if (j && j.ok) { form.reset(); resetCheck(); ev("generate_lead"); status.textContent = "Thanks, your request was received. We reply by email."; }
        else { resetCheck(); status.textContent = (j && j.error) || "Sorry, that didn't go through. Please try again or call us."; }
      })
      .catch(function () { resetCheck(); status.textContent = "Sorry, that didn't go through. Please try again or call us."; });
  });
})();
"""


def ga_js(cfg):
    ga = opt(cfg, "ga4_id")
    return ("window.dataLayer = window.dataLayer || [];\nfunction gtag(){dataLayer.push(arguments);}\n"
            f"gtag('js', new Date());\ngtag('config', {json.dumps(ga)});\n")


def csp(cfg):
    script, style, font, connect, frame = ["'self'"], ["'self'", "'unsafe-inline'"], ["'self'", "data:"], ["'self'"], []
    if opt(cfg, "CHAT_WIDGET_ID"):
        script += ["https://*.leadconnectorhq.com", "https://*.msgsndr.com"]
        style.append("https://*.leadconnectorhq.com")
        font.append("https://*.leadconnectorhq.com")
        connect += ["https://*.leadconnectorhq.com", "wss://*.leadconnectorhq.com", "https://*.msgsndr.com"]
        frame += ["https://*.leadconnectorhq.com", "https://*.msgsndr.com"]
    if opt(cfg, "turnstile_site_key"):
        script.append(TURNSTILE)
        frame.append(TURNSTILE)
    if opt(cfg, "ga4_id"):
        script.append("https://www.googletagmanager.com")
        connect += ["https://*.google-analytics.com", "https://*.analytics.google.com", "https://*.googletagmanager.com"]
    ct = opt(cfg, "call_tracking_script_url")
    if ct:
        o = urlparse(ct)
        origin = f"https://{o.hostname}"
        for lst in (script, connect):
            if origin not in lst:
                lst.append(origin)
    dedupe = lambda xs: list(dict.fromkeys(xs))
    parts = [
        "default-src 'self'",
        "script-src " + " ".join(dedupe(script)),
        "style-src " + " ".join(dedupe(style)),
        "font-src " + " ".join(dedupe(font)),
        "img-src 'self' data: https:",
        "connect-src " + " ".join(dedupe(connect)),
        "frame-src " + (" ".join(dedupe(frame)) if frame else "'none'"),
        "form-action 'self'", "base-uri 'self'", "frame-ancestors 'none'",
    ]
    return "; ".join(parts)


def vercel_json(cfg):
    headers = [
        {"key": "X-Content-Type-Options", "value": "nosniff"},
        {"key": "X-Frame-Options", "value": "DENY"},
        {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
        {"key": "Content-Security-Policy", "value": csp(cfg)},
    ]
    if noindex(cfg):
        headers.insert(0, {"key": "X-Robots-Tag", "value": "noindex, nofollow"})
    return {
        "cleanUrls": True,
        "trailingSlash": False,
        "functions": {"api/form-lead.js": {"maxDuration": 60}},
        "headers": [{"source": "/(.*)", "headers": headers}],
    }


def visible_text(text):
    attrs = " ".join(re.findall(r'\b(?:alt|title)="([^"]*)"', text))
    t = re.sub(r"<script.*?</script>", " ", text, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    return html.unescape(t + " " + attrs).replace(REVIEW_LINK_TEXT, " ")  # the one allowed review phrase


def lint_copy(files):
    """Fail on banned copy in the visible text (and alt/title text) of generated pages."""
    problems = []
    for fn, text in files.items():
        vis = visible_text(text)
        pats = [p for p in BANNED_COPY if not (os.path.basename(fn) in LEGAL_PAGES and p in LEGAL_EXEMPT)]
        for pat in pats:
            m = re.search(pat, vis, flags=re.I)
            if m:
                problems.append(f"{fn}: banned copy '{m.group(0)}'")
    return problems


def build(cfg, out_dir):
    files = pages(cfg)
    problems = lint_copy(files)
    if problems:
        raise ConfigError("copy check failed:\n  " + "\n  ".join(problems))
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(os.path.join(out_dir, "api"))
    written = []

    def w(rel, text):
        p = os.path.join(out_dir, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        written.append(rel)
    for fn, text in files.items():
        w(fn, text)
    accent = cfg.get("accent_color", "#1f6feb")
    if not re.fullmatch(r"#[0-9a-fA-F]{3,6}", accent):
        accent = "#1f6feb"
    w("styles.css", f":root{{--accent:{accent}}}\n" + CSS)
    w("site.js", JS)
    if opt(cfg, "ga4_id"):
        w("ga.js", ga_js(cfg))
    w("robots.txt", "User-agent: *\nDisallow: /\n" if noindex(cfg) else "User-agent: *\nAllow: /\n")
    w("vercel.json", json.dumps(vercel_json(cfg), indent=2) + "\n")
    for im in ([cfg["logo"]] if cfg.get("logo") else []) + list(cfg.get("photos") or []):
        os.makedirs(os.path.join(out_dir, "img"), exist_ok=True)
        shutil.copyfile(os.path.join(cfg["_assets_dir"], im["src"]), os.path.join(out_dir, "img", im["src"]))
        written.append("img/" + im["src"])
    shutil.copyfile(FORM_LEAD_SRC, os.path.join(out_dir, "api", "form-lead.js"))
    written.append("api/form-lead.js")
    w("README.md", f"# {cfg['business_name']}\n\nGENERATED by client-kit/site-generator/generate.py. Do not edit by hand; "
      "edit the client.json and regenerate.\n\nDeploy this folder as its own Vercel project with "
      "client-kit/scripts/deploy-preview.sh, never through the HMHQ project. Env vars for api/form-lead.js: see "
      "client-kit/form-lead/README.md.\n")
    return sorted(set(written))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("config", help="path to the client's client.json")
    ap.add_argument("--out", help="output folder (default client-kit/sites/<slug>)")
    ap.add_argument("--assets", help="images folder (default: assets/ next to client.json)")
    args = ap.parse_args(argv)
    try:
        cfg = load_config(args.config, args.assets)
        out = args.out or os.path.join(KIT, "sites", cfg["slug"])
        written = build(cfg, out)
    except (ConfigError, json.JSONDecodeError, OSError, KeyError, TypeError) as e:
        print(f"generate.py: {e}", file=sys.stderr)
        return 1
    print(f"Wrote {len(written)} files to {os.path.relpath(out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
