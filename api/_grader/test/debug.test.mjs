// Team-only debug for "no Google profile matched": the searches tried, the top candidates each returned,
// and why each was passed over. It goes in the NEEDS YOU email and nowhere the shop can see.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { findBusiness, rejectReason } from '../collect/places.mjs';
import { collectFacts, grade } from '../grade.mjs';
import { lookupDebugText, payload, renderReport, DEBUG_MAX_LINES } from '../report.mjs';
import { getTrade } from '../trades/index.mjs';
import { place, stubFetch } from './helpers.mjs';

const hvac = getTrade('hvac');
const typed = { businessName: 'Haddix', website: 'haddixheatandair.com', town: 'Waco', state: 'TX' };
const withAddr = (p, formattedAddress, extra = {}) => ({ ...p, formattedAddress, pureServiceAreaBusiness: false, ...extra });

// What Places returns for each search in the fixture: a Haddix in Oklahoma, a Haddix with no address
// and nothing backing it, and other Waco shops.
const tulsa = withAddr(place({ name: 'Haddix Heating & Air', website: 'https://haddixok.com/', state: 'OK', town: 'Tulsa', reviews: 41 }), '410 S Main St, Tulsa, OK 74103, USA');
const hidden = { ...place({ name: 'Haddix Heating & Air', reviews: 3 }), addressComponents: [], primaryType: null, primaryTypeDisplayName: null,
  types: ['point_of_interest'], pureServiceAreaBusiness: true };
const pros = withAddr(place({ name: 'Waco Air Pros', website: 'https://www.wacoairpros.com/', reviews: 512 }), '1200 Franklin Ave, Waco, TX 76701, USA');
const brazos = withAddr(place({ name: 'Brazos Comfort Heating & Air', website: 'http://brazoscomfort.com', reviews: 88 }), '88 Valley Mills Dr, Waco, TX 76710, USA');
const fixture = (q) => (q === 'Haddix, Waco, TX' ? [pros, tulsa, brazos] : q === 'Haddix HVAC Waco, TX' ? [hidden, pros] : []);
const haddixInput = { businessName: 'Haddix', website: 'haddixheatandair.com', town: 'Waco, TX', trade: 'hvac', ai: false };
const env = { GOOGLE_PLACES_API_KEY: 'AIzaTESTKEY-should-never-appear-1234567' };

test('rejectReason names why a candidate lost: name, state, no-evidence', () => {
  assert.equal(rejectReason(pros, typed, hvac), 'name');
  assert.equal(rejectReason(tulsa, typed, hvac), 'state');
  assert.equal(rejectReason(hidden, typed, hvac), 'no-evidence');
  assert.equal(rejectReason(place({ name: 'Haddix Heating & Air' }), typed, hvac), 'match');
});

test('findBusiness fills the trace with each query and its top 5 candidates', async () => {
  const trace = [];
  const many = Array.from({ length: 8 }, (_, i) => place({ name: `Other Shop ${i}` }));
  const search = async (q) => (q === 'Haddix' ? many : fixture(q));
  assert.equal(await findBusiness(typed, 'key', hvac, { search, trace }), null);
  assert.deepEqual(trace.map((t) => t.query), ['Haddix, Waco, TX', 'Haddix HVAC Waco, TX', 'haddixheatandair.com', 'Haddix']);
  assert.deepEqual(trace[0].candidates.map((c) => c.reason), ['name', 'state', 'name']);
  assert.deepEqual(trace[0].candidates[1], { name: 'Haddix Heating & Air', address: '410 S Main St, Tulsa, OK 74103, USA', host: 'haddixok.com',
    type: 'hvac_contractor', reviews: 41, serviceArea: false, reason: 'state' });
  assert.equal(trace[1].candidates[0].serviceArea, true);
  assert.equal(trace[3].count, 8);
  assert.equal(trace[3].candidates.length, 5, 'top 5 only');
});

test('collectFacts keeps the lookup debug only when no profile matched', async () => {
  let f = stubFetch({ places: fixture });
  try {
    const facts = await collectFacts(haddixInput, env);
    assert.equal(facts.profile.found, false);
    assert.equal(facts.lookupDebug.length, 4);
  } finally { f.restore(); }
  f = stubFetch({ places: () => [place({ name: 'Haddix Heating & Air', website: 'https://haddixheatandair.com' })] });
  try {
    const r = await grade(haddixInput, env);
    assert.equal(r.facts.profile.found, true);
    assert.equal(r.facts.lookupDebug, null);
    assert.equal(lookupDebugText(r.facts), '');
  } finally { f.restore(); }
});

