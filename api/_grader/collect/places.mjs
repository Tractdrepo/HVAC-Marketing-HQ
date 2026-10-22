// Google Places API (New). Needs GOOGLE_PLACES_API_KEY.
import { categoryMatches } from '../score.mjs';
import { nameMatches, nameWords } from '../names.mjs';
import { STATES } from '../trades/region.mjs';

const ENDPOINT = 'https://places.googleapis.com/v1/places:searchText';
const DETAIL_FIELDS = ['id', 'displayName', 'primaryType', 'primaryTypeDisplayName', 'rating', 'userRatingCount',
  'reviews', 'photos', 'regularOpeningHours', 'nationalPhoneNumber', 'websiteUri', 'businessStatus',
  'paymentOptions', 'accessibilityOptions', 'addressComponents', 'formattedAddress', 'shortFormattedAddress',
  'types', 'pureServiceAreaBusiness', 'location'];
const RANK_FIELDS = ['id', 'displayName', 'rating', 'userRatingCount', 'websiteUri', 'primaryType', 'location'];
// Rank searches read up to three pages (60 results), so a shop past 20th gets its real position.
const RANK_PAGES = 3;

async function searchPage(textQuery, fields, key, extra = {}) {
  const res = await fetch(ENDPOINT, {
    method: 'POST',
    signal: AbortSignal.timeout(10000),
    headers: {
      'content-type': 'application/json',
      'X-Goog-Api-Key': key,
      'X-Goog-FieldMask': [...fields.map((f) => `places.${f}`), 'nextPageToken'].join(','),
    },
    body: JSON.stringify({ textQuery, pageSize: 20, languageCode: 'en', regionCode: 'US', includePureServiceAreaBusinesses: true, ...extra }),
  });
  if (!res.ok) throw new Error(`Places ${res.status}: ${(await res.text()).slice(0, 200)}`);
  const j = await res.json();
  return { places: j.places || [], next: j.nextPageToken || null };
}

async function searchText(textQuery, fields, key, extra = {}) {
  return (await searchPage(textQuery, fields, key, extra)).places;
}

const samePlace = (place) => (p) => p.id === place.id || (place.websiteUri && host(p.websiteUri) === host(place.websiteUri));

// A rank search: pages on until the shop turns up or the pages run out. Google needs a moment before
// a page token works, so later pages wait briefly. Returns the first page too, for the competitors.
export async function rankSearch(query, place, key, extra = {}, { page = searchPage, pages = RANK_PAGES, waitMs = 1500 } = {}) {
  const all = [];
  let first = null;
  let token = null;
  for (let i = 0; i < pages; i++) {
    if (i) await new Promise((r) => setTimeout(r, waitMs));
    let got;
    try { got = await page(query, RANK_FIELDS, key, token ? { ...extra, pageToken: token } : extra); } catch (err) {
      if (!i) throw err;
      break; // a later page failing still leaves a real "not in the first N"
    }
    first ??= got.places;
    all.push(...got.places);
    if (got.places.some(samePlace(place)) || !got.next) break;
    token = got.next;
  }
  const idx = all.findIndex(samePlace(place));
  return { query, rank: idx + 1, marketSize: all.length, results: first || [] };
}

export const host = (u) => { if (!u) return null; try { return new URL(/^https?:/i.test(u) ? u : `https://${u}`).hostname.replace(/^www\./, '').toLowerCase() || null; } catch { return null; } };
const norm = (s) => (s || '').toLowerCase().replace(/&/g, 'and').replace(/[^a-z0-9 ]/g, ' ').replace(/\s+/g, ' ').trim();

// The registrable label of a host: "haddixheatandair" for www.haddixheatandair.com, book.haddixheatandair.com
// or haddixheatandair.co.uk. Shared hosts (Facebook, Wix, Google Sites...) have no label of the shop's own.
const SECOND_LEVEL = new Set(['co', 'com', 'net', 'org', 'gov', 'edu', 'ac']);
const SHARED_HOSTS = new Set(['facebook', 'google', 'business', 'wixsite', 'godaddysites', 'square', 'weebly', 'wordpress',
  'blogspot', 'squarespace', 'yelp', 'linktr', 'instagram', 'nextdoor', 'angi', 'homeadvisor', 'bbb', 'thumbtack', 'site', 'carrd', 'vercel', 'netlify']);
