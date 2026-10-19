#!/usr/bin/env python3
"""Minimal client site generator (client-kit). NOT part of the HMHQ marketing site.

Writes a small static site for ONE client from ONE config file (client.json):
    python3 client-kit/site-generator/generate.py client-kit/site-generator/clients/practice-hvac-co/client.json
Output goes to client-kit/sites/<slug>/ (or --out DIR). client-kit/ is in the repo's .vercelignore,
so nothing here is deployed by the HMHQ project. Deploy the output folder as its OWN Vercel project.

Safety rules baked in (tests enforce them):
- NOINDEX: robots meta noindex,nofollow on every page + X-Robots-Tag header in the output vercel.json
  + robots.txt Disallow: / . Turn NOINDEX off only at go-live with Logan's approval.
- TEST_SITE: a visible "TEST SITE - not a real business" banner on every page, and the phone must be
  a fictional 555-01xx number.
- Forms are email-only: no phone input, no SMS opt-in. They post to FORM_ENDPOINT (the form-lead function).
- Chat widget loader only when CHAT_WIDGET_ID is set; HMHQ's own widget id is refused.
- Copy lint: no reviews/testimonials/stats/guarantees/"what if we miss" wording in generated pages.
"""
import argparse
import html
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(HERE)
FORM_LEAD_SRC = os.path.join(KIT, "form-lead", "api", "form-lead.js")
HMHQ_WIDGET_ID = "6ad452bad3ae3b035c14772f"  # HMHQ's own GHL widget. Never on a client site.
TEST_BANNER = "TEST SITE – not a real business"
FORM_SERVICES = ["Repair", "Tune-Up/Maintenance", "New System Estimate", "Indoor Air Quality", "Other"]
# Copy that must never appear on a generated client page (proof, promises, review gating, miss scenarios).
BANNED_COPY = [
    r"testimonial", r"\breviews?\b", r"\bstars?\b", r"\brated\b", r"\d+\s*%", r"guarantee", r"\bpromise",
    r"what if we miss", r"if we miss", r"\bmissed call", r"years of experience", r"\bhappy customers\b",
    r"\b#1\b", r"\bbest\b", r"more calls", r"more jobs", r"rank", r"\btext me\b", r"\bsms\b", r"opt[- ]?in",
]


class ConfigError(ValueError):
    pass


def esc(s):
    return html.escape(str(s), quote=True)


def load_config(path):
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    validate(cfg)
    return cfg


def validate(cfg):
    for key in ("slug", "business_name", "phone", "services", "service_areas", "FORM_ENDPOINT"):
        if not cfg.get(key):
            raise ConfigError(f"client.json: '{key}' is required")
    if not re.fullmatch(r"[a-z0-9-]+", cfg["slug"]):
        raise ConfigError("client.json: slug must be lowercase letters, digits and dashes")
    wid = str(cfg.get("CHAT_WIDGET_ID") or "").strip()
    if wid == HMHQ_WIDGET_ID:
        raise ConfigError("client.json: CHAT_WIDGET_ID is HMHQ's own widget. Use the client's widget id or leave it empty")
    if wid and not re.fullmatch(r"[A-Za-z0-9]+", wid):
        raise ConfigError("client.json: CHAT_WIDGET_ID must be alphanumeric")
    digits = re.sub(r"\D", "", cfg["phone"])
    if len(digits) != 10:
        raise ConfigError("client.json: phone must be a 10-digit US number")
    if cfg.get("TEST_SITE") and not re.fullmatch(r"\d{3}55501\d{2}", digits):
        raise ConfigError("client.json: a TEST_SITE must use a fictional 555-01xx phone number")
    if cfg.get("TEST_SITE") and not cfg.get("NOINDEX", True):
        raise ConfigError("client.json: a TEST_SITE can never turn NOINDEX off")
    for s in cfg["services"]:
        if s.get("form_value") not in FORM_SERVICES:
            raise ConfigError(f"client.json: service form_value must be one of {FORM_SERVICES}")


