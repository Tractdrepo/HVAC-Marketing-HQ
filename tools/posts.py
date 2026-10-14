# Posts: short blog posts (600 to 1,000 words), each aimed at one search an HVAC owner makes.
# Same format as GUIDES in guides.py, so the same renderer can show them.
# Rules: every number or claim about Google, Meta or the industry comes from a page in "sources"
# (fetched Oct 2026). No invented stats, no client results, no testimonials. Plain words. No em-dashes.
# Body blocks: ("p", text) · ("ul", [items]) · ("ol", [items]) · ("table", [header, *rows]) · ("note", text) · ("cta",)
# Body text may contain simple inline HTML (<b>, <a>) and {u:key} links. Takeaways, headings and FAQ are plain text (escaped).

UPDATED = "Oct 14, 2026"
AUTHOR = "Logan, founder of HVAC Marketing HQ"
DATE = "2026-10-14"

POSTS = [
    # ------------------------------------------------------------------ 1. Google Ads budget
    {
        "slug": "how-much-to-spend-on-google-ads-hvac",
        "title": "How much should an HVAC company spend on Google Ads?",
        "short": "Google Ads budget",
        "desc": "There's no right number from a chart. Here's how to work out a Google Ads budget from the jobs you want, what a click costs in your town and how Google actually spends a daily budget.",
        "read": 5,
        "date": DATE,
        "takeaways": [
            "Start from the number of booked jobs you want, then work backward to clicks and cost.",
            "Use Google's own Keyword Planner to see what clicks cost in your service area, not a national average.",
            "Google can spend up to 2 times your daily budget on a busy day, but no more than 30.4 times it in a month.",
            "Track phone calls as conversions, or you can't tell which dollars booked jobs.",
        ],
        "sections": [
            ("Why there's no single right number", [
                ("p", "You'll see posts that say an HVAC company should spend a set amount, or a set share of revenue, on Google Ads. We don't publish a number like that, because the right budget depends on things that change from town to town: what a click costs in your area, how many of those clicks call, and how many calls you book."),
                ("p", "What a click costs isn't fixed. Google Ads runs an auction for each search. Google says your position depends on your bid, the quality of your ad and landing page, the search context (terms, location, device, time) and how competitive the auction is. It also says higher quality ads can often lead to lower costs per click. So two shops in the same town can pay different amounts for the same search."),
            ]),
            ("Work it out backward from jobs", [
                ("p", "The simplest way to set a budget is to start with the result you want and work back. You need four numbers, all your own:"),
                ("ol", [
                    "<b>Jobs you want from ads each month.</b> Be honest about how many your crew can take on.",
                    "<b>Your booking rate.</b> Out of every 10 calls, how many turn into a booked job? Your call log or your CSR can tell you.",
                    "<b>Your call rate from clicks.</b> Out of every 100 ad clicks, how many call or fill out a form? You'll only know this once tracking is set up.",
                    "<b>Your cost per click.</b> Get a starting estimate from Keyword Planner for your own keywords and towns.",
                ]),
                ("p", "Then the math is: jobs wanted, divided by booking rate, gives calls needed. Calls needed, divided by call rate, gives clicks needed. Clicks needed, times cost per click, gives your monthly budget."),
                ("table", [
                    ["Step", "Example (made-up numbers to show the math)"],
                    ["Jobs wanted per month", "20"],
                    ["Booking rate", "50% of calls book, so 40 calls needed"],
                    ["Call rate from clicks", "10% of clicks call, so 400 clicks needed"],
                    ["Cost per click", "$X from Keyword Planner, so budget = 400 times $X"],
                ]),
                ("note", "The numbers above are an example of the method, not a benchmark. Use your own. If you don't know your call rate yet, start smaller and measure for a month."),
            ]),
            ("Use Google's own tools for your town", [
                ("p", "Keyword Planner, inside Google Ads, gives a forecast of the clicks, conversions and impressions you're likely to get for a budget. Google says the forecasts are refreshed daily, based on the last 7 to 10 days and adjusted for seasonality. You can change the average daily budget and watch the forecast move."),
                ("p", "Set the plan to your real service area. Google lets you target by city, by postal code or by a radius around a location. It also warns that a very small radius or area can mean your ads show only now and then, or not at all."),
            ]),
            ("How Google spends a daily budget", [
                ("p", "This trips up a lot of owners. In Google Ads you set an <b>average</b> daily budget. Google says on some days you won't reach it and on others you'll go over. For most campaigns, Google won't charge more than <b>2 times</b> your average daily budget on any one day, and no more than <b>30.4 times</b> it in a month (30.4 is the average number of days in a month)."),
                ("p", "So if you want to spend about $3,040 a month, the daily budget is about $100. A hot Tuesday in July might spend $180. A mild Sunday might spend $40. Over the month it evens out, and the cap protects you."),
            ]),
            ("Stop paying for clicks that can't book", [
                ("ul", [
                    "<b>Add negative keywords.</b> Google describes negative keywords as search terms you exclude. For HVAC that often means \"jobs\", \"salary\", \"school\", \"parts\" and \"DIY\". Google also warns that too many negatives can shrink your reach.",
                    "<b>Track calls as conversions.</b> Google Ads can count calls from your ads and calls to a forwarding number on your website, with a minimum call length you choose. Without this, you only see clicks.",
                    "<b>Answer the phone.</b> A click that rings out is money spent for nothing. <a href=\"{u:missed-call-text-back}\">Missed-call text-back</a> catches the ones you can't pick up.",
                    "<b>Plan for the season.</b> The BLS notes HVAC techs often work overtime in peak heating and cooling seasons. Many shops raise budgets when the phones already ring and lower them in the shoulder months.",
                ]),
                ("p", "Want help setting it up? See how we handle <a href=\"{u:google-ads}\">Google Ads for HVAC</a>, or compare it with <a href=\"{u:local-services-ads}\">Local Services Ads</a>."),
                ("cta",),
            ]),
        ],
        "faq": [
            ("How small a budget can I start with?", "Enough to get a useful number of clicks each month, so you can learn your call rate and booking rate. Use Keyword Planner to see what that costs in your area."),
            ("Why did Google spend more than my daily budget?", "Google treats the daily budget as an average. For most campaigns it can spend up to 2 times that on one day, but not more than 30.4 times it in a month."),
            ("Should I spend the same every month?", "Not always. Many shops spend more in peak heating and cooling months, when more homeowners search, and less in mild months."),
        ],
        "sources": [
            ("Google Ads Help: About average daily budgets", "https://support.google.com/google-ads/answer/6385083"),
            ("Google Ads Help: About Ad Rank", "https://support.google.com/google-ads/answer/1722122"),
            ("Google Ads Help: Actual cost-per-click", "https://support.google.com/google-ads/answer/6297"),
            ("Google Ads Help: Using Keyword Planner", "https://support.google.com/google-ads/answer/7337243"),
            ("Google Ads Help: Location targeting", "https://support.google.com/google-ads/answer/1722043"),
            ("Google Ads Help: About negative keywords", "https://support.google.com/google-ads/answer/2453972"),
            ("Google Ads Help: Phone call conversion tracking", "https://support.google.com/google-ads/answer/6100664"),
            ("U.S. Bureau of Labor Statistics: HVAC mechanics and installers", "https://www.bls.gov/ooh/installation-maintenance-and-repair/heating-air-conditioning-and-refrigeration-mechanics-and-installers.htm"),
        ],
        "related": ["google-ads-vs-local-services-ads-hvac", "hvac-marketing-cost"],
    },
    # ------------------------------------------------------------------ 2. Local Services Ads
    {
        "slug": "google-local-services-ads-hvac",
        "title": "Google Local Services Ads for HVAC: how they work and how leads are charged",
        "short": "Local Services Ads",
        "desc": "What Local Services Ads are, what counts as a charged lead, what Google says affects your ranking, and how credits work when a lead isn't real.",
        "read": 5,
        "date": DATE,
        "takeaways": [
            "Local Services Ads charge per lead (a call, message or booking), not per click.",
            "Google says missed calls and slow replies can hurt your ranking.",
            "Reviews, response time, photos and completed verification all count toward your profile quality.",
            "Invalid or low-quality leads aren't charged, and Google may credit them back later.",
        ],
        "sections": [
            ("What Local Services Ads are", [
                ("p", "Local Services Ads are the listings with the Google Verified badge that show at the top of Google for searches like \"furnace repair near me\". Google calls them pay-per-lead listings for verified local service providers. A homeowner sees your name, rating and hours, and can call, message or book from the ad."),
                ("p", "To get the badge, your business goes through Google's verification checks. Google says it will place a listing below providers who've finished all onboarding requirements until you're done."),
            ]),
            ("How you're charged", [
                ("p", "With regular Google Ads you pay for clicks. With Local Services Ads you pay for leads. Google says you're charged for each valid lead you get through the ad, and your monthly budget caps what you spend."),
                ("p", "Here's what Google says counts:"),
                ("table", [
                    ["Lead type", "When it's charged"],
                    ["Phone call", "When you answer, or reach the customer. For a missed call, the customer has to stay on the line more than 20 seconds."],
                    ["Message", "When you get a text or email from the customer. Google says message leads are usually priced lower than calls, though not always."],
                    ["Booking", "Booking requests are charged in the US and Canada only, where bookings are offered."],
                    ["Repeat contact", "Follow-up calls or messages from the same customer within 15 days aren't charged again."],
                ]),
                ("p", "Google says lead prices vary by location, job type, lead type and bidding mode. That's why we don't quote a typical cost per lead. Your account shows what you're actually paying."),
            ]),
            ("What Google says affects your ranking", [
                ("p", "Google lists the factors in its Local Services help pages:"),
                ("ul", [
                    "<b>Your bid.</b> The most you're willing to pay for a lead. You may pay less.",
                    "<b>How likely you are to get the lead.</b> This includes how fast you respond, the service and location searched, the services in your profile, and whether you accept messages and bookings.",
                    "<b>Profile quality.</b> Ratings, review count, average response time, good photos and completed verification.",
                    "<b>A healthy mix of providers.</b> Google says it also tries to give all providers a fair chance.",
                ]),
                ("p", "Google is blunt about one thing: if you regularly fail to answer calls or reply to messages, your ad ranking may be affected. For an HVAC shop on a roof all afternoon, that's the real risk. <a href=\"{u:missed-call-text-back}\">Missed-call text-back</a> and fast replies protect it."),
                ("p", "Google also recommends its Maximize Leads bid mode, where it sets your bid to get the most leads within your budget."),
            ]),
            ("When a lead isn't a real lead", [
                ("p", "Not every call is a job. Some are wrong numbers, sales pitches or jobs you don't do. Google says leads it finds invalid or low quality aren't charged. It also says charged leads are reassessed over time and may be credited automatically if later found to be low quality, and that in most cases credits land within 30 days."),
                ("p", "You can also rate each lead in your account and dispute one you think isn't valid. A successful dispute is credited back in the US and Canada. Make it a habit: whoever handles leads checks them every week."),
            ]),
            ("Getting more out of it", [
                ("ol", [
                    "List only the services and areas you actually want. A lead for a job you won't take still costs money.",
                    "Turn on messages and bookings if your team can answer them fast.",
                    "Keep asking for reviews. Rating and review count are part of profile quality. See <a href=\"{u:review-requests}\">review requests</a>.",
                    "Check leads weekly, rate them and dispute the bad ones.",
                ]),
                ("p", "Want someone to run it? See our <a href=\"{u:local-services-ads}\">Local Services Ads management</a>."),
                ("cta",),
            ]),
        ],
        "faq": [
            ("Do I pay for clicks on Local Services Ads?", "No. Google charges for valid leads, such as calls, messages and bookings, not for clicks or views."),
            ("Am I charged for missed calls?", "Google says a missed call can be charged if the customer stays on the line more than 20 seconds. That's why answering fast matters."),
            ("Do Local Services Ads help my map ranking?", "No. They show separately, at the top of the page. Google says you can't pay for a better local ranking."),
        ],
        "sources": [
            ("Google: Local Services Ads overview", "https://business.google.com/us/ad-solutions/local-service-ads/"),
            ("Google Local Services Help: How Local Services Ads work", "https://support.google.com/localservices/answer/6224841"),
            ("Google Local Services Help: How you're charged for leads", "https://support.google.com/adwords/answer/7195435"),
            ("Google Local Services Help: About ad rankings", "https://support.google.com/localservices/answer/7527305"),
            ("Google Local Services Help: Lead credits and feedback", "https://support.google.com/google-ads/answer/7435486"),
            ("Google Local Services Help: Disputing leads", "https://support.google.com/localservices/answer/11444536"),
            ("Google Business Profile Help: Tips to improve your local ranking", "https://support.google.com/business/answer/7091"),
        ],
        "related": ["google-ads-vs-local-services-ads-hvac", "google-map-pack-hvac"],
    },
    # ------------------------------------------------------------------ 3. Google Ads vs LSA
    {
        "slug": "google-ads-vs-local-services-ads-hvac",
        "title": "Google Ads vs Local Services Ads for HVAC companies",
        "short": "Google Ads vs LSA",
        "desc": "Pay per click or pay per lead? How Google Ads and Local Services Ads differ in cost, control and ranking, and when an HVAC company should run one, the other or both.",
        "read": 5,
        "date": DATE,
        "takeaways": [
            "Google Ads charge per click. Local Services Ads charge per lead.",
            "Google Ads give you more control: keywords, negatives, ad text and landing pages.",
            "Local Services Ads lean on your reviews, response time and verification.",
            "Many shops run both, as long as they can track which one booked the jobs.",
        ],
        "sections": [
            ("The short version", [
                ("p", "Both show at the top of Google. Both can bring in calls. The big difference is what you pay for and how much you control. Google Ads (search ads) charge when someone clicks. Local Services Ads charge when someone calls, messages or books."),
            ]),
            ("Side by side", [
                ("table", [
                    ["", "Google Ads (search)", "Local Services Ads"],
                    ["You pay for", "Clicks. Your actual cost per click is usually below your max bid.", "Valid leads: calls, messages and bookings."],
                    ["Badge", "None", "Google Verified, after verification checks"],
                    ["What decides position", "Bid, ad and landing page quality, search context, auction competition and ad assets", "Bid, how likely you are to get the lead, responsiveness, profile quality (ratings, reviews, photos, verification)"],
                    ["Where the click goes", "Your website or a call", "Your Local Services profile, a call, message or booking"],
                    ["Control", "Keywords, negative keywords, ad text, landing pages, locations, schedules", "Services, service areas, budget, bid mode"],
                    ["Bad traffic", "You pay for the click, so negatives and tracking matter", "Invalid or low-quality leads aren't charged and may be credited"],
                    ["Budget", "Average daily budget, up to 2 times on one day, 30.4 times per month cap", "Weekly or monthly budget you can change any time"],
                ]),
            ]),
            ("When Google Ads makes more sense", [
                ("ul", [
                    "<b>You want to push one service.</b> Google Ads lets you bid on exact searches, like heat pump installation, and send them to a page about that one service.",
                    "<b>You have a strong website.</b> Google says landing page quality is part of Ad Rank. A fast page that matches the search can lower your costs.",
                    "<b>You want to control the message.</b> You write the ad, pick the offer and choose the hours your ads run.",
                ]),
                ("p", "The catch is that you pay for every click, including ones that don't call. That makes negative keywords and call tracking a must. See <a href=\"{u:google-ads}\">how we run Google Ads for HVAC</a>."),
            ]),
            ("When Local Services Ads make more sense", [
                ("ul", [
                    "<b>You have good reviews.</b> Google says ratings and review count are part of profile quality.",
                    "<b>You answer fast.</b> Google says regularly missing calls or messages may hurt your ranking.",
                    "<b>You don't want to manage keywords.</b> You pick services and areas, and Google matches searches to them.",
                ]),
                ("p", "The catch is less control. You can't write ad text or choose keywords, and the price of a lead varies by location, job type, lead type and bid mode."),
            ]),
            ("Running both", [
                ("p", "Plenty of shops run both. That's fine, with two rules. First, track every call so you know which one booked the job. Google Ads can count calls from ads and calls to a forwarding number on your site; Local Services Ads show leads in your account. Second, look at cost per booked job, not cost per click or cost per lead. A cheap lead that never books is not cheap."),
                ("p", "Neither one moves your spot in the map pack. Google says you can't pay for a better local ranking. That work happens on your <a href=\"{u:google-business-profile}\">Google Business Profile</a> and <a href=\"{u:local-seo}\">local SEO</a>."),
                ("p", "We manage both: see <a href=\"{u:google-ads}\">Google Ads</a> and <a href=\"{u:local-services-ads}\">Local Services Ads</a>."),
                ("cta",),
            ]),
        ],
        "faq": [
            ("Which is cheaper, Google Ads or Local Services Ads?", "It depends on your town, your services and how well you answer and book. Compare cost per booked job, from your own tracking, after a month or two."),
            ("Can I run both at the same time?", "Yes. Track calls from each so you know which one is booking jobs."),
            ("Do I need a website for Local Services Ads?", "The ad sends people to your Local Services profile, a call or a message. A good website still helps homeowners who look you up before they call."),
        ],
        "sources": [
            ("Google Ads Help: About Ad Rank", "https://support.google.com/google-ads/answer/1722122"),
            ("Google Ads Help: Actual cost-per-click", "https://support.google.com/google-ads/answer/6297"),
            ("Google Ads Help: About average daily budgets", "https://support.google.com/google-ads/answer/6385083"),
            ("Google Ads Help: Phone call conversion tracking", "https://support.google.com/google-ads/answer/6100664"),
            ("Google: Local Services Ads overview", "https://business.google.com/us/ad-solutions/local-service-ads/"),
            ("Google Local Services Help: How you're charged for leads", "https://support.google.com/adwords/answer/7195435"),
            ("Google Local Services Help: About ad rankings", "https://support.google.com/localservices/answer/7527305"),
            ("Google Business Profile Help: Tips to improve your local ranking", "https://support.google.com/business/answer/7091"),
        ],
        "related": ["how-much-to-spend-on-google-ads-hvac", "google-local-services-ads-hvac"],
    },
    # ------------------------------------------------------------------ 4. HVAC SEO
    {
        "slug": "hvac-seo-what-moves-rankings",
        "title": "HVAC SEO: what actually moves rankings in the map and organic results",
        "short": "HVAC SEO",
        "desc": "The map pack and the regular results rank differently. What Google says matters for each, what an HVAC company can change this month, and what to stop paying for.",
        "read": 6,
        "date": DATE,
        "takeaways": [
            "The map pack runs on relevance, distance and prominence. You can't change distance.",
            "Your Google profile's category, services and reviews do most of the map work.",
            "Organic results run on helpful pages, clear titles and links from other sites.",
            "Nobody can guarantee a #1 ranking. Google says so itself.",
        ],
        "sections": [
            ("Two kinds of results, two sets of rules", [
                ("p", "When a homeowner searches \"AC repair\" plus your town, Google usually shows ads, then a map with three businesses, then the regular website results. The map comes from your <a href=\"{u:google-business-profile}\">Google Business Profile</a>. The regular results come from your website. They overlap, but they aren't the same thing, so they need different work."),
            ]),
            ("The map: relevance, distance, prominence", [
                ("p", "Google says local results are based mainly on three things. <b>Relevance</b> is how well your profile matches the search. <b>Distance</b> is how far you are from the searcher. <b>Prominence</b> is how well known you are, including how many sites link to you and how many reviews you have. Google says more reviews and positive ratings can help your local ranking."),
                ("p", "What moves the map, in plain terms:"),
                ("ol", [
                    "<b>The right primary category.</b> Google says to pick the fewest categories that describe your core business, and to focus on the most specific ones.",
                    "<b>A real business name.</b> Google says your name should match your real-world name, and extra words in it can get your profile suspended.",
                    "<b>A service area, done right.</b> Google says service-area businesses should hide their address, keep one profile for the central office, and set a service area that generally stays within about 2 hours of driving.",
                    "<b>Steady reviews and replies.</b> See <a href=\"{u:guide-google-reviews-hvac}\">how many Google reviews an HVAC company needs</a>.",
                    "<b>Complete, current details.</b> Google says complete and detailed information helps it match you to searches.",
                ]),
                ("p", "One thing doesn't move the map: money. Google says there's no way to request or pay for a better local ranking."),
            ]),
            ("Organic results: pages people find useful", [
                ("p", "Google's SEO Starter Guide says to make content helpful, reliable and people-first. For an HVAC site that means one clear page per service you want more of (AC repair, furnace repair, heat pumps, maintenance plans) that answers what a homeowner wants to know: do you serve my area, how fast can you come, what does it cost to start, and how do I book."),
                ("ul", [
                    "<b>Clear title links.</b> Google says the title link helps people decide which result to click. \"AC Repair in Waco | Your Company\" beats \"Home\".",
                    "<b>Readable URLs.</b> Google suggests words in the URL that help users, like /ac-repair.",
                    "<b>Links from other sites.</b> Google says it mainly finds pages through links from pages it already knows. Local suppliers, sponsorships and associations are good places to earn them.",
                    "<b>A fast, mobile-friendly site.</b> Google says Core Web Vitals are used by its ranking systems, but that good scores don't guarantee a top spot and that it still shows the most relevant content first.",
                ]),
            ]),
            ("What to stop paying for", [
                ("ul", [
                    "<b>Bought links.</b> Google's spam policies list buying or selling links for ranking as link spam.",
                    "<b>Copy-paste city pages.</b> Google calls pages aimed at cities that all funnel to one page doorway abuse, and mass-made pages with little value scaled content abuse. A town page should have real work, real reviews and real details from that town.",
                    "<b>Meta keywords.</b> Google says it doesn't use the keywords meta tag.",
                    "<b>Ranking guarantees.</b> Google says no one can guarantee a #1 ranking, and that if an SEO promises one, you should look elsewhere.",
                    "<b>Fake addresses.</b> Google says P.O. boxes, remote mailboxes and virtual offices aren't eligible.",
                ]),
            ]),
            ("How long it takes", [
                ("p", "Google says some changes take effect in a few hours and others can take several months, and suggests waiting a few weeks before judging a change. Profile fixes are the quickest to make. New pages and links take longer to build."),
                ("p", "Start with the free report card to see where you stand today, then see our <a href=\"{u:local-seo}\">local SEO</a> plans."),
                ("cta",),
            ]),
        ],
        "faq": [
            ("Is the map pack the same as SEO?", "They're related but different. The map comes from your Google Business Profile. The regular results come from your website. Good local SEO works on both."),
            ("Can I rank in a town where I don't have an office?", "In the regular results, yes, with a real page about your work there. In the map, distance matters, and Google doesn't allow fake addresses to get around it."),
            ("Does running Google Ads help my SEO?", "No. Google says you can't pay for a better local ranking. Ads show separately."),
        ],
        "sources": [
            ("Google Business Profile Help: Tips to improve your local ranking", "https://support.google.com/business/answer/7091"),
            ("Google: Guidelines for representing your business on Google", "https://support.google.com/business/answer/3038177"),
            ("Google Search Central: SEO Starter Guide", "https://developers.google.com/search/docs/fundamentals/seo-starter-guide"),
            ("Google Search Central: Do you need an SEO?", "https://developers.google.com/search/docs/fundamentals/do-i-need-seo"),
            ("Google Search Central: Spam policies", "https://developers.google.com/search/docs/essentials/spam-policies"),
            ("Google Search Central: Page experience", "https://developers.google.com/search/docs/appearance/page-experience"),
        ],
        "related": ["google-map-pack-hvac", "hvac-website-checklist"],
    },
    # ------------------------------------------------------------------ 5. Reviews
    {
        "slug": "get-more-google-reviews-hvac",
        "title": "How to get more HVAC reviews on Google (within Google's rules)",
        "short": "Getting more reviews",
        "desc": "A simple system for asking every customer for a Google review, what Google and the FTC don't allow, and how to reply so the next homeowner calls you.",
        "read": 5,
        "date": DATE,
        "takeaways": [
            "Ask every customer, the same way, right after the job. A link or QR code makes it easy.",
            "No discounts, gift cards or entries for reviews. Google prohibits it.",
            "Don't filter out unhappy customers. Google bans selectively asking for positive reviews.",
            "Reply to every review in your own words.",
        ],
        "sections": [
            ("Why reviews matter for an HVAC shop", [
                ("p", "Google says more reviews and positive ratings can help your business's local ranking. Reviews also show up right next to your name in the map, so a homeowner with a dead furnace sees them before they call. More reviews, coming in steadily, help on both fronts."),
            ]),
            ("The system: ask everyone, every time", [
                ("p", "Most shops don't have a review problem. They have an asking problem. Techs forget, the office is busy, and the request goes out in a burst once a quarter. A system fixes that:"),
                ("ol", [
                    "<b>Get your review link.</b> Google says you can ask customers to visit a Google link or scan a QR code to leave a review. Put the QR code on invoices, leave-behind cards and the truck.",
                    "<b>Send it the same day.</b> Ask while the visit is fresh, by text right after the job is closed. That's what <a href=\"{u:review-requests}\">review requests</a> automate.",
                    "<b>Ask everyone.</b> Every finished job gets the same request, whether the tech thinks it went great or not.",
                    "<b>Keep it simple.</b> One short message, one link. Customers need to be signed into a Google account to leave a review, so don't bury the link.",
                    "<b>Follow up once.</b> One reminder is fine. Pestering isn't.",
                ]),
            ]),
            ("What Google doesn't allow", [
                ("p", "Google's review policies are strict, and breaking them can get reviews removed. Here's what's out:"),
                ("ul", [
                    "<b>Incentives.</b> Google prohibits offering free or discounted goods or services in exchange for posting a review, or for changing or removing a negative one. No \"$25 off your next tune-up for a 5-star review\".",
                    "<b>Review gating.</b> Google says businesses may not discourage negative reviews or selectively ask happy customers for reviews. That means no \"rate us 1 to 5 first, and only 4s and 5s get the Google link\" funnel.",
                    "<b>Paid or fake reviews.</b> Google removes reviews that are paid for, directly or in kind, or posted from many accounts by one person.",
                    "<b>Pressure on site.</b> Google says not to require or pressure customers to leave a review while you're at their home.",
                    "<b>Review quotas for staff.</b> Google lists asking staff to get a certain number of reviews as not allowed.",
                    "<b>Scripted content.</b> Don't ask customers to include specific words.",
                ]),
                ("p", "It isn't only Google. The FTC's 2024 rule bans buying or selling fake reviews, offering incentives tied to a positive or negative review, and using threats or intimidation to stop or remove a negative review."),
            ]),
            ("Reply to every review", [
                ("p", "Google says replies are public and help you build relationships with customers, and advises against sending the same generic thank-you to everyone. Name the job if it's not private, thank them, and keep it short."),
                ("p", "For a bad review, reply calmly, once. Say what you'll do to make it right and give a way to reach you. The next homeowner reads your reply more closely than the complaint."),
            ]),
            ("How many is enough?", [
                ("p", "Google doesn't publish a target. Compare yourself with the three shops in the map for your main service and town. See <a href=\"{u:guide-google-reviews-hvac}\">how many Google reviews an HVAC company needs</a> for more on that."),
                ("cta",),
            ]),
        ],
        "faq": [
            ("Can I give a discount for leaving a review?", "No. Google prohibits offering free or discounted goods or services in exchange for reviews, and the FTC rule bans incentives tied to a review's sentiment."),
            ("Can I only send the review link to happy customers?", "No. Google says businesses may not selectively ask for positive reviews. Ask every customer the same way."),
            ("Can I ask a customer to delete a bad review?", "You can't offer anything in exchange for removing it, and you can't threaten them. Reply publicly, try to fix the problem, and let the customer decide."),
        ],
        "sources": [
            ("Google Business Profile Help: Read and reply to reviews", "https://support.google.com/business/answer/3474122"),
            ("Google Business Profile Help: Tips to get more reviews", "https://support.google.com/business/answer/7035772"),
            ("Google Maps user contributed content policy: Fake engagement", "https://support.google.com/contributionpolicy/answer/7400114"),
            ("Google Business Profile Help: Tips to improve your local ranking", "https://support.google.com/business/answer/7091"),
            ("FTC: Final rule banning fake reviews and testimonials (Aug 2024)", "https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials"),
        ],
        "related": ["google-reviews-hvac", "google-map-pack-hvac"],
    },
    # ------------------------------------------------------------------ 6. Website design
    {
        "slug": "hvac-website-design",
        "title": "HVAC website design: what a contractor site needs to book calls",
        "short": "HVAC website design",
        "desc": "A good HVAC website isn't about looks. It's about a homeowner on a phone finding your number, trusting you and calling in under a minute. Here's what that takes.",
        "read": 5,
        "date": DATE,
        "takeaways": [
            "Design for a phone first. Your number and a call button should be on every screen.",
            "One page per service and real town pages beat one long homepage.",
            "Speed matters. Google's good mark for load time (LCP) is 2.5 seconds or less.",
            "Track calls from the site, or you can't tell what it books.",
        ],
        "sections": [
            ("Who you're designing for", [
                ("p", "Picture the customer: it's hot, the AC quit, and they're on a phone looking at three shops. They want to know three things fast. Do you do this? Do you come to my area? How do I reach you right now? A site that answers those in a few seconds books calls. A site that makes them hunt loses them to the next tab."),
            ]),
            ("What every HVAC site needs", [
                ("ol", [
                    "<b>A tap-to-call number at the top of every page.</b> On a phone it should stay in view as they scroll.",
                    "<b>A clear headline.</b> What you do and where: \"AC and furnace repair in Waco and nearby towns.\" Not a slogan.",
                    "<b>One page per main service.</b> AC repair, furnace repair, heat pumps, installs, maintenance plans. Google's SEO guide calls for helpful, people-first content, and a page about one thing matches a search for that thing.",
                    "<b>Real town pages.</b> One page for each town you take calls in, with real jobs, photos and reviews from there. Google's spam policies call near-copy city pages that funnel to one page doorway abuse, so make each one real.",
                    "<b>Proof.</b> Your real Google rating and reviews, photos of your crew and trucks, license numbers and years in business.",
                    "<b>A short form.</b> Name, phone, what's wrong. Not 12 fields. Some people would rather type than call.",
                    "<b>Hours and emergency service, stated plainly.</b> If you take after-hours calls, say so at the top.",
                ]),
                ("p", "For a full checklist, see the <a href=\"{u:guide-hvac-website-checklist}\">HVAC website checklist</a>."),
            ]),
            ("Fast and mobile-friendly", [
                ("p", "Google says Core Web Vitals are used by its ranking systems. It gives three marks for a good experience:"),
                ("table", [
                    ["Measure", "What it means", "Google's good mark"],
                    ["Largest Contentful Paint (LCP)", "How fast the main content shows up", "2.5 seconds or less"],
                    ["Interaction to Next Paint (INP)", "How fast the page reacts when someone taps", "Under 200 milliseconds"],
                    ["Cumulative Layout Shift (CLS)", "How much the page jumps around while loading", "Under 0.1"],
                ]),
                ("p", "Google also says good scores don't guarantee a top ranking, and it still shows the most relevant content first. So speed doesn't replace good pages. It keeps a homeowner from leaving before they see them. Big hero videos, sliders and chat pop-ups that cover the call button are the usual culprits."),
                ("p", "Google also asks two simple questions in its page experience guide: does your content display well on mobile, and are your pages served securely (HTTPS)? Both should be a yes."),
            ]),
            ("If you run ads, the site matters even more", [
                ("p", "Google Ads gives each keyword a Quality Score from 1 to 10, and landing page experience is one of its three parts: how relevant and useful your page is to the people who click your ad. Google's Ad Rank also weighs landing page quality. A matching service page can make the same click cost less. See <a href=\"{u:google-ads}\">Google Ads for HVAC</a>."),
            ]),
            ("Measure calls, not visits", [
                ("p", "Traffic doesn't pay the bills. Booked jobs do. Google Ads can count calls to a forwarding number shown on your site after an ad click, with a minimum call length you choose. Add call tracking for your other traffic too, so you can see which pages make the phone ring. And make sure every call gets answered, or texted back with <a href=\"{u:missed-call-text-back}\">missed-call text-back</a>."),
                ("p", "Ready for a site built around the phone? See our <a href=\"{u:website}\">HVAC websites</a>, or start with the free report card."),
                ("cta",),
            ]),
        ],
        "faq": [
            ("How many pages does an HVAC website need?", "Enough to give each main service and each main town its own useful page, plus about, reviews and contact. For most shops that's more than five and fewer than you'd think."),
            ("Should I put prices on my website?", "If you have a set price, like a tune-up or a diagnostic fee, showing it can help. For installs, explain what goes into the price and offer a free estimate."),
            ("Does a faster site rank higher?", "Google says Core Web Vitals are used by its ranking systems, but relevant content still comes first. Speed mostly helps by keeping visitors from leaving."),
        ],
        "sources": [
            ("Google Search Central: Understanding Core Web Vitals", "https://developers.google.com/search/docs/appearance/core-web-vitals"),
            ("Google Search Central: Page experience", "https://developers.google.com/search/docs/appearance/page-experience"),
            ("Google Search Central: SEO Starter Guide", "https://developers.google.com/search/docs/fundamentals/seo-starter-guide"),
            ("Google Search Central: Spam policies", "https://developers.google.com/search/docs/essentials/spam-policies"),
            ("Google Ads Help: About Quality Score", "https://support.google.com/google-ads/answer/2404197"),
            ("Google Ads Help: About Ad Rank", "https://support.google.com/google-ads/answer/1722122"),
            ("Google Ads Help: Phone call conversion tracking", "https://support.google.com/google-ads/answer/6100664"),
        ],
        "related": ["hvac-website-checklist", "hvac-seo-what-moves-rankings"],
    },
    # ------------------------------------------------------------------ 7. Lead generation
    {
        "slug": "hvac-lead-generation-bought-vs-owned",
        "title": "HVAC lead generation: bought leads vs leads you own",
        "short": "Bought vs owned leads",
        "desc": "Paying per lead is quick. Owning the channels that bring in calls lasts. How the two compare, what to ask any lead seller, and how to build calls that don't stop when you stop paying.",
        "read": 5,
        "date": DATE,
        "takeaways": [
            "Bought leads stop the day you stop paying. Owned channels keep working.",
            "Owned means your Google profile, website, reviews and phone number are in your name.",
            "Google says you can't pay for a better map ranking, so that spot has to be earned.",
            "Judge every source by cost per booked job, not cost per lead.",
        ],
        "sections": [
            ("Two ways to get the phone to ring", [
                ("p", "There are two kinds of HVAC leads. <b>Bought leads</b> are ones you pay for one at a time, or per click: lead sellers, Local Services Ads, Google Ads. <b>Owned leads</b> come from things you control: your <a href=\"{u:google-business-profile}\">Google Business Profile</a>, your website and its rankings, your reviews, your past customers and your phone number."),
                ("p", "Neither is bad. Bought leads are fast. Owned channels are slow to build but don't send a bill for every call. Most healthy shops use both and slowly shift the mix toward owned."),
            ]),
            ("Side by side", [
                ("table", [
                    ["", "Bought leads", "Owned leads"],
                    ["Speed to first call", "Can start once ads or listings go live", "Builds over time"],
                    ["Cost", "You pay for every lead or click", "Mostly time and upkeep, plus any help you hire"],
                    ["When you stop paying", "Calls stop", "Rankings, reviews and past customers keep working"],
                    ["Who controls it", "The platform's rules and prices", "You, within Google's guidelines"],
                    ["Examples", "Lead sellers, Local Services Ads, Google Ads", "Google profile, website, reviews, maintenance plan customers"],
                ]),
            ]),
            ("Not all bought leads are the same", [
                ("p", "Local Services Ads are a bought lead, but a fair one. Google charges for valid leads, says invalid or low-quality leads aren't charged, and once a customer reaches out, says the lead is yours to turn into a customer. Google Ads charge per click, and you control the keywords, the ad and the page."),
                ("p", "Third-party lead sellers vary a lot. Before you sign with any of them, ask:"),
                ("ol", [
                    "Is this lead sent only to me, or to other contractors too?",
                    "What counts as a lead I pay for, and how do I get credit for a bad one?",
                    "Is there a contract term or a monthly minimum?",
                    "Did the homeowner agree to be contacted by my company?",
                    "Can I see where the lead came from?",
                ]),
            ]),
            ("What owning your leads really means", [
                ("p", "Owning isn't just a feeling. It's whose name is on the accounts. Check these:"),
                ("ul", [
                    "<b>Your Google Business Profile.</b> You should be the primary owner. Google says owners have full control and managers have mostly the same access, except they can't add or remove users or remove the profile. An agency should be a manager.",
                    "<b>Your domain and website.</b> In your name, so you keep them if you change vendors.",
                    "<b>Your phone number.</b> If a tracking number is on your profile and trucks, make sure it can be moved to you.",
                    "<b>Your reviews.</b> They live on your profile, so they're yours as long as the profile is.",
                    "<b>Your customer list.</b> Every past customer is a future tune-up, repair or replacement.",
                ]),
                ("p", "Google also says there's no way to pay for a better local ranking. That's why the map spot, once earned, is one of the most valuable things an HVAC shop owns. See <a href=\"{u:local-seo}\">local SEO</a>."),
            ]),
            ("Building owned leads", [
                ("ol", [
                    "Get your Google profile right: category, services, hours, photos. See <a href=\"{u:guide-google-map-pack-hvac}\">how the map pack works</a>.",
                    "Ask every customer for a review with <a href=\"{u:review-requests}\">review requests</a>.",
                    "Build a <a href=\"{u:website}\">website</a> with a page per service and town.",
                    "Catch every call you can't answer with <a href=\"{u:missed-call-text-back}\">missed-call text-back</a>, so paid and owned leads don't leak.",
                    "Use paid ads to fill gaps while owned channels grow, and track cost per booked job for each.",
                ]),
                ("p", "See all of it in one place on our <a href=\"{u:plans}\">plans page</a>, or read the <a href=\"{u:hvac-marketing}\">HVAC marketing guide</a>."),
                ("cta",),
            ]),
        ],
        "faq": [
            ("Are Local Services Ads bought leads?", "Yes, you pay per lead. But Google doesn't charge for leads it finds invalid, and the customer contacts you directly through your own listing."),
            ("Should I stop buying leads?", "Not right away. Use them to keep the schedule full while you build owned channels, then compare cost per booked job and cut what doesn't pay."),
            ("How do I know if I own my Google profile?", "Open the profile's people and access settings. You should be listed as the primary owner. If an agency is the owner, ask them to transfer it to you."),
        ],
        "sources": [
            ("Google Local Services Help: How Local Services Ads work", "https://support.google.com/localservices/answer/6224841"),
            ("Google Local Services Help: How you're charged for leads", "https://support.google.com/adwords/answer/7195435"),
            ("Google Ads Help: Actual cost-per-click", "https://support.google.com/google-ads/answer/6297"),
            ("Google Business Profile Help: Owners and managers", "https://support.google.com/business/answer/3403100"),
            ("Google Business Profile Help: Tips to improve your local ranking", "https://support.google.com/business/answer/7091"),
            ("Google: Guidelines for representing your business on Google", "https://support.google.com/business/answer/3038177"),
        ],
        "related": ["questions-to-ask-hvac-marketing-agency", "hvac-marketing-cost"],
    },
    # ------------------------------------------------------------------ 8. Facebook ads
    {
        "slug": "facebook-ads-for-hvac",
        "title": "Facebook ads for HVAC: when they work (seasonal tune-ups, retargeting)",
        "short": "Facebook ads",
        "desc": "Facebook isn't where homeowners search for a repair. It's where you remind them about a tune-up before the season and follow up with people who visited your site. How to use it for that.",
        "read": 5,
        "date": DATE,
        "takeaways": [
            "Google catches people searching right now. Facebook reaches people before they need you.",
            "The best HVAC uses are seasonal tune-ups, maintenance plans and retargeting site visitors.",
            "The Meta Pixel on your site lets you measure results and build audiences of past visitors.",
            "Target your real service area. Meta lets you set a radius around a city or a custom spot.",
        ],
        "sections": [
            ("Search vs scroll", [
                ("p", "On Google, a homeowner with a broken AC is looking for you. On Facebook and Instagram, they're scrolling past friends' photos. That's a different moment. Facebook ads rarely beat Google for \"my furnace just died\". Where they can work is reaching people <b>before</b> they need you, and staying in front of people who already looked at your site."),
                ("p", "There's a big audience to reach. The EIA's 2020 home energy survey found 88% of U.S. households use air conditioning, with 92% in the Midwest and 93% in the South. Every one of those systems needs care."),
            ]),
            ("When Facebook ads work for HVAC", [
                ("ul", [
                    "<b>Pre-season tune-ups.</b> The BLS notes HVAC techs often work overtime in peak heating and cooling seasons. Ads for spring AC tune-ups and fall furnace checks fill the schedule before the rush, when your crew has room.",
                    "<b>Maintenance plans.</b> A plan is an easy offer to explain in a short ad, and it brings repeat work you own.",
                    "<b>Retargeting.</b> Show ads to people who visited your site but didn't call. They already know your name.",
                    "<b>Past customers.</b> Remind them it's time for service, or tell them about a new product like heat pumps.",
                    "<b>Shoulder months.</b> When search slows down, Facebook can keep the board from going empty.",
                ]),
            ]),
            ("When they usually don't", [
                ("ul", [
                    "Emergency repair calls, where Google search and <a href=\"{u:local-services-ads}\">Local Services Ads</a> are a better fit.",
                    "Brand-new shops with no reviews, photos or site to send people to.",
                    "Shops with no one to answer leads fast. A form lead that waits a day goes cold.",
                ]),
            ]),
            ("The setup that matters", [
                ("ol", [
                    "<b>Install the Meta Pixel.</b> Meta describes it as code on your website that tracks visitor activity, so you can measure how well ads work and build custom audiences for targeting.",
                    "<b>Build a website visitor audience.</b> Meta's website custom audiences let you target people who visited your site within a time window you choose. Exclude people who already booked.",
                    "<b>Set your service area.</b> Meta lets you target a radius around a city (10 to 50 miles) or around a custom location (about 0.63 to 50 miles). Match it to where your trucks actually go.",
                    "<b>Consider lead ads.</b> Meta's lead ads use a mobile-friendly form that fills in details people already shared with Facebook, so it's quick to sign up for a tune-up. Then call fast.",
                    "<b>Send clicks to a matching page.</b> A tune-up ad should land on a tune-up page with the price and a call button, not your homepage.",
                ]),
            ]),
            ("A simple seasonal plan", [
                ("p", "Before cooling season, run a spring AC tune-up offer to your service area and your past customers. Before heating season, switch to furnace and heat pump checks. All year, run a small retargeting ad to recent site visitors with your reviews and phone number. Judge it the same way as every other channel: cost per booked job, from your own records."),
                ("p", "See how we run <a href=\"{u:facebook-ads}\">Facebook ads for HVAC</a>, and how they fit with <a href=\"{u:google-ads}\">Google Ads</a>."),
                ("cta",),
            ]),
        ],
        "faq": [
            ("Do Facebook ads work for HVAC repair calls?", "Usually not as well as Google, because people with a broken system search for help. Facebook works better for tune-ups, maintenance plans and retargeting."),
            ("What is retargeting?", "Showing ads to people who already visited your website. The Meta Pixel on your site makes it possible."),
            ("Should I use Facebook lead ads?", "They can work for tune-up and maintenance plan offers, as long as someone calls the lead back fast."),
        ],
        "sources": [
            ("Meta for Developers: Meta Pixel", "https://developers.facebook.com/docs/meta-pixel"),
            ("Meta for Developers: Website custom audiences", "https://developers.facebook.com/docs/marketing-api/audiences/guides/website-custom-audiences"),
            ("Meta for Developers: Lead ads", "https://developers.facebook.com/docs/marketing-api/guides/lead-ads"),
            ("Meta for Developers: Basic targeting (location radius)", "https://developers.facebook.com/docs/marketing-api/audiences/reference/basic-targeting"),
            ("U.S. Energy Information Administration: Nearly 90% of U.S. households used air conditioning in 2020", "https://www.eia.gov/todayinenergy/detail.php?id=52558"),
            ("U.S. Bureau of Labor Statistics: HVAC mechanics and installers", "https://www.bls.gov/ooh/installation-maintenance-and-repair/heating-air-conditioning-and-refrigeration-mechanics-and-installers.htm"),
        ],
        "related": ["how-much-to-spend-on-google-ads-hvac", "hvac-lead-generation-bought-vs-owned"],
    },
]