export function domainLabel(h) {
  const parts = (h || '').toLowerCase().replace(/\.$/, '').split('.').filter(Boolean);
  if (parts.length < 2) return '';
  const i = parts.length >= 3 && SECOND_LEVEL.has(parts[parts.length - 2]) && parts[parts.length - 1].length === 2 ? parts.length - 3 : parts.length - 2;
  const label = parts[i];
  return SHARED_HOSTS.has(label) ? '' : label;
}

// Words that only say what kind of shop it is. "Haddix" and "Haddix Heating & Air" are the same shop;
// "Haddix" and "Haddix Plumbing Supply" are not, because "supply" says something more.
export const GENERIC_NAME_WORDS = new Set(['heating', 'air', 'cooling', 'conditioning', 'hvac', 'ac', 'plumbing',
  'services', 'service', 'company', 'co', 'llc', 'inc', 'and', 'mechanical', 'refrigeration']);
const nameTokens = (s) => (s || '').toLowerCase().replace(/\ba\/c\b/g, 'ac').replace(/&/g, ' and ').replace(/[^a-z0-9]+/g, ' ')
  .trim().split(' ').filter(Boolean)
  .map((w) => (w === 'heat' ? 'heating' : w)); // "Heat & Air" and "Heating & Air" are the same words

// True when two business names are the same shop typed differently: one contains the other with most of
// its length (the old rule), or one name's words are all in the other and every leftover word is a
// generic trade word. The shared words must include at least one that isn't generic.
export function sameBusinessName(a, b) {
  const na = norm(a);
  const nb = norm(b);
  if (!na || !nb) return false;
  if (na === nb) return true;
  if ((na.includes(nb) || nb.includes(na)) && Math.min(na.length, nb.length) >= 0.6 * Math.max(na.length, nb.length)) return true;
  const ta = nameTokens(a);
  const tb = nameTokens(b);
  const [short, long] = ta.length <= tb.length ? [ta, tb] : [tb, ta];
  if (!short.some((w) => !GENERIC_NAME_WORDS.has(w))) return false;
  const left = [...long];
  for (const w of short) {
    const i = left.indexOf(w);
    if (i < 0) return false;
    left.splice(i, 1);
  }
  return left.every((w) => GENERIC_NAME_WORDS.has(w));
}

// Google types that say "a trade contractor". A service-area shop with its address hidden still has these.
const TRADE_TYPES = new Set(['hvac_contractor', 'air_conditioning_contractor', 'heating_contractor',
  'air_conditioning_repair_service', 'furnace_repair_service', 'plumber', 'electrician', 'general_contractor']);
function tradeTyped(p, trade) {
  const types = [p.primaryType, ...(p.types || [])].filter(Boolean).map((t) => String(t).toLowerCase());
  if (types.some((t) => TRADE_TYPES.has(t) || trade?.categories?.typeIds?.includes(t))) return true;
  const shown = (p.primaryTypeDisplayName?.text || '').toLowerCase();
  return Boolean(shown) && (Boolean(trade?.categories?.names?.includes(shown))
    || /\b(hvac|heating|air conditioning|plumb\w*|electric\w*|general contractor)\b/.test(shown));
}

// The shop's distinctive name words ("haddix" in "Haddix Heating & Air"), for comparing domain labels.
function distinctiveWords(businessName, trade, town) {
  const words = trade ? nameWords(businessName, trade, town) : nameTokens(businessName).filter((w) => !GENERIC_NAME_WORDS.has(w));
  return words.filter((w) => w.length >= 4);
}

// Pick the shop out of one set of search results.
// A website match wins anywhere: the same host, or the same registrable label on another subdomain or
// path. A name-only match must be in the state the shop gave us. Service-area shops often hide their
// address, so Google gives no address or only "Waco, TX" or "Texas": with no state to read, a name
// match also needs one more sign it's the shop (the typed town in its address, a website on the shop's
// domain or one carrying the shop's name word like haddixhvac.com, or a trade category with a strict
// name match). A candidate whose address is clearly in another state is never taken on its name.
export function pickPlace(all, input, trade) {
  const m = placeMatcher(input, trade);
  return all.find((p) => m.site && host(p.websiteUri) === m.site)
    || all.find((p) => m.sameDomain(p))
    || all.find((p) => m.nameOk(p, (q) => norm(q.displayName?.text) === norm(input.businessName)))
    || all.find((p) => m.nameOk(p, (q) => sameBusinessName(q.displayName?.text, input.businessName)))
    || (trade && all.find((p) => m.nameOk(p, m.looseName)))
    || null;
}

