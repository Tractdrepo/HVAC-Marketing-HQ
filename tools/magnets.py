# Free downloads offered for an email. The page content stays free on the site; the download is the
# printable version, emailed so the shop has it later. Delivery: api/magnet.js.

SCORECARD = {
    "key": "scorecard",
    "file": "downloads/hvac-online-scorecard.pdf",
    "title": "The 40-point HVAC online scorecard",
    "sub": "Website, Google profile, reviews and follow-up. Print it, check yes or no, add up your score.",
    "scoring": [("35 to 40", "Strong. Keep it up and keep adding reviews."), ("25 to 34", "Leaking calls. Fix the no's under speed and follow-up first."), ("Under 25", "Costing you jobs every week. Start with speed, tap-to-call and missed-call text-back.")],
    "sections": [
        ("Website: speed and phone", [
            "The home page shows something useful within about 2.5 seconds on your phone's mobile data.",
            "Your phone number is a tap-to-call button at the top of every page.",
            "Nothing covers the screen when a page opens: no pop-up, no full-screen chat.",
            "Text is readable without zooming, and buttons are easy to hit with a thumb.",
            "The site scores in the green on Google's PageSpeed Insights for mobile.",
        ]),
        ("Website: getting found", [
            "A separate page for each service you want more of: AC repair, heating, installs, maintenance plans.",
            "A real page for each town you take calls in, not the same page with the name swapped.",
            "Each page title says what and where, like \"AC Repair in Dallas, TX | Your Shop\".",
            "Business name, address and phone on the site match your Google profile exactly.",
            "Your Google profile links to your site, and your site links back to your profile.",
        ]),
        ("Website: turning visits into calls", [
            "The first screen says what you do, where, and how to reach you, in one short line.",
            "There's a way to book or request service without calling.",
            "Forms are short: name, phone, what's wrong. Four fields or fewer.",
            "Form fills get an answer within minutes, including after hours.",
            "Financing, if you offer it, sits on the install and replacement pages.",
        ]),
        ("Website: trust and tracking", [
            "Real photos of your crew, trucks and work. No stock photos.",
            "Your real Google reviews on the page, ideally from the same town and service.",
            "Your contractor license number in the footer.",
            "You can see how many calls and forms came from the site each month.",
            "Someone updates the site when hours, services or prices change.",
        ]),
        ("Google Business Profile", [
            "The profile is verified, and you own it, not a past agency or employee.",
            "Primary category is HVAC contractor or the closest fit, with secondary categories for the services you want.",
            "The business name is your real name, with no keywords added.",
            "The service area lists the towns you really serve.",
            "Hours are right, including after-hours or emergency hours if you take those calls.",
            "Every service you offer is listed, with a short description.",
            "At least 10 real photos of your crew, trucks and installs, with new ones each month.",
            "A post in the last 30 days: a tune-up reminder, a recent job or a seasonal offer.",
            "The website link goes to your site, tagged so you can see the calls it sends.",
            "The phone number is one your office or your text-back system always answers.",
        ]),
        ("Reviews", [
            "Every customer gets asked, after every job. No picking only the happy ones.",
            "The ask goes out by text within a few hours of the job, with a direct link.",
            "Every review gets a reply, good or bad, within a few days.",
            "Replies mention the service and town in plain words.",
            "You know your rating and review count against the top three shops on the map near you.",
        ]),
        ("Follow-up", [
            "Every missed call gets a text back within minutes, including nights and weekends.",
            "Every estimate gets at least three follow-ups before it's marked lost.",
            "Past customers get a spring AC and a fall heating tune-up reminder.",
            "Maintenance plan members get a renewal reminder before the plan lapses.",
            "One place shows calls, texts, booked jobs and reviews, so you know what's working.",
        ]),
    ],
}
assert sum(len(i) for _, i in SCORECARD["sections"]) == 40

MAGNETS = {SCORECARD["key"]: SCORECARD}