def noindex(cfg):
    return bool(cfg.get("TEST_SITE")) or bool(cfg.get("NOINDEX", True))


def tel(cfg):
    d = re.sub(r"\D", "", cfg["phone"])
    return f"+1{d}"


# ---------- layout ----------

def nav(cfg):
    links = [("/", "Home"), ("/services", "Services"), ("/service-areas", "Service areas"), ("/contact", "Contact")]
    return "".join(f'<a href="{h}">{esc(t)}</a>' for h, t in links)


def chat_loader(cfg):
    wid = str(cfg.get("CHAT_WIDGET_ID") or "").strip()
    if not wid:
        return ""  # widget id not known yet: loader skipped
    return (f'<script src="https://widgets.leadconnectorhq.com/loader.js" '
            f'data-resources-url="https://widgets.leadconnectorhq.com/chat-widget/loader.js" '
            f'data-widget-id="{esc(wid)}" data-source="WEB_USER" defer></script>')


def schema(cfg):
    ld = {
        "@context": "https://schema.org",
        "@type": "HVACBusiness",
        "name": cfg["business_name"],
        "telephone": tel(cfg),
        "areaServed": [{"@type": "City", "name": f"{t}, {cfg.get('state', 'TX')}"} for t in cfg["service_areas"]],
    }
    if cfg.get("street_address"):
        ld["address"] = {"@type": "PostalAddress", "streetAddress": cfg["street_address"],
                         "addressLocality": cfg.get("city", ""), "addressRegion": cfg.get("state", "")}
    # No AggregateRating / review markup, ever (self-serving review markup is ineligible).
    return '<script type="application/ld+json">' + json.dumps(ld).replace("</", "<\\/") + "</script>"


def page(cfg, title, desc, body):
    robots = '<meta name="robots" content="noindex,nofollow">' if noindex(cfg) else ""
    banner = f'<div class="test-banner" role="note">{esc(TEST_BANNER)}</div>' if cfg.get("TEST_SITE") else ""
    name = esc(cfg["business_name"])
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
</head>
<body>
{banner}
<header class="top"><div class="wrap"><a class="brand" href="/">{name}</a><nav>{nav(cfg)}</nav>
<a class="btn call" href="tel:{tel(cfg)}">Call {esc(cfg['phone'])}</a></div></header>
<main class="wrap">
{body}
</main>
<footer class="foot"><div class="wrap">
<p>{name} · Serving {esc(', '.join(cfg['service_areas']))}, {esc(cfg.get('state', 'TX'))}</p>
<p>{esc(cfg.get('hours', ''))}</p>
<p>License: {esc(cfg.get('license', ''))}</p>
<p><a href="/privacy">Privacy</a></p>
{f'<p><strong>{esc(TEST_BANNER)}.</strong> Practice site for internal testing.</p>' if cfg.get('TEST_SITE') else ''}
</div></footer>
<script src="/site.js" defer></script>
{chat_loader(cfg)}
</body>
</html>
"""


def lead_form(cfg):
    opts = "".join(f'<option value="{esc(s)}">{esc(s)}</option>' for s in FORM_SERVICES)
    hidden = "".join(f'<input type="hidden" name="{k}">' for k in
                     ("utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid"))
    return f"""<form id="lead-form" class="lead-form" action="{esc(cfg['FORM_ENDPOINT'])}" method="post" novalidate>