// The checks pickPlace runs, shared with rejectReason so the team's debug note says why a candidate lost.
function placeMatcher({ businessName, website, town, state }, trade) {
  const label = domainLabel(host(website));
  // A shop whose "website" is a Facebook page or similar shares its host with everyone else there.
  const site = label ? host(website) : null;
  const st = (state || '').trim().toUpperCase();
  const townN = norm(town);
  const words = label ? distinctiveWords(businessName, trade, town) : [];

  const strictName = (p) => norm(p.displayName?.text) === norm(businessName) || sameBusinessName(p.displayName?.text, businessName);
  const looseName = (p) => strictName(p)
    || Boolean(trade && nameMatches(`${p.displayName?.text} ${host(p.websiteUri) || ''}`, businessName, trade, town, { slugMin: 4 }));
  // The name on the profile itself, without its website: an alt domain can back this, not stand in for it.
  const shownName = (p) => strictName(p) || Boolean(trade && nameMatches(p.displayName?.text, businessName, trade, town, { slugMin: 4 }));

  const inTown = (p) => Boolean(townN) && [p.formattedAddress, p.shortFormattedAddress, townOf(p)]
    .some((a) => ` ${norm(a)} `.includes(` ${townN} `));
  const sameDomain = (p) => Boolean(label) && domainLabel(host(p.websiteUri)) === label;
  const altDomain = (p) => {
    const theirs = domainLabel(host(p.websiteUri));
    return Boolean(theirs) && words.some((w) => theirs.includes(w) && label.includes(w));
  };
  // Name-only candidates: same state (or no state typed) → name is enough; no readable state → name
  // plus another sign; another state → never.
  const extraSign = (p) => inTown(p) || sameDomain(p) || (altDomain(p) && shownName(p)) || (tradeTyped(p, trade) && strictName(p));
  const nameOk = (p, match) => {
    const theirs = stateOf(p);
    if (!st || theirs) return (!st || theirs.toUpperCase() === st) && match(p);
    if (!match(p)) return false;
    return extraSign(p);
  };
  return { site, st, strictName, looseName, sameDomain, nameOk, extraSign };
}

// One word for why pickPlace passed over a candidate: "name" (not the shop's name), "state" (named
// right but its address is in another state), "no-evidence" (named right, no state to read and nothing
// else backing it), or "match" if it would in fact be picked.
export function rejectReason(p, input, trade) {
  const m = placeMatcher(input, trade);
  if ((m.site && host(p.websiteUri) === m.site) || m.sameDomain(p)) return 'match';
  const named = trade ? m.looseName(p) : m.strictName(p);
  if (!named) return 'name';
  if (m.nameOk(p, trade ? m.looseName : m.strictName)) return 'match';
  const theirs = stateOf(p);
  if (m.st && theirs && theirs.toUpperCase() !== m.st) return 'state';
  return 'no-evidence';
}

// What the team's debug note shows of one candidate. Only fields Google returned; no keys or URLs.
export function candidateSummary(p, input, trade) {
  return {
    name: p.displayName?.text || null,
    address: p.formattedAddress || p.shortFormattedAddress || null,
    host: host(p.websiteUri),
    type: p.primaryType || null,
    reviews: p.userRatingCount ?? null,
    serviceArea: typeof p.pureServiceAreaBusiness === 'boolean' ? p.pureServiceAreaBusiness : null,
    reason: rejectReason(p, input, trade),
  };
}

// The searches we try, in order. "<name> HVAC <town>" finds shops whose typed name is shorter than
// their Google name ("Haddix" for "Haddix Heating & Air").
export function lookupQueries({ businessName, website, town, state }, trade) {
  const where = [town, state].filter(Boolean).join(', ');
  const kind = trade?.label || 'HVAC';
  const withKind = new RegExp(`\\b${kind}\\b`, 'i').test(businessName || '') ? null : `${businessName} ${kind}${where ? ` ${where}` : ''}`;
  return [...new Set([where ? `${businessName}, ${where}` : businessName, businessName && withKind, host(website), businessName].filter(Boolean))];
}

