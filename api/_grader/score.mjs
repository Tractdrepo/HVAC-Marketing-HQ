// Fixed scoring rules. Pure functions: facts in, grades out. No network, no AI.
//
// A fact set to null (or undefined) means "could not be measured". Those criteria are
// left out and the area is scored on what remains, so nothing counts against a shop
// that we could not check.

export const WEIGHTS = { profile: 0.30, reviews: 0.25, website: 0.30, listings: 0.15 };

const LETTERS = [[93, 'A'], [90, 'A−'], [87, 'B+'], [83, 'B'], [80, 'B−'],
  [77, 'C+'], [73, 'C'], [70, 'C−'], [60, 'D'], [0, 'F']];

export function letter(score) {
  if (score == null) return null;
  return LETTERS.find(([min]) => score >= min)[1];
}

const known = (v) => v !== null && v !== undefined;
const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
const tier = (value, tiers) => tiers.find(([min]) => value >= min)[1];
const tierUpTo = (value, tiers) => tiers.find(([max]) => value <= max)[1];

// One graded line. points = null when not measured.
function line(id, label, max, points, fix = null) {
  const measured = known(points);
  return { id, label, max, points: measured ? clamp(Math.round(points * 10) / 10, 0, max) : null, measured, fix };
}

function total(lines, penalty = 0) {
  const measured = lines.filter((l) => l.measured);
  if (!measured.length) return null;
  const max = measured.reduce((s, l) => s + l.max, 0);
  const pts = measured.reduce((s, l) => s + l.points, 0) - penalty;
  return Math.round(clamp((pts / max) * 100, 0, 100));
}

function area(lines, penalty = 0, extra = {}) {
  const score = total(lines, penalty);
  const failed = lines.filter((l) => l.measured && l.points < l.max && l.fix);
  const top = failed.sort((a, b) => (b.max - b.points) - (a.max - a.points))[0] || null;
  return { score, grade: letter(score), lines, topFix: top ? top.fix : null, topFixId: top ? top.id : null, ...extra };
}

// Search position: 1-based rank, 0 = not in results, null = not measured.
export function positionPoints(rank, marketSize) {
  if (!known(rank)) return null;
  if (known(marketSize) && marketSize < 6) {
    return rank === 1 ? 40 : rank === 2 ? 30 : rank === 3 ? 20 : 10;
  }
  if (rank === 0 || rank > 20) return 0;
  if (rank === 1) return 40;
  if (rank <= 3) return 34;
  if (rank <= 5) return 24;
  if (rank <= 10) return 12;
  return 5;
}

// ---------- 1. Google profile ----------
export function scoreProfile(p, trade) {
  if (!p || p.found === false) return area([], 0, { notFound: true });

  const searches = (p.searches || []).filter((s) => known(s.rank));
  const searchPts = searches.length
    ? searches.reduce((s, x) => s + positionPoints(x.rank, x.marketSize), 0) / searches.length
    : null;
  const worst = searches.slice().sort((a, b) => (a.rank || 99) - (b.rank || 99)).pop();

  let photoPts = null;
  if (p.photos) {
    const n = p.photos.count ?? 0;
    const own = p.photos.byBusiness;
    photoPts = Math.min(n, 10) + (known(own) ? (own >= 5 ? 5 : own >= 1 ? 3 : 0) : 0);
  }

  const cat = p.primaryCategory;
  const catPts = !known(p.primaryCategory) ? 0 : categoryMatches(cat, trade) ? 10 : 3;

  let detailPts = null;
  if (known(p.paymentListed) || known(p.accessibilityListed)) {
    detailPts = (p.paymentListed ? 6 : 0) + (p.accessibilityListed ? 4 : 0);
  }

  const lines = [
    line('search', 'Local search position', 40, searchPts,
      worst && searches.length ? `Move up in "${worst.query}" results; today you are ${rankText(worst.rank)}.` : null),
    line('photos', 'Photos', 15, photoPts,
      p.photos ? `Add your own photos to Google (jobs, trucks, team). Google shows ${p.photos.count ?? 0} now${known(p.photos.byBusiness) ? `, ${p.photos.byBusiness} of them yours` : ''}.` : null),
    line('website', 'Links to your website', 10, known(p.linksToSite) ? (p.linksToSite ? 10 : 0) : null,
      'Point your Google profile\'s website link at your own site.'),
    line('category', 'Right category', 10, catPts,
      known(cat) ? `Change your main Google category from "${cat?.name || cat}" to "${titleCase(trade.categories.names[0])}".` : `Set a main Google category of "${titleCase(trade.categories.names[0])}".`),
    line('hours', 'Hours listed', 10, known(p.hasHours) ? (p.hasHours ? 10 : 0) : null,
      'Add your business hours to Google.'),
    line('details', 'Details filled in', 10, detailPts,
      'Fill in payment options and accessibility on your Google profile.'),
    line('phone', 'Phone listed', 5, known(p.hasPhone) ? (p.hasPhone ? 5 : 0) : null,
      'Add your phone number to Google.'),
  ];

  const closed = p.operational === false;
  // Google's data doesn't show posts, so this is advice, never a deduction.
  const result = area(lines, closed ? 40 : 0, { closed, advice: [{ id: 'posts', fix: 'Post on your Google profile every week (a finished job, a seasonal tip). Google rewards active profiles.' }] });
  if (closed) { result.topFix = 'Google does not show your business as open. Fix the status on your profile first.'; result.topFixId = 'closed'; }
  return result;
}

