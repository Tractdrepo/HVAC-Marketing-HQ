// Collect public facts about a business, then score them with the fixed rules.
import { getTrade } from './trades/index.mjs';
import { scoreAll } from './score.mjs';
import { fetchHomepage, ruleTitleVerdict, townPages } from './collect/homepage.mjs';
import { blogFreshness } from './collect/blog.mjs';
import { findBusiness, townOf, stateOf, localRank, areaRank, newestReviewDays, placeFacts, host } from './collect/places.mjs';
import { splitTown } from './trades/region.mjs';
import { pagespeed } from './collect/pagespeed.mjs';

// deps.ai stands in for ./ai.mjs (tests pass a stub).
export async function collectFacts(input, env = process.env, deps = {}) {
  const trade = getTrade(input.trade);
  const google = env.GOOGLE_PLACES_API_KEY;
  const useAi = Boolean(env.ANTHROPIC_API_KEY) && input.ai !== false;
  const ai = deps.ai !== undefined ? deps.ai : useAi ? await import('./ai.mjs') : null;
  const notes = [];
  // Steps that should have worked and didn't. Any failure makes the run partial: the grade would be
  // built on missing facts, so it goes to the team to check and send by hand, not to the shop.
  const failures = [];
  const fail = (msg) => { failures.push(msg); notes.push(msg); };
  let { town, state } = splitTown(input.town);
  state = input.state || state;

  const sitePromise = fetchHomepage(input.website, trade);
  const speedPromise = pagespeed(/^https?:/.test(input.website) ? input.website : `https://${input.website}`, env.PAGESPEED_API_KEY || env.GOOGLE_PLACES_API_KEY, { timeoutMs: 35000 });

  // Google profile and reviews
  let place = null;
  let gp = { profile: null, reviews: null };
  if (google) {
    try {
      place = await findBusiness({ ...input, town, state }, google, trade);
      if (place) {
        town = townOf(place) || town;
        state = stateOf(place) || state;
        // One search in their own town, one across everything within about 20 miles (the towns they serve).
        // One search in their own town, one across every HVAC business within 30 miles (the report says so).
        const [searches, newest] = await Promise.all([
          (async () => {
            const own = town ? await localRank(trade.searchQueries[0].replace('{town}', town).replace(', {state}', state ? `, ${state}` : ''), place, google) : null;
            const wide = await areaRank(trade.areaQuery, place, google, Math.round(trade.areaMiles * 1609))
              .then((r) => r && { ...r, query: `${trade.areaQuery} within ${trade.areaMiles} miles of ${town || 'you'}` })
              .catch((err) => { fail(`Google area search failed: ${err.message}`); return null; });
            return [own, wide].filter(Boolean);
          })(),
          newestReviewDays(place.id, google),
        ]);
        gp = placeFacts(place, searches, trade, { website: input.website });
        // The five "most relevant" reviews only prove the newest is at least that recent.
        if (newest.days != null) gp.reviews.newestDays = newest.days;
        else {
          if (gp.reviews.newestDays != null && gp.reviews.newestDays > 30) gp.reviews.newestDays = null;
          notes.push(`Newest-review lookup failed (${newest.error}); turn on "Places API" for the key to measure it.`);
        }
      } else {
        gp.profile = { found: false };
        // A shop that gave us its name and website almost always has a profile; not finding one is
        // far more often our lookup missing it than the shop not having one.
        if (input.website && input.businessName) fail('No Google profile found for this name and website.');
        else notes.push('No Google profile found for this name and website.');
      }
    } catch (err) {
      fail(`Google lookup failed: ${err.message}`);
    }
  } else {
    notes.push('GOOGLE_PLACES_API_KEY not set: profile and reviews not measured.');
  }

  // Directory search runs while the home page and speed test finish.
  const dirPromise = ai
    ? ai.directorySearch({ businessName: gp.profile?.name || input.businessName, town, state }, trade).catch((err) => ({ error: err.message }))
    : null;

  const [site, speed] = await Promise.all([sitePromise, speedPromise]);
  if (!site.fetched) notes.push(`Home page could not be fetched (${site.error}).`);
  if (speed.error) notes.push(`Speed test did not finish (${speed.error}); speed points left out.`);

  const blog = site.fetched ? await blogFreshness(site.blogUrl) : null;
  if (blog?.error) notes.push(`Blog check failed (${blog.error}).`);
  const website = site.fetched ? { ...site, performance: speed.performance, lighthouse: speed.lighthouse, blog } : { fetched: false };
  if (site.fetched) website.areaPages = townPages(site, state, trade);
  if (site.fetched) {
    // A license number is only checked where the trade's license rule applies.
    if (trade.licenseState && state !== trade.licenseState) website.license = null;
    website.titleVerdict = ai ? await ai.titleVerdict(site, trade).catch((err) => { fail(`AI title check failed: ${err.message}`); return null; }) : null;
    website.titleVerdict ??= ruleTitleVerdict(site, trade, { town, state });
  }

  // Listings
  const googlePhone = gp.profile?.phone ? gp.profile.phone.replace(/\D/g, '').slice(-10) : null;
  const listings = {
    phoneMatch: !site.fetched || !googlePhone ? undefined : site.phones.length ? site.phones.includes(googlePhone) : null,
    googleLinksSite: gp.profile?.found ? Boolean(gp.profile.websiteUri && host(gp.profile.websiteUri) === host(input.website)) : undefined,
    facebookLinked: site.fetched ? site.facebookLinked : undefined,
    directoriesFound: undefined,
  };
  if (dirPromise) {
    const d = await dirPromise;
    if (d.error) fail(`AI directory search failed (${d.error}); directories could not be checked.`);
    else {
      listings.directoriesFound = d.found;
      listings.directoriesChecked = d.checked;
      listings.directoryModel = d.model;
    }
  } else {
    notes.push('ANTHROPIC_API_KEY not set: directory search skipped, title checked by fixed rule.');
  }

  if (ai && gp.reviews?.shownText?.length) {
    gp.reviews.themes = await ai.reviewThemes(gp.reviews.shownText).catch((err) => { fail(`AI review themes failed: ${err.message}`); return null; });
  }

  return {
    trade: trade.id, businessName: gp.profile?.name || input.businessName, siteUrl: input.website, town, state,
    profile: gp.profile, reviews: gp.reviews, website, listings, notes, ai: Boolean(ai),
    partial: failures.length > 0, failures,
  };
}