// Find the business itself. Owners type their name a little differently than Google shows it
// ("Heating and Air" vs "Heat & Air", or just "Haddix"), and profiles often link a different page or
// domain, so match on the distinctive name words too. A Places error on one search doesn't stop the
// others; if nothing matched and a search errored, the error is thrown so the run is marked partial.
// trace, when given, gets one entry per search tried: { query, count, candidates (top 5), error }, so
// a run that finds nothing can show the team what Google returned. The error is a one-word kind only.
export async function findBusiness(input, key, trade, { search = searchText, trace = null } = {}) {
  let error = null;
  for (const q of lookupQueries(input, trade)) {
    let all;
    try { all = await search(q, DETAIL_FIELDS, key); } catch (err) {
      error ??= err;
      trace?.push({ query: q, count: 0, candidates: [], error: true });
      continue;
    }
    const found = pickPlace(all, input, trade);
    trace?.push({ query: q, count: all.length, candidates: all.slice(0, 5).map((p) => candidateSummary(p, input, trade)), matched: Boolean(found) });
    if (found) return found;
  }
  if (error) throw error;
  return null;
}

// The place's state: from its address parts, else read off the end of its address ("Waco, TX 76701, USA",
// "Waco, TX" or "Texas, USA"). Null when Google gives no address or none with a state in it.
export function stateOf(place) {
  const c = (place.addressComponents || []).find((a) => a.types?.includes('administrative_area_level_1'));
  if (c?.shortText) return c.shortText;
  for (const a of [place.formattedAddress, place.shortFormattedAddress]) {
    const s = addressState(a);
    if (s) return s;
  }
  return null;
}

const STATE_BY_NAME = new Map(Object.entries(STATES).map(([abbr, name]) => [name.toLowerCase(), abbr]));
export function addressState(address) {
  const parts = String(address || '').split(',').map((x) => x.trim()).filter(Boolean);
  if (parts.length && /^(usa|us|united states( of america)?)$/i.test(parts[parts.length - 1])) parts.pop();
  const last = parts[parts.length - 1];
  if (!last) return null;
  const m = last.match(/^([A-Za-z]{2})(?:\s+\d{5}(?:-\d{4})?)?$/);
  if (m && STATES[m[1].toUpperCase()]) return m[1].toUpperCase();
  const named = last.replace(/\s+\d{5}(?:-\d{4})?$/, '').toLowerCase();
  return STATE_BY_NAME.get(named) || null;
}

export function townOf(place) {
  const c = (place.addressComponents || []).find((a) => a.types?.includes('locality'));
  return c?.longText || null;
}

// Google's Places API (New) only returns the five "most relevant" reviews, which can be months old
// for a shop that gets reviews every week. The older Place Details endpoint can sort by newest.
// Needs "Places API" (not only "Places API (New)") enabled on the key; returns null when it isn't.
export async function newestReviewDays(placeId, key, { now = Date.now() } = {}) {
  try {
    const u = `https://maps.googleapis.com/maps/api/place/details/json?place_id=${encodeURIComponent(placeId)}&fields=reviews&reviews_sort=newest&key=${encodeURIComponent(key)}`;
    const res = await fetch(u, { signal: AbortSignal.timeout(8000) });
    const j = await res.json();
    if (j.status !== 'OK') return { days: null, error: `${j.status}${j.error_message ? `: ${j.error_message.slice(0, 120)}` : ''}` };
    const list = j.result?.reviews || [];
    // OK with no reviews is an answer, not a failure: there is nothing to date.
    if (!list.length) return { days: null, noReviews: true };
    const t = Math.max(...list.map((r) => (r.time || 0) * 1000));
    if (!(Number.isFinite(t) && t > 0)) return { days: null, error: 'reviews came back without dates' };
    return { days: Math.max(0, Math.floor((now - t) / 86400000)) };
  } catch (err) {
    return { days: null, error: err.message };
  }
}

// Rank among every HVAC shop within the area radius of the shop itself. Small-town shops serve the towns
// around them, and "HVAC near [tiny town]" makes almost anyone first. Service-area shops hide their
// location, so center is the fallback: the middle of the shops in their own town search.
export async function areaRank(query, place, key, radiusM = 32000, center = null, opts = {}) {
  const c = place.location || center;
  if (!c) return null;
  const r = await rankSearch(query, place, key, {
    locationBias: { circle: { center: { latitude: c.latitude, longitude: c.longitude }, radius: radiusM } },
  }, opts);
  return { ...r, area: true };
}

