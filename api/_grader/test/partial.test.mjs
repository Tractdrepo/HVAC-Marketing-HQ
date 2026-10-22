// Partial runs: a failed AI step, a Places error, or no Google profile for a shop that gave its name and
// website must not reach the shop as a graded report.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { collectFacts, grade, scoreFacts } from '../grade.mjs';
import { holdReason } from '../report.mjs';
import { scoreAll, scoreProfile } from '../score.mjs';
import { getTrade } from '../trades/index.mjs';
import { place, stubFetch } from './helpers.mjs';

const hvac = getTrade('hvac');
const env = { GOOGLE_PLACES_API_KEY: 'test-key' };
const haddixInput = { businessName: 'Haddix', website: 'haddixheatandair.com', town: 'Waco, TX', trade: 'hvac', ai: false };
const desert = place({ name: 'Desert West Air Conditioning', website: 'https://dwsnv.com/', state: 'NV', town: 'Las Vegas', reviews: 900 });
const desertInput = { businessName: 'Desert West', website: 'dwsnv.com', town: 'Las Vegas, NV', trade: 'hvac', ai: false };

// An ai.mjs stand-in. Pass the names of steps that should throw.
const fakeAi = (broken = []) => {
  const step = (name, value) => async () => { if (broken.includes(name)) throw new Error(`Anthropic 529 overloaded (${name})`); return value; };
  return {
    titleVerdict: step('titleVerdict', 'clear'),
    directorySearch: step('directorySearch', { found: ['Yelp'], checked: ['Yelp', 'BBB'], model: 'test' }),
    reviewThemes: step('reviewThemes', { praise: 'fast service', complaint: null }),
    openingParagraph: step('openingParagraph', 'A short summary.'),
  };
};

test('profile not found scores null and is left out of the weighting, not 0', () => {
  const p = scoreProfile({ found: false }, hvac);
  assert.equal(p.score, null);
  assert.equal(p.notFound, true);
  const website = { fetched: true, pageCount: 10, serviceTopics: ['AC repair', 'heating', 'installation', 'maintenance plan'], areaPages: ['a', 'b', 'c'],
    booking: true, https: true, mobileViewport: true, tapToCall: true, emergency: true, financing: true, license: true, chat: true, schema: true, reviewsOnSite: true, faq: true,
    titleVerdict: 'clear', blog: { found: true, newestDays: 10 } };
  const withMissing = scoreAll({ profile: { found: false }, reviews: null, website, listings: null }, hvac);
  const websiteOnly = scoreAll({ profile: null, reviews: null, website, listings: null }, hvac);
  assert.equal(withMissing.overall, websiteOnly.overall);
  assert.equal(withMissing.overall, withMissing.areas.website.score);
});

test('no profile for a shop that gave a name and website: partial, with the failure listed', async () => {
  const f = stubFetch({ places: () => [] });
  try {
    const facts = await collectFacts(haddixInput, env);
    assert.equal(facts.partial, true);
    assert.deepEqual(facts.failures, ['No Google profile found for this name and website.']);
    assert.equal(scoreFacts(facts).areas.profile.score, null);
  } finally { f.restore(); }
});

test('no profile when the shop gave no website is a note, not a failure', async () => {
  const f = stubFetch({ places: () => [] });
  try {
    const facts = await collectFacts({ ...haddixInput, businessName: '' }, env);
    assert.ok(!facts.failures.some((x) => /No Google profile/.test(x)));
    assert.ok(facts.notes.some((x) => /No Google profile/.test(x)));
  } finally { f.restore(); }
});

test('a Places error makes the run partial', async () => {
  const f = stubFetch({ places: () => { throw new Error('quota'); } });
  try {
    const facts = await collectFacts(haddixInput, env);
    assert.equal(facts.partial, true);
    assert.match(facts.failures[0], /^Google lookup failed: Places 500/);
  } finally { f.restore(); }
});

test('a clean run with a profile is not partial', async () => {
  const f = stubFetch({ places: () => [desert] });
  try {
    const r = await grade(desertInput, env);
    assert.equal(r.partial, false);
    assert.deepEqual(r.failures, []);
    assert.equal(r.facts.profile.found, true);
    assert.ok(r.report.overall != null);
    assert.equal(holdReason(r), null);
  } finally { f.restore(); }
});