export function categoryMatches(cat, trade) {
  if (!cat) return false;
  const id = (cat.id || '').toLowerCase();
  const name = (cat.name || String(cat)).toLowerCase();
  return trade.categories.typeIds.includes(id) || trade.categories.names.includes(name);
}

// ---------- 2. Reviews ----------
export function scoreReviews(r, trade) {
  if (!r || !known(r.count) || r.count === 0) {
    return area([line('rating', 'Star rating', 35, r && r.count === 0 ? 0 : null, 'Start asking every finished job for a Google review.')]);
  }
  const t = trade.reviews;
  const comp = r.competitors && r.competitors.n > 0 ? r.competitors : null;

  let ratingPts = null;
  if (known(r.rating)) {
    ratingPts = tier(r.rating, t.ratingTiers);
    if (comp && known(comp.avgRating)) {
      const d = Math.round((r.rating - comp.avgRating) * 10) / 10;
      ratingPts += d >= 0.1 ? 3 : d > -0.1 ? 0 : d >= -0.3 ? -3 : d >= -0.5 ? -5 : -7;
    }
  }

  let countPts = tier(r.count, t.countTiers);
  if (comp && known(comp.avgCount) && comp.avgCount > 0) {
    const ratio = r.count / comp.avgCount;
    countPts += ratio >= 1 ? 3 : ratio >= 0.6 ? 0 : ratio >= 0.3 ? -2 : ratio >= 0.1 ? -4 : -5;
  }

  const recentPts = known(r.newestDays) ? tierUpTo(r.newestDays, t.recencyTiers) : null;
  const lowPts = known(r.lowInShown)
    ? [10, 7, 4][r.lowInShown] ?? 1
    : null;

  const compText = comp ? ` The top shops near you average ${comp.avgRating?.toFixed(1)} stars and ${Math.round(comp.avgCount)} reviews.` : '';
  return area([
    line('rating', 'Star rating', 35, ratingPts, `Your rating is ${r.rating?.toFixed(1)}.${compText} Ask happy customers right after the job.`),
    line('count', 'Number of reviews', 30, countPts, `You have ${r.count} Google reviews.${compText} A review request after every job closes the gap.`),
    line('recent', 'Most recent review', 15, recentPts, known(r.newestDays) ? `Your newest review is ${r.newestDays} days old. Ask after every completed job.` : null),
    line('low', 'Low reviews shown first', 10, lowPts, `${r.lowInShown} of the reviews Google shows first are three stars or lower. Reply to them and bury them with new ones.`),
  ], 0, {
    themes: r.themes || null,
    // Google's data doesn't show owner replies, so this is advice, never a deduction.
    advice: [{ id: 'replies', fix: 'Reply to every review, good and bad. Customers read the replies and Google sees an active owner.' }],
  });
}