def scorecard_print_html(brand, domain):
    m = SCORECARD
    n = 0
    secs = []
    for h, items in m["sections"]:
        lis = []
        for it in items:
            n += 1
            lis.append(f'<li><span class="n">{n}</span><span class="t">{it}</span><span class="box">Yes</span><span class="box">No</span></li>')
        secs.append(f'<section><h2>{h}</h2><ol>{"".join(lis)}</ol></section>')
    score = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td></tr>" for a, b in m["scoring"])
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex"><title>{m['title']}</title>
<style>
@font-face {{ font-family: Archivo; font-weight: 600 800; font-stretch: 100% 125%; src: url(../fonts/Archivo-600-800.woff2) format('woff2'); }}
@font-face {{ font-family: 'IBM Plex Sans'; font-weight: 400; src: url(../fonts/IBMPlexSans-400.woff2) format('woff2'); }}
@page {{ size: Letter; margin: 14mm 14mm 16mm; }}
* {{ box-sizing: border-box; }}
body {{ font: 10.5pt/1.4 'IBM Plex Sans', Helvetica, Arial, sans-serif; color: #101826; margin: 0; }}
header {{ display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 3px solid; border-image: linear-gradient(90deg, #47b8ff, #ff6a2b) 1; padding-bottom: 10px; margin-bottom: 14px; }}
h1 {{ font: 800 21pt/1.1 Archivo, Helvetica, sans-serif; margin: 0 0 4px; }}
header p {{ margin: 0; color: #4b5a6c; }}
.brand {{ text-align: right; font-weight: 700; font-size: 10pt; }} .brand small {{ display: block; font-weight: 400; color: #4b5a6c; }}
h2 {{ font: 700 12pt/1.2 Archivo, Helvetica, sans-serif; margin: 12px 0 4px; color: #0b5e93; }}
section {{ break-inside: avoid; }}
ol {{ list-style: none; padding: 0; margin: 0; }}
li {{ display: grid; grid-template-columns: 22px 1fr 42px 42px; gap: 8px; align-items: center; padding: 4px 0; border-bottom: 1px solid #e3e7ec; }}
.n {{ font: 600 8.5pt monospace; color: #8a97a8; }}
.box {{ border: 1.2px solid #9aa6b5; border-radius: 4px; text-align: center; font-size: 8pt; color: #6b7889; padding: 2px 0; }}
.score {{ margin-top: 16px; border: 1px solid #d5dbe3; border-radius: 8px; padding: 10px 14px; break-inside: avoid; }}
.score table {{ width: 100%; border-collapse: collapse; }} .score td {{ padding: 4px 6px; }}
.total {{ font: 700 12pt Archivo, Helvetica, sans-serif; }}
footer {{ margin-top: 14px; font-size: 9pt; color: #4b5a6c; }}
</style></head><body>
<header><div><h1>{m['title']}</h1><p>{m['sub']}</p></div><div class="brand">{brand}<small>{domain}</small></div></header>
{''.join(secs)}
<div class="score"><p class="total">Your score: ______ / 40</p><table>{score}</table></div>
<footer>Want this checked for you? Get a free report card at {domain}/report-card: your Google profile, reviews, website and listings graded against the shops near you.</footer>
</body></html>"""


def magnet_box(u, key="scorecard", heading=None):
    m = MAGNETS[key]
    return f"""<div class="magnet reveal">
  <div class="magnet-copy"><span class="eyebrow">Free download</span><h3>{heading or m['title']}</h3><p>{m['sub']} We'll email you the printable PDF.</p></div>
  <form class="magnet-form" data-magnet="{key}" novalidate>
    <input type="text" name="company_fax" tabindex="-1" autocomplete="off" class="hp" aria-hidden="true">
    <label class="sr-only" for="mg-name-{key}">First name</label><input id="mg-name-{key}" name="first_name" placeholder="First name" autocomplete="given-name" required>
    <label class="sr-only" for="mg-email-{key}">Email</label><input id="mg-email-{key}" name="email" type="email" placeholder="Email" autocomplete="email" required>
    <button class="btn btn-primary" type="submit">Email me the PDF</button>
    <p class="magnet-fine">One email with the PDF. No sales calls. Unsubscribe anytime.</p>
    <p class="magnet-msg" role="status"></p>
  </form>
</div>"""