<label>Name <input name="name" autocomplete="name" maxlength="100" required></label>
<label>Email <input type="email" name="email" autocomplete="email" maxlength="254" required></label>
<label>Town or ZIP <input name="town_zip" maxlength="100"></label>
<label>Service needed <select name="service">{opts}</select></label>
<label>Message <textarea name="message" rows="4" maxlength="2000"></textarea></label>
<div class="hp" aria-hidden="true"><label>Company fax <input name="company_fax" tabindex="-1" autocomplete="off"></label></div>
{hidden}
<button class="btn" type="submit">Send</button>
<p class="form-note">We reply by email. To talk now, call {esc(cfg['phone'])}.</p>
<p class="form-status" role="status" aria-live="polite"></p>
</form>"""


# ---------- pages ----------

def pages(cfg):
    name = cfg["business_name"]
    areas = cfg["service_areas"]
    svc_cards = "".join(f'<div class="card"><h3>{esc(s["name"])}</h3><p>{esc(s["blurb"])}</p></div>' for s in cfg["services"])
    area_list = "".join(f"<li>{esc(t)}, {esc(cfg.get('state', 'TX'))}</li>" for t in areas)
    out = {}
    out["index.html"] = page(cfg, "Heating and air conditioning", cfg.get("tagline", ""), f"""
<section class="hero"><h1>{esc(name)}</h1><p>{esc(cfg.get('tagline', ''))}</p>
<p><a class="btn" href="/contact">Request service</a> <a class="btn ghost" href="tel:{tel(cfg)}">Call {esc(cfg['phone'])}</a></p></section>
<section><h2>Services</h2><div class="grid">{svc_cards}</div></section>
<section><h2>Where we work</h2><ul class="areas">{area_list}</ul></section>""")
    out["services.html"] = page(cfg, "Services", f"Heating and cooling services from {name}.", f"""
<h1>Services</h1><div class="grid">{svc_cards}</div>
<p><a class="btn" href="/contact">Request service</a></p>""")
    out["service-areas.html"] = page(cfg, "Service areas", f"Towns served by {name}.", f"""
<h1>Service areas</h1><p>We work in these towns:</p><ul class="areas">{area_list}</ul>""")
    out["contact.html"] = page(cfg, "Contact", f"Request service from {name}.", f"""
<h1>Request service</h1>{lead_form(cfg)}""")
    out["privacy.html"] = page(cfg, "Privacy", f"Privacy policy for {name}.", f"""
<h1>Privacy</h1><p><strong>Placeholder.</strong> The client privacy policy template is waiting on a lawyer's sign-off.
It must cover the contact form, the chat widget, text message opt-out (reply STOP) and analytics before launch.</p>""")
    out["404.html"] = page(cfg, "Page not found", "Page not found.", """