// ---------- 3. Website ----------
export function scoreWebsite(w, trade) {
  if (!w || !w.fetched) return area([], 0, { notFetched: true });

  const sizePts = w.pageCount >= 15 ? 6 : w.pageCount >= 8 ? 4 : w.pageCount >= 4 ? 2 : 0;
  const svc = (w.serviceTopics || []).length;
  const svcPts = svc >= 4 ? 8 : svc >= 2 ? 5 : svc >= 1 ? 2 : 0;
  const areaN = (w.areaPages || []).length;
  const areaPts = areaN >= 3 ? 6 : areaN >= 1 ? 3 : 0;
  const missingSvc = Object.keys(trade.servicePages).filter((k) => !(w.serviceTopics || []).includes(k));

  const lh = w.lighthouse;
  const lhVals = lh ? [lh.seo, lh.accessibility, lh.bestPractices].filter(known) : [];
  const lhPts = lhVals.length ? (lhVals.reduce((a, b) => a + b, 0) / lhVals.length) * 10 : null;

  const titlePts = { clear: 10, vague: 4, wrong: 0 }[w.titleVerdict] ?? null;
  const mobilePts = (known(w.mobileViewport) || known(w.https))
    ? (w.mobileViewport ? 6 : 0) + (w.https ? 4 : 0) : null;
  const yes = (v, pts) => known(v) ? (v ? pts : 0) : null;

  const lines = [
    line('pages', 'Pages that bring searches', 20, sizePts + svcPts + areaPts,
      svc < 4 ? `Give each service its own page. We did not find pages for ${missingSvc.slice(0, 3).join(', ')}.`
        : areaN < 3 ? 'Add a page for each town you serve, with real jobs from that town.'
          : 'Add more pages for the services and towns you want to be found for.'),
    line('booking', 'A clear way to book', 15, yes(w.booking, 15),
      'Put a "Book service" button on your home page that goes straight to a form or your booking system.'),
    line('speed', 'Speed on a phone', 10, known(w.performance) ? w.performance * 10 : null,
      known(w.performance) ? `Google scores your site ${Math.round(w.performance * 100)} out of 100 for speed on a phone.` : null),
    line('lighthouse', 'Search basics, accessibility, best practices', 10, lhPts,
      'Fix the search-basics and accessibility issues Google flags on your home page.'),
    line('title', 'Title says what and where', 10, titlePts,
      `Make your page title say what you do and where, like "${trade.label} repair in [your town]".`),
    line('mobile', 'Works on a phone, loads securely', 10, mobilePts,
      !w.https ? 'Move your site to https so browsers stop marking it "not secure".' : 'Make your site lay out properly on a phone.'),
    line('call', 'Tap-to-call phone number', 5, yes(w.tapToCall, 5),
      'Make your phone number tappable on phones.'),
    line('emergency', 'Emergency or 24/7 service shown', 5, yes(w.emergency, 5),
      'If you take emergency calls, say so on the home page.'),
    line('financing', 'Financing shown', 5, yes(w.financing, 5),
      'If you offer financing, show it on the home page. It matters on replacement jobs.'),
    line('license', 'License number shown', 5, yes(w.license, 5),
      `We did not find your ${trade.licenseName} on the home page. Add it to the footer.`),
    line('chat', 'Chat or after-hours answer', 5, yes(w.chat, 5),
      'We did not find a chat tool. Add one so after-hours visitors get an answer.'),
    line('schema', 'Business details code for Google and AI search', 5, yes(w.schema, 5),
      'Add business details code (LocalBusiness markup) so Google and AI tools like ChatGPT can read your name, phone and the towns you serve.'),
    line('reviewsOnSite', 'Reviews shown on the site', 5, yes(w.reviewsOnSite, 5),
      'Show your Google reviews on your website. Visitors who came from an ad or a search see proof before they call.'),
    line('faq', 'Common questions answered', 3, yes(w.faq, 3),
      'Answer the questions customers ask (what a new system costs, how long a repair takes). AI search tools quote pages that answer them.'),
    line('blog', 'Fresh articles', 5, blogPoints(w.blog),
      !w.blog?.found ? 'Start a blog: one helpful article a month (AC tune-up tips, what a new system costs) gives Google something new to rank.'
        : `Your newest blog post is ${w.blog.newestDays} days old. Post a helpful article every month.`),
  ];
  const result = area(lines);
  if (w.placeholderPhone) result.notes = [`Your home page shows a placeholder number (${w.placeholderPhone}). Replace it with your real number.`];
  return result;
}