test('lookupDebugText is compact, capped and has no keys', async () => {
  const f = stubFetch({ places: fixture });
  let facts;
  try { facts = await collectFacts(haddixInput, env); } finally { f.restore(); }
  const text = lookupDebugText(facts);
  console.log(`--- example debug section ---\n${text}\n---`);
  assert.match(text, /^Google lookup debug \(team only\)/);
  assert.match(text, /Q1 "Haddix, Waco, TX": 3 results/);
  assert.match(text, /Haddix Heating & Air \| 410 S Main St, Tulsa, OK 74103, USA \| haddixok\.com \| hvac_contractor \| 41 rev \| SAB no -> state/);
  assert.match(text, /SAB yes -> no-evidence/);
  assert.match(text, /Waco Air Pros .* -> name/);
  assert.ok(!/AIza|key=|googleapis/.test(text));
  // 4 queries x 5 candidates would be 25 lines; more than that is cut to the cap.
  const big = { lookupDebug: Array.from({ length: 6 }, (_, i) => ({ query: `q${i}`, count: 9, candidates: Array.from({ length: 5 }, () => ({ name: 'X', reason: 'name' })) })) };
  const lines = lookupDebugText(big).split('\n');
  assert.equal(lines.length, DEBUG_MAX_LINES);
  assert.match(lines.at(-1), /more lines cut/);
  assert.equal(lookupDebugText({ lookupDebug: [{ query: 'https://x.test/?key=SECRET123', count: 0, candidates: [] }] }).includes('SECRET123'), false);
});

test('the shop\'s report and results page never carry the debug', async () => {
  const f = stubFetch({ places: fixture });
  try {
    const r = await grade(haddixInput, env);
    assert.ok(r.facts.lookupDebug);
    const out = renderReport(r, { firstName: 'Logan', bookingUrl: 'https://hvacmarketinghq.com/book', siteUrl: 'https://hvacmarketinghq.com' });
    const page = JSON.stringify(payload(r, 'Logan'));
    for (const s of [out.html, out.text, out.subject, page]) {
      assert.ok(!/lookup debug|haddixok|Waco Air Pros|no-evidence/.test(s));
    }
  } finally { f.restore(); }
});

// The request handler end to end: the NEEDS YOU email has the debug, the shop's email does not.
const require = createRequire(import.meta.url);
async function submit(lead, places) {
  Object.assign(process.env, {
    RESEND_API_KEY: 're_test', LEAD_TO: 'team@example.com', LEAD_FROM: 'Reports <reports@example.com>',
    TURNSTILE_SECRET: 'ts_test', REPORT_CARD_AUTO: 'on', GOOGLE_PLACES_API_KEY: env.GOOGLE_PLACES_API_KEY,
  });
  delete process.env.ANTHROPIC_API_KEY;
  delete process.env.UPSTASH_REDIS_REST_URL;
  delete process.env.KV_REST_API_URL;
  const handler = require('../../lead.js');
  const f = stubFetch({ places });
  const res = { code: 0, status(c) { this.code = c; return this; }, json(b) { this.body = b; return this; }, setHeader() {} };
  try {
    await handler({ method: 'POST', headers: { origin: 'https://hvacmarketinghq.com', 'content-type': 'application/json', 'x-forwarded-for': `10.1.0.${Math.floor(Math.random() * 250)}` },
      body: { first_name: 'Logan', 'cf-turnstile-response': 'tok', ...lead } }, res);
  } finally { f.restore(); }
  return { res, emails: f.calls.filter((c) => c.url.startsWith('https://api.resend.com/')).map((c) => c.body) };
}

test('handler: no profile matched puts the debug in the team email only', async () => {
  const { res, emails } = await submit({ website: 'haddixheatandair.com', business: 'Haddix', town: 'Waco, TX', email: 'shop9@example.com' }, fixture);
  assert.equal(res.code, 200);
  const team = emails.find((e) => /^NEEDS YOU/.test(e.subject));
  assert.ok(team);
  assert.deepEqual(team.to, ['team@example.com']);
  assert.match(team.text, /Send it by hand[\s\S]*\n\nGoogle lookup debug \(team only\)/);
  assert.match(team.text, /Q2 "Haddix HVAC Waco, TX": 2 results/);
  assert.match(team.text, /-> state/);
  const toShop = emails.filter((e) => e.to.includes('shop9@example.com'));
  assert.equal(toShop.length, 1);
  for (const e of toShop) assert.ok(!/lookup debug|haddixok|Waco Air Pros|-> (name|state|no-evidence)/.test(JSON.stringify(e)));
  for (const e of emails) assert.ok(!JSON.stringify(e).includes(env.GOOGLE_PLACES_API_KEY), 'no API key in any email');
});

test('handler: a matched profile sends no debug anywhere', async () => {
  // Another website: the daily one-per-site cap already counted haddixheatandair.com above.
  const shop = place({ name: 'Haddix Heating & Air', website: 'https://haddixhvac-waco.com' });
  const { emails } = await submit({ website: 'haddixhvac-waco.com', business: 'Haddix', town: 'Waco, TX', email: 'shop10@example.com' }, () => [shop]);
  assert.ok(emails.some((e) => /^Your (report card: .+ gets an? [A-F]|HVAC report card for .+ is ready)/.test(e.subject)), 'the graded report went out');
  assert.ok(emails.some((e) => /^Sent: /.test(e.subject)));
  for (const e of emails) assert.ok(!/lookup debug/.test(JSON.stringify(e)));
});
