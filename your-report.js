// Personal results page. The report travels in the link (#r=...), so nothing is stored on a server.
(function () {
  var root = document.getElementById("yr");
  if (!root) return;
  var BOOK = root.getAttribute("data-book");
  var esc = function (s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; });
  };
  var data = null;
  try {
    var m = location.hash.match(/r=([A-Za-z0-9_-]+)/);
    if (m) {
      var b64 = m[1].replace(/-/g, "+").replace(/_/g, "/");
      var bin = atob(b64 + "===".slice((b64.length + 3) % 4));
      var bytes = new Uint8Array(bin.length);
      for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
      data = JSON.parse(new TextDecoder().decode(bytes));
    }
  } catch (e) { data = null; }

  var book = function (label, cls) {
    return '<a class="btn btn-primary ' + (cls || "") + '" href="' + esc(BOOK) + '">' + esc(label || "Book a 15-minute call") + ' <span class="arrow">→</span></a>';
  };

  if (!data || !data.a) {
    root.innerHTML = '<section class="yr-hero"><div class="wrap"><span class="eyebrow">Your report card</span><h1>We couldn\'t open this report.</h1>' +
      '<p class="lede">The link may have been cut off by your email app. Open it again from the email, or book a call and we\'ll walk you through it.</p>' + book() + '</div></section>';
    return;
  }

  var NAMES = { profile: "Google profile", reviews: "Reviews", website: "Website", listings: "Listings" };
  var HOW = {
    profile: {
      h: "How we fix your Google profile",
      p: "We set your profile up the way Google ranks it: the right main category, hours, services, service area and payment details, then post the job photos you text us every week. Setup is in every plan. On Growth and up we run it for you month to month.",
    },
    reviews: {
      h: "How we fix your reviews",
      p: "Every finished job gets a review request by text, sent for you, in every plan. Happy customers get a one-tap link to Google. On Growth and up we also reply to every review, so the next customer sees an owner who answers.",
    },
    website: {
      h: "How we fix your website",
      p: "We build a fast site on our HVAC build: a page for each service and the towns you serve, tap-to-call and a book-service button on every page, and every missed call texted back in 60 seconds. You own the site and the domain.",
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

  var cards = areas.map(function (a, n) {
    var how = HOW[a.k];
    var fixes = (a.fx || []).map(function (f) { return "<li>" + esc(f) + "</li>"; }).join("");
    var ok = a.s != null && !(a.fx || []).length;
    return '<article class="yr-area' + (n === 0 && a.s != null && a.s < 80 ? " yr-weak" : "") + '">' +
      '<div class="yr-area-head"><b class="yr-g g-' + gcls(a.g) + '">' + esc(a.g || "N/A") + '</b><div><h3>' + esc(NAMES[a.k]) + "</h3>" +
      (a.s != null ? '<span class="yr-score">' + a.s + " / 100</span>" : '<span class="yr-score">Not measured</span>') + "</div></div>" +
      '<p class="yr-saw"><span>What we saw</span>' + esc(a.saw) + "</p>" +
      (fixes ? '<div class="yr-fixes"><span>What to fix</span><ol>' + fixes + "</ol></div>" : "") +
      (ok ? '<p class="yr-ok">Nothing to fix here. Keep doing what you are doing.</p>' : "") +
      (!ok ? '<div class="yr-how"><h4>' + esc(how.h) + "</h4><p>" + esc(how.p) + "</p></div>" : "") +
      "</article>";
  });
  var mid = Math.ceil(cards.length / 2);
  var weak = data.lo ? NAMES[data.lo] : null;

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
    '<section class="yr-body"><div class="wrap">' +
      '<div class="yr-head"><h2>' + (weak ? "Start with your " + esc(weak === "Google profile" ? weak : weak.toLowerCase()) + "." : "Here's what we found.") + "</h2>" +
      "<p>Each area below shows what we saw, what to fix first, and how we'd fix it for you. Weakest area first.</p></div>" +
      cards.slice(0, mid).join("") +
      '<div class="yr-band"><div><h3>Want these fixed for you?</h3><p>Book 15 minutes. We go through your report line by line and tell you what we would do first, how long it takes, and what it costs.</p></div>' + book("Book my 15-minute call") + "</div>" +
      cards.slice(mid).join("") +
    "</div></section>" +
    '<section class="yr-close"><div class="wrap">' +
      "<h2>What happens on the call</h2>" +
      '<ol class="yr-steps"><li><b>We walk your report.</b> Every grade above, in plain words, with your search results on screen.</li>' +
      "<li><b>We show the fix order.</b> What moves calls first, what can wait, and which plan covers it.</li>" +
      "<li><b>You decide.</b> Plans are month to month. If it's not a fit, you keep the report and the fix list.</li></ol>" +
      book("Book a 15-minute call") +
      '<p class="muted yr-fine">Grades come from what anyone can see in public on ' + (date ? esc(date) : "the day we checked") + ". Anything we couldn't measure is left out of your grade, not counted against you.</p>" +
    "</div></section>";
})();