function blogPoints(b) {
  if (!b) return null;
  if (!b.found) return 0;
  if (!known(b.newestDays)) return null;
  return b.newestDays <= 60 ? 5 : b.newestDays <= 180 ? 2 : 0;
}

// ---------- 4. Listings ----------
export function scoreListings(l, trade) {
  if (!l) return area([]);
  const phoneLine = line('phone', 'Phone on Google matches your website', 25,
    l.phoneMatch === null ? 8 : known(l.phoneMatch) ? (l.phoneMatch ? 25 : 0) : null,
    l.phoneMatch === null ? 'Show your phone number on your home page so customers and Google see the same one.'
      : 'The phone number on Google does not match your website. Use one number everywhere.');
  const linkLine = line('googleLink', 'Google links to this website', 10, known(l.googleLinksSite) ? (l.googleLinksSite ? 10 : 0) : null,
    'Point your Google profile at this website.');

  if (Array.isArray(l.directoriesFound)) {
    const checked = l.directoriesChecked || trade.directories.map((d) => d.name);
    const missing = checked.filter((d) => !l.directoriesFound.includes(d));
    return area([
      line('directories', 'Directories a web search finds you on', 65, (l.directoriesFound.length / checked.length) * 65,
        `A web search did not turn up a listing for you on ${missing.slice(0, 3).join(', ')}.`),
      phoneLine, linkLine,
    ], 0, { found: l.directoriesFound, checked });
  }

  // Directory search failed or was skipped: consistency only.
  const scale = (ln, max) => ({ ...ln, max, points: ln.measured ? (ln.points / ln.max) * max : null });
  if (!phoneLine.measured && !linkLine.measured) return area([], 0, { fallback: true });
  return area([
    line('base', 'Directory search could not run', 30, 30),
    scale(phoneLine, 35), scale(linkLine, 20),
    line('facebook', 'Website links to a Facebook page', 15, known(l.facebookLinked) ? (l.facebookLinked ? 15 : 0) : null,
      'Link your Facebook page from your website.'),
  ], 0, { fallback: true });
}

// ---------- Overall ----------
export function scoreAll(facts, trade) {
  const areas = {
    profile: scoreProfile(facts.profile, trade),
    reviews: scoreReviews(facts.reviews, trade),
    website: scoreWebsite(facts.website, trade),
    listings: scoreListings(facts.listings, trade),
  };
  // No overall grade unless we could see the Google profile or the website.
  const graded = known(areas.profile.score) || known(areas.website.score)
    ? Object.entries(areas).filter(([, a]) => known(a.score)) : [];
  const weight = graded.reduce((s, [k]) => s + WEIGHTS[k], 0);
  const overall = graded.length
    ? Math.round(graded.reduce((s, [k, a]) => s + a.score * WEIGHTS[k], 0) / weight)
    : null;
  const weakest = graded.sort((a, b) => a[1].score - b[1].score)[0]?.[0] || null;
  return { trade: trade.id, criteriaVersion: trade.criteriaVersion, overall, grade: letter(overall), weakest, areas };
}

function rankText(rank) {
  if (!rank) return 'not in the first 20';
  const v = rank % 100;
  const sfx = ['th', 'st', 'nd', 'rd'];
  return rank + (sfx[(v - 20) % 10] || sfx[v] || sfx[0]);
}

function titleCase(s) {
  return s.replace(/\b\w/g, (c) => c.toUpperCase()).replace(/\bHvac\b/, 'HVAC');
}
