// Test helpers: Google Places candidates and a stand-in for fetch, so nothing touches the network.
import { readFileSync } from 'node:fs';

export const sampleHome = readFileSync(new URL('./fixtures/sample-home.html', import.meta.url), 'utf8');

// A Places (New) result as searchText returns it.
export function place({ id, name, website = null, state = 'TX', town = 'Waco', reviews = 0, rating = 4.8 }) {
  return {
    id: id || name.toLowerCase().replace(/[^a-z0-9]+/g, '-'),
    displayName: { text: name },
    websiteUri: website,
    primaryType: 'hvac_contractor',
    primaryTypeDisplayName: { text: 'HVAC contractor' },
    rating,
    userRatingCount: reviews,
    nationalPhoneNumber: '(254) 777-0142',
    businessStatus: 'OPERATIONAL',
    regularOpeningHours: { weekdayDescriptions: ['Monday: Open 24 hours'] },
    addressComponents: [
      { longText: town, shortText: town, types: ['locality'] },
      { longText: state, shortText: state, types: ['administrative_area_level_1'] },
    ],
    location: { latitude: 31.55, longitude: -97.15 },
    reviews: [],
    photos: [],
  };
}

const json = (body, status = 200) => ({ ok: status < 400, status, url: '', json: async () => body, text: async () => JSON.stringify(body) });

// Replace global fetch for one test. places(query) returns the candidates for a Places text search (or
// throws to simulate a Places error). Returns the list of calls and a restore function.
export function stubFetch({ places = () => [], home = sampleHome } = {}) {
  const real = globalThis.fetch;
  const calls = [];
  globalThis.fetch = async (url, opts = {}) => {
    const u = String(url);
    const body = opts.body && typeof opts.body === 'string' && opts.body.startsWith('{') ? JSON.parse(opts.body) : opts.body;
    calls.push({ url: u, body });
    if (u.startsWith('https://places.googleapis.com/')) {
      try { return json({ places: await places(body.textQuery) }); } catch (err) { return json({ error: err.message }, 500); }
    }
    if (u.startsWith('https://maps.googleapis.com/')) return json({ status: 'REQUEST_DENIED' });
    if (u.startsWith('https://www.googleapis.com/pagespeedonline/')) return json({}, 429);
    if (u.startsWith('https://challenges.cloudflare.com/')) return json({ success: true });
    if (u.startsWith('https://api.resend.com/')) return json({ id: 'test' });
    // Home page and blog fetches.
    return { ok: true, status: 200, url: u, text: async () => home, json: async () => ({}) };
  };
  return { calls, restore: () => { globalThis.fetch = real; } };
}
