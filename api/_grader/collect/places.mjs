// Google Places API (New). Needs GOOGLE_PLACES_API_KEY.
import { categoryMatches } from '../score.mjs';

const ENDPOINT = 'https://places.googleapis.com/v1/places:searchText';
const DETAIL_FIELDS = ['id', 'displayName', 'primaryType', 'primaryTypeDisplayName', 'rating', 'userRatingCount',
  'reviews', 'photos', 'regularOpeningHours', 'nationalPhoneNumber', 'websiteUri', 'businessStatus',
  'paymentOptions', 'accessibilityOptions', 'addressComponents', 'formattedAddress'];
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

export const host = (u) => { try { return new URL(/^https?:/.test(u) ? u : `https://${u}`).hostname.replace(/^www\./, '').toLowerCase(); } catch { return null; } };
const norm = (s) => (s || '').toLowerCase().replace(/&/g, 'and').replace(/[^a-z0-9 ]/g, ' ').replace(/\s+/g, ' ').trim();

// Find the business itself. Prefer a result whose website is on the same domain.
export async function findBusiness({ businessName, website, town, state }, key) {
  const where = [town, state].filter(Boolean).join(', ');
  const results = await searchText(where ? `${businessName}, ${where}` : businessName, DETAIL_FIELDS, key);
  const site = host(website);
  return results.find((p) => site && host(p.websiteUri) === site)
    || results.find((p) => norm(p.displayName?.text) === norm(businessName))
    || results.find((p) => norm(p.displayName?.text).includes(norm(businessName)) || norm(businessName).includes(norm(p.displayName?.text)))
    || null;
}

export function stateOf(place) {
  const c = (place.addressComponents || []).find((a) => a.types?.includes('administrative_area_level_1'));
  return c?.shortText || null;
}

export function townOf(place) {
  const c = (place.addressComponents || []).find((a) => a.types?.includes('locality'));
  return c?.longText || null;
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