for (const step of ['titleVerdict', 'directorySearch', 'reviewThemes', 'openingParagraph']) {
  test(`a failed Anthropic step (${step}) makes the run partial`, async () => {
    const withReviews = { ...desert, reviews: [{ rating: 5, text: { text: 'Great' }, publishTime: new Date().toISOString() }] };
    const f = stubFetch({ places: () => [withReviews] });
    try {
      const r = await grade({ ...desertInput, ai: true }, env, { ai: fakeAi([step]) });
      assert.equal(r.partial, true, step);
      assert.equal(r.failures.length, 1, r.failures.join('; '));
      assert.match(r.failures[0], /Anthropic 529/);
      assert.match(holdReason(r), /some checks failed[\s\S]*Anthropic 529/);
    } finally { f.restore(); }
  });
}

test('with every Anthropic step working the run is complete and gets the AI summary', async () => {
  const withReviews = { ...desert, reviews: [{ rating: 5, text: { text: 'Great' }, publishTime: new Date().toISOString() }] };
  const f = stubFetch({ places: () => [withReviews] });
  try {
    const r = await grade({ ...desertInput, ai: true }, env, { ai: fakeAi() });
    assert.equal(r.partial, false, r.failures.join('; '));
    assert.equal(r.report.opening, 'A short summary.');
  } finally { f.restore(); }
});

// The request handler end to end, with fetch stubbed: which emails go out.
const require = createRequire(import.meta.url);
async function submit(lead, places) {
  Object.assign(process.env, {
    RESEND_API_KEY: 're_test', LEAD_TO: 'team@example.com', LEAD_FROM: 'Reports <reports@example.com>',
    TURNSTILE_SECRET: 'ts_test', REPORT_CARD_AUTO: 'on', GOOGLE_PLACES_API_KEY: 'test-key',
  });
  delete process.env.ANTHROPIC_API_KEY;
  delete process.env.UPSTASH_REDIS_REST_URL;
  delete process.env.KV_REST_API_URL;
  const handler = require('../../lead.js');
  const f = stubFetch({ places });
  const res = { code: 0, status(c) { this.code = c; return this; }, json(b) { this.body = b; return this; }, setHeader() {} };
  try {
    await handler({ method: 'POST', headers: { origin: 'https://hvacmarketinghq.com', 'content-type': 'application/json', 'x-forwarded-for': `10.0.0.${Math.floor(Math.random() * 250)}` },
      body: { first_name: 'Logan', 'cf-turnstile-response': 'tok', ...lead } }, res);
  } finally { f.restore(); }
  return { res, emails: f.calls.filter((c) => c.url.startsWith('https://api.resend.com/')).map((c) => c.body) };
}

test('handler: a partial run sends the shop the "sending by hand" email and the team the failures, not the report', async () => {
  const { res, emails } = await submit({ website: 'haddixheatandair.com', business: 'Haddix', town: 'Waco, TX', email: 'shop1@example.com' }, () => []);
  assert.equal(res.code, 200);
  const toShop = emails.filter((e) => e.to[0] === 'shop1@example.com');
  assert.equal(toShop.length, 1);
  assert.match(toShop[0].text, /couldn't finish this one, so I'll put it together myself/);
  assert.ok(!toShop.some((e) => /^Your (report card: .+ gets an? [A-F]|HVAC report card for .+ is ready)/.test(e.subject)), 'no graded report to the shop');
  const team = emails.find((e) => /^NEEDS YOU/.test(e.subject));
  assert.ok(team, 'team was told');
  assert.match(team.text, /No Google profile found for this name and website/);
  assert.match(team.text, /not sent/);
});

test('handler: a complete run still emails the graded report to the shop', async () => {
  const { emails } = await submit({ website: 'dwsnv.com', business: 'Desert West', town: 'Las Vegas, NV', email: 'shop2@example.com' }, () => [desert]);
  const toShop = emails.filter((e) => e.to[0] === 'shop2@example.com');
  assert.equal(toShop.length, 1);
  assert.match(toShop[0].subject, /^Your (report card: Desert West Air Conditioning gets an? |HVAC report card for Desert West Air Conditioning is ready)/);
  assert.ok(emails.some((e) => /^Sent: /.test(e.subject)));
  assert.ok(!emails.some((e) => /^NEEDS YOU/.test(e.subject)));
});
