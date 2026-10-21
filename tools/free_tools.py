"""Ten more free HVAC calculators, driven by a small spec and gcalc.js.

Each NEW_TOOLS entry has the same keys as build.py's TOOLS entries, plus:
  fields:  [{"id", "label", "default", "hint"?, "options"?: [[value, label], ...]}]
  outputs: [{"id", "label", "expr", "fmt"}]  (expr is JavaScript over field ids
           and earlier output ids; fmt is money, int, pct or num1)
Percent fields are typed as whole numbers (40 means 40%), so exprs divide by 100.
"""
import json

YOURS = "An example. Change it to your own number."


def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&#39;"))


NEW_TOOLS = [
    {"slug": "hvac-cost-per-lead-calculator", "name": "Cost per lead calculator", "line": "What each lead and each booked job costs you",
     "title": "HVAC cost per lead calculator",
     "desc": "Free calculator: see what each lead and each booked job costs your HVAC company. Put in your marketing spend, leads and booking rate. No email needed.",
     "lede": "Put in what you spent on marketing last month, how many leads came in and how many of them you booked. A cheap lead that never books can cost more than a pricey one that does.",
     "formula": ["Cost per lead = marketing spend / leads", "Booked jobs = leads x booking rate", "Cost per booked job = marketing spend / booked jobs"],
     "improve": [("Answer every call", "A lead you miss still costs money. Text back missed calls so they don't call the next shop."), ("Track which source booked", "Ask every caller how they found you, or use tracking numbers, so you know which spend books jobs."), ("Follow up on the ones that didn't book", "A quick text a day later turns some 'not yet' leads into jobs at no extra cost.")],
     "service": "missed-call-text-back", "guide": "hvac-marketing-cost",
     "fields": [
         {"id": "spend", "label": "Marketing spend last month ($)", "default": "5000", "hint": YOURS},
         {"id": "leads", "label": "Leads that came in", "default": "100", "hint": "Calls, forms and chats from new customers."},
         {"id": "book", "label": "Share of leads you booked (%)", "default": "50", "hint": YOURS},
     ],
     "outputs": [
         {"id": "cpl", "label": "cost per lead", "expr": "leads > 0 ? spend / leads : NaN", "fmt": "money"},
         {"id": "jobs", "label": "booked jobs", "expr": "leads * book / 100", "fmt": "int"},
         {"id": "cpj", "label": "cost per booked job", "expr": "jobs > 0 ? spend / jobs : NaN", "fmt": "money"},
     ]},
    {"slug": "hvac-close-rate-calculator", "name": "Close rate calculator", "line": "Your booking and close rates, and what one point is worth",
     "title": "HVAC close rate calculator",
     "desc": "Free calculator: work out your HVAC booking rate and close rate, and what one more point of closing is worth in revenue. Your numbers, no email needed.",
     "lede": "Put in your leads, the calls you booked and the jobs you sold, plus your average sale. See your rates and how much revenue each extra point of close rate would bring in a month.",
     "formula": ["Booking rate = booked / leads", "Close rate = sold / booked", "Revenue per 1 point of close rate = booked x 1% x average sale"],
     "improve": [("Follow up on every estimate", "Many homeowners need a nudge. A text and a call in the days after the visit wins some back."), ("Send reviews before the visit", "A homeowner who has read your reviews is easier to close."), ("Answer fast", "The shop that calls back first often gets the booking.")],
     "service": "estimate-follow-up", "guide": "questions-to-ask-hvac-marketing-agency",
     "fields": [
         {"id": "leads", "label": "Leads a month", "default": "120", "hint": YOURS},
         {"id": "booked", "label": "Appointments booked a month", "default": "70"},
         {"id": "sold", "label": "Jobs sold a month", "default": "40"},
         {"id": "ticket", "label": "Average sale ($)", "default": "900", "hint": YOURS},
     ],
     "outputs": [
         {"id": "bookrate", "label": "booking rate", "expr": "leads > 0 ? booked / leads * 100 : NaN", "fmt": "pct"},
         {"id": "closerate", "label": "close rate", "expr": "booked > 0 ? sold / booked * 100 : NaN", "fmt": "pct"},
         {"id": "revenue", "label": "revenue a month from sold jobs", "expr": "sold * ticket", "fmt": "money"},
         {"id": "perpoint", "label": "extra revenue a month for each 1 point of close rate", "expr": "booked * 0.01 * ticket", "fmt": "money"},
     ]},
    {"slug": "lsa-cost-calculator", "name": "Local Services Ads cost calculator", "line": "What Local Services Ads cost and bring back",
     "title": "Local Services Ads cost calculator for HVAC",
     "desc": "Free calculator: estimate what Google Local Services Ads cost your HVAC company each month, how many jobs they book and the revenue back for each dollar. Your numbers.",
     "lede": "Local Services Ads charge per lead. Put in what you pay per lead, how many you get a month, how many you book and your average ticket to see the monthly cost, jobs and revenue.",
     "formula": ["Monthly cost = cost per lead x leads a month", "Booked jobs = leads a month x booking rate", "Revenue = booked jobs x average ticket", "Revenue per $1 spent = revenue / monthly cost"],
     "improve": [("Answer every lead fast", "Paid leads that go to voicemail are money spent for nothing."), ("Dispute leads that don't fit", "Google lets you ask for credit on some leads that aren't real jobs. Check yours."), ("Grow your reviews", "Reviews show on your ad, so they matter to the homeowner choosing who to call.")],
     "service": "local-services-ads", "guide": "google-map-pack-hvac",
     "fields": [
         {"id": "cpl", "label": "What you pay per lead ($)", "default": "60", "hint": YOURS},
         {"id": "leads", "label": "Leads a month", "default": "40"},
         {"id": "book", "label": "Share of leads you book (%)", "default": "50", "hint": YOURS},
         {"id": "ticket", "label": "Average ticket ($)", "default": "500"},
     ],
     "outputs": [
         {"id": "cost", "label": "monthly cost", "expr": "cpl * leads", "fmt": "money"},
         {"id": "jobs", "label": "booked jobs a month", "expr": "leads * book / 100", "fmt": "num1"},
         {"id": "revenue", "label": "revenue a month", "expr": "jobs * ticket", "fmt": "money"},
         {"id": "ret", "label": "revenue back for each $1 spent", "expr": "cost > 0 ? revenue / cost : NaN", "fmt": "num1"},
     ]},
    {"slug": "google-ads-budget-calculator-hvac", "name": "Google Ads budget calculator", "line": "The ad budget it takes to hit your job goal",
     "title": "Google Ads budget calculator for HVAC",
     "desc": "Free calculator: work back from the jobs you want each month to the Google Ads budget an HVAC company would need, using your cost per click and call rates.",
     "lede": "Start with the jobs you want from ads each month. Put in how many callers you book, how many clicks turn into calls and what a click costs, and the tool works back to a budget.",
     "formula": ["Calls needed = target jobs / booking rate", "Clicks needed = calls needed / click-to-call rate", "Monthly budget = clicks needed x cost per click", "Ad cost per booked job = budget / target jobs"],
     "improve": [("Send clicks to a page that matches", "A page about the exact service they searched turns more clicks into calls."), ("Book more of the calls", "Raising your booking rate cuts the budget you need for the same jobs."), ("Cut searches that don't book", "Check the search terms report and block ones that bring the wrong calls.")],
     "service": "google-ads", "guide": "hvac-marketing-cost",
     "fields": [
         {"id": "target", "label": "Jobs you want from ads a month", "default": "30", "hint": YOURS},
         {"id": "book", "label": "Share of calls you book (%)", "default": "50"},
         {"id": "ctc", "label": "Share of clicks that call (%)", "default": "10", "hint": "Check your own ads account. This is only an example."},
         {"id": "cpc", "label": "Cost per click ($)", "default": "25", "hint": YOURS},
     ],
     "outputs": [
         {"id": "calls", "label": "calls needed a month", "expr": "book > 0 ? target / (book / 100) : NaN", "fmt": "int"},
         {"id": "clicks", "label": "clicks needed a month", "expr": "ctc > 0 ? calls / (ctc / 100) : NaN", "fmt": "int"},
         {"id": "budget", "label": "monthly budget needed", "expr": "clicks * cpc", "fmt": "money"},
         {"id": "perjob", "label": "ad cost per booked job", "expr": "target > 0 ? budget / target : NaN", "fmt": "money"},
     ]},
    {"slug": "hvac-maintenance-plan-calculator", "name": "Maintenance plan calculator", "line": "What your service agreements bring in a year",
     "title": "HVAC maintenance plan calculator",
     "desc": "Free calculator: see the yearly recurring revenue from your HVAC maintenance plan members, including renewals and the repair work members bring in.",
     "lede": "Put in your members, what the plan costs a year, how many renew and the extra repair work a member brings in. See what the plan is worth this year and what carries into next year.",
     "formula": ["Plan revenue = members x plan price a year", "Repair revenue = members x extra repair revenue per member", "Total this year = plan revenue + repair revenue", "Members next year = members x renewal rate"],
     "improve": [("Offer the plan on every call", "Every service visit is a chance to sign a member."), ("Remind before renewal", "A text before the plan runs out keeps more members."), ("Book tune-ups early", "Seasonal reminders fill slow weeks with member visits.")],
     "service": "seasonal-campaigns", "guide": "hvac-marketing-cost",
     "fields": [
         {"id": "members", "label": "Plan members today", "default": "300", "hint": YOURS},
         {"id": "price", "label": "Plan price a year ($)", "default": "200"},
         {"id": "renew", "label": "Share who renew each year (%)", "default": "70", "hint": YOURS},
         {"id": "extra", "label": "Extra repair revenue per member a year ($)", "default": "150", "hint": "Repairs members buy beyond the plan itself."},
     ],
     "outputs": [
         {"id": "plan", "label": "plan revenue a year", "expr": "members * price", "fmt": "money"},
         {"id": "repairs", "label": "repair revenue from members a year", "expr": "members * extra", "fmt": "money"},
         {"id": "total", "label": "total yearly revenue from members", "expr": "plan + repairs", "fmt": "money"},
         {"id": "next", "label": "members who renew next year", "expr": "members * renew / 100", "fmt": "int"},
     ]},
    {"slug": "hvac-marketing-budget-calculator", "name": "Marketing budget calculator", "line": "Turn a share of revenue into a monthly budget",
     "title": "HVAC marketing budget calculator",
     "desc": "Free calculator: turn your HVAC company's yearly revenue and the share you want to spend on marketing into a yearly and monthly marketing budget.",
     "lede": "Put in your yearly revenue and the share you want to put into marketing. Pick the share that fits your goals and margins; there's no single right number, so try a few.",
     "formula": ["Yearly budget = yearly revenue x share to marketing", "Monthly budget = yearly budget / 12", "Jobs to cover a month = monthly budget / average ticket"],
     "improve": [("Spend on what books jobs", "Track booked jobs by source so the budget goes where it pays."), ("Keep the customers you have", "Reviews, reminders and plans cost less than finding new customers."), ("Plan for the seasons", "Spend more before the busy months and on tune-ups in the slow ones.")],
     "service": "hq-command-center", "guide": "hvac-marketing-cost",
     "fields": [
         {"id": "revenue", "label": "Yearly revenue ($)", "default": "1500000", "hint": YOURS},
         {"id": "share", "label": "Share to marketing (%)", "default": "5", "hint": "Your choice. Try a few to compare."},
         {"id": "ticket", "label": "Average ticket ($)", "default": "500"},
     ],
     "outputs": [
         {"id": "year", "label": "yearly marketing budget", "expr": "revenue * share / 100", "fmt": "money"},
         {"id": "month", "label": "monthly marketing budget", "expr": "year / 12", "fmt": "money"},
         {"id": "jobs", "label": "jobs a month to cover the budget in revenue", "expr": "ticket > 0 ? month / ticket : NaN", "fmt": "num1"},
     ]},
    {"slug": "hvac-customer-lifetime-value-calculator", "name": "Customer lifetime value calculator", "line": "What one customer is worth over the years",
     "title": "HVAC customer lifetime value calculator",
     "desc": "Free calculator: see what one HVAC customer is worth over the years in revenue and gross profit, from your average ticket, visits a year and years they stay.",
     "lede": "One furnace repair can turn into years of tune-ups, repairs and a new system. Put in your own numbers to see what a customer is worth, and what you can afford to spend to win one.",
     "formula": ["Revenue a year = average ticket x visits a year", "Lifetime revenue = revenue a year x years as a customer", "Lifetime gross profit = lifetime revenue x gross margin"],
     "improve": [("Ask for a review after every job", "Happy customers who leave reviews help win the next ones."), ("Sign them to a plan", "Plan members tend to come back on a schedule."), ("Stay in touch", "Seasonal reminders keep you the shop they call.")],
     "service": "review-requests", "guide": "google-reviews-hvac",
     "fields": [
         {"id": "ticket", "label": "Average ticket ($)", "default": "450", "hint": YOURS},
         {"id": "visits", "label": "Visits a year", "default": "1.5"},
         {"id": "years", "label": "Years as a customer", "default": "6", "hint": YOURS},
         {"id": "margin", "label": "Gross margin (%)", "default": "45"},
     ],
     "outputs": [
         {"id": "yearly", "label": "revenue a year per customer", "expr": "ticket * visits", "fmt": "money"},
         {"id": "life", "label": "lifetime revenue per customer", "expr": "yearly * years", "fmt": "money"},
         {"id": "profit", "label": "lifetime gross profit per customer", "expr": "life * margin / 100", "fmt": "money"},
     ]},
    {"slug": "hvac-seo-roi-calculator", "name": "SEO ROI calculator", "line": "Whether extra Google calls pay for SEO",
     "title": "HVAC SEO ROI calculator",
     "desc": "Free calculator: check if local SEO pays for itself for an HVAC company. Put in the extra calls from Google, your booking rate, ticket, margin and monthly cost.",
     "lede": "Put in how many extra calls a month you get (or expect) from Google search and the map, your booking rate, average ticket, margin and what you pay. See the profit and return.",
     "formula": ["Extra jobs = extra calls x booking rate", "Extra gross profit = extra jobs x average ticket x margin", "ROI = (extra gross profit - monthly cost) / monthly cost"],
     "improve": [("Fill out your Google profile", "Services, photos and hours all help you show up for the right searches."), ("Build a page for each service and town", "Homeowners search for a service in a place. Give them a page that matches."), ("Get more reviews", "Reviews help you show up and help the caller choose you.")],
     "service": "local-seo", "guide": "google-map-pack-hvac",
     "fields": [
         {"id": "calls", "label": "Extra calls a month from Google", "default": "20", "hint": YOURS},
         {"id": "book", "label": "Share of calls you book (%)", "default": "50"},
         {"id": "ticket", "label": "Average ticket ($)", "default": "500"},
         {"id": "margin", "label": "Gross margin (%)", "default": "45"},
         {"id": "cost", "label": "SEO cost a month ($)", "default": "1000", "hint": YOURS},
     ],
     "outputs": [
         {"id": "jobs", "label": "extra jobs a month", "expr": "calls * book / 100", "fmt": "num1"},
         {"id": "profit", "label": "extra gross profit a month", "expr": "jobs * ticket * margin / 100", "fmt": "money"},
         {"id": "net", "label": "profit after the SEO cost", "expr": "profit - cost", "fmt": "money"},
         {"id": "roi", "label": "return on the monthly cost", "expr": "cost > 0 ? net / cost * 100 : NaN", "fmt": "pct"},
     ]},
    {"slug": "after-hours-call-calculator", "name": "After-hours call calculator", "line": "What missed night and weekend calls cost",
     "title": "After-hours call calculator for HVAC",
     "desc": "Free calculator: see what missed after-hours calls on nights and weekends could cost your HVAC company in a year. Your numbers, no email needed.",
     "lede": "No heat at 9pm doesn't wait for Monday. Put in your after-hours calls a week, how many go unanswered, your average ticket and how many you'd book to see the yearly cost.",
     "formula": ["Missed calls a week = after-hours calls x share missed", "Lost jobs a week = missed calls x booking rate", "Lost revenue a year = lost jobs a week x average ticket x 52"],
     "improve": [("Text back every missed call", "A reply within 10 seconds tells the caller someone will help."), ("Put chat on your site", "AI web chat takes the address and the problem at night, so you can call back first thing."), ("Say your hours plainly", "Tell callers when you'll call back so they don't keep dialing other shops.")],
     "service": "ai-web-chat", "guide": "missed-call-text-back-hvac",
     "fields": [
         {"id": "calls", "label": "After-hours calls a week", "default": "15", "hint": YOURS},
         {"id": "missed", "label": "Share that go unanswered (%)", "default": "50"},
         {"id": "ticket", "label": "Average ticket ($)", "default": "450"},
         {"id": "book", "label": "Share you'd book if answered (%)", "default": "50", "hint": YOURS},
     ],
     "outputs": [
         {"id": "week", "label": "missed calls a week", "expr": "calls * missed / 100", "fmt": "num1"},
         {"id": "jobs", "label": "lost jobs a year", "expr": "week * book / 100 * 52", "fmt": "int"},
         {"id": "year", "label": "lost revenue a year", "expr": "jobs * ticket", "fmt": "money"},
     ]},
    {"slug": "hvac-estimate-follow-up-calculator", "name": "Estimate follow-up calculator", "line": "What following up on quotes is worth",
     "title": "HVAC estimate follow-up calculator",
     "desc": "Free calculator: see the extra revenue an HVAC company could win each month and year by closing more replacement estimates with follow-up.",
     "lede": "Put in your replacement estimates a month, the average price, your close rate now and the close rate you think follow-up could reach. See what the gap is worth.",
     "formula": ["Jobs now = estimates x close rate now", "Jobs with follow-up = estimates x close rate with follow-up", "Extra revenue a month = (jobs with follow-up - jobs now) x average price", "Extra revenue a year = extra a month x 12"],
     "improve": [("Follow up the same day", "A thank-you text with the quote keeps you top of mind."), ("Check in a few days later", "Answer questions about financing and options before they shop around."), ("Keep going", "Some homeowners take weeks to decide. A steady, polite follow-up keeps you in it.")],
     "service": "estimate-follow-up", "guide": "questions-to-ask-hvac-marketing-agency",
     "fields": [
         {"id": "est", "label": "Replacement estimates a month", "default": "20", "hint": YOURS},
         {"id": "price", "label": "Average replacement price ($)", "default": "10000"},
         {"id": "now", "label": "Close rate now (%)", "default": "30"},
         {"id": "after", "label": "Close rate with follow-up (%)", "default": "35", "hint": "Your guess. Try a few."},
     ],
     "outputs": [
         {"id": "jobsnow", "label": "jobs closed a month now", "expr": "est * now / 100", "fmt": "num1"},
         {"id": "jobsafter", "label": "jobs closed a month with follow-up", "expr": "est * after / 100", "fmt": "num1"},
         {"id": "month", "label": "extra revenue a month", "expr": "(jobsafter - jobsnow) * price", "fmt": "money"},
         {"id": "year", "label": "extra revenue a year", "expr": "month * 12", "fmt": "money"},
     ]},
]


