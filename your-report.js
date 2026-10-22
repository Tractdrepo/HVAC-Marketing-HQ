// Personal results page. The report travels in the link (#r=...), so nothing is stored on a server.
(function () {
  var root = document.getElementById("yr");
  if (!root) return;
  var BOOK = root.getAttribute("data-book");
  var esc = function (s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; });
  };
  // #z= is the compressed link the email sends now; #r= is the older plain one.
  var m = location.hash.match(/([rz])=([A-Za-z0-9_-]+)/);
  var bytes = null;
  try {
    if (m) {
      var b64 = m[2].replace(/-/g, "+").replace(/_/g, "/");
      var bin = atob(b64 + "===".slice((b64.length + 3) % 4));
      bytes = new Uint8Array(bin.length);
      for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    }
  } catch (e) { bytes = null; }
  var parse = function (b) { try { return JSON.parse(new TextDecoder().decode(b)); } catch (e) { return null; } };
  if (bytes && m[1] === "z" && window.DecompressionStream) {
    new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream("deflate-raw"))).arrayBuffer()
      .then(function (buf) { render(parse(new Uint8Array(buf))); }, function () { render(null); });
  } else {
    render(bytes && m[1] === "r" ? parse(bytes) : null);
  }

  function render(data) {

  var book = function (label, cls) {
    return '<a class="btn btn-primary ' + (cls || "") + '" href="' + esc(BOOK) + '">' + esc(label || "Book a 15-minute call") + ' <span class="arrow">→</span></a>';
  };

  if (!data || !data.a) {
    root.innerHTML = '<section class="yr-hero"><div class="wrap"><span class="eyebrow">Your report card</span><h1>We couldn\'t open this report.</h1>' +
      '<p class="lede">The link may have been cut off by your email app. Open it again from the email, or book a call and we\'ll walk you through it.</p>' + book() + '</div></section>';
    return;
  }

  // Texting waits on carrier (A2P) approval. While false, text-back is sold as going live soon, never as
  // live. Keep in step with TEXTING_LIVE in api/_grader/report.mjs.
  var TEXTING_LIVE = false;
  var SOON = TEXTING_LIVE ? "" : " Goes live in the next couple of weeks.";
  var NAMES = { profile: "Google profile", reviews: "Reviews", website: "Website", listings: "Listings" };
  var HOW = {
    profile: {
      h: "How we fix your Google profile",
      p: "We set your profile up the way Google ranks it: the right main category, hours, services, service area and payment details, then post an update with the job photos you text us every week. Setup is in every plan. On Growth and up we run it for you every month.",
    },
    reviews: {
      h: "How we fix your reviews",
      p: "Every finished job gets a review request, sent for you, in every plan. Happy customers get a one-tap link to Google. On Growth and up we also reply to every review, so the next customer sees an owner who answers.",
    },
    website: {
      h: "How we fix your website",
      p: "We build a fast site on our HVAC build: a page for each service and the towns you serve, tap-to-call and a book-service button on every page, a helpful article every month, and every missed call texted back within 10 seconds" + (TEXTING_LIVE ? "" : " (going live in the next couple of weeks)") + ". You own the site and the domain.",
    },
    listings: {
      h: "How we fix your listings",
      p: "We make your name, address and phone match everywhere customers and Google look: Google, Facebook, Yelp, BBB, Angi, Nextdoor and the rest. Managed for you on Dominate, or as an add-on to any plan.",
    },
  };
  var gcls = function (g) { return !g ? "na" : g.charAt(0).toLowerCase(); };
  var date = "";
  try { date = new Date(data.d + "T12:00:00").toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" }); } catch (e) {}

  // Weakest first, so the page leads with what costs the most calls.
  var areas = data.a.slice().sort(function (x, y) {
    var a = x.s == null ? 101 : x.s, b = y.s == null ? 101 : y.s;
    return a - b;
  });

  // Each fix comes with how we handle it: [fix, how]. Older links carry plain strings.
  var fixItem = function (f) {
    var t = typeof f === "string" ? f : f[0], h = typeof f === "string" ? "" : f[1];
    return "<li><span class=\"yr-fix-t\">" + esc(t) + "</span>" + (h ? '<span class="yr-fix-h"><b>How we fix it:</b> ' + esc(h) + "</span>" : "") + "</li>";
  };
  var cards = areas.map(function (a, n) {
    var how = HOW[a.k];
    var list = a.fx || [];
    var structured = list.length && typeof list[0] !== "string";
    var fixes = list.map(fixItem).join("");
    var ok = a.s != null && !list.length;
    return '<article class="yr-area' + (n === 0 && a.s != null && a.s < 80 ? " yr-weak" : "") + '">' +
      '<div class="yr-area-head"><b class="yr-g g-' + gcls(a.g) + '">' + esc(a.g || "N/A") + '</b><div><h3>' + esc(NAMES[a.k]) + "</h3>" +
      (a.s != null ? '<span class="yr-score">' + a.s + " / 100</span>" : '<span class="yr-score">Not measured</span>') + "</div></div>" +
      '<p class="yr-saw"><span>What we saw</span>' + esc(a.saw) + "</p>" +
      (fixes ? '<div class="yr-fixes"><span>What to fix, and how we fix it</span><ol>' + fixes + "</ol></div>" : "") +
      (ok ? '<p class="yr-ok">Nothing to fix here. Keep doing what you are doing.</p>' : "") +
      (!ok && !structured ? '<div class="yr-how"><h4>' + esc(how.h) + "</h4><p>" + esc(how.p) + "</p></div>" : "") +
      "</article>";
  });
  var mid = Math.ceil(cards.length / 2);
  var weak = data.lo ? NAMES[data.lo] : null;
  var weakArea = null;
  data.a.forEach(function (a) { if (a.k === data.lo) weakArea = a; });
  var weakFix = weakArea && weakArea.fx && weakArea.fx[0] ? (typeof weakArea.fx[0] === "string" ? weakArea.fx[0] : weakArea.fx[0][0]) : null;

  // Book and Repeat speak to what we saw when the link carries it (b, rv), else stay general.
  var b = data.b, rv = data.rv;
  var bookSaw = !b ? "" : "On your site we found " +
    (b.k === "online" ? "online booking" : b.k === "form" ? "a contact form, but no online booking" : "no way to book or request service") +
    ", " + (b.c ? "a chat tool" : "no chat") + " and " + (b.t ? "a tap-to-call number" : "no tap-to-call number") + ".";
  var repeatSaw = !rv ? "" : rv.n + " Google reviews" + (rv.d != null ? ", the newest " + (rv.d === 0 ? "today" : rv.d + " days ago") : "") + ".";
  var tile = function (h, p, tag) { return '<div><h4>' + esc(h) + (tag ? ' <small class="yr-tag">' + esc(tag) + "</small>" : "") + "</h4><p>" + esc(p) + "</p></div>"; };
  var section = function (n, word, title, lede, saw, tiles, cls) {
    return '<section class="yr-body yr-pillar ' + (cls || "") + '"><div class="wrap">' +
      '<div class="yr-head"><span class="yr-step">' + n + " · " + word + "</span><h2>" + esc(title) + "</h2><p>" + esc(lede) + "</p></div>" +
      (saw ? '<p class="yr-pillar-saw"><b>What we saw:</b> ' + esc(saw) + "</p>" : "") +
      '<div class="yr-ops-grid">' + tiles.join("") + "</div></div></section>";
  };
  var bookLine = !b ? "Make it easy to book from any page." : b.k === "online" ? "Keep online booking, and catch the calls you miss." : b.k === "form" ? "Add online booking next to your form, and text back every missed call." : "Add a book-service button and text back every missed call.";
  var repeatLine = !rv ? "Ask for a review after every job." : rv.n < 100 ? "Ask for a review after every job to close the gap on the top shops near you." : "Keep reviews coming every week and reply to every one.";

  root.innerHTML =
    '<section class="yr-hero"><div class="wrap yr-hero-in">' +
      '<div><span class="eyebrow">HVAC report card' + (date ? " · " + esc(date) : "") + "</span>" +
      "<h1>" + (data.f ? esc(data.f) + ", here's" : "Here's") + " how " + esc(data.n) + " shows up online.</h1>" +
      '<p class="lede">' + esc(data.s) + "</p>" +
      '<div class="yr-cta">' + book("Book a 15-minute call") + '<span class="muted">We walk through this report with you and show what fixing it would cost. No pitch deck.</span></div></div>' +
      '<div class="yr-overall"><small>Overall</small><b class="g-' + gcls(data.g) + '">' + esc(data.g || "N/A") + "</b>" + (data.o != null ? "<span>" + data.o + " / 100</span>" : "") +
      '<ul>' + data.a.map(function (a) { return '<li><span>' + esc(NAMES[a.k]) + '</span><b class="g-' + gcls(a.g) + '">' + esc(a.g || "N/A") + "</b></li>"; }).join("") + "</ul>" +
      (data.w ? '<p class="muted">' + esc(data.w) + "</p>" : "") + "</div>" +
    "</div></section>" +
    '<nav class="yr-method wrap" aria-label="Report sections"><a href="#yr-rank"><b>1</b> Rank</a><a href="#yr-book"><b>2</b> Book</a><a href="#yr-repeat"><b>3</b> Repeat</a><a href="#yr-plan"><b>✓</b> Your plan</a></nav>' +
    '<section class="yr-body" id="yr-rank"><div class="wrap">' +
      '<div class="yr-head"><span class="yr-step">1 · Rank</span><h2>' + (weak ? "Start with your " + esc(weak === "Google profile" ? weak : weak.toLowerCase()) + "." : "How customers find you.") + "</h2>" +
      "<p>This is your report card: how you show up when someone nearby searches for HVAC. Each area shows what we saw, what to fix, and how we fix it for you. Weakest area first.</p></div>" +
      cards.slice(0, mid).join("") +
      '<div class="yr-band"><div><h3>Want these fixed for you?</h3><p>Book 15 minutes. We go through your report line by line and tell you what we would do first, how long it takes, and what it costs.</p></div>' + book("Book my 15-minute call") + "</div>" +
      cards.slice(mid).join("") +
    "</div></section>" +
    '<div id="yr-book">' + section("2", "Book", "Turn visits and calls into booked jobs.",
      "Ranking gets you the call. A homeowner with a broken AC books whoever answers first or lets them book right away, so every page needs an easy way to book and every missed call needs an answer.",
      bookSaw, [
        tile("Book-service button and form", "Every site we build has a book-service button and a short form on every page, landing in your inbox app.", "Every plan"),
        tile("Missed calls texted back", "Every missed call gets a text within 10 seconds, so the caller books with you instead of the next shop." + SOON, "Every plan"),
        tile("AI web chat", "Answers questions on your site and books jobs after hours, when your office is closed.", "Growth and up"),
        tile("AI phone answering", "An AI receptionist picks up when you can't, during the rush or after hours.", "Add-on"),
        tile("One inbox", "Calls, texts and web leads land in one inbox app your office and techs can all see.", "Every plan"),
        tile("Booking hookup", "New jobs go straight into ServiceTitan, Housecall Pro or Jobber.", "Dominate"),
      ]) + "</div>" +
    '<div id="yr-repeat">' + section("3", "Repeat", "Customers who come back, and send others.",
      "The shops that stay on top don't win one job at a time. They ask every customer for a review, answer every review, and stay in touch so last summer's repair becomes this fall's tune-up.",
      repeatSaw, [
        tile("Review requests", "A request after every finished job with a one-tap link to Google.", "Every plan"),
        tile("Review replies", "We write and post a reply to every review, good and bad.", "Growth and up"),
        tile("Quote follow-up", "Open estimates get followed up until they are booked or lost.", "Growth and up"),
        tile("Tune-up and win-back reminders", "Past customers hear from you each season, so slow months fill up.", "Growth and up"),
        tile("HQ Command Center", "Calls, jobs and reviews in one live dashboard you can open anytime.", "Every plan"),
        tile("Fresh content", "A new article every month keeps your site growing in search.", "Growth and up"),
      ], "yr-ops") + "</div>" +
    '<section class="yr-close" id="yr-plan"><div class="wrap">' +
      "<h2>Your plan in three lines</h2>" +
      '<ol class="yr-steps yr-plan">' +
        "<li><b>Rank.</b> " + esc(weakFix || "Keep your Google profile and site growing.") + "</li>" +
        "<li><b>Book.</b> " + esc(bookLine) + "</li>" +
        "<li><b>Repeat.</b> " + esc(repeatLine) + "</li></ol>" +
      '<p class="yr-close-lede">On a 15-minute call we walk your report, show the fix order and what it costs. If it\'s not a fit, you keep the report and the fix list.</p>' +
      book("Book my 15-minute call") +
      '<p class="muted yr-fine">Grades come from what anyone can see in public on ' + (date ? esc(date) : "the day we checked") + ". Anything we couldn't measure is left out of your grade, not counted against you. Map rankings compare you with HVAC businesses within 30 miles of your shop.</p>" +
    "</div></section>";
  }
})();
