import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { letter, positionPoints, scoreAll, scoreProfile, scoreReviews, scoreWebsite, scoreListings } from '../score.mjs';
import { scoreFacts } from '../grade.mjs';
import { getTrade, tradeIds } from '../trades/index.mjs';

const hvac = getTrade('hvac');
const load = (f) => JSON.parse(readFileSync(new URL(`./fixtures/${f}`, import.meta.url)));

test('letters follow the cut-offs', () => {
  assert.equal(letter(93), 'A');
  assert.equal(letter(92), 'A−');
  assert.equal(letter(73), 'C');
  assert.equal(letter(59), 'F');
  assert.equal(letter(null), null);
});

test('search position tiers, including small markets', () => {
  assert.deepEqual([1, 2, 3, 4, 6, 11, 21, 41, 0].map((r) => positionPoints(r, 20)), [40, 36, 36, 30, 22, 12, 4, 0, 0]);
  assert.deepEqual([1, 2, 3, 4].map((r) => positionPoints(r, 4)), [40, 30, 20, 10]);
  assert.equal(positionPoints(null, 20), null);
});

test('fixtures land where expected: strong A, mid around C, weak D or F', () => {
  const strong = scoreFacts(load('hvac-strong.json'));
  const mid = scoreFacts(load('hvac-mid.json'));
  const weak = scoreFacts(load('hvac-weak.json'));
  assert.ok(strong.overall >= 90, `strong ${strong.overall}`);
  assert.ok(mid.overall >= 62 && mid.overall <= 80, `mid ${mid.overall}`);
  assert.ok(weak.overall < 60, `weak ${weak.overall}`);
  assert.ok(['profile', 'website'].includes(weak.weakest), weak.weakest);
});

test('same facts always give the same grade', () => {
  const f = load('hvac-mid.json');
  assert.deepEqual(scoreFacts(f), scoreFacts(structuredClone(f)));
});

test('unmeasured checks are left out, not counted as zero', () => {
  const w = load('hvac-weak.json').website;
  const area = scoreWebsite(w, hvac);
  const speed = area.lines.find((l) => l.id === 'speed');
  assert.equal(speed.measured, false);
  // Same site with a perfect speed score must not score lower than with speed unmeasured... and
  // the unmeasured version is graded out of 80, not 100.
  const measuredMax = area.lines.filter((l) => l.measured).reduce((s, l) => s + l.max, 0);
  assert.equal(measuredMax, 80);
});

test('an area with nothing measured is dropped and the rest re-weighted', () => {
  const f = load('hvac-mid.json');
  const without = scoreAll({ ...f, website: { fetched: false } }, hvac);
  assert.equal(without.areas.website.score, null);
  const { profile, reviews, listings } = without.areas;
  const expected = Math.round((profile.score * 0.30 + reviews.score * 0.25 + listings.score * 0.15) / 0.70);
  assert.equal(without.overall, expected);
});

test('a closed business loses 40 profile points', () => {
  const p = load('hvac-strong.json').profile;
  const open = scoreProfile(p, hvac).score;
  const closed = scoreProfile({ ...p, operational: false }, hvac);
  assert.equal(open - closed.score, 40);
  assert.match(closed.topFix, /open/);
});

test('wrong category gets 3, right category 10', () => {
  const p = load('hvac-strong.json').profile;
  const cat = (c) => scoreProfile({ ...p, primaryCategory: c }, hvac).lines.find((l) => l.id === 'category').points;
  assert.equal(cat({ id: 'hvac_contractor' }), 10);
  assert.equal(cat({ name: 'Air conditioning contractor' }), 10);
  assert.equal(cat({ id: 'plumber', name: 'Plumber' }), 3);
  assert.equal(cat(null), 0);
});

test('reviews compare against local competitors', () => {
  const base = { rating: 4.6, count: 140, newestDays: 5, lowInShown: 0 };
  const alone = scoreReviews(base, hvac).lines;
  const behind = scoreReviews({ ...base, competitors: { n: 3, avgRating: 4.8, avgCount: 610 } }, hvac).lines;
  assert.equal(alone[0].points - behind[0].points, 3); // 0.2 below: −3
  assert.equal(alone[1].points - behind[1].points, 2); // 23% of their count (10–30%): −2
});

test('zero reviews scores zero, not unmeasured', () => {
  assert.equal(scoreReviews({ count: 0 }, hvac).score, 0);
});

test('top fix is the costliest failed criterion', () => {
  const mid = scoreFacts(load('hvac-mid.json'));
  assert.match(mid.areas.listings.topFix, /web search did not turn up/);
  assert.match(mid.areas.reviews.topFix, /140 Google reviews|4\.6/);
});

test('listings fall back to consistency when directory search did not run, with no free points', () => {
  const a = scoreListings({ phoneMatch: true, googleLinksSite: true, facebookLinked: false }, hvac);
  assert.equal(a.fallback, true);
  assert.deepEqual(a.couldNotCheck, ['directories']);
  // Phone 35 + link 20 of the 70 points we could check; directories are left out, not given away.
  assert.equal(a.score, 79);
  const dir = a.lines.find((l) => l.id === 'directories');
  assert.equal(dir.measured, false);
  assert.equal(dir.points, null);
  assert.ok(!a.lines.some((l) => l.id === 'base'));
  // A shop that fails every check we could run gets 0, not the old 30-point floor.
  assert.equal(scoreListings({ phoneMatch: false, googleLinksSite: false, facebookLinked: false }, hvac).score, 0);
});

test('placeholder number becomes a note, not a deduction', () => {
  const a = scoreWebsite(load('hvac-weak.json').website, hvac);
  assert.match(a.notes[0], /placeholder/);
});

test('every trade config loads and has the fields the scorer needs', () => {
  for (const id of tradeIds) {
    const t = getTrade(id);
    for (const k of ['searchQueries', 'categories', 'reviews', 'tradeWords', 'servicePages', 'licensePattern', 'directories']) {
      assert.ok(t[k], `${id}.${k}`);
    }
    assert.ok(Object.keys(t.servicePages).length >= 4);
  }
  assert.throws(() => getTrade('roofing'), /Unknown trade/);
});

test('no overall grade when neither the profile nor the website could be checked', () => {
  const r = scoreAll({ profile: null, reviews: null, website: { fetched: false }, listings: {} }, hvac);
  assert.equal(r.overall, null);
  assert.equal(r.areas.listings.score, null);
});
