# Guides: long-form, sourced articles. Rendered by build.py (guide_page / guides_page).
# Rules: every number has a source in "sources" or is our own; no invented stats or proof; plain words.
# Body blocks: ("p", text) · ("ul", [items]) · ("ol", [items]) · ("table", [header, *rows]) · ("note", text) · ("cta",)
# Text may contain simple inline HTML (<b>, <a>).

UPDATED = "Oct 12, 2026"
AUTHOR = "Logan, founder of HVAC Marketing HQ"

GUIDES = [
    {
        "slug": "google-map-pack-hvac",
        "title": "How Google picks the HVAC companies in the map pack",
        "short": "Map pack ranking",
        "desc": "The three things Google says decide local rankings, what an HVAC company can actually change, and what to stop paying for.",
        "read": 8,
        "takeaways": [
            "Google says local results come down to three things: relevance, distance and prominence.",
            "You can't change distance, so the work goes into relevance (categories, services, pages) and prominence (reviews, activity, links).",
            "The fastest wins are usually your main category, your service list and a steady flow of new reviews.",
            "Nobody can guarantee a #1 spot. Be careful with anyone who does.",
        ],
        "sections": [
            ("What the map pack is", [
                ("p", "Search \"AC repair near me\" on a phone and the first thing you see, under any ads, is a map with three businesses. That's the map pack, also called the local pack. Tap \"more places\" and you get the full local list. For an HVAC company, being in those first three is usually worth more than any page-one website ranking, because the map shows your stars, your hours and a call button before the homeowner ever visits a site."),
            ]),
            ("The three things Google says it looks at", [
                ("p", "Google publishes how local ranking works in its Business Profile help pages. It names three factors:"),
                ("ul", [
                    "<b>Relevance:</b> how well your profile matches what the person searched for.",
                    "<b>Distance:</b> how far your business is from the person searching, or from the place they named.",
                    "<b>Prominence:</b> how well known your business is, which Google says includes reviews, links and how you show up across the web.",
                ]),
                ("p", "Google also says there's no way to pay for a better local ranking. Local Services Ads and Google Ads sit above the map, but they don't move your spot in it."),
            ]),
            ("Distance: the one you can't change", [
                ("p", "A shop on the north side of town will usually rank better for searches on the north side. That's why a company can be #2 in one neighborhood and #14 a few miles away. You can't move your shop, and you shouldn't fake an address: Google's guidelines don't allow it, and a suspended profile is far worse than a lower ranking."),
                ("p", "What you can do is make it obvious where you work. Set your service area in your profile, and build a real page on your website for each town you take calls in, with your work there and reviews from customers there."),
            ]),
            ("Relevance: where most shops leave easy points", [
                ("p", "Relevance is mostly about telling Google exactly what you do. The common misses we see:"),
                ("ol", [
                    "<b>The wrong main category.</b> Your primary category carries the most weight. For most shops it should be \"HVAC contractor\" or \"Air conditioning contractor\", not \"Contractor\" or \"Electrician\".",
                    "<b>No services listed.</b> Add every service you want calls for: AC repair, furnace repair, heat pump installation, duct cleaning, maintenance plans.",
                    "<b>A website with one page.</b> If your site has no page about AC repair, Google has less to match against an AC repair search. One clear page per service you want more of helps.",
                    "<b>Hours that are wrong.</b> If you take emergency calls, say so. Profiles that look closed at the moment of the search lose the click.",
                ]),
            ]),
            ("Prominence: the slow, steady part", [
                ("p", "Prominence is where steady work beats one-time fixes. Google says more reviews and positive ratings can help your local ranking, and that replying shows you value customers' feedback. In practice that means:"),
                ("ul", [
                    "Ask every customer for a review after every finished job, not in bursts.",
                    "Reply to every review, good or bad, in your own words.",
                    "Post photos of real jobs and your real crew and trucks.",
                    "Keep your name, address and phone the same everywhere: Facebook, Yelp, BBB, Angi, Nextdoor and the rest.",
                ]),
                ("p", "See <a href=\"{u:guide-google-reviews-hvac}\">how many Google reviews an HVAC company needs</a> for the review side in detail."),
            ]),
            ("What to stop paying for", [
                ("ul", [
                    "<b>Guaranteed rankings.</b> Google says nobody can guarantee a local ranking. A guarantee usually means fine print.",
                    "<b>Fake addresses or virtual offices</b> to rank in another town. These break Google's guidelines and get profiles suspended.",
                    "<b>Keyword-stuffed business names</b> like \"Best AC Repair Waco Heating &amp; Air\". Google's guidelines say your name should match your real-world name.",
                    "<b>Review packages</b> that buy or swap reviews. Google removes them, and the FTC's 2024 rule on consumer reviews bans buying fake ones.",
                ]),
            ]),
            ("How to check where you stand", [
                ("p", "Search your top two services plus your town, on your phone, from a few spots in your service area. Write down where you show up. Or let us do it: the free report card runs two real searches for your town and shows where you land against the top shops near you."),
                ("cta",),
            ]),
        ],
        "faq": [
            ("How long does it take to move up the map?", "Fixes to your category, services and hours can show up within weeks. Moving up through reviews and town pages is slower, usually months, and depends on how crowded your market is."),
            ("Do Google Ads help my map ranking?", "No. Google says you can't pay to improve your local ranking. Ads and Local Services Ads show above the map, separately."),
            ("Should I open a second location to rank in another town?", "Only if it's a real, staffed location. A virtual office or a mailbox breaks Google's guidelines and can get your profile suspended."),
        ],
        "sources": [
            ("Google Business Profile Help: Tips to improve your local ranking on Google", "https://support.google.com/business/answer/7091"),
            ("Google: Guidelines for representing your business on Google", "https://support.google.com/business/answer/3038177"),
            ("FTC: Final rule banning fake reviews and testimonials (Aug 2024)", "https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials"),
        ],
        "related": ["google-reviews-hvac", "hvac-website-checklist"],
    },
    {
        "slug": "google-reviews-hvac",
        "title": "How many Google reviews does an HVAC company need?",
        "short": "Google reviews",
        "desc": "There's no magic number. What matters is how recent and steady your reviews are, how you ask, and why filtering out unhappy customers is against Google's rules.",
        "read": 7,
        "takeaways": [
            "There's no number Google publishes. Compare yourself with the shops that outrank you, not with a national average.",
            "Recent, steady reviews beat a big pile of old ones. A shop that finishes jobs every day should get reviews every week.",
            "Ask every customer the same way, every time. Filtering out unhappy customers before they reach Google breaks Google's rules.",
            "Reply to every review. It shows the next customer how you treat people.",
        ],
        "sections": [
            ("The honest answer: enough to beat the shops above you", [
                ("p", "You'll find blog posts with a magic number. Google doesn't publish one. What it does say is that review count and rating are part of how prominent your business looks, and prominence is one of the three things local ranking depends on (see <a href=\"{u:guide-google-map-pack-hvac}\">how the map pack works</a>)."),
                ("p", "So the useful comparison is local. Search your main service and your town, look at the three shops in the map pack, and note their star rating, how many reviews they have and how old their newest review is. That's your bar. Our free report card does exactly this comparison against the top three shops in your search."),
            ]),
            ("Why recent reviews matter more than a big total", [
                ("p", "Homeowners read the newest reviews first, and a profile whose last review is five months old looks like a business that slowed down. A steady flow also protects you: one bad review lands among several good ones instead of sitting on top for weeks."),
                ("p", "A busy shop finishes jobs every day. If reviews arrive once a month, the problem isn't your work, it's that nobody is asking."),
            ]),
            ("How to ask without nagging", [
                ("ol", [
                    "<b>Ask right after the job</b>, while the house is cool again. A text with a direct link to your review form works better than asking on the spot.",
                    "<b>Ask everyone</b>, the same way, every time. Make it automatic when a job is marked done so it never depends on someone remembering.",
                    "<b>Keep it short</b> and from a real person: \"Thanks for having us out today. If we did right by you, a quick Google review helps a lot.\"",
                    "<b>One reminder at most.</b> Then stop.",
                ]),
            ]),
            ("Review gating: the practice to avoid", [
                ("p", "Some review tools first ask \"How did we do, 1 to 5?\" and send only the 4s and 5s to Google, while the 1s, 2s and 3s go to a private form. It's sold as a feature. It's against Google's rules. Google's Maps content policy says businesses may not \"discourage or prohibit negative reviews, or selectively solicit positive reviews from customers.\" Reviews that break the policy can be removed."),
                ("note", "We ask every customer the same way and never filter. If a customer is unhappy, the right move is to fix the job and reply to the review, not hide it."),
            ]),
            ("What to do about a bad review", [
                ("ul", [
                    "Reply within a day or two, calmly. Thank them, say what you'll do, and take it offline with a phone number.",
                    "Don't argue the details in public. The next customer is reading your reply more than their review.",
                    "Only flag a review for removal if it breaks Google's rules (fake, spam, off-topic or abusive). Disliking it isn't enough.",
                    "Keep asking every customer. Fresh good reviews put one bad one in context.",
                ]),
            ]),
            ("Should you reply to every review?", [
                ("p", "Yes. Google says replying shows customers you value them. It also gives you a chance to mention the service and town naturally (\"Glad we got your heat pump running in Hewitt\"), which reads better to the next homeowner than a stock \"Thanks!\"."),
                ("cta",),
            ]),
        ],
        "faq": [
            ("Can I offer a discount for a review?", "No. Google's policy doesn't allow offering incentives for reviews, and the FTC's 2024 review rule also covers paid reviews that require a certain sentiment."),
            ("Can my employees or family leave reviews?", "They shouldn't. Reviews should come from real customers. Google can remove reviews it sees as a conflict of interest."),
            ("Do star ratings below 5.0 hurt me?", "Not much, and a perfect 5.0 from a few reviews can look less believable than a 4.8 from hundreds. Volume and recency matter."),
        ],
        "sources": [
            ("Google Maps user-generated content policy: Prohibited and restricted content", "https://support.google.com/contributionpolicy/answer/7400114"),
            ("Google Business Profile Help: Tips to get more reviews", "https://support.google.com/business/answer/3474122"),
            ("Google Business Profile Help: Tips to improve your local ranking on Google", "https://support.google.com/business/answer/7091"),
            ("FTC: Final rule banning fake reviews and testimonials (Aug 2024)", "https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials"),
        ],
        "related": ["google-map-pack-hvac", "missed-call-text-back-hvac"],
    },
    {
        "slug": "missed-call-text-back-hvac",
        "title": "Missed-call text-back for HVAC: how it works and how to do it legally",
        "short": "Missed-call text-back",
        "desc": "What missed-call text-back is, why it matters most on the hottest days, the carrier registration it needs, and the Texas texting rules to know.",
        "read": 7,
        "takeaways": [
            "When you can't answer, the caller gets a text from your business within seconds, so they reply to you instead of calling the next shop.",
            "It matters most on the days you're busiest, which are the days you miss the most calls.",
            "Business texting from a local number needs carrier registration (A2P 10DLC). Unregistered texts get filtered or blocked.",
            "Texting someone who just called you is different from cold texting. Never send marketing texts to people who didn't ask.",
        ],
        "sections": [
            ("How it works", [
                ("p", "Your existing number forwards through a system that rings your phones as usual. If nobody picks up, the caller gets a text from your business a few seconds after the call ends: \"Hi, this is Your Shop Heating &amp; Air. Sorry we missed you, we're on a job. What's going on with your system?\" They reply, the conversation lands in a shared inbox your office and techs can see, and someone books the call."),
                ("p", "You keep your number. Customers keep calling the number on your trucks."),
            ]),
            ("Why it matters most in July", [
                ("p", "Your phone rings most when it's hottest, and that's exactly when your techs are in attics and the office is on another line. A homeowner with a dead AC in 100-degree heat won't wait for a call back; they'll dial the next shop on the map. A text in seconds holds them long enough for you to answer."),
                ("p", "It also catches the calls you'd never know you missed: after hours, during lunch, when the line was busy."),
            ]),
            ("The registration it needs: A2P 10DLC", [
                ("p", "U.S. carriers require businesses that text customers from a regular 10-digit local number to register first. It's called A2P 10DLC (application-to-person, 10-digit long code). You register your business and describe the kinds of messages you'll send. Unregistered business texts get filtered, slowed down or blocked."),
                ("p", "Registration asks for your legal business name and tax ID, and checks that your website explains how people opt in and opt out. That's one reason your privacy policy and terms need to mention texting."),
            ]),
            ("Texas rules to know", [
                ("p", "Texas expanded its telemarketing law in 2025 (Senate Bill 140) so that it covers text messages as well as calls. The safe rule for an HVAC company is simple:"),
                ("ul", [
                    "Reply to people who contacted you. A text back to someone who just called you is a conversation they started.",
                    "Get clear consent before any marketing texts, such as tune-up reminders or promotions, and keep a record of it.",
                    "Every marketing text says how to stop: \"Reply STOP to opt out.\" Honor it right away.",
                    "Never cold text a list.",
                ]),
                ("note", "This is general information, not legal advice. Federal law (the TCPA) also applies to texts. If you plan marketing campaigns, have a lawyer look at your consent wording."),
            ]),
            ("What a good text-back setup includes", [
                ("ol", [
                    "A first text within seconds, written in your voice, that asks what's wrong.",
                    "A shared inbox, so whoever is free can answer.",
                    "A link to book, for customers who'd rather pick a time themselves.",
                    "Alerts to your phone when a customer replies.",
                    "Tracking, so you can see how many missed calls turned into booked jobs.",
                ]),
                ("cta",),
            ]),
        ],
        "faq": [
            ("Will customers find the text annoying?", "It goes only to people who just called you, once, so it reads as a quick response rather than marketing."),
            ("Do I have to change my phone number?", "No. Your existing line forwards through the system."),
            ("What about after-hours calls?", "The same text goes out, and the message can say when you'll call back or offer an emergency option."),
        ],
        "sources": [
            ("CTIA: Wireless industry messaging commitment (links the Messaging Principles and Best Practices)", "https://www.ctia.org/the-wireless-industry/industry-commitments/messaging-interoperability-sms-mms"),
            ("Texas Legislature: SB 140 (89th Legislature, 2025)", "https://capitol.texas.gov/BillLookup/History.aspx?LegSess=89R&Bill=SB140"),
        ],
        "related": ["google-reviews-hvac", "hvac-website-checklist"],
    },
    {
        "slug": "hvac-website-checklist",
        "title": "The HVAC website checklist: 20 things that decide if the phone rings",
        "short": "Website checklist",
        "desc": "A free, 20-point checklist for HVAC company websites: speed, calls, service pages, trust and tracking. No email required.",
        "read": 9,
        "takeaways": [
            "Most HVAC website visitors are on a phone and in a hurry. Speed and a tap-to-call button come first.",
            "One page per service you want more of, and one page per town you really serve.",
            "Real photos and real reviews beat stock images and claims.",
            "If you can't tell which calls came from the website, you can't tell if it's working.",
        ],
        "sections": [
            ("How to use this", [
                ("p", "Open your website on your phone, not your computer, and go down the list. Give yourself a point for each yes. Anything under 15 means the site is costing you calls. You can also skip the work: the free report card checks most of these for you and compares you with the shops near you."),
            ]),
            ("Speed and phone (1–5)", [
                ("ol", [
                    "The home page shows something useful within about 2.5 seconds on your phone's mobile data. (Google's own target for the main content of a page is 2.5 seconds; test it free at PageSpeed Insights.)",
                    "Your phone number is a tap-to-call button at the top of every page.",
                    "Nothing covers the screen when the page opens: no pop-up, no full-screen chat.",
                    "Text is readable without zooming, and buttons are easy to hit with a thumb.",
                    "The site scores in the green on Google's PageSpeed Insights for mobile.",
                ]),
            ]),
            ("Getting found (6–10)", [
                ("ol", [
                    "<b>Service pages:</b> a separate page for each service you want more of: AC repair, heating repair, installs and replacements, maintenance plans.",
                    "<b>Town pages:</b> a real page for each town you take calls in, with work and reviews from that town. Not the same page with the name swapped.",
                    "Each page's title says what it is and where: \"AC Repair in Waco, TX | Your Shop Heating &amp; Air\".",
                    "Your business name, address and phone on the site match your Google Business Profile exactly.",
                    "Your Google Business Profile links to your website, and your website links to your profile.",
                ]),
            ]),
            ("Turning visits into calls (11–15)", [
                ("ol", [
                    "The first screen says what you do, where, and how to reach you, in one short line.",
                    "There's a way to book or request service without calling, for people who'd rather not.",
                    "Forms are short: name, phone, what's wrong. Four fields or fewer.",
                    "Missed calls and form fills get an answer within minutes, including after hours.",
                    "If you offer financing, it's on the install and replacement pages, near the quote form.",
                ]),
            ]),
            ("Trust (16–18)", [
                ("ol", [
                    "Real photos of your crew, your trucks and your work. No stock photos of smiling models.",
                    "Your real Google reviews on the page, ideally from the same town and service.",
                    "Your contractor license number shown in the footer, plus any real brand certifications you hold.",
                ]),
            ]),
            ("Tracking (19–20)", [
                ("ol", [
                    "You can see how many calls and forms came from the website each month.",
                    "Someone updates the site when hours, services or prices change.",
                ]),
                ("cta",),
            ]),
        ],
        "faq": [
            ("Do I need a new website to fix these?", "Often not. Many of these are fixes to an existing site. If the site is slow and has one page, a rebuild is usually cheaper than patching."),
            ("Is WordPress bad?", "No, but it needs updates and plugins kept current, and slow themes are common. What matters is the checklist, not the platform."),
            ("Why no email gate on this checklist?", "Because it's more useful to you this way. If you want it done for you, the report card checks it against your competitors."),
        ],
        "sources": [
            ("Google: Largest Contentful Paint (web.dev)", "https://web.dev/articles/lcp"),
            ("Google PageSpeed Insights", "https://pagespeed.web.dev/"),
        ],
        "related": ["google-map-pack-hvac", "hvac-marketing-cost"],
    },
    {
        "slug": "hvac-marketing-cost",
        "title": "What HVAC marketing costs in 2026: published prices compared",
        "short": "What marketing costs",
        "desc": "Real, published prices from HVAC marketing agencies and tools, what each one includes, and the questions to ask before you sign.",
        "read": 8,
        "takeaways": [
            "Published HVAC marketing prices run from about $249 a month for a template site bundle to $5,000 a month and up for full-service agencies, before ad spend.",
            "Compare what's included, not the headline price: website build fees, ad spend, contracts and who owns the site.",
            "Read the terms. Several agencies' headline promises are qualified in the fine print.",
            "A common budgeting rule of thumb is 5 to 10 percent of revenue on all marketing, ads included.",
        ],
        "sections": [
            ("Published prices, side by side", [
                ("p", "These are prices the companies publish on their own sites, as we read them in October 2026. Prices change, so check each link before you decide."),
                ("table", [
                    ["Company", "What it is", "Published price", "Notes from their own pages"],
                    ["Footbridge Media", "Template site, SEO, Google profile, reviews", "$249/mo, $0 setup", "Month-to-month, 90-day money-back"],
                    ["Websites for HVAC", "HVAC site, text-back, reviews, SEO tiers", "$499–$2,499/mo monthly; $399–$1,999/mo annual founding rate; $1,995–$4,499 build", "Build fee non-refundable; their Terms say the site goes offline if you cancel"],
                    ["RS Gonzales", "Full-service HVAC agency, ads managed", "$2,200 / $3,500 / $5,000 a month, plus ad spend", "12-month term; $3,000/mo minimum ad spend; $4,500 website buyout if you leave early"],
                    ["Hook Agency", "SEO, ads and websites for trades", "Local SEO $2,800/mo; websites $1,000–$2,000/mo for 12 months", "Websites paid over 12 months"],
                    ["Podium", "Texting and reviews software", "From $399/mo (third-party price trackers)", "Software you run yourself; no website"],
                ]),
            ]),
            ("What moves the price", [
                ("ul", [
                    "<b>Ad spend.</b> Agencies that run Google, Meta or Local Services Ads charge a management fee on top of the money paid to the platforms.",
                    "<b>Website build fees.</b> Some charge up front, some spread it over a 12-month contract, some include it.",
                    "<b>Contract length.</b> Month-to-month costs more per month; 12-month terms often come with buyouts if you leave.",
                    "<b>How much is done for you.</b> Software you run yourself is cheap. Done-for-you work costs more because someone does it.",
                ]),
            ]),
            ("Five questions to ask before you sign", [
                ("ol", [
                    "<b>If I cancel, what happens to my website?</b> Get it in writing. \"You own your website\" sometimes means \"after 12 months\" or \"after a buyout\".",
                    "<b>Who owns my Google Business Profile and my phone number?</b> They should be in your name.",
                    "<b>What's the total monthly cost, including ad spend and fees?</b> \"0% markup\" can sit next to fees above a spending cap.",
                    "<b>What do you guarantee, and what happens if you miss it?</b> Guarantees on rankings are a red flag. Guarantees on response times and launch dates are reasonable.",
                    "<b>How will I see results?</b> A monthly PDF is not the same as a dashboard of calls and booked jobs.",
                ]),
            ]),
            ("How we price", [
                ("p", "Our plans and prices are on our <a href=\"{u:plans}\">pricing page</a>, monthly or annual, with the build fee shown. You own your domain, website content, Google profile and reviews, and every plan includes missed-call text-back and review requests. If you're not happy in the first 30 days after launch, you get your first month back."),
                ("cta",),
            ]),
        ],
        "faq": [
            ("How much should an HVAC company spend on marketing?", "A common rule of thumb is 5 to 10 percent of revenue, ads included. A shop growing fast or entering a new market often spends more."),
            ("Is a $249 website enough?", "It can be, for a basic presence. Check what happens to the site if you leave, how many pages you get and who answers the leads."),
            ("Are long contracts bad?", "Not always, but know the exit terms before you sign: buyouts, notice periods and what you keep."),
        ],
        "sources": [
            ("Footbridge Media pricing", "https://www.footbridgemedia.com/"),
            ("Websites for HVAC pricing", "https://websitesforhvac.com/pricing"),
            ("RS Gonzales pricing", "https://rsgonzales.com/pricing/"),
            ("Hook Agency pricing", "https://hookagency.com/pricing/"),
        ],
        "related": ["hvac-website-checklist", "missed-call-text-back-hvac"],
    },
    {
        "slug": "scorpion-alternative-hvac",
        "title": "Scorpion alternatives for HVAC companies: what to compare before you sign",
        "short": "Scorpion alternatives",
        "desc": "What Scorpion's own FAQ says about contracts, website ownership and leaving, what its reviews complain about, and the questions to ask any HVAC marketing agency.",
        "read": 7,
        "takeaways": [
            "Scorpion's FAQ says its marketing technology (website and SEO) typically needs a 12-month contract; ads are typically month to month.",
            "If you leave, Scorpion says you keep your domain, content and images and get your site's static files, but you'll need another vendor to rebuild the site, because the CMS is theirs.",
            "Scorpion doesn't publish prices on its FAQ; it says the investment depends on your goals.",
            "Whoever you pick, get the exit terms, ownership and total monthly cost in writing before you sign.",
        ],
        "sections": [
            ("Who Scorpion is a good fit for", [
                ("p", "Scorpion is one of the biggest marketing companies for home services. It builds websites on its own platform, runs SEO and ads, and sells software around them. Its Trustpilot reviews mostly praise specific account managers. For a large, multi-location company with a big ad budget and someone in-house to manage the relationship, that scale can make sense."),
                ("p", "Most owner-run HVAC shops are in a different spot: a few trucks, the owner answering the phone, and no appetite for a year-long contract before they know it works. That's who this guide is for."),
            ]),
            ("What Scorpion's own FAQ says", [
                ("p", "These points are from Scorpion's FAQ page as we read it on October 12, 2026. Check the link before you decide, since terms change."),
                ("table", [
                    ["Question", "Scorpion's answer"],
                    ["Contract length", "Typically 12 months for marketing technology (website, SEO). Digital ads like Google Ads, LSAs and Meta are typically month to month."],
                    ["Do I own my website?", "Yes, after the contract is complete. You don't own the underlying CMS; your domains, content and imagery stay yours."],
                    ["What happens if I leave?", "You get the site's static files, design assets and content, and key accounts like analytics are transferred. You'll need another vendor to rebuild the site on a CMS of your choice."],
                    ["Price", "Not published. \"The investment you decide to make with Scorpion depends on your business goals.\""],
                ]),
            ]),
            ("What reviewers complain about", [
                ("p", "On October 12, 2026, Scorpion had a 4.0 TrustScore on Trustpilot from 35 reviews: 71% five-star and 26% one-star. The critical reviews repeat a few themes:"),
                ("ul", [
                    "Long contracts and charges they didn't expect.",
                    "Leads that weren't for their business, and credits that were slow to arrive.",
                    "Slow offboarding, including one former client whose site showed a default server page after the contract ended.",
                ]),
                ("note", "35 reviews is a small sample for a company this size, and each review is one side of the story. Use them as questions to ask, not as a verdict."),
            ]),
            ("What to compare in any alternative", [
                ("ol", [
                    "<b>Exit terms.</b> If you cancel in month four, what do you walk away with: a working website, or files you have to rebuild?",
                    "<b>Ownership.</b> Your domain, Google Business Profile, reviews and phone number should be in your name from day one.",
                    "<b>Total monthly cost.</b> Plan price, build fee, ad management fees and ad spend, added up.",
                    "<b>Response time.</b> How fast is a missed call answered? That's often worth more than any ranking.",
                    "<b>Reporting.</b> Can you see calls and booked jobs whenever you want, or only in a monthly PDF?",
                ]),
            ]),
            ("How we compare", [
                ("p", "We built HVAC Marketing HQ for owner-run shops: a fast website you own, a Google profile we actually run, missed-call text-back and review requests, and the HQ Command Center dashboard so you can check the numbers yourself. Our prices and plan details are on the <a href=\"{u:plans}\">pricing page</a>. We don't run ad campaigns today, so if paid ads are most of what you need, a larger agency may suit you better."),
                ("cta",),
            ]),
        ],
        "faq": [
            ("Is Scorpion good for HVAC companies?", "It can be, especially for larger multi-location companies with big ad budgets. Read the contract, exit and ownership terms first, and compare the total monthly cost with other options."),
            ("Do you own your website with Scorpion?", "Scorpion's FAQ says you own your website after the contract is complete, but not the CMS it runs on. If you leave, you get static files and content and need another vendor to rebuild."),
            ("How much does Scorpion cost?", "Scorpion doesn't publish prices on its FAQ; it says the investment depends on your business goals. Ask for the full monthly cost, including ad spend and fees, in writing."),
            ("What should a small HVAC shop look for in an alternative?", "Published prices, a short commitment, a site you own outright and a fast response to missed calls. Our guide to what HVAC marketing costs compares published prices across companies."),
        ],
        "sources": [
            ("Scorpion FAQ", "https://www.scorpion.co/faq/"),
            ("Scorpion reviews on Trustpilot", "https://www.trustpilot.com/review/scorpion.co"),
        ],
        "related": ["hvac-marketing-cost", "hvac-website-checklist"],
    },
]
