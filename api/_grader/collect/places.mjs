// Google Places API (New). Needs GOOGLE_PLACES_API_KEY.
import { categoryMatches } from '../score.mjs';
import { nameMatches } from '../names.mjs';

const ENDPOINT = 'https://places.googleapis.com/v1/places:searchText';
const DETAIL_FIELDS = ['id', 'displayName', 'primaryType', 'primaryTypeDisplayName', 'rating', 'userRatingCount',
  'reviews', 'photos', 'regularOpeningHours', 'nationalPhoneNumber', 'websiteUri', 'businessStatus',
  'paymentOptions', 'accessibilityOptions', 'addressComponents', 'formattedAddress', 'location'];
const RANK_FIELDS = ['id', 'displayName', 'rating', 'userRatingCount', 'websiteUri', 'primaryType'];

async function searchText(textQuery, fields, key, extra = {}) {
  const res = await fetch(ENDPOINT, {
    method: 'POST',
    signal: AbortSignal.timeout(10000),
    headers: {
      'content-type': 'application/json',
      'X-Goog-Api-Key': key,
      'X-Goog-FieldMask': fields.map((f) => `places.${f}`).join(','),
    },
    body: JSON.stringify({ textQuery, pageSize: 20, languageCode: 'en', regionCode: 'US', ...extra }),
  });
  if (!res.ok) throw new Error(`Places ${res.status}: ${(await res.text()).slice(0, 200)}`);
  return (await res.json()).places || [];
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

// Pick the shop out of one set of search results.
// A website match wins anywhere: the same host, or the same registrable label on another subdomain or
// path. A name-only match must be in the state the shop gave us.
export function pickPlace(all, { businessName, website, town, state }, trade) {
  const label = domainLabel(host(website));
  // A shop whose "website" is a Facebook page or similar shares its host with everyone else there.
  const site = label ? host(website) : null;
  const st = (state || '').trim().toUpperCase();
  const inState = (p) => !st || !stateOf(p) || stateOf(p).toUpperCase() === st;
  const results = all.filter(inState);
  return all.find((p) => site && host(p.websiteUri) === site)
    || all.find((p) => label && domainLabel(host(p.websiteUri)) === label)
    || results.find((p) => norm(p.displayName?.text) === norm(businessName))
    || results.find((p) => sameBusinessName(p.displayName?.text, businessName))
    || (trade && results.find((p) => nameMatches(`${p.displayName?.text} ${host(p.websiteUri) || ''}`, businessName, trade, town, { slugMin: 4 })))
    || null;
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
export async function findBusiness(input, key, trade, { search = searchText } = {}) {
  let error = null;
  for (const q of lookupQueries(input, trade)) {
    let all;
    try { all = await search(q, DETAIL_FIELDS, key); } catch (err) { error ??= err; continue; }
    const found = pickPlace(all, input, trade);
    if (found) return found;
  }
  if (error) throw error;
  return null;
}

export function stateOf(place) {
  const c = (place.addressComponents || []).find((a) => a.types?.includes('administrative_area_level_1'));
  return c?.shortText || null;
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
    const t = Math.max(...(j.result?.reviews || []).map((r) => (r.time || 0) * 1000));
    return { days: Number.isFinite(t) && t > 0 ? Math.max(0, Math.floor((now - t) / 86400000)) : null };
  } catch (err) {
    return { days: null, error: err.message };
  }
}

// Rank among every HVAC shop within about 20 miles of the shop itself. Small-town shops serve the towns
// around them, and "HVAC near [tiny town]" makes almost anyone first.
export async function areaRank(query, place, key, radiusM = 32000) {
  if (!place.location) return null;
  const results = await searchText(query, RANK_FIELDS, key, {
    locationBias: { circle: { center: { latitude: place.location.latitude, longitude: place.location.longitude }, radius: radiusM } },
  });
  const idx = results.findIndex((p) => p.id === place.id || (place.websiteUri && host(p.websiteUri) === host(place.websiteUri)));
  return { query, rank: idx + 1, marketSize: results.length, results, area: true };
}

// Rank of the place in a local search. Searches once more if missing (Google's order shifts).
export async function localRank(query, place, key) {
  let results;
  let idx = -1;
  for (let attempt = 0; attempt < 2 && idx < 0; attempt++) {
    results = await searchText(query, RANK_FIELDS, key);
    idx = results.findIndex((p) => p.id === place.id || (place.websiteUri && host(p.websiteUri) === host(place.websiteUri)));
  }
  return { query, rank: idx + 1, marketSize: results.length, results };
}

// Turn the Places record and local searches into profile and review facts.
export function placeFacts(place, searches, trade, { now = Date.now(), website } = {}) {
  const businessName = norm(place.displayName?.text);
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
      photos: { count: photos.length, byBusiness },
      linksToSite: website ? host(place.websiteUri) === host(website) : Boolean(place.websiteUri),
      primaryCategory: place.primaryType || place.primaryTypeDisplayName
        ? { id: place.primaryType || null, name: place.primaryTypeDisplayName?.text || place.primaryType } : null,
      categoryOk: categoryMatches({ id: place.primaryType, name: place.primaryTypeDisplayName?.text }, trade),
      hasHours: Boolean(place.regularOpeningHours?.weekdayDescriptions?.length || place.regularOpeningHours?.periods?.length),
      paymentListed: place.paymentOptions ? Object.keys(place.paymentOptions).length > 0 : false,
      accessibilityListed: place.accessibilityOptions ? Object.keys(place.accessibilityOptions).length > 0 : false,
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
