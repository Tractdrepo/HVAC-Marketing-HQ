import test from 'node:test';
import assert from 'node:assert/strict';
import { newestReviewNote, collectFacts } from '../grade.mjs';
import { newestReviewDays } from '../collect/places.mjs';
import { place, stubFetch } from './helpers.mjs';

test('service-area shops get a plain note, not "turn on Places API"', () => {
  const n = newestReviewNote({ days: null, serviceArea: true });
  assert.match(n, /doesn't return service-area profiles/);
  assert.doesNotMatch(n, /public address/);
  assert.doesNotMatch(n, /turn on/);
});

test('NOT_FOUND from the older endpoint is not blamed on the key', () => {
  const n = newestReviewNote({ days: null, error: 'NOT_FOUND: The provided Place ID is no longer valid.' });
  assert.doesNotMatch(n, /turn on/);
  assert.match(n, /5 reviews Google shows/);
});

test('REQUEST_DENIED still says to turn on Places API', () => {
  assert.match(newestReviewNote({ days: null, error: 'REQUEST_DENIED: not enabled' }), /turn on "Places API"/);
});

const env = { GOOGLE_PLACES_API_KEY: 'test-key' };
const input = { businessName: 'Brazos Air', website: 'brazosair.com', town: 'Waco, TX', trade: 'hvac', ai: false };
const shop = (extra = {}) => ({ ...place({ name: 'Brazos Air', website: 'https://brazosair.com/', reviews: 40 }), ...extra });
const detailsCalls = (calls) => calls.filter((c) => c.url.startsWith('https://maps.googleapis.com/maps/api/place/details/'));
const reviewNotes = (facts) => facts.notes.filter((n) => /newest|review age/i.test(n));

test('older endpoint answers OK with zero reviews: noReviews, not an undefined error', async () => {
  const f = stubFetch({ details: () => ({ status: 'OK', result: {} }) });
  try {
    const r = await newestReviewDays('abc', 'k');
    assert.deepEqual(r, { days: null, noReviews: true });
    const n = newestReviewNote(r);
    assert.doesNotMatch(n, /undefined/);
    assert.doesNotMatch(n, /failed/);
  } finally { f.restore(); }
});

test('a note with no error never prints "(undefined)"', () => {
  assert.doesNotMatch(newestReviewNote({ days: null }), /undefined/);
});

test('a profile with 0 reviews gets no review-age note', async () => {
  const f = stubFetch({ places: () => [shop({ userRatingCount: 0 })], details: () => ({ status: 'OK', result: {} }) });
  try {
    const facts = await collectFacts(input, env);
    assert.deepEqual(reviewNotes(facts), []);
    assert.ok(!facts.notes.some((n) => /undefined/.test(n)));
  } finally { f.restore(); }
});

test('a service-area shop with 0 reviews gets no review-age note', async () => {
  const f = stubFetch({ places: () => [shop({ userRatingCount: 0, pureServiceAreaBusiness: true })] });
  try {
    const facts = await collectFacts(input, env);
    assert.deepEqual(reviewNotes(facts), []);
  } finally { f.restore(); }
});

test('a service-area shop skips the older review lookup (no Place Details call)', async () => {
  const f = stubFetch({ places: () => [shop({ pureServiceAreaBusiness: true })], details: () => { throw new Error('must not be called'); } });
  try {
    const facts = await collectFacts(input, env);
    assert.equal(detailsCalls(f.calls).length, 0);
    assert.ok(reviewNotes(facts).some((n) => /service-area profiles/.test(n)));
  } finally { f.restore(); }
});

test('a shop with a public address does call the older review lookup', async () => {
  const now = Math.floor(Date.now() / 1000);
  const f = stubFetch({ places: () => [shop({ pureServiceAreaBusiness: false })], details: () => ({ status: 'OK', result: { reviews: [{ time: now - 3 * 86400 }] } }) });
  try {
    const facts = await collectFacts(input, env);
    assert.equal(detailsCalls(f.calls).length, 1);
    assert.equal(facts.reviews.newestDays, 3);
    assert.deepEqual(reviewNotes(facts), []);
  } finally { f.restore(); }
});