export function scoreFacts(facts) {
  const trade = getTrade(facts.trade);
  return scoreAll({ profile: facts.profile, reviews: facts.reviews, website: facts.website, listings: facts.listings }, trade);
}

export async function grade(input, env = process.env, deps = {}) {
  const facts = await collectFacts(input, env, deps);
  const report = scoreFacts(facts);
  // A partial run goes to the team, not the shop, so it skips the AI summary.
  if (facts.ai && report.overall != null && !facts.partial) {
    const { openingParagraph } = deps.ai || await import('./ai.mjs');
    const { sawLine } = await import('./report.mjs');
    const seen = Object.fromEntries(Object.keys(report.areas).map((k) => [k, sawLine(k, facts, report.areas[k])]));
    let summaryError = null;
    report.opening = await openingParagraph(report, facts.businessName, seen).catch((err) => { summaryError = err; return null; });
    if (summaryError) {
      facts.failures.push(`AI summary failed: ${summaryError.message}`);
      facts.notes.push(`AI summary failed: ${summaryError.message}`);
      facts.partial = true;
    } else if (!report.opening) facts.notes.push('AI summary was empty or dropped; the plain summary was used.');
  }
  return { gradedAt: new Date().toISOString(), facts, report, partial: facts.partial, failures: facts.failures };
}
