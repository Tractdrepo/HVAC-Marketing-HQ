// Collect public facts about a business, then score them with the fixed rules.
import { getTrade } from './trades/index.mjs';
import { scoreAll } from './score.mjs';
import { fetchHomepage, ruleTitleVerdict, townPages } from './collect/homepage.mjs';
import { blogFreshness } from './collect/blog.mjs';
import { findBusiness, townOf, stateOf, localRank, areaRank, newestReviewDays, placeFacts, host } from './collect/places.mjs';
import { splitTown } from './trades/region.mjs';
import { pagespeed } from './collect/pagespeed.mjs';

export async function collectFacts(input, env = process.env) {
  const trade = getTrade(input.trade);
  const google = env.GOOGLE_PLACES_API_KEY;
  const useAi = Boolean(env.ANTHROPIC_API_KEY) && input.ai !== false;
  const ai = useAi ? await import('./ai.mjs') : null;
  const notes = [];
  let { town, state } = splitTown(input.town);
  state = input.state || state;

  const sitePromise = fetchHomepage(input.website, trade);
  const speedPromise = pagespeed(/^https?:/.test(input.website) ? input.website : `https://${input.website}`, env.PAGESPEED_API_KEY, { timeoutMs: 35000 });

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
        const [searches, newest] = await Promise.all([
          Promise.all([
            town ? localRank(trade.searchQueries[0].replace('{town}', town).replace(', {state}', state ? `, ${state}` : ''), place, google) : null,
            areaRank(trade.areaQuery, place, google).then((r) => r && { ...r, query: `${trade.areaQuery} within 20 miles of ${town || 'you'}` }).catch(() => null),
          ]).then((list) => list.filter(Boolean)),
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
        notes.push('No Google profile found for this name and website.');
      }
    } catch (err) {
      notes.push(`Google lookup failed: ${err.message}`);
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
    website.titleVerdict = ai ? await ai.titleVerdict(site, trade).catch((err) => { notes.push(`AI title check failed: ${err.message}`); return null; }) : null;
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
    if (d.error) notes.push(`Directory search failed (${d.error}); listings use the consistency fallback.`);
    else {
      listings.directoriesFound = d.found;
      listings.directoriesChecked = d.checked;
      listings.directoryModel = d.model;
    }
  } else {
    notes.push('ANTHROPIC_API_KEY not set: directory search skipped, title checked by fixed rule.');
  }

  if (ai && gp.reviews?.shownText?.length) {
    gp.reviews.themes = await ai.reviewThemes(gp.reviews.shownText).catch((err) => { notes.push(`AI review themes failed: ${err.message}`); return null; });
  }

  return {
    trade: trade.id, businessName: gp.profile?.name || input.businessName, siteUrl: input.website, town, state,
    profile: gp.profile, reviews: gp.reviews, website, listings, notes, ai: Boolean(ai),
  };
}

export function scoreFacts(facts) {
  const trade = getTrade(facts.trade);
  return scoreAll({ profile: facts.profile, reviews: facts.reviews, website: facts.website, listings: facts.listings }, trade);
}

export async function grade(input, env = process.env) {
  const facts = await collectFacts(input, env);
  const report = scoreFacts(facts);
  if (facts.ai && report.overall != null) {
    const { openingParagraph } = await import('./ai.mjs');
    const { sawLine } = await import('./report.mjs');
    const seen = Object.fromEntries(Object.keys(report.areas).map((k) => [k, sawLine(k, facts, report.areas[k])]));
    report.opening = await openingParagraph(report, facts.businessName, seen).catch((err) => { facts.notes.push(`AI summary failed: ${err.message}`); return null; });
    if (!report.opening) facts.notes.push('AI summary was empty or dropped; the plain summary was used.');
  }
  return { gradedAt: new Date().toISOString(), facts, report };
}