def gcalc_widget(t):
    rows = []
    for f in t["fields"]:
        fid = f"g-{t['slug']}-{f['id']}"
        if f.get("options"):
            opts = "".join(
                f'<option value="{_esc(v)}"{" selected" if str(v) == str(f["default"]) else ""}>{_esc(lbl)}</option>'
                for v, lbl in f["options"])
            ctl = f'<select id="{_esc(fid)}" name="{_esc(f["id"])}">{opts}</select>'
        else:
            ctl = f'<input id="{_esc(fid)}" type="text" inputmode="decimal" name="{_esc(f["id"])}" value="{_esc(f["default"])}">'
        hint = f'<div class="hint">{_esc(f["hint"])}</div>' if f.get("hint") else ""
        rows.append(f'    <div class="field"><label for="{_esc(fid)}">{_esc(f["label"])}</label>{ctl}{hint}</div>')
    outs = "\n".join(f'    <div class="row"><span class="big" data-out="{_esc(o["id"])}">–</span><p>{_esc(o["label"])}</p></div>'
                     for o in t["outputs"])
    spec = {"fields": [f["id"] for f in t["fields"]],
            "outputs": [{"id": o["id"], "expr": o["expr"], "fmt": o["fmt"]} for o in t["outputs"]]}
    spec_json = json.dumps(spec).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    fields = "\n".join(rows)
    return f"""<div class="calc gcalc" data-tool="{_esc(t['slug'])}">
  <div>
{fields}
  </div>
  <div class="calc-out" aria-live="polite">
{outs}
    <p style="font-size:.85rem">Your numbers; this is math, not a promise of results.</p>
    <a class="calc-next" href="#report-card">See which shops near you are getting these calls: free report card &rarr;</a>
  </div>
  <script type="application/json" class="gcalc-spec">{spec_json}</script>
</div>"""
