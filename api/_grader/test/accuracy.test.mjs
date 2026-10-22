// Report card accuracy fixes from the Sagan Heating and Air test (22 Oct 2026).
import test from 'node:test';
import assert from 'node:assert/strict';
import hvac from '../trades/hvac.mjs';
import { scoreProfile } from '../score.mjs';
import { placeFacts, rankSearch, centerOf } from '../collect/places.mjs';
import { greetName, bookLines, repeatLines, sawLine, TEXTING_LIVE } from '../report.mjs';
import { place } from './helpers.mjs';

const sab = (over = {}) => ({
  ...place({ name: 'Sagan Heating and Air Conditioning', website: 'http://www.saganair.com/', reviews: 80, rating: 5 }),
  primaryType: 'general_contractor', primaryTypeDisplayName: { text: 'General contractor' },
  pureServiceAreaBusiness: true, location: undefined,
  photos: Array.from({ length: 10 }, () => ({ authorAttributions: [{ displayName: 'Sagan Heating and Air Conditioning' }] })),
  ...over,
});

test('a broad Google type ("General contractor") is not graded or shown as the category', () => {
  const { profile } = placeFacts(sab(), [], hvac, { website: 'saganair.com' });
  assert.equal(profile.categoryHidden, true);
  assert.equal(profile.primaryCategory, null);
  const cat = scoreProfile(profile, hvac).lines.find((l) => l.id === 'category');
  assert.equal(cat.measured, false);
  assert.doesNotMatch(sawLine('profile', { profile }, {}), /General contractor/i);
});

test('a real HVAC category still scores, a wrong specific one still loses points', () => {
  const ok = placeFacts({ ...sab(), primaryType: 'hvac_contractor', primaryTypeDisplayName: { text: 'HVAC contractor' } }, [], hvac).profile;
  assert.equal(scoreProfile(ok, hvac).lines.find((l) => l.id === 'category').points, 10);
  const off = placeFacts({ ...sab(), primaryType: 'roofing_contractor', primaryTypeDisplayName: { text: 'Roofing contractor' } }, [], hvac).profile;
  assert.equal(scoreProfile(off, hvac).lines.find((l) => l.id === 'category').points, 3);
});

test('service-area shops are not marked down for accessibility', () => {
  const { profile } = placeFacts(sab({ paymentOptions: { acceptsCreditCards: true } }), [], hvac);
  assert.equal(profile.accessibilityListed, null);
  assert.equal(scoreProfile(profile, hvac).lines.find((l) => l.id === 'details').points, 10);
});

test('photos: ten from Google reads as "at least 10", all posted by the shop', () => {
  const { profile } = placeFacts(sab(), [], hvac);
  const saw = sawLine('profile', { profile }, {});
  assert.match(saw, /at least 10 photos, all posted by you/);
  assert.doesNotMatch(saw, /\(10 yours\)/);
});

test('rank search pages past 20 and reports the real position', async () => {
  const me = { id: 'me' };
  const pages = [
    { places: Array.from({ length: 20 }, (_, i) => ({ id: `a${i}`, location: { latitude: 31.5, longitude: -97.1 } })), next: 't1' },
    { places: Array.from({ length: 20 }, (_, i) => ({ id: i === 0 ? 'me' : `b${i}` })), next: 't2' },
  ];
  let n = 0;
  const r = await rankSearch('HVAC near Waco, TX', me, 'k', {}, { page: async () => pages[n++], waitMs: 0 });
  assert.equal(r.rank, 21);
  assert.equal(n, 2, 'stops paging once found');
  assert.equal(r.results.length, 20, 'competitors come from the first page');
  const c = centerOf(r.results);
  assert.ok(Math.abs(c.latitude - 31.5) < 1e-9 && Math.abs(c.longitude + 97.1) < 1e-9);
});

test('greeting keeps short names like LT and fixes case', () => {
  assert.equal(greetName('LT'), 'LT');
  assert.equal(greetName('J'), '');
  assert.equal(greetName('logan'), 'Logan');
  assert.equal(greetName('Mary Jo'), 'Mary Jo');
  assert.equal(greetName('a@b.com'), '');
});

test('book box reads cleanly and does not sell text-back as live before texting is approved', () => {
  const [saw, how] = bookLines({ b: { k: 'form', c: false, t: true } });
  assert.match(saw, /found a contact form and a tap-to-call number, but no online booking or chat\./);
  if (!TEXTING_LIVE) {
    assert.match(how, /goes live in the next couple of weeks/);
    assert.doesNotMatch(how, /every missed call gets a text/i);
    assert.doesNotMatch(repeatLines({ rv: { n: 80, d: null } })[1], /\btexts?\b/);
  }
});

test('missing payment options are "couldn\'t see", and the area search reads as a ranking, not a typed search', () => {
  const { profile } = placeFacts(sab(), [{ query: 'HVAC businesses within 30 miles of Waco', rank: 12, marketSize: 20, area: true }], hvac);
  assert.equal(profile.paymentListed, null);
  const area = scoreProfile(profile, hvac);
  assert.equal(area.lines.find((l) => l.id === 'details').measured, false);
  assert.match(sawLine('profile', { profile }, area), /12th among HVAC businesses within 30 miles of Waco/);
  assert.match(area.topFix, /^Move up among HVAC businesses within 30 miles of Waco; today you are 12th\.$/);
});
