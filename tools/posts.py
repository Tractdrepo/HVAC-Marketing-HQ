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
        "desc": "There's no right number from a chart. Work out an HVAC Google Ads budget from the jobs you want and what a click costs in your town.",
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
        "related": ["google-ads-vs-local-services-ads-hvac", "hvac-marketing-cost", "facebook-ads-for-hvac"],
    },
    # ------------------------------------------------------------------ 2. Local Services Ads
    {
        "slug": "google-local-services-ads-hvac",
        "title": "Google Local Services Ads for HVAC: how they work and how leads are charged", "seo_title": "Google Local Services Ads for HVAC: Costs and How They Work",
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
        "desc": "Pay per click or pay per lead? How Google Ads and Local Services Ads differ in cost, control and ranking, and when an HVAC company should run each.",
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
        "title": "How HVAC rankings work: what moves the map pack and organic results", "seo_title": "HVAC SEO: What Moves Map Pack and Organic Rankings",
        "short": "HVAC SEO",
        "desc": "The map pack and the regular results rank differently. What Google says matters for each, and what an HVAC company can change this month.",
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
        "title": "How to get more HVAC reviews on Google (within Google's rules)", "seo_title": "How to Get More Google Reviews for Your HVAC Company",
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
        "title": "What an HVAC contractor website needs to book calls",
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
        "title": "Bought HVAC leads vs leads you own: which to pay for",
        "short": "Bought vs owned leads",
        "desc": "Paying per lead is quick. Owning the channels that bring in calls lasts. How bought and owned HVAC leads compare, and what to ask any lead seller.",
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
        "title": "Facebook ads for HVAC: when they work (seasonal tune-ups, retargeting)", "seo_title": "Facebook Ads for HVAC: When They Actually Work",
        "short": "Facebook ads",
        "desc": "Facebook isn't where homeowners search for a repair. It's where you remind past visitors about tune-ups before the season. When HVAC Facebook ads work.",
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

    # ------------------------------------------------------------------ 9. Best agencies listicle
    {
        "slug": "best-hvac-marketing-agencies",
        "title": "The best HVAC marketing companies in 2026, compared and priced", "seo_title": "Best HVAC Marketing Companies in 2026: 8 Agencies Compared",
        "short": "Best HVAC marketing companies",
        "desc": "Eight HVAC marketing companies compared on published price, contract, website ownership and fit, with sources. We're on the list, and we say so.",
        "read": 12,
        "date": "2026-10-15",
        "updated": "2026-10-23",
        "takeaways": [
            "Only three of the eight agencies here publish real prices: us, Websites for HVAC and Footbridge Media. RS Gonzales and Hook Agency publish starting prices.",
            "The big home-service agencies (Scorpion, Blue Corona and RYNO, Valve+Meter) don't publish prices and mostly serve larger shops.",
            "\"You own your website\" means little unless the contract says so. Read the terms, not the sales page.",
            "Pick by your size and budget first. The right agency for a $5M shop is the wrong one for a three-truck shop.",
        ],
        "sections": [
            ("Read this first: we're on this list", [
                ("note", "HVAC Marketing HQ wrote this, and we put ourselves first. Every agency on it sells HVAC marketing, so we have a stake. To keep it fair, every price and term below comes from the agency's own website, linked at the bottom, as published in October 2026. Where an agency doesn't publish something, we say so instead of guessing. If you spot something out of date, <a href=\"{u:contact}\">tell us</a> and we'll fix it."),
                ("p", "Most \"best agencies\" lists are written by an agency that ranks itself first and keeps the criteria vague. We'd rather show our work. Here's how we compared them."),
                ("ul", [
                    "<b>HVAC focus.</b> Does the agency work only with HVAC companies, or with dozens of trades?",
                    "<b>Published pricing.</b> Can you see what it costs before you get on a sales call?",
                    "<b>Contract.</b> How long are you locked in, and what does it take to leave?",
                    "<b>Website ownership.</b> Do you keep a working site if you leave, and is that in the terms?",
                    "<b>Follow-up built in.</b> Are missed-call text-back and review requests part of the plan, or extras?",
                    "<b>Fit for owner-run shops.</b> Does the agency take shops under $1M a year?",
                ]),
            ]),
            ("What to look for in an HVAC marketing company", [
                ("p", "\"Best\" depends on your shop. A company that's right for a $5M operation with a big ad budget can be wrong for a three-truck shop, and the other way around. These are the questions that separate them, and the ones we used below."),
                ("ul", [
                    "<b>Can you see the price and the contract before a sales call?</b> Three companies on this list publish full prices, two publish starting prices, and three don't publish prices.",
                    "<b>Do you keep your website if you leave?</b> Answers range from \"yours outright\" to \"the site goes offline\". The terms page is where to check.",
                    "<b>Is the plan built for your size?</b> Some companies say on their own site that they work best with larger shops or bigger ad budgets. That's useful to know before you call.",
                    "<b>Is follow-up included?</b> Missed-call text-back and review requests are in some plans and extras in others.",
                ]),
            ]),
            ("Quick picks", [
                ("table", [
                    ["#", "Agency", "Best for", "Published price"],
                    ["1", "HVAC Marketing HQ", "Owner-run HVAC shops that want the whole system for a flat monthly price", "$499 to $2,499/mo, build $1,995 to $4,500"],
                    ["2", "Websites for HVAC", "HVAC shops that want one company per area", "$499 to $2,499/mo, build $1,995 to $4,499"],
                    ["3", "Footbridge Media", "The lowest monthly price, especially for Nexstar and CertainPath members", "$249/mo, no setup fee"],
                    ["4", "RS Gonzales", "Shops ready to spend $3,000+ a month on ads", "$2,200 to $5,000/mo plus ad spend"],
                    ["5", "Hook Agency", "Shops over $2M a year that want SEO, ads and video", "SEO from $2,800/mo; bundles $3,500 to $15,000+/mo"],
                    ["6", "Scorpion", "Large shops that want a big team and many products", "Not published"],
                    ["7", "Blue Corona and RYNO", "Larger home-service companies with big budgets", "Not published"],
                    ["8", "Valve+Meter", "Shops that want an assessment-led plan tied to job data", "Not published"],
                ]),
            ]),
            ("1. HVAC Marketing HQ (that's us)", [
                ("p", "<b>Best for:</b> owner-run HVAC shops, from one truck to several locations, that want their website, Google profile, SEO and lead follow-up run by one HVAC-only team."),
                ("ul", [
                    "<b>Price:</b> Starter $499, Growth $999, Dominate $1,499 and Multi-location $2,499 a month, 20% off billed annually. One-time build fee of $1,995 to $4,500. Google Ads, Local Services Ads and Facebook ads are $299 a month each, with ad spend billed to you and never marked up. See <a href=\"{u:plans}\">plans</a>.",
                    "<b>Contract:</b> 6-month first term, then month to month. First month refunded if you're not happy within 30 days of launch.",
                    "<b>Ownership:</b> your site, domain, Google profile and reviews are yours.",
                    "<b>Built in:</b> missed-call text-back within 10 seconds and review requests on every plan, plus <a href=\"{u:hq-command-center}\">HQ Command Center</a>, a CRM with unlimited logins for your team.",
                ]),
                ("p", "<b>Not the right fit if:</b> you want photo and video shoots, you need a big in-house team on weekly calls, or you can't take on more work right now. We're also new, so we can't show you years of case studies yet. Start with the <a href=\"{u:report-card}\">free report card</a> and judge the work yourself."),
            ]),
            ("2. Websites for HVAC", [
                ("p", "<b>Best for:</b> HVAC shops that want one company per area. Their monthly prices match ours at every plan level."),
                ("ul", [
                    "<b>Price:</b> $499 to $2,499 a month billed monthly, or $399 to $1,999 billed annually, plus a build fee of $1,995 to $4,499.",
                    "<b>Contract:</b> month to month.",
                    "<b>Ownership:</b> their terms say the site goes offline if you leave. Ask what you keep.",
                    "<b>Strengths:</b> HVAC only, clear published pricing, and an exclusive territory offer.",
                ]),
                ("p", "<b>Not the right fit if:</b> keeping a working website after you leave matters to you. Our <a href=\"{u:guide-websites-for-hvac-alternative}\">side-by-side comparison</a> has the 12-month math."),
            ]),
            ("3. Footbridge Media", [
                ("p", "<b>Best for:</b> the lowest monthly price with no setup fee, especially if you're a Nexstar or CertainPath member."),
                ("ul", [
                    "<b>Price:</b> $249 a month, $0 setup. Member rates are $194 a month for Nexstar and CertainPath, $223 for Praxis S-10. Google Ads management is $249 a month after the first month, plus spend.",
                    "<b>Contract:</b> none; either side can end it with written notice. 90-day money-back guarantee.",
                    "<b>Ownership:</b> their terms cover handing over files after 90 days.",
                    "<b>Strengths:</b> low price, priced add-ons you can buy online, and review requests included.",
                ]),
                ("p", "<b>Not the right fit if:</b> you want an HVAC-only team (they serve about 15 trades) or missed-call text-back in the plan. See the <a href=\"{u:guide-footbridge-media-alternative-hvac}\">full comparison</a>."),
            ]),
            ("4. RS Gonzales", [
                ("p", "<b>Best for:</b> HVAC-focused shops ready to spend at least $3,000 a month on ads and hand marketing to a larger team."),
                ("ul", [
                    "<b>Price:</b> Grow $2,200, Accelerate $3,500 and Dominate $5,000 a month, plus ad spend with a $3,000 monthly minimum. A $500 onboarding deposit.",
                    "<b>Contract:</b> 12 months on their pricing page. 30-day money-back on the first month.",
                    "<b>Ownership:</b> the website is yours after 12 months, or with a $4,500 buyout.",
                    "<b>Strengths:</b> deep HVAC content, a CRM that syncs with field software, and a website included in the plan.",
                ]),
                ("p", "<b>Not the right fit if:</b> your all-in budget is under about $1,500 a month. The <a href=\"{u:guide-rs-gonzales-alternative}\">comparison</a> works out the 12-month cost."),
            ]),
            ("5. Hook Agency", [
                ("p", "<b>Best for:</b> shops doing over $2M a year that want SEO, ads, Meta ads with video and a custom website from one partner."),
                ("ul", [
                    "<b>Price:</b> local SEO from $2,800 a month, Google Ads from $2,000, Meta ads from $3,000, websites $12,000 to $24,000 paid over 12 months. Bundles from $3,500 to $15,000+ a month.",
                    "<b>Contract:</b> their pages differ on whether terms are yearly or month to month. Ask.",
                    "<b>Ownership:</b> they say you own your website 100%.",
                    "<b>Strengths:</b> a large content library and a long track record across trades.",
                ]),
                ("p", "<b>Not the right fit if:</b> your shop does under $1M a year; their own forms say that's not a fit. They also serve over 30 trades. See the <a href=\"{u:guide-hook-agency-alternative-hvac}\">comparison</a>."),
            ]),
            ("6. Scorpion", [
                ("p", "<b>Best for:</b> large shops that want a big agency with its own software and many add-on products."),
                ("ul", [
                    "<b>Price:</b> not published. Their FAQ says it depends on your goals, and the next step is a meeting.",
                    "<b>Contract:</b> their FAQ describes a 12-month term for website and SEO; ads are month to month.",
                    "<b>Ownership:</b> their FAQ says the site is built on their own platform, so leaving means a rebuild.",
                    "<b>Strengths:</b> scale, many products and a large team.",
                ]),
                ("p", "<b>Not the right fit if:</b> you want to see a price before a sales call, or keep your site if you leave. Our <a href=\"{u:guide-scorpion-alternative-hvac}\">Scorpion guide</a> quotes their FAQ."),
            ]),
            ("7. Blue Corona and RYNO", [
                ("p", "<b>Best for:</b> larger home-service companies with big budgets. Blue Corona now operates as part of RYNO, and the two sites share the same terms."),
                ("ul", [
                    "<b>Price:</b> no pricing page. RYNO's plumbing FAQ says clients \"typically invest $5,000 or more\". Older Blue Corona pages put ongoing SEO at $1,500 to $20,000 a month.",
                    "<b>Contract:</b> Blue Corona's copy says no long-term contracts, but the published terms point to an agreement that isn't public.",
                    "<b>Ownership:</b> \"You own 100% of everything we create\" in their sales copy; there's no ownership clause in the published terms.",
                    "<b>Strengths:</b> a big service menu, from SEO and ads to direct mail and call tracking.",
                ]),
                ("p", "<b>Not the right fit if:</b> you're an owner-run shop with a budget under a few thousand a month."),
            ]),
            ("8. Valve+Meter", [
                ("p", "<b>Best for:</b> shops that want a plan built from their own job and invoice data, starting with an assessment."),
                ("ul", [
                    "<b>Price:</b> not published. The only offer is a free marketing assessment.",
                    "<b>Contract:</b> not published.",
                    "<b>Ownership:</b> they say clients keep their website and data.",
                    "<b>Strengths:</b> a clear \"Math Before Marketing\" approach that ties spend to booked jobs. Most of their case studies are HVAC, though they serve 15 trades.",
                ]),
                ("p", "<b>Not the right fit if:</b> you want to know the price before you talk to anyone."),
            ]),
            ("How to choose", [
                ("ol", [
                    "<b>Start with your budget, all in.</b> Add the monthly fee, any build fee and ad spend for 12 months. Our <a href=\"{u:tools/hvac-marketing-budget-calculator}\">marketing budget calculator</a> helps.",
                    "<b>Read the terms, not the sales page.</b> Look for the contract length, the cancellation notice and what happens to your website when you leave.",
                    "<b>Ask who does the work.</b> An HVAC-only team won't need you to explain what a tune-up is.",
                    "<b>Ask what they'll report.</b> Booked jobs and answered calls beat clicks and impressions. See our <a href=\"{u:guide-questions-to-ask-hvac-marketing-agency}\">seven questions to ask any agency</a>.",
                    "<b>Check your own numbers first.</b> The <a href=\"{u:report-card}\">free report card</a> shows where you stand before anyone pitches you.",
                ]),
                ("p", "Want everything side by side? See <a href=\"{u:compare}\">how HVAC marketing companies compare</a>, or read our guide to <a href=\"{u:hvac-marketing}\">marketing for HVAC companies</a>."),
                ("cta",),
            ]),
        ],
        "faq": [
            ("What is the best HVAC marketing company?", "There isn't one best for every shop. From what each company publishes: Footbridge Media has the lowest published monthly price, RS Gonzales and Hook Agency set higher minimums or revenue fits, and Scorpion, Blue Corona/RYNO and Valve+Meter don't publish prices and mostly serve larger shops. We built HVAC Marketing HQ for owner-run shops that want the whole system at a published flat price. Pick by your budget, the contract and what you keep if you leave."),
            ("How much does an HVAC marketing agency cost?", "Of the agencies here that publish prices, monthly fees run from $249 (Footbridge Media) to $5,000 (RS Gonzales) before ad spend. The larger agencies don't publish prices; one says its clients typically invest $5,000 or more a month."),
            ("Why do you rank yourselves first?", "Because we built what we think an owner-run HVAC shop needs, at a price it can see up front. We say so at the top, and every other agency's facts come from its own site so you can check them."),
            ("Should I pick an HVAC-only agency?", "It helps. An HVAC-only team already knows your services, seasons and customers, so you spend less time explaining your business."),
            ("Do I own my website with these agencies?", "It varies. Several say you do in their sales copy but not in their terms. Ask for the contract and read the section on what happens when you leave."),
        ],
        "sources": [
            ("Websites for HVAC: Pricing", "https://websitesforhvac.com/pricing"),
            ("Websites for HVAC: Terms", "https://websitesforhvac.com/terms"),
            ("Footbridge Media: HVAC marketing", "https://www.footbridgemedia.com/who-we-help/hvac-marketing-seo"),
            ("Footbridge Media: Terms", "https://www.footbridgemedia.com/terms"),
            ("Footbridge Media: Nexstar members", "https://www.footbridgemedia.com/nexstar"),
            ("RS Gonzales: Pricing", "https://rsgonzales.com/pricing/"),
            ("RS Gonzales: Terms and conditions", "https://rsgonzales.com/terms-and-conditions/"),
            ("Hook Agency: Pricing", "https://hookagency.com/pricing/"),
            ("Hook Agency: Contact (fit by revenue)", "https://hookagency.com/contact-us/"),
            ("Scorpion: FAQ", "https://www.scorpion.co/faq/"),
            ("RYNO: Plumbing industry FAQ", "https://www.rynoss.com/industries/plumbing/"),
            ("Blue Corona: Digital marketing", "https://www.bluecorona.com/digital-marketing/"),
            ("Valve+Meter: HVAC", "https://valveandmeter.com/trades/hvac/"),
            ("Valve+Meter: Free marketing assessment", "https://valveandmeter.com/request-marketing-assessment/"),
        ],
        "related": ["questions-to-ask-hvac-marketing-agency", "hvac-marketing-cost", "scorpion-alternative-hvac"],
    },
    # ------------------------------------------------------------------ Oct 15 batch: CRM, ServiceTitan vs HCP, ideas, leads, advertising, Google Verified
    {'slug': 'best-crm-for-hvac',
     'title': 'The best CRM for HVAC companies in 2026: field software vs a marketing CRM', 'seo_title': 'Best CRM for HVAC Companies in 2026, Compared',
     'short': 'Best CRM for HVAC',
     'desc': 'ServiceTitan, Housecall Pro, Jobber, FieldEdge and HighLevel compared for HVAC: what each does, published prices, and why many shops run two.',
     'read': 8,
     'date': '2026-10-15',
     'takeaways': ['Field service software runs jobs: dispatch, invoices, techs. A marketing CRM works leads: missed calls, follow-up texts, review asks.',
                   "Housecall Pro, Jobber and HighLevel publish prices. ServiceTitan and FieldEdge don't, so you need a quote.",
                   'Many HVAC shops run both kinds: field software for the work, a marketing CRM for the leads before and after it.',
                   'Pick by how you lose money today: missed calls and slow follow-up, or messy dispatch and billing.'],
     'sections': [('Read this first: we use one of these',
                   [('note',
                     'HVAC Marketing HQ wrote this. Our <a href="{u:hq-command-center}">HQ Command Center</a> is the CRM we set up for clients, built on HighLevel, so we have a stake '
                     "in one of the five tools below. We don't sell or resell ServiceTitan, Housecall Pro, Jobber or FieldEdge. Every price and feature comes from the vendor's own "
                     'site, linked at the bottom, as checked in October 2026. Where a vendor doesn\'t publish a price, we say "not published" instead of guessing.'),
                    ('p',
                     '"CRM" means two different things in HVAC. Owners ask for the best one and get answers that compare tools built for different jobs. So before the list, here\'s '
                     'the split.')]),
                  ('Field service software vs a marketing CRM',
                   [('p',
                     '<b>Field service software</b> runs the work once a job exists. Think dispatch board, tech mobile app, price book, estimates, invoices, payments and service '
                     'agreements. ServiceTitan, Housecall Pro, Jobber and FieldEdge all sit here. Most of them also have a customer list, which is why they get called a CRM.'),
                    ('p',
                     "<b>A marketing or lead CRM</b> works the person before they're a job, and after. It catches the missed call, texts back, keeps the lead in a pipeline, sends the "
                     'follow-up when an estimate goes quiet, and asks for the review. HighLevel sits here.'),
                    ('table',
                     [['Job to be done', 'Field service software', 'Marketing CRM'],
                      ['Dispatch techs and route trucks', 'Yes, core job', 'No'],
                      ['Price book, estimates, invoices', 'Yes, core job', 'Not the focus'],
                      ['Online booking', 'Yes, in most', 'Yes, calendars and booking links'],
                      ['Text back a missed call', 'Varies, often an add-on', 'Yes, core job'],
                      ['Lead pipeline and follow-up', 'Some', 'Yes, core job'],
                      ['Review requests', 'Yes, in most, sometimes an add-on', 'Yes']]),
                    ('p',
                     'The lines blur every year. Field software vendors keep adding marketing tools, and marketing CRMs keep adding booking. But the core job of each is still '
                     "different, and that's the thing to match to your shop.")]),
                  ('1. ServiceTitan',
                   [('p', '<b>What it is:</b> field service software for the trades, sold in three packages: Starter, Essentials and The Works.'),
                    ('ul',
                     ["<b>Price:</b> not published. ServiceTitan's pricing page says pricing is per technician and asks you to request pricing.",
                      '<b>Packages:</b> Starter covers dispatching, scheduling, call booking, invoicing and the price book. Essentials adds mobile estimates and payroll. The Works is '
                      "the full suite. ServiceTitan's help center says custom reports are only on The Works.",
                      '<b>Booking:</b> Scheduling Pro, a separate Pro product, lets customers book online or by text based on real-time availability.',
                      '<b>Marketing and reviews:</b> Marketing Pro is a separate Pro product for email, direct mail and campaigns. Marketing Pro Reputation sends review requests by '
                      'text or email after a job and pulls Google, Facebook and Yelp reviews into one feed.']),
                    ('p',
                     '<b>Worth a look if:</b> you have enough techs that per-technician pricing makes sense, and you want dispatch, payroll and reporting in one system. Get a written '
                     "quote that lists each Pro product you'd add.")]),
                  ('2. Housecall Pro',
                   [('p', '<b>What it is:</b> field service software with published plans: Basic, Essentials and MAX.'),
                    ('ul',
                     ['<b>Price:</b> its pricing page lists Basic at $59 a month billed annually or $79 monthly for 1 user, Essentials at $149 annually or $189 monthly for 5 users, '
                      'and MAX at $299 annually or $329 monthly for 8 users. Extra users on MAX are $35 a month each. Some of its trade pages show higher numbers, so confirm on the '
                      'pricing page.',
                      '<b>Booking:</b> online booking is listed in the Basic plan. Customers can book through Google, your website or a shared link.',
                      '<b>Marketing and reviews:</b> review management is listed in Basic. Its Marketing Center holds email, text and postcard campaigns. A voice add-on with call '
                      'tracking is sold separately.',
                      '<b>Trial:</b> 14 days free, no credit card, per its pricing page.']),
                    ('p',
                     '<b>Worth a look if:</b> you want to see the price before a sales call and you run a small to mid-size team. See our <a '
                     'href="{u:post-servicetitan-vs-housecall-pro}">ServiceTitan vs Housecall Pro</a> breakdown.')]),
                  ('3. Jobber',
                   [('p', '<b>What it is:</b> field service software for many home service trades, with published plans: Core, Connect, Grow and Plus.'),
                    ('ul',
                     ['<b>Price:</b> its pricing page says plans start at $29 a month billed annually. Team plans and monthly billing cost more. Teams of 16 or more are told to '
                      'contact sales.',
                      '<b>Booking:</b> customers can request or book work from a form on your website, social profiles or client hub. Jobber says it can schedule the job and assign a '
                      'team member when a booking comes in.',
                      '<b>Reviews:</b> Jobber can text or email a review ask after a visit, a closed job or a paid invoice, and it sends one ask per client every six months at most. '
                      'Its own pages differ on whether Reviews is included or an add-on, so ask.',
                      '<b>Trial:</b> 14 days free, no credit card, per its pricing page.']),
                    ('p',
                     "<b>Worth a look if:</b> you're a smaller shop and want simple quoting, scheduling and invoicing. Jobber serves many trades, not just HVAC, so check the HVAC "
                     'parts you need, like service agreements and equipment records.')]),
                  ('4. FieldEdge',
                   [('p', '<b>What it is:</b> field service software with three tiers: Select, Premier and Elite.'),
                    ('ul',
                     ['<b>Price:</b> not published. Its pricing page says tiers can be customized and points you to a demo for a quote.',
                      '<b>Tiers:</b> Premier adds advanced dispatching, multi-option quotes and advanced service agreements. Elite adds outbound call recording, Proposal Pro and '
                      'MarketingEdge with 2-way texting.',
                      '<b>Accounting:</b> FieldEdge says it syncs with QuickBooks to cut out double entry.',
                      "<b>Booking:</b> we didn't find a customer online booking feature described on its public pages. Ask in the demo."]),
                    ('p', "<b>Worth a look if:</b> QuickBooks sync and service agreements are at the top of your list, and you're fine getting a quote.")]),
                  ('5. HighLevel (what our HQ Command Center runs on)',
                   [('p',
                     "<b>What it is:</b> a marketing CRM. It isn't built for dispatch or invoicing. It's built for leads: calls, texts, pipelines, follow-up, booking and reviews."),
                    ('ul',
                     ['<b>Price:</b> its pricing page lists Starter at $97 a month, Unlimited at $297 and Agency Pro at $497. Text, phone and email usage is billed on top, per its '
                      'help center.',
                      '<b>Missed calls:</b> it has a built-in missed-call text-back setting on each phone number, and replies land in one inbox.',
                      '<b>Reviews:</b> it can send review requests by text and email, and it pulls reviews from connected Google and Facebook accounts into one dashboard.',
                      '<b>Booking:</b> calendars and booking links, which can go in the missed-call text.']),
                    ('p',
                     '<b>The honest catch:</b> HighLevel is a big platform, and most of it is aimed at agencies. Setting up the pipelines, automations, phone numbers and texting '
                     'rules takes real time. That\'s the work we do for clients inside <a href="{u:hq-command-center}">HQ Command Center</a>, on every <a href="{u:plans}">plan</a>. '
                     'You can also buy HighLevel direct and set it up yourself.')]),
                  ('Why many shops run both',
                   [('p',
                     "Field software is great once a call is booked. It's weaker at the moments before that: the call you missed at 6:40 pm, the lead that filled out a form and never "
                     'heard back, the $9,000 estimate nobody followed up on. A marketing CRM is built for those moments, and weak at dispatch and billing.'),
                    ('p',
                     'So a common setup is field software for the work and a marketing CRM for the leads. The CRM handles <a href="{u:missed-call-text-back}">missed-call '
                     'text-back</a>, <a href="{u:estimate-follow-up}">estimate follow-up</a> and <a href="{u:review-requests}">review requests</a>. The field software handles the '
                     'job. If you go this way, decide which system owns the customer record, and avoid sending two review asks for the same job.')]),
                  ('How to pick',
                   [('ol',
                     ['<b>Find your biggest leak.</b> If calls ring out and leads go cold, start with lead follow-up. Our <a href="{u:tools/missed-call-cost-calculator}">missed call '
                      'cost calculator</a> puts a number on it. If jobs get lost between the office and the truck, start with field software.',
                      '<b>Count your techs.</b> ServiceTitan prices per technician. Housecall Pro and Jobber price by plan and users. Know your count before any demo.',
                      "<b>Get the full price in writing.</b> For tools that don't publish prices, ask for each add-on, setup fee and contract term on paper.",
                      '<b>Ask who sets it up.</b> Software you never finish setting up does nothing.']),
                    ('p',
                     'Not sure where your leaks are? Start with a <a href="{u:report-card}">free report card</a>, or read how we think about <a href="{u:hvac-lead-generation}">HVAC '
                     'lead generation</a>.'),
                    ('cta',)])],
     'faq': [('Is ServiceTitan a CRM?',
              "It has customer records, but it's mainly field service software: dispatch, estimates, invoices and payroll. Its marketing and online booking tools are separate Pro "
              'products.'),
             ('Do I need both field software and a marketing CRM?',
              'Not always. A small shop can start with one. Many shops add a marketing CRM when missed calls, slow follow-up or review asks become the bottleneck.'),
             ('Which of these publish prices?',
              "As checked in October 2026, Housecall Pro, Jobber and HighLevel publish prices. ServiceTitan and FieldEdge don't; you request a quote."),
             ('What does HQ Command Center cost?', "It's included in every HVAC Marketing HQ plan, with logins for your whole team. See our plans page for prices.")],
     'sources': [('ServiceTitan: Pricing', 'https://www.servicetitan.com/pricing'),
                 ('ServiceTitan: Scheduling Pro', 'https://www.servicetitan.com/features/pro/scheduling'),
                 ('ServiceTitan: Marketing Pro Reputation', 'https://www.servicetitan.com/features/pro/marketing/reputation'),
                 ('ServiceTitan: Pro products', 'https://www.servicetitan.com/features/pro'),
                 ('Housecall Pro: Pricing and plans', 'https://www.housecallpro.com/pricing/'),
                 ('Housecall Pro Help: Marketing Center overview', 'https://help.housecallpro.com/en/articles/11057071-marketing-center-overview'),
                 ('Jobber: Pricing', 'https://www.getjobber.com/pricing/'),
                 ('Jobber Help: Online booking', 'https://help.getjobber.com/en/articles/online-booking/'),
                 ('Jobber Help: Reviews', 'https://help.getjobber.com/en/articles/reviews-marketing-tools/'),
                 ('FieldEdge: Pricing', 'https://fieldedge.com/pricing/'),
                 ('FieldEdge: HVAC software', 'https://fieldedge.com/hvac-software/'),
                 ('HighLevel: Pricing', 'https://www.gohighlevel.com/pricing'),
                 ('HighLevel Support: Pricing and billing guide', 'https://help.gohighlevel.com/support/solutions/articles/155000001156-highlevel-pricing-guide'),
                 ('HighLevel: Missed call text back', 'https://www.gohighlevel.com/post/missed-call-text-back'),
                 ('HighLevel: Reputation management', 'https://www.gohighlevel.com/online-reputation-management-software')],
     'related': ['servicetitan-vs-housecall-pro', 'missed-call-text-back-hvac', 'hvac-lead-generation-bought-vs-owned', 'get-more-google-reviews-hvac']},
    {'slug': 'servicetitan-vs-housecall-pro',
     'title': 'ServiceTitan vs Housecall Pro for HVAC: pricing, fit and features compared', 'seo_title': 'ServiceTitan vs Housecall Pro for HVAC: Pricing and Fit',
     'short': 'ServiceTitan vs Housecall Pro',
     'desc': 'ServiceTitan vs Housecall Pro for HVAC shops: how each prices, which size of shop each fits, and how booking, marketing and reviews compare.',
     'read': 7,
     'date': '2026-10-15',
     'takeaways': ["Housecall Pro publishes its prices. ServiceTitan doesn't; it prices per technician and you request a quote.",
                   'Housecall Pro lists online booking and review management in its lowest plan. ServiceTitan sells online booking and reviews as separate Pro products.',
                   'ServiceTitan splits its core software into Starter, Essentials and The Works. Housecall Pro has Basic, Essentials and MAX.',
                   'Neither replaces lead follow-up on its own. Check how each handles missed calls before you sign.'],
     'sections': [('Who wrote this, and how',
                   [('note',
                     "HVAC Marketing HQ wrote this. We don't sell, resell or get paid by ServiceTitan or Housecall Pro, . Every price and feature below comes from each company's own "
                     "website, linked at the bottom, as checked in October 2026. Where something isn't published, we say so. Software prices change often, so confirm before you "
                     'sign.'),
                    ('p',
                     'ServiceTitan and Housecall Pro are both field service software. They run the job: booking, dispatch, estimates, invoices and payments. The big differences for '
                     'an HVAC owner are how you pay, how much of the system you need, and which marketing pieces come in the box.')]),
                  ('At a glance',
                   [('table',
                     [['', 'ServiceTitan', 'Housecall Pro'],
                      ['Published price', 'Not published', 'Yes, on its pricing page'],
                      ["How it's priced", 'Per technician, by quote', 'By plan, with users included'],
                      ['Plans', 'Starter, Essentials, The Works', 'Basic, Essentials, MAX'],
                      ['Online booking', 'Scheduling Pro, a separate Pro product', 'Listed in Basic'],
                      ['Review requests', 'Marketing Pro Reputation, a separate Pro product', 'Review management listed in Basic'],
                      ['Email and mail campaigns', 'Marketing Pro, a separate Pro product', 'Marketing Center: email, text, postcards'],
                      ['Free trial', 'Not published', '14 days, no credit card']])]),
                  ('Pricing model',
                   [('p', '<b>Housecall Pro</b> lists three plans on its pricing page:'),
                    ('ul',
                     ['<b>Basic:</b> $59 a month billed annually, or $79 billed monthly. 1 user.',
                      '<b>Essentials:</b> $149 a month billed annually, or $189 billed monthly. 5 users.',
                      '<b>MAX:</b> $299 a month billed annually, or $329 billed monthly. 8 users, with extra users at $35 a month each.']),
                    ('p',
                     'Some Housecall Pro trade pages show higher numbers than the main pricing page, so check the pricing page itself and ask what your quote includes. Its voice '
                     'add-on, with call tracking, is sold separately and priced on request.'),
                    ('p',
                     "<b>ServiceTitan</b> doesn't publish prices. Its pricing page says pricing is per technician and asks you to request pricing. Third-party sites post estimates, "
                     "but they don't agree with each other, so we don't repeat them here. The Pro products, such as Scheduling Pro and Marketing Pro, are sold on top of the core "
                     'package.'),
                    ('p',
                     'What that means for you: with Housecall Pro you can work out the software cost before a call. With ServiceTitan, your bill moves with your tech count and the '
                     'Pro products you add. Ask for a written quote with every line on it, plus any setup or implementation fee and the contract term.')]),
                  ('Who each fits',
                   [('p',
                     "Neither vendor sets a minimum size on its public pages. ServiceTitan's pricing page says its plans fit businesses at any size. But the way each one prices "
                     'points to a natural fit.'),
                    ('ul',
                     ['<b>Housecall Pro fits</b> owner-run shops and small to mid-size teams that want a known monthly price, a quick start and booking and reviews in the lowest '
                      "plan. The user counts in each plan (1, 5 and 8) tell you who it's built around.",
                      "<b>ServiceTitan fits</b> shops with enough techs and office staff to use the deeper parts: payroll, advanced reporting and custom reports. ServiceTitan's help "
                      "center says custom reports are only on The Works package. If you'll use those, per-technician pricing can make sense. If you won't, you may pay for depth you "
                      "don't need."]),
                    ('p',
                     "A simple test: list the five things you'd use every week. If they're booking, dispatch, invoices, payments and review asks, both tools do that. If your list "
                     'includes payroll, commissions and custom reports, look harder at ServiceTitan.')]),
                  ('Booking',
                   [('p',
                     '<b>Housecall Pro</b> lists online booking in its Basic plan. Its pages say customers can book through Google, your website or a shared link, and the booking '
                     'page can show services, prices and service areas.'),
                    ('p',
                     '<b>ServiceTitan</b> handles online booking with Scheduling Pro. It lets customers book online or by text based on real-time availability, and can take payment '
                     'and sign up members at booking. Call booking for your CSRs is part of the core Starter package.'),
                    ('note',
                     'Online booking doesn\'t help the caller who rings out. If you miss calls after hours or on busy days, look at <a href="{u:missed-call-text-back}">missed-call '
                     'text-back</a> as well. Our <a href="{u:tools/missed-call-cost-calculator}">missed call cost calculator</a> shows what those calls may be worth.')]),
                  ('Marketing',
                   [('p',
                     "<b>Housecall Pro's</b> Marketing Center puts email, text and postcard campaigns in one place. Its help center says campaigns can be one-time blasts or triggered "
                     'flows, with triggers such as Job Completed and Estimate Declined. Email campaigns need customer consent.'),
                    ('p',
                     "<b>ServiceTitan's</b> Marketing Pro covers email, direct mail and campaigns tied to your customer and job data. It's a separate Pro product, so price it with "
                     'your quote.'),
                    ('p',
                     "Both work from the customers already in your system. That's useful for tune-up reminders and past customers. Neither one is a full lead engine on its own: they "
                     'don\'t build your website, rank you on Google or run your ads. For how those pieces fit together, see our guide to <a href="{u:hvac-marketing}">HVAC '
                     'marketing</a>.')]),
                  ('Reviews',
                   [('p',
                     '<b>Housecall Pro</b> lists review management in Basic. Its pages say review requests go out by text or email after each job, and you can track and reply to '
                     'reviews from a dashboard.'),
                    ('p',
                     "<b>ServiceTitan's</b> Marketing Pro Reputation sends review requests by text or email after a job, pulls Google, Facebook and Yelp reviews into one feed, and "
                     'links each review to the customer, job and tech. It also says it keeps business listings consistent across 60+ sites.'),
                    ('p',
                     'With either tool, the ask only works if it goes out every time, soon after the job. Our guide to <a href="{u:guide-google-reviews-hvac}">Google reviews for '
                     'HVAC</a> covers timing and wording, and the <a href="{u:tools/google-review-gap-calculator}">review gap calculator</a> shows how long it may take to catch the '
                     'top shop near you.')]),
                  ('Questions to ask in either demo',
                   [('p', 'Sales demos show the best parts. These questions get you to the parts that decide your monthly bill and your daily work.'),
                    ('ol',
                     ["<b>What's the total monthly cost for my team?</b> Give them your tech count and office count, and ask for every add-on on paper.",
                      "<b>Is there a setup or onboarding fee?</b> And how long until we're live?",
                      "<b>What's the contract term?</b> Can we go month to month, and what does it cost to leave early?",
                      "<b>Which plan has online booking and review requests?</b> Ask them to show it in the plan you'd buy, not the top one.",
                      '<b>What happens to a call we miss?</b> Ask whether the caller gets a text back, and whether that costs extra.',
                      '<b>Can we export our customers and job history if we leave?</b> Your customer list is yours. Make sure you can take it with you.']),
                    ('p',
                     "Write the answers down side by side. The cheaper tool on paper isn't always cheaper once add-ons are in, and the bigger tool isn't always better if your team "
                     "won't use half of it.")]),
                  ('Where we fit in',
                   [('p',
                     'We don\'t replace either one. A shop can keep its field software for the job and use our <a href="{u:hq-command-center}">HQ Command Center</a>, the CRM we set '
                     'up for clients, built on HighLevel, for the leads: <a href="{u:missed-call-text-back}">missed calls</a>, <a href="{u:estimate-follow-up}">estimate follow-up</a> '
                     'and <a href="{u:review-requests}">review requests</a>. If you already send review asks from ServiceTitan or Housecall Pro, we\'d set things up so customers '
                     "don't get two."),
                    ('p', 'For a wider look at five tools, read <a href="{u:post-best-crm-for-hvac}">the best CRM for HVAC companies</a>. Or see our <a href="{u:plans}">plans</a>.'),
                    ('cta',)])],
     'faq': [('Is Housecall Pro cheaper than ServiceTitan?',
              "We can't say for sure, because ServiceTitan doesn't publish prices. Housecall Pro lists plans from $59 a month billed annually. Get a written ServiceTitan quote for "
              'your tech count to compare.'),
             ('Does ServiceTitan include online booking?',
              'Online booking is Scheduling Pro, which ServiceTitan lists as a separate Pro product. Call booking for your office staff is in the core Starter package.'),
             ('Can I switch from Housecall Pro to ServiceTitan later?',
              'You can. Ask each vendor what data they can import, what setup costs, and how long it takes before you commit.'),
             ('Do either of them text back missed calls?',
              'Not as a core feature on the pages we checked. Housecall Pro sells a voice add-on separately. Ask each vendor directly, or use a marketing CRM for missed-call '
              'text-back.')],
     'sources': [('ServiceTitan: Pricing', 'https://www.servicetitan.com/pricing'),
                 ('ServiceTitan: Scheduling Pro', 'https://www.servicetitan.com/features/pro/scheduling'),
                 ('ServiceTitan: Marketing Pro Reputation', 'https://www.servicetitan.com/features/pro/marketing/reputation'),
                 ('ServiceTitan: Pro products', 'https://www.servicetitan.com/features/pro'),
                 ('Housecall Pro: Pricing and plans', 'https://www.housecallpro.com/pricing/'),
                 ('Housecall Pro: LLM info page (plans and users)', 'https://www.housecallpro.com/llm-info/'),
                 ('Housecall Pro Help: Marketing Center overview', 'https://help.housecallpro.com/en/articles/11057071-marketing-center-overview'),
                 ('Housecall Pro Help: Campaigns step-by-step guide', 'https://help.housecallpro.com/en/articles/8832769-campaigns-step-by-step-guide'),
                 ('Housecall Pro: Automated marketing', 'https://www.housecallpro.com/features/automated-marketing/')],
     'related': ['best-crm-for-hvac', 'google-reviews-hvac', 'missed-call-text-back-hvac', 'hvac-marketing-cost']},
    {'slug': 'hvac-marketing-ideas',
     'title': 'HVAC marketing ideas that book jobs: 21 ideas sorted by cost',
     'short': 'HVAC marketing ideas',
     'desc': '21 HVAC marketing ideas that book jobs, sorted into free, low cost and paid. Each one is short, practical and fair to your customers.',
     'read': 8,
     'date': '2026-10-15',
     'takeaways': ['Start with the free ideas: your Google profile, reviews and past customers cost time, not money.',
                   "Google says you can't pay for a better map ranking, so the free work on your profile matters.",
                   "Ask every customer for a review. Google's rules ban picking only the happy ones.",
                   'Add paid ads once the phone is answered every time and you can track which calls book.'],
     'sections': [('How to use this list',
                   [('p',
                     'Most HVAC marketing lists are long and vague. This one is short and sorted by what it costs. The free ideas cost you time. The low cost ideas need a tool or a '
                     'small spend. The paid ideas need an ad budget.'),
                    ('p',
                     'Do them roughly in order. Paid ads send more calls, but if calls go to voicemail or quotes never get a follow-up, more calls just means more waste. Fix the '
                     'leaks first, then turn up the volume.'),
                    ('note',
                     "We left out cold calling and cold texting on purpose. Texas SB 140 took effect on September 1, 2025 and brings marketing texts under the state's telemarketing "
                     'law. Market to people who asked to hear from you.')]),
                  ('Free ideas (cost: your time)',
                   [('ul',
                     ['<b>1. Fill in every part of your Google Business Profile.</b> Google says local results are based mainly on relevance, distance and prominence, and that '
                      'complete, detailed info helps you match searches. Set your category, services, hours and photos. See our <a href="{u:google-business-profile}">Google Business '
                      'Profile</a> service.',
                      '<b>2. Set a service area instead of showing a home address.</b> Google lets a business that travels to customers hide its address and show only the area it '
                      'serves. Most HVAC shops fit that description.',
                      '<b>3. Post offers and updates on your profile.</b> Google Business Profile has Updates, Offers and Events posts. Google archives posts older than 6 months '
                      'unless you set a date range, so post a fresh tune-up offer each season.',
                      "<b>4. Ask every customer for a Google review.</b> Your profile has a Get more reviews option that gives you a link or a QR code. Google's policy bans asking "
                      'only happy customers, so ask everyone. Our <a href="{u:tools/google-review-gap-calculator}">review gap calculator</a> shows how long it takes to catch the top '
                      'shop.',
                      '<b>5. Reply to every review, good or bad.</b> A short, calm reply shows the next homeowner that a real person runs the shop. Read our <a '
                      'href="{u:guide-google-reviews-hvac}">Google reviews guide</a> for how to reply.',
                      '<b>6. Call back every missed call the same day.</b> A missed call is often a job that went to the next shop. Run your own numbers in the <a '
                      'href="{u:tools/missed-call-cost-calculator}">missed call cost calculator</a>.',
                      '<b>7. Remind past customers about tune-ups before the season.</b> ENERGY STAR suggests a cooling check in spring and a heating check in fall, before '
                      'contractors get busy. Email or call past customers who agreed to hear from you.',
                      "<b>8. Ask every caller how they found you.</b> Write it on the job. After a month you'll know which channel books jobs and which just rings."])]),
                  ('Low cost ideas (cost: a tool or a small spend)',
                   [('ul',
                     ["<b>9. Text back missed calls automatically.</b> When you can't pick up, the caller gets a text within 10 seconds and can reply with the problem. They called "
                      'you first, so you\'re answering them, not cold texting. See <a href="{u:missed-call-text-back}">missed-call text-back</a>.',
                      '<b>10. Send a review request after every job.</b> Automate the ask so it goes out to every customer, every time, right after the work is done. See <a '
                      'href="{u:review-requests}">review requests</a>.',
                      '<b>11. Follow up on every open quote.</b> A replacement quote that never gets a second touch is easy to lose. Use the <a '
                      'href="{u:tools/hvac-estimate-follow-up-calculator}">estimate follow-up calculator</a> to see what one extra close is worth, then set up <a '
                      'href="{u:estimate-follow-up}">estimate follow-up</a>.',
                      '<b>12. Sell a maintenance plan.</b> Plan members come back twice a year, and those visits often turn into repairs and replacements. Price yours with the <a '
                      'href="{u:tools/hvac-maintenance-plan-calculator}">maintenance plan calculator</a>.',
                      '<b>13. Put your review QR code on invoices and leave-behinds.</b> Google suggests places like receipts and thank you emails. Note that Google says the reviews '
                      'QR code can only be made on a computer browser.',
                      "<b>14. Build a page for each service and each town.</b> Google's own SEO guide says useful, people-first content is likely to matter more than any other tip in "
                      'it. One clear page per service and town beats one page that lists everything. See <a href="{u:website}">HVAC websites</a> and <a href="{u:local-seo}">local '
                      'SEO</a>.',
                      '<b>15. Answer website visitors after hours.</b> Chat can take the address and the problem at night so you can call back first thing. See <a '
                      'href="{u:ai-web-chat}">AI web chat</a> and the <a href="{u:tools/after-hours-call-calculator}">after-hours call calculator</a>.',
                      '<b>16. Thank customers who send referrals.</b> A thank-you card or a credit on their next tune-up for a referral is fine. Just never offer anything in exchange '
                      'for a review, which Google bans.'])]),
                  ('Paid ideas (cost: an ad budget)',
                   [('ul',
                     ["<b>17. Run Local Services Ads.</b> Google charges per valid lead, not per click, and says leads it finds invalid aren't charged. Estimate a budget with the <a "
                      'href="{u:tools/lsa-cost-calculator}">LSA cost calculator</a> and see <a href="{u:local-services-ads}">Local Services Ads</a>.',
                      '<b>18. Run Google Ads with a call button.</b> You pay per click. Google says a click on a call asset on mobile costs the same as a click on the headline. Plan '
                      'spend with the <a href="{u:tools/google-ads-budget-calculator-hvac}">Google Ads budget calculator</a> and see <a href="{u:google-ads}">Google Ads</a>.',
                      "<b>19. Remind past website visitors on Facebook before the season.</b> Meta's Pixel lets you build a custom audience of people who visited your site. A tune-up "
                      'reminder to them works better than a cold ad. See <a href="{u:facebook-ads}">Facebook ads</a>.',
                      '<b>20. Plan spring and fall campaigns ahead of time.</b> Line up your tune-up offer, profile post, email and ads before the first hot or cold week, not during '
                      'it. See <a href="{u:seasonal-campaigns}">seasonal campaigns</a>.',
                      '<b>21. Answer every call, even at peak.</b> On the busiest days the phone rings while every tech and CSR is busy. An AI answering line can book or take a '
                      'message so no caller hits voicemail. See <a href="{u:ai-phone-answering}">AI phone answering</a>.'])]),
                  ('What not to do',
                   [('p', 'Some "ideas" you\'ll see online can cost you your profile or worse. Skip these:'),
                    ('ul',
                     ["<b>Review gating.</b> Sending only happy customers to Google, and the rest to a private form, is selective asking. Google's policy lists it as fake engagement "
                      'and removes those reviews.',
                      "<b>Paying for reviews.</b> Google bans offering discounts or gifts for reviews. The FTC's rule on fake reviews, in effect since October 21, 2024, bans buying "
                      'positive or negative reviews and fake reviews outright.',
                      '<b>Cold texting and cold calling lists.</b> In Texas, SB 140 puts marketing texts under the telemarketing law. Stick to people who reached out to you or agreed '
                      'to hear from you.'])]),
                  ('Where to start this week',
                   [('ol',
                     ['Fix your Google profile (ideas 1 to 3).',
                      'Start asking every customer for a review (ideas 4 and 10).',
                      'Stop losing calls (ideas 6, 9 and 21).',
                      'Then add one paid channel and track booked jobs from it (ideas 17 or 18).']),
                    ('p',
                     'Want to see how your shop stacks up first? Get a free <a href="{u:report-card}">report card</a>, check what a plan costs on our <a href="{u:plans}">plans '
                     'page</a>, or read the full guide to <a href="{u:hvac-marketing}">marketing for HVAC companies</a>.'),
                    ('cta',)])],
     'faq': [("What's the cheapest HVAC marketing that works?",
              "Your Google Business Profile, reviews and past customers. They cost time, not ad money, and Google says you can't pay for a better map ranking anyway."),
             ('Can I text past customers about a tune-up?',
              "Only people who agreed to hear from you. In Texas, SB 140 brings marketing texts under the state's telemarketing law, so don't text lists of people who never asked."),
             ('Can I ask only happy customers for reviews?', "No. Google's policy bans selectively asking for positive reviews. Ask every customer, the same way, every time."),
             ('When should I start paid ads?', "Once every call gets answered or called back and you can tell which calls became jobs. Otherwise you can't tell if the ads pay.")],
     'sources': [('Google Business Profile Help: Tips to improve your local ranking', 'https://support.google.com/business/answer/7091'),
                 ('Google Business Profile Help: Manage your service area', 'https://support.google.com/business/answer/10514137'),
                 ('Google Business Profile Help: About posts', 'https://support.google.com/business/answer/7662907'),
                 ('Google Business Profile Help: Create a link or QR code to request reviews', 'https://support.google.com/business/answer/16816815'),
                 ('Google Business Profile Help: Tips to get more reviews', 'https://support.google.com/business/answer/3474122'),
                 ('Google Maps user contributed content policy: Prohibited and restricted content', 'https://support.google.com/contributionpolicy/answer/7400114'),
                 ('FTC: Final rule banning fake reviews and testimonials (Aug 2024)',
                  'https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials'),
                 ('ENERGY STAR: Heating and cooling maintenance checklist', 'https://www.energystar.gov/saveathome/heating-cooling/maintenance-checklist'),
                 ('Google Search Central: SEO Starter Guide', 'https://developers.google.com/search/docs/fundamentals/seo-starter-guide'),
                 ('Google Local Services Help: How leads work', 'https://support.google.com/adwords/answer/7195435'),
                 ('Google Ads Help: About call assets', 'https://support.google.com/google-ads/answer/2453991'),
                 ('Meta for Developers: Website custom audiences', 'https://developers.facebook.com/docs/marketing-api/audiences/guides/website-custom-audiences'),
                 ('Texas Legislature: SB 140 (89th Legislature, 2025)', 'https://capitol.texas.gov/BillLookup/History.aspx?LegSess=89R&Bill=SB140'),
                 ('Paul Hastings: Texas SB 140 broadens state telemarketing rules to marketing texts',
                  'https://www.paulhastings.com/insights/ph-privacy/marketing-texts-in-texas-sb-140-broadens-state-telemarketing-regulations')],
     'related': ['how-to-get-more-hvac-leads', 'get-more-google-reviews-hvac', 'missed-call-text-back-hvac', 'hvac-marketing-cost']},
    {'slug': 'how-to-get-more-hvac-leads',
     'title': 'How to get more HVAC leads: every channel compared',
     'short': 'Get more HVAC leads',
     'desc': 'Ten ways to get more HVAC leads, compared by speed, how you pay and who owns the lead. From your Google profile to Angi, Thumbtack and missed calls.',
     'read': 8,
     'date': '2026-10-15',
     'takeaways': ['Fix the leaks first: missed calls and unasked reviews cost leads you already earned.',
                   'Google Ads charge per click, Local Services Ads per valid lead, and Meta by impressions, clicks or actions.',
                   'Lead sites sell you a contact, but the homeowner may also be talking to other pros.',
                   'Judge every channel by cost per booked job and by whether you keep the customer.'],
     'sections': [('Three questions for every channel',
                   [('p', 'There are only so many ways for a homeowner to find an HVAC company. Each one is worth asking three questions about:'),
                    ('ul',
                     ['<b>How fast does it work?</b> Some channels can ring the phone this week. Others take months to build.',
                      '<b>How do you pay?</b> Per click, per lead, a flat fee, or just your time.',
                      '<b>Who owns the lead?</b> Does the customer end up on your list, or does the platform keep the relationship?']),
                    ('p',
                     "We don't quote cost-per-lead numbers in this post. Prices change by town, season and job type, and the platforms set them. Instead we link to how each platform "
                     'says it charges. Use our <a href="{u:tools/hvac-cost-per-lead-calculator}">cost per lead calculator</a> with your own numbers.')]),
                  ('Every channel side by side',
                   [('table',
                     [['Channel', 'Speed', 'Cost model', 'Who owns the lead'],
                      ['Google Business Profile', 'Builds over weeks and months', 'Free (your time)', 'You'],
                      ['SEO and your website', 'Slow, builds over months', 'Your time or a flat monthly fee', 'You'],
                      ['Google Ads', 'Fast, once ads go live', 'Per click', 'You'],
                      ['Local Services Ads', "Fast, once you're approved", 'Per valid lead', 'You, once they contact you'],
                      ['Facebook ads', 'Fast for reminders, weak for urgent repairs', 'Impressions, clicks or actions you choose', 'You'],
                      ['Referrals', 'Slow, steady', 'Free, or a thank-you', 'You'],
                      ['Review requests', 'Builds with every job', 'Free, or a tool', 'You'],
                      ['Past customers', 'Fast', 'Free, or a tool', 'You'],
                      ['Lead sites (Angi, Thumbtack)', 'Fast', 'Per lead (read the terms)', 'Shared: other pros may get the same request'],
                      ['Missed-call recovery', 'Same day', 'A tool or your time', 'You']])]),
                  ('Channels you own',
                   [('p',
                     "<b>Google Business Profile.</b> This is the map listing. Google says local results are based mainly on relevance, distance and prominence, and that there's no "
                     'way to request or pay for a better local ranking. Prominence includes how many reviews you have and how many sites link to you. See <a '
                     'href="{u:google-business-profile}">Google Business Profile</a> and our <a href="{u:guide-google-map-pack-hvac}">map pack guide</a>.'),
                    ('p',
                     "<b>SEO and your website.</b> Your site is where Google Ads, Local Services Ads and your profile all send people. Google's SEO guide says helpful, people-first "
                     'content is likely to matter more than any other tip in it. Build one clear page per service and town. See <a href="{u:local-seo}">local SEO</a> and <a '
                     'href="{u:website}">websites</a>, and check the payback with the <a href="{u:tools/hvac-seo-roi-calculator}">SEO ROI calculator</a>.'),
                    ('p',
                     '<b>Referrals.</b> Happy customers tell neighbors. Make it easy: a card with your number, a thank-you when a referral books. Never tie a reward to a review.'),
                    ('p',
                     '<b>Review requests.</b> Reviews help you rank and help callers pick you. Google gives you a review link and QR code under Get more reviews. Its policy bans '
                     'asking only happy customers and bans incentives for reviews. Ask everyone with <a href="{u:review-requests}">review requests</a>.'),
                    ('p',
                     '<b>Past customers.</b> The people who already paid you are the easiest to book again. ENERGY STAR suggests a cooling check in spring and a heating check in '
                     'fall. Remind customers who agreed to hear from you, and offer a <a href="{u:tools/hvac-maintenance-plan-calculator}">maintenance plan</a>. Our <a '
                     'href="{u:seasonal-campaigns}">seasonal campaigns</a> handle the timing.')]),
                  ('Channels you pay for',
                   [('p',
                     '<b>Google Ads.</b> You pay per click, and you pick the keywords, the ad and the landing page. Google says a click on a call asset on mobile costs the same as a '
                     'click on the headline, and call reporting can count calls as conversions using Google forwarding numbers. See <a href="{u:google-ads}">Google Ads</a> and the <a '
                     'href="{u:tools/google-ads-budget-calculator-hvac}">Google Ads budget calculator</a>.'),
                    ('p',
                     "<b>Local Services Ads.</b> Google charges per valid lead, not per click. It says leads it judges invalid at first contact aren't charged, and that message leads "
                     'cost half of a phone lead in the US and Canada. You set an average weekly budget. See <a href="{u:local-services-ads}">Local Services Ads</a> and the <a '
                     'href="{u:tools/lsa-cost-calculator}">LSA cost calculator</a>.'),
                    ('p',
                     "<b>Facebook ads.</b> Meta's docs say the billing event can be impressions, clicks or other actions. Facebook is weak for an urgent no-heat call, because people "
                     "search Google for that. It's better for tune-up reminders to people who visited your site, using a Pixel custom audience. See <a "
                     'href="{u:facebook-ads}">Facebook ads</a>.'),
                    ('p',
                     "<b>Lead sites like Angi and Thumbtack.</b> These sites sell you the contact details of a homeowner who asked for help. Thumbtack says there's no charge to join "
                     'and no membership fee, and that you control your budget for leads. Before you buy from any lead site, read how a lead is priced and credited, and ask whether '
                     'other pros get the same request. In 2023 the FTC ordered HomeAdvisor, a company affiliated with Angi, to pay up to $7.2 million over claims about the leads it '
                     'sold to service providers.'),
                    ('note',
                     'Lead sites can fill a slow week, but the customer found the site, not you. Our post on <a href="{u:post-hvac-lead-generation-bought-vs-owned}">bought vs owned '
                     'leads</a> covers what to ask any lead seller.')]),
                  ('Missed-call recovery: the lead you already paid for',
                   [('p',
                     "Every channel above ends with a phone ringing. If no one answers, you paid for a lead and got nothing. This matters more for Local Services Ads now. Google's "
                     'lead charging page says that from October 1, 2026, a missed call during business hours can be charged if the caller stays on the line for more than 20 seconds.'),
                    ('p', 'Three fixes, in order of cost:'),
                    ('ol',
                     ['Call back every missed call the same day.',
                      'Text back missed calls automatically with <a href="{u:missed-call-text-back}">missed-call text-back</a>. The caller reached out first, so this isn\'t cold '
                      'texting.',
                      'Have every call answered with <a href="{u:ai-phone-answering}">AI phone answering</a>, and catch site visitors at night with <a href="{u:ai-web-chat}">AI web '
                      'chat</a>.']),
                    ('p', 'See what it\'s costing you with the <a href="{u:tools/missed-call-cost-calculator}">missed call cost calculator</a>.')]),
                  ('Which order to do it in',
                   [('p',
                     "Before you add any channel, decide how you'll measure it. Ask every caller how they found you, and give each paid channel its own tracked number where the "
                     'platform allows it. Then compare channels by booked jobs and revenue, not by clicks or raw leads. A cheap lead that never books costs more than a pricey one '
                     'that does.'),
                    ('ol',
                     ['Stop the leaks: answer or call back every call, and follow up on every quote with <a href="{u:estimate-follow-up}">estimate follow-up</a>.',
                      'Fix your Google profile and ask every customer for a review.',
                      'Remind past customers before each season.',
                      'Add Local Services Ads or Google Ads for fast calls, and track booked jobs from each.',
                      'Build your website and SEO so the calls keep coming when ads pause.',
                      'Use lead sites only to fill gaps, and only after reading the terms.']),
                    ('p',
                     'Want it all in one place? See <a href="{u:hvac-lead-generation}">HVAC lead generation</a>, the <a href="{u:hq-command-center}">HQ Command Center</a> or our <a '
                     'href="{u:plans}">plans</a>. Or start with a free <a href="{u:report-card}">report card</a> to see who\'s getting the calls near you.'),
                    ('cta',)])],
     'faq': [("What's the fastest way to get more HVAC leads?",
              'Stop losing the ones you have: answer or text back every missed call and follow up on quotes. For new calls, Google Ads and Local Services Ads can start once they go '
              'live.'),
             ('Are Angi and Thumbtack leads worth it?',
              'It depends on your close rate and the terms. Read how a lead is priced and credited, ask if other pros get the same request, and compare cost per booked job with your '
              'other channels.'),
             ('How do Local Services Ads charge?',
              "Per valid lead, not per click. Google says invalid leads aren't charged and message leads cost half of a phone lead in the US and Canada."),
             ('Can I pay to rank higher on Google Maps?',
              "No. Google says there's no way to request or pay for a better local ranking. Your profile, reviews and website are what move it.")],
     'sources': [('Google Business Profile Help: Tips to improve your local ranking', 'https://support.google.com/business/answer/7091'),
                 ('Google Search Central: SEO Starter Guide', 'https://developers.google.com/search/docs/fundamentals/seo-starter-guide'),
                 ('Google Business Profile Help: Create a link or QR code to request reviews', 'https://support.google.com/business/answer/16816815'),
                 ('Google Maps user contributed content policy: Prohibited and restricted content', 'https://support.google.com/contributionpolicy/answer/7400114'),
                 ('ENERGY STAR: Heating and cooling maintenance checklist', 'https://www.energystar.gov/saveathome/heating-cooling/maintenance-checklist'),
                 ('Google Ads Help: About call assets', 'https://support.google.com/google-ads/answer/2453991'),
                 ('Google Local Services Help: How leads work', 'https://support.google.com/adwords/answer/7195435'),
                 ('Meta for Developers: Billing events', 'https://developers.facebook.com/docs/marketing-api/bidding/overview/billing-events'),
                 ('Meta for Developers: Website custom audiences', 'https://developers.facebook.com/docs/marketing-api/audiences/guides/website-custom-audiences'),
                 ('Thumbtack: How Thumbtack works for pros', 'https://www.thumbtack.com/postservice'),
                 ('FTC: HomeAdvisor matter', 'https://www.ftc.gov/legal-library/browse/cases-proceedings/1923106-homeadvisor-matter')],
     'related': ['hvac-marketing-ideas', 'hvac-lead-generation-bought-vs-owned', 'google-ads-vs-local-services-ads-hvac', 'google-map-pack-hvac']},
    {'slug': 'hvac-advertising',
     'title': 'HVAC advertising: where to spend first, online and offline',
     'short': 'HVAC advertising',
     'desc': 'Google Ads, Local Services Ads, Facebook, Nextdoor, YouTube, signs, truck wraps, EDDM and radio: how each charges and how to track it.',
     'read': 7,
     'date': '2026-10-15',
     'takeaways': ['Spend first where people are already looking for a repair: Google search ads and Local Services Ads.',
                   'Facebook, Instagram, Nextdoor and YouTube reach people before they need you. They suit tune-ups and maintenance plans.',
                   'Yard signs, truck wraps, mailers and radio can work, but only count if you give each one its own phone number or QR code.',
                   'Each channel charges a different way: per click, per lead, per 1,000 views, per view, per piece or per spot.'],
     'sections': [('Start with where the calls already are',
                   [('p',
                     "Most HVAC calls start with a problem. The AC quits. The furnace won't light. The homeowner grabs a phone and searches. So the first money should go where people "
                     "are already searching, not where you'd most like to be seen."),
                    ('p',
                     "That's why this list starts with Google. The other channels come after, in rough order of how close each one is to a call. We won't give you cost or return "
                     "numbers for any of them. They change from town to town and month to month. We'll show how each one charges, what it's good for, and how to tell if it's "
                     'working.'),
                    ('table',
                     [['Channel', 'How it charges', 'Best for'],
                      ['Google search ads', 'Per click', 'People searching for a repair now'],
                      ['Local Services Ads', 'Per valid lead', 'Calls from the top of Google'],
                      ['Facebook and Instagram', 'Per 1,000 views or per click, by auction', 'Tune-ups, plans, retargeting'],
                      ['Nextdoor', 'Per 1,000 views or per click, by bid', 'Being seen in set neighborhoods'],
                      ['YouTube', 'Per view (30 seconds or a click)', 'Name recognition in your area'],
                      ['EDDM mailers', 'Postage per piece, plus printing', 'Whole mail routes near your jobs'],
                      ['Yard signs and truck wraps', 'One-time cost', 'Being seen where you already work'],
                      ['Radio', 'Per spot, set by the station', 'Name recognition over months']])]),
                  ('1. Google search ads',
                   [('p',
                     "With Google Ads you pay per click. Google says your actual cost per click is the final amount you're charged, and it's often less than your maximum bid. You pay "
                     'only what it takes to beat the ad just below yours. If 500 people see your ad and 23 click, you pay for those 23 clicks.'),
                    ('p',
                     'This is the channel closest to a booked job, because the person typed "AC repair near me" a second ago. It\'s also where you control the most: which searches, '
                     'which towns, which hours.'),
                    ('p',
                     "<b>How to track it:</b> turn on call reporting. Google shows a Google forwarding number in your ads and records each call's time, length and campaign, then "
                     'sends the call to your real line. Google says not to print or reuse that number anywhere else, because it can change. Then count calls as conversions, with a '
                     'minimum call length you choose.'),
                    ('p',
                     'How much to spend is its own question. We cover it in <a href="{u:post-how-much-to-spend-on-google-ads-hvac}">how much to spend on Google Ads</a>, and our <a '
                     'href="{u:tools/google-ads-budget-calculator-hvac}">Google Ads budget calculator</a> runs the math with your numbers.')]),
                  ('2. Local Services Ads',
                   [('p',
                     'Local Services Ads are the listings with the Google Verified badge at the very top of the page. You pay per valid lead (a call, message or booking), not per '
                     'click. Your business has to pass Google\'s screening first. We explain the charges in <a href="{u:post-google-local-services-ads-hvac}">our Local Services Ads '
                     'guide</a> and the badge in <a href="{u:post-google-guaranteed-hvac}">Google Guaranteed and Google Verified for HVAC</a>.'),
                    ('p',
                     "One thing is new. Google says it's moving Local Services Ads into Performance Max campaigns with pay-per-lead goals. The first phase started in August 2026 for "
                     'select US home service providers, and Google names HVAC as one of them. You still pay for valid leads, not clicks. Phone call leads are required. Keywords '
                     "aren't used, and manual bids are no longer supported."),
                    ('p',
                     "<b>How to track it:</b> leads show in your account. In the new setup Google says they're on the Leads page under Conversions in Google Ads. Google also says "
                     "your old Local Services reports don't carry over, so save copies before you move."),
                    ('p',
                     'Not sure which of the two Google channels comes first? Read <a href="{u:post-google-ads-vs-local-services-ads-hvac}">Google Ads vs Local Services Ads</a>.')]),
                  ('3. Facebook and Instagram',
                   [('p',
                     "Meta runs one ad system for both apps. Ads compete in an auction, and Meta says you're only charged the bid needed to win. Depending on your goal, you pay for "
                     "impressions (shown as cost per 1,000 views) or for clicks. Meta says there's no minimum budget, and you can set a daily budget or one total budget for the whole "
                     'run.'),
                    ('p',
                     "People on Facebook aren't searching for a repair. They're scrolling. So these ads work best before the season: a fall furnace tune-up, a spring AC check, a "
                     'maintenance plan, or a reminder to people who already visited your site. We go deeper in <a href="{u:post-facebook-ads-for-hvac}">Facebook ads for HVAC</a>.'),
                    ('p', '<b>How to track it:</b> send each ad to a page with its own tracked link (see the tracking section below), and use a call tracking number on that page.')]),
                  ('4. Nextdoor',
                   [('p',
                     "Nextdoor is built around neighborhoods, which fits a business with a service area. Nextdoor's help pages describe bids by cost per 1,000 impressions (CPM) or by "
                     'click (CPC). With a fixed CPM you pay a set amount for every 1,000 times your ad is shown. Nextdoor offers pay-as-you-go billing against a daily budget, and a '
                     'monthly subscription that charges your daily budget times 30 up front.'),
                    ('p',
                     "<b>Good for:</b> being seen in the exact neighborhoods you want more work in, with a seasonal offer. Like Facebook, it's not where people search for an "
                     'emergency repair.'),
                    ('p', '<b>How to track it:</b> a tracked link and a separate call tracking number, the same as Facebook.')]),
                  ('5. YouTube',
                   [('p',
                     'YouTube ads are bought in Google Ads. For skippable ads using cost-per-view bidding, Google says you pay when someone watches 30 seconds (or the whole ad, if '
                     "it's shorter) or interacts with it, whichever comes first. If they skip early, you don't pay for that view. Google says the average cost per view moves with ad "
                     'length, quality, targeting and the auction.'),
                    ('p',
                     "<b>Good for:</b> putting your face and your trucks in front of homeowners in your area, so your name feels familiar when they do search. It's a slower, "
                     "name-building channel. Don't expect calls the first week."),
                    ('p',
                     '<b>How to track it:</b> watch for more searches of your company name and more calls on your other tracked numbers. Put a tracked link or a unique number in the '
                     'video itself.')]),
                  ('6. Direct mail with EDDM',
                   [('p',
                     'Every Door Direct Mail (EDDM) is a USPS service. You pick mail routes on a USPS map instead of buying a mailing list. Pieces are addressed to "Postal Customer". '
                     "With EDDM Retail you don't need a postage permit, and USPS says there are no annual fees."),
                    ('p',
                     'USPS lists EDDM Retail flats at $0.26 per piece for postage, before printing. USPS rules say an EDDM Retail mailing has to be at least 200 pieces and no more '
                     'than 5,000 pieces per ZIP Code per day. You have to take whole routes, not part of one, and drop them off at the Post Office that serves those routes.'),
                    ('p',
                     "<b>Good for:</b> the streets around jobs you've already done, a new subdivision, or a pre-season tune-up offer. The SBA also points to EDDM as a low-cost way to "
                     'reach a neighborhood.'),
                    ('p',
                     '<b>How to track it:</b> print a phone number used only on this mailer, and a QR code with a tracked link. Then every call or visit from that number or link came '
                     'from the mailer.')]),
                  ('7. Yard signs and truck wraps',
                   [('p',
                     'These cost money once, then keep working. The SBA lists vehicle wraps as a form of out-of-home advertising and says it can be a great addition if you serve '
                     'local customers. Every truck in a driveway and every yard sign after an install is seen by the neighbors.'),
                    ('ul',
                     ['<b>Yard signs:</b> ask the homeowner first, and check your city or HOA rules on signs.',
                      '<b>Truck wraps:</b> keep it readable from a car. Name, what you do, one phone number, one web address.',
                      '<b>Both:</b> the SBA suggests adding a web address or QR code so people can follow up on their phone.']),
                    ('p',
                     '<b>How to track it:</b> give the wraps one call tracking number and the yard signs another. Ask every new caller how they heard about you, and write it down.')]),
                  ('8. Radio',
                   [('p',
                     "Stations sell air time in spots, and the price depends on the station and the time of day. The SBA's radio guide splits the day into parts like morning drive "
                     "and afternoon drive, and says the station's sales staff can help match a time slot to the listeners you want. It suggests short ads run often, in the same slot "
                     'each day, and says to give radio three to six months before you judge it.'),
                    ('p', '<b>Good for:</b> shops that want their name known across a whole metro, with a budget that can wait months for results.'),
                    ('p', '<b>How to track it:</b> a phone number read only on the radio, and an easy web address that points to a tracked link.')]),
                  ('How to track every channel the same way',
                   [('p', "If you can't tell which channel made the phone ring, you can't tell where to put more money. Two simple tools cover almost everything:"),
                    ('ol',
                     ['<b>Call tracking numbers.</b> A separate number for each channel: mailer, wrap, yard sign, radio, Facebook, Nextdoor. Calls forward to your main line, and each '
                      "call is logged to the right source. For Google Ads, use Google's own call reporting.",
                      '<b>Tracked links and QR codes.</b> Google Analytics reads three tags on a link: utm_source, utm_medium and utm_campaign. For example: utm_source=eddm, '
                      'utm_medium=mail, utm_campaign=fall-tuneup. Google says to use lowercase and keep names the same each time, because "FallTuneup" and "fall-tuneup" count as two '
                      'campaigns. Turn that link into a QR code for print.']),
                    ('p',
                     'Then look at booked jobs, not just calls. Our <a href="{u:tools/hvac-cost-per-lead-calculator}">cost per lead calculator</a> shows what each lead and each '
                     'booked job costs by channel. And every channel works better if the phone gets answered. <a href="{u:missed-call-text-back}">Missed-call text-back</a> catches '
                     "the ones you can't pick up.")]),
                  ("Where we'd spend first",
                   [('ol',
                     ['Google search ads and Local Services Ads, with call tracking on from day one.',
                      'A full, current <a href="{u:google-business-profile}">Google Business Profile</a> and steady <a href="{u:review-requests}">review requests</a>, because both '
                      'Google channels show your rating.',
                      'Seasonal offers on Facebook, Instagram or Nextdoor, aimed at past customers and site visitors. See <a href="{u:seasonal-campaigns}">seasonal campaigns</a>.',
                      'Wraps and yard signs, since your trucks are out there anyway.',
                      'EDDM, YouTube and radio once the first steps are tracked and paying off.']),
                    ('p',
                     'Want a budget to start from? Try the <a href="{u:tools/hvac-marketing-budget-calculator}">marketing budget calculator</a>, or see our <a '
                     'href="{u:plans}">plans</a>.'),
                    ('cta',)])],
     'faq': [("What's the best advertising for an HVAC company?",
              'Start where people already search for a repair: Google search ads and Local Services Ads. Add other channels once you can track calls from each one.'),
             ('How do I know if a mailer or truck wrap is working?',
              'Give it its own call tracking number and a QR code with a tracked link. Calls and visits on those come only from that piece.'),
             ('Do I need a permit to send EDDM mailers?',
              'Not for EDDM Retail. USPS says no permit or annual fee is needed. You pay postage per piece and drop the mail off at the Post Office that serves your routes.'),
             ('How do YouTube ads charge?',
              'For skippable ads with cost-per-view bidding, Google charges when someone watches 30 seconds, the whole ad if shorter, or interacts with it.')],
     'sources': [('Google Ads Help: Actual cost-per-click', 'https://support.google.com/google-ads/answer/6297'),
                 ('Google Ads Help: Google forwarding number', 'https://support.google.com/google-ads/answer/2382961'),
                 ('Google Ads Help: About phone call conversion tracking', 'https://support.google.com/google-ads/answer/6100664'),
                 ('Google Ads Help: Local Services Ads transition to Performance Max campaigns with pay-per-lead goals', 'https://support.google.com/google-ads/answer/17213585'),
                 ('Google Ads Help: About pay-per-lead goals for Performance Max campaigns', 'https://support.google.com/google-ads/answer/17325249'),
                 ("Google Ads Help: About YouTube's cost-per-view (CPV) bidding", 'https://support.google.com/google-ads/answer/2472735'),
                 ('Meta: How much it costs to advertise on Facebook', 'https://www.facebook.com/business/help/201828586525529'),
                 ('Meta: Facebook and Instagram ads pricing overview', 'https://www.facebook.com/business/ads/pricing'),
                 ('Nextdoor Help: Setting your spend using budget and bids', 'https://help.nextdoor.com/s/article/Ads-Manager-Setting-Your-Spend-Using-Budget-Bids?language=en_US'),
                 ('Nextdoor Help: Advertise on Nextdoor with a monthly subscription',
                  'https://help.nextdoor.com/s/article/Advertise-on-Nextdoor-with-a-Monthly-Subscription?language=en_US'),
                 ('USPS: Every Door Direct Mail', 'https://www.usps.com/business/every-door-direct-mail.htm'),
                 ('USPS Postal Explorer: Quick Service Guide 140, EDDM-Retail', 'https://pe.usps.com/text/qsg300/q140.htm'),
                 ('SBA: Is out of home marketing right for you?', 'https://legacy.sba.gov/blog/out-home-marketing-right-you'),
                 ('SBA: Should you advertise on local radio?', 'https://www.sba.gov/blog/should-you-advertise-local-radio'),
                 ('SBA: Direct mail is hot again', 'https://www.sba.gov/blog/2019/2019-04/direct-mail-hot-again-heres-how-use-it/'),
                 ('Google Analytics Help: URL builders, collect campaign data with custom URLs', 'https://support.google.com/analytics/answer/10917952')],
     'related': ['how-much-to-spend-on-google-ads-hvac', 'google-ads-vs-local-services-ads-hvac', 'facebook-ads-for-hvac', 'hvac-marketing-cost']},
    {'slug': 'google-guaranteed-hvac',
     'title': 'Google Guaranteed for HVAC companies: what changed and how to get the Google Verified badge', 'seo_title': 'Google Guaranteed for HVAC: Getting the Verified Badge',
     'short': 'Google Guaranteed',
     'desc': 'Google retired the Google Guaranteed badge and its money back guarantee. What the Google Verified badge means for HVAC shops, and the checks to get it.',
     'read': 6,
     'date': '2026-10-15',
     'takeaways': ['Google Guaranteed and Google Screened are gone. Google folded them into one Google Verified badge in late 2025.',
                   'The money back guarantee for homeowners ended with it. Old claims had to be about jobs booked before December 7, 2025.',
                   "For HVAC in the US, Google's screening lists background checks, liability insurance and state licenses.",
                   'Ads moving to Performance Max with pay-per-lead goals keep the badge automatically, but Google can ask for checks again.'],
     'sections': [('The short answer: Google Guaranteed is now Google Verified',
                   [('p',
                     "If you're searching for how to get Google Guaranteed, here's the news first. Google has retired it. Google's help pages say it launched a single Google Verified "
                     "badge for all Local Services advertisers, and that the Google Guarantee badge and its money back guarantee were discontinued. Google's Local Services page gives "
                     'the date as October 20, 2025. Another copy of the same Google page says November 7, 2025.'),
                    ('p',
                     'Google says Google Verified replaces the older badges and programs: Google Guaranteed, Google Screened, License Verified by Google and the Money Back Guarantee. '
                     'If you already had a badge, Google says you got the new one automatically and your ads kept running. New advertisers get it by passing Local Services screening '
                     'and verification.'),
                    ('note',
                     'You\'ll still see "Google Guaranteed" in old blog posts, agency pitches and even some older Google pages. When someone sells you on the guarantee, ask what they '
                     'mean. The badge homeowners see today is Google Verified.')]),
                  ('What the old guarantee covered',
                   [('p',
                     "It helps to know what went away, because homeowners may still ask. Under the old Google Guarantee, if a customer who found you through Local Services Ads wasn't "
                     'happy with the quality of the work, Google could, at its sole discretion, pay them back up to the amount paid for the first service. In the US there was a '
                     'lifetime limit of $2,000 per customer.'),
                    ('p', "Google's page listed what it didn't cover:"),
                    ('ul', ['Add-on or future projects', 'Damage to property', 'Unhappiness with the price or with how fast the provider responded', 'Cancellations']),
                    ('p',
                     'When it ended, Google said eligible customers could still ask for money back on services booked through Local Services Ads before December 7, 2025, as long as '
                     'they asked within 30 days of the job being finished. That window has now closed.')]),
                  ('Google Screened vs Google Guaranteed',
                   [('p', 'Before the change there were two main badges, and people mixed them up all the time.'),
                    ('table',
                     [['Badge', 'Who it was for', 'What it meant'],
                      ['Google Guaranteed', 'Home service providers, like HVAC, plumbing and electrical', "Passed Google's checks, plus the money back guarantee for customers"],
                      ['Google Screened',
                       'Professional services like law, financial planning and real estate, plus some other categories',
                       'Passed background and license checks. No money back guarantee'],
                      ['Google Verified (now)',
                       'All Local Services advertisers who pass screening',
                       "Passed Google's screening for that category and location. No money back guarantee"]]),
                    ('p', 'So for an HVAC company, the question "Screened or Guaranteed?" no longer applies. There\'s one badge.')]),
                  ('What Google checks for HVAC companies',
                   [('p', "Google says screening depends on your business category and where you are. For HVAC in the US, Google's requirements table lists these checks:"),
                    ('ul',
                     ['<b>Background checks.</b> A business check, an owner check and a service professional check. Google says all owners must pass a criminal background check, and '
                      "so must every worker who does the core work for customers, including employees and contractors. Google says the background check doesn't pull your credit.",
                      '<b>Insurance.</b> General liability and professional liability. You upload your certificate of insurance. Google says the minimum amount depends on the '
                      "category and location, and the name on the policy must match the name you signed up with. If it doesn't, you need a DBA (doing business as) document.",
                      '<b>Licenses.</b> Google says it checks the state licenses your business and its owners or managers need, against state databases, to the extent possible.']),
                    ('p',
                     'Google also says some businesses can apply for background check equivalency. If Google approves your own background check process, your techs can answer leads '
                     "without a separate check by Google's providers.")]),
                  ('How to get the Google Verified badge',
                   [('ol',
                     ['<b>Sign up for Local Services Ads</b> and pick HVAC as your category, with the services and areas you actually want.',
                      '<b>Get your papers ready.</b> Certificate of insurance with a policy number, in the same business name you sign up with. Your state HVAC license numbers for '
                      'the business and owners.',
                      '<b>Finish the background checks</b> for owners and the techs who go into homes, or apply for equivalency if you already run your own.',
                      '<b>Keep it current.</b> Update insurance and licenses before they expire, and add new techs as you hire them.']),
                    ('p', "Google says a listing that hasn't finished every onboarding step is placed below providers who have. So a half-done profile costs you spots at the top.")]),
                  ('Where screening usually gets stuck',
                   [('p', "Most delays come from paperwork that doesn't line up with what Google asked for. Based on Google's own rules, check these before you upload anything:"),
                    ('ul',
                     ["<b>Names that don't match.</b> Google says the name on your insurance must match the name you signed up with. If your policy is under your LLC and your listing "
                      'uses a trade name, have the DBA document ready.',
                      '<b>Documents that can be edited.</b> Google asks for a real, non-editable certificate of insurance with a policy number on it. A screenshot or a typed list '
                      "won't do.",
                      '<b>Missing people.</b> Every owner needs a background check, not just the one filling out the form. So does each tech who goes into homes.',
                      "<b>New hires.</b> A tech who joins after you're verified still needs to be checked before they work your Local Services leads."]),
                    ('p', "If you run more than one location or brand, give each its own clean set of papers. It's easier to keep track of what expires when."),
                    ('note',
                     "Google's exact requirements change by category, state and over time. The table in your Local Services or Google Ads account is the final word for your "
                     'business.')]),
                  ("What's changing in 2026",
                   [('p',
                     'Google is moving Local Services Ads into Performance Max campaigns with pay-per-lead goals inside Google Ads. Google says the first phase began in August 2026 '
                     'for select US home service providers, including HVAC.'),
                    ('p', 'For the badge, Google says:'),
                    ('ul',
                     ['If you already passed verification, your verified status and badge move to Google Ads automatically.',
                      "Insurance and license reverification are no longer required for campaigns that move over. If more checks are needed, you'll see a notice in your Google Ads "
                      'account.',
                      'Eligible businesses show the badge after passing business registration and representative checks.',
                      'You may be asked to repeat checks. Not finishing them may lead to losing the badge, paused ads or a suspended account.']),
                    ('p',
                     'Google also updated its Local Services policies in 2026. It renamed them "Local Services Ads requirements", with the new version taking effect July 31, 2026, '
                     'and said the change lines the rules up with the new badge.')]),
                  ('Does the badge matter without the guarantee?',
                   [('p',
                     "It still tells a homeowner that Google checked you before showing you at the top of the page. But it's not the only thing they see. Google lists your rating, "
                     'review count, response time and finished verification as part of your profile quality for Local Services rankings.'),
                    ('p',
                     'So the badge gets you in. Fast answers and good reviews decide how often the phone rings. <a href="{u:review-requests}">Review requests</a> after every job and '
                     '<a href="{u:missed-call-text-back}">missed-call text-back</a> help with both. For how leads are charged and credited, see <a '
                     'href="{u:post-google-local-services-ads-hvac}">Local Services Ads for HVAC</a>. To see what a lead may cost you, try the <a '
                     'href="{u:tools/lsa-cost-calculator}">Local Services Ads cost calculator</a>.'),
                    ('p', 'Want someone to handle the setup and screening? See our <a href="{u:local-services-ads}">Local Services Ads management</a>.'),
                    ('cta',)])],
     'faq': [('Can I still get Google Guaranteed?',
              'No. Google retired it in late 2025. The badge now is Google Verified, which you get by passing Local Services screening and verification.'),
             ('Does Google still pay homeowners back if a job goes wrong?',
              'No. The money back guarantee ended with the Google Guarantee badge. Claims were only open for jobs booked before December 7, 2025, filed within 30 days of the job.'),
             ("What's the difference between Google Screened and Google Guaranteed?",
              'Google Screened was mainly for professional services like law and real estate. Google Guaranteed was for home services and came with the money back guarantee. Both are '
              'now one Google Verified badge.'),
             ('Do I need a background check for every tech?',
              'Google says every worker who does the core work for customers needs one, unless Google approves your own background check process as equivalent.')],
     'sources': [('Google Local Services Help: About Google Verified badge', 'https://support.google.com/localservices/answer/16498018'),
                 ('Google Local Services Help: The Google Guarantee', 'https://support.google.com/localservices/answer/7549288'),
                 ('Google Business Profile Community: Upcoming changes to Local Services Ads Google Guarantee badges',
                  'https://support.google.com/business/community-guide/366556199/upcoming-changes-to-local-services-ads-google-guarantee-badges?hl=en'),
                 ('Google Local Services Help: About Google Screened', 'https://support.google.com/localservices/answer/9376654'),
                 ('Google Local Services Help: Business screening and verification requirements, United States',
                  'https://support.google.com/localservices/answer/12174778?hl=en&co=GENIE.CountryCode%3DUS'),
                 ('Google Local Services Help: Understand the screening and verification process', 'https://support.google.com/localservices/answer/6226575'),
                 ('Google Local Services Help: Getting started with Local Services Ads', 'https://support.google.com/localservices/answer/6224841'),
                 ('Google Local Services Help: About ad rankings', 'https://support.google.com/localservices/answer/7527305'),
                 ('Google Ads Help: Local Services Ads transition to Performance Max campaigns with pay-per-lead goals', 'https://support.google.com/google-ads/answer/17213585'),
                 ('Google Ads Help: Business screening and verification for campaigns with pay-per-lead goals', 'https://support.google.com/google-ads/answer/18260066'),
                 ('Google Advertising Policies Help: Local Services Ads policy update (June 2026)', 'https://support.google.com/adspolicy/answer/17083421')],
     'related': ['google-local-services-ads-hvac', 'google-ads-vs-local-services-ads-hvac', 'google-reviews-hvac', 'google-map-pack-hvac']},
]