<h1>Page not found</h1><p><a href="/">Go to the home page</a></p>""")
    return out


CSS = """*{box-sizing:border-box}body{margin:0;font:16px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:#1b1f24}
.wrap{max-width:960px;margin:0 auto;padding:0 16px}.test-banner{background:#b00020;color:#fff;text-align:center;font-weight:700;padding:8px 12px}
.top .wrap{display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between;padding:12px 16px}
.brand{font-weight:700;color:inherit;text-decoration:none}nav a{margin-right:12px;color:inherit}
.btn{display:inline-block;background:var(--accent);color:#fff;border:0;border-radius:6px;padding:10px 16px;text-decoration:none;font:inherit;cursor:pointer}
.btn.ghost{background:transparent;color:var(--accent);border:2px solid var(--accent)}.hero{padding:32px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}.card{border:1px solid #d0d7de;border-radius:8px;padding:16px}
.lead-form{display:grid;gap:12px;max-width:520px}.lead-form label{display:grid;gap:4px}.lead-form input,.lead-form select,.lead-form textarea{font:inherit;padding:8px;border:1px solid #8c959f;border-radius:6px}
.hp{position:absolute;left:-10000px;width:1px;height:1px;overflow:hidden}.foot{margin-top:48px;background:#f6f8fa;padding:24px 0;font-size:14px}
"""

JS = r"""// Client site JS: keep UTMs/gclid from the landing URL in hidden fields, and send the lead form as JSON.
(function () {
  var keys = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid"];
  var q = new URLSearchParams(location.search);
  keys.forEach(function (k) {
    var v = q.get(k) || sessionStorage.getItem(k);
    if (q.get(k)) sessionStorage.setItem(k, v);
    document.querySelectorAll('input[name="' + k + '"]').forEach(function (el) { if (v) el.value = v; });
  });
  var form = document.getElementById("lead-form");
  if (!form) return;
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var status = form.querySelector(".form-status");
    var data = {};
    new FormData(form).forEach(function (v, k) { data[k] = v; });
    status.textContent = "Sending...";
    fetch(form.getAttribute("action"), { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) })
      .then(function (r) { return r.json().catch(function () { return { ok: false }; }); })
      .then(function (j) {
        if (j && j.ok) { form.reset(); status.textContent = "Thanks, your request was received. We reply by email."; }
        else { status.textContent = (j && j.error) || "Sorry, that didn't go through. Please try again or call us."; }
      })
      .catch(function () { status.textContent = "Sorry, that didn't go through. Please try again or call us."; });
  });
})();
"""


def csp(cfg):
    ghl = bool(str(cfg.get("CHAT_WIDGET_ID") or "").strip())
    lc = " https://*.leadconnectorhq.com https://*.msgsndr.com" if ghl else ""
    parts = [
        "default-src 'self'",
        f"script-src 'self'{lc}",
        f"style-src 'self' 'unsafe-inline'{' https://*.leadconnectorhq.com' if ghl else ''}",
        f"font-src 'self' data:{' https://*.leadconnectorhq.com' if ghl else ''}",
        "img-src 'self' data: https:",
        f"connect-src 'self'{lc + ' wss://*.leadconnectorhq.com' if ghl else ''}",
        f"frame-src {'https://*.leadconnectorhq.com https://*.msgsndr.com' if ghl else "'none'"}",
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


def lint_copy(files):
    """Fail on banned copy in the visible text of generated pages (scripts/markup stripped)."""
    problems = []
    for fn, text in files.items():
        visible = re.sub(r"<script.*?</script>", " ", text, flags=re.S)
        visible = re.sub(r"<[^>]+>", " ", visible)
        for pat in BANNED_COPY:
            m = re.search(pat, visible, flags=re.I)
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
    for fn, text in files.items():
        with open(os.path.join(out_dir, fn), "w", encoding="utf-8") as f:
            f.write(text)
    accent = cfg.get("accent_color", "#1f6feb")
    if not re.fullmatch(r"#[0-9a-fA-F]{3,6}", accent):
        accent = "#1f6feb"
    with open(os.path.join(out_dir, "styles.css"), "w", encoding="utf-8") as f:
        f.write(f":root{{--accent:{accent}}}\n" + CSS)
    with open(os.path.join(out_dir, "site.js"), "w", encoding="utf-8") as f:
        f.write(JS)
    with open(os.path.join(out_dir, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nDisallow: /\n" if noindex(cfg) else "User-agent: *\nAllow: /\n")
    with open(os.path.join(out_dir, "vercel.json"), "w", encoding="utf-8") as f:
        json.dump(vercel_json(cfg), f, indent=2)
        f.write("\n")
    shutil.copyfile(FORM_LEAD_SRC, os.path.join(out_dir, "api", "form-lead.js"))
    with open(os.path.join(out_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(f"# {cfg['business_name']}\n\nGENERATED by client-kit/site-generator/generate.py. Do not edit by hand; "
                "edit the client.json and regenerate.\n\nDeploy this folder as its own Vercel project (Root Directory = "
                "this folder), never through the HMHQ project. Env vars for api/form-lead.js: see "
                "client-kit/form-lead/README.md.\n")
    return sorted(list(files) + ["styles.css", "site.js", "robots.txt", "vercel.json", "api/form-lead.js", "README.md"])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("config", help="path to the client's client.json")
    ap.add_argument("--out", help="output folder (default client-kit/sites/<slug>)")
    args = ap.parse_args(argv)
    try:
        cfg = load_config(args.config)
        out = args.out or os.path.join(KIT, "sites", cfg["slug"])
        written = build(cfg, out)
    except (ConfigError, json.JSONDecodeError, OSError) as e:
        print(f"generate.py: {e}", file=sys.stderr)
        return 1
    print(f"Wrote {len(written)} files to {os.path.relpath(out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