// The middle of a set of search results, for centering the area search on a service-area shop's town.
export function centerOf(results) {
  const pts = (results || []).map((p) => p.location).filter((l) => Number.isFinite(l?.latitude) && Number.isFinite(l?.longitude));
  if (!pts.length) return null;
  return { latitude: pts.reduce((s, l) => s + l.latitude, 0) / pts.length, longitude: pts.reduce((s, l) => s + l.longitude, 0) / pts.length };
}

// Rank of the place in a local search, reading up to 60 results.
export async function localRank(query, place, key, opts = {}) {
  return rankSearch(query, place, key, {}, opts);
}

// Types Google's data gives a trade shop whatever its profile shows. They say nothing about the category.
const BROAD_TYPES = new Set(['general_contractor', 'service', 'establishment', 'point_of_interest', 'store']);

// Turn the Places record and local searches into profile and review facts.
export function placeFacts(place, searches, trade, { now = Date.now(), website } = {}) {
  const businessName = norm(place.displayName?.text);
  // Google's data hands over at most ten photos, so ten means "ten or more".
  const photos = place.photos || [];
  const shownFirst = photos.slice(0, 10);
  const byBusiness = shownFirst.filter((ph) => (ph.authorAttributions || []).some((a) => norm(a.displayName) === businessName)).length;

  const reviews = place.reviews || [];
  const newest = reviews.map((r) => Date.parse(r.publishTime)).filter(Number.isFinite).sort((a, b) => b - a)[0];

  // Competitors: first three other businesses in the first search with the right category or a rating.
  const first = searches[0];
  const others = (first?.results || []).filter((p) => p.id !== place.id && p.userRatingCount > 0).slice(0, 3);
  const competitors = others.length ? {
    n: others.length,
    names: others.map((p) => p.displayName?.text),
    avgRating: others.reduce((s, p) => s + (p.rating || 0), 0) / others.length,
    avgCount: others.reduce((s, p) => s + (p.userRatingCount || 0), 0) / others.length,
  } : null;

  return {
    profile: {
      found: true,
      name: place.displayName?.text,
      searches: searches.map(({ query, rank, marketSize }) => ({ query, rank, marketSize })),
      photos: { count: photos.length, byBusiness, capped: photos.length >= 10 },
      linksToSite: website ? host(place.websiteUri) === host(website) : Boolean(place.websiteUri),
      // Google's data files most trade shops under a broad type ("General contractor") even when the profile
      // shows "HVAC contractor", so a broad type means we can't see the real category: left out, not graded.
      categoryHidden: BROAD_TYPES.has(place.primaryType),
      primaryCategory: (place.primaryType || place.primaryTypeDisplayName) && !BROAD_TYPES.has(place.primaryType)
        ? { id: place.primaryType || null, name: place.primaryTypeDisplayName?.text || place.primaryType } : null,
      categoryOk: categoryMatches({ id: place.primaryType, name: place.primaryTypeDisplayName?.text }, trade),
      hasHours: Boolean(place.regularOpeningHours?.weekdayDescriptions?.length || place.regularOpeningHours?.periods?.length),
      paymentListed: place.paymentOptions ? Object.keys(place.paymentOptions).length > 0 : false,
      // A service-area shop has no storefront to describe, so accessibility doesn't apply.
      accessibilityListed: place.pureServiceAreaBusiness ? null : place.accessibilityOptions ? Object.keys(place.accessibilityOptions).length > 0 : false,
      hasPhone: Boolean(place.nationalPhoneNumber),
      operational: place.businessStatus ? place.businessStatus === 'OPERATIONAL' : null,
      phone: place.nationalPhoneNumber || null,
      websiteUri: place.websiteUri || null,
    },
    reviews: {
      rating: place.rating ?? null,
      count: place.userRatingCount ?? 0,
      newestDays: newest ? Math.floor((now - newest) / 86400000) : null,
      lowInShown: reviews.length ? reviews.filter((r) => r.rating <= 3).length : null,
      shownText: reviews.map((r) => ({ rating: r.rating, text: r.text?.text || r.originalText?.text || '' })),
      competitors,
    },
  };
}
