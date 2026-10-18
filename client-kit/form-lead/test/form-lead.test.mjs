// form-lead tests: fetch is stubbed, so nothing reaches GHL. Run: node --test client-kit/form-lead/test/
import { test, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const handler = require('../api/form-lead.js');
const { mapService, SERVICES } = handler;

const ENV = {
  GHL_TOKEN: 'pit-test-token-not-real',
  GHL_LOCATION_ID: 'loc_test',
  GHL_FIELD_LEAD_SOURCE: 'cf_lead_source',
  GHL_FIELD_SERVICE: 'cf_service',
  GHL_PIPELINE_ID: 'pipe_test',
  GHL_STAGE_ID: 'stage_new',
  ALLOWED_ORIGINS: 'https://www.client-hvac.com, https://client-hvac.com',
};
const ORIGIN = 'https://www.client-hvac.com';

let saved;
let ipCount = 0;
// Fake clock and sleep, so retry waits are instant and measurable.
const realDeps = { ...handler.deps };
let clock = 0;
let sleeps = [];
beforeEach(() => {
  saved = { ...process.env };
  Object.assign(process.env, ENV);
  clock = Date.parse('2026-10-18T16:30:00Z');
  sleeps = [];
  handler.deps.now = () => clock;
  handler.deps.sleep = async (ms) => { sleeps.push(ms); clock += ms; };
});
afterEach(() => { process.env = saved; Object.assign(handler.deps, realDeps); });

const json = (body, status = 200, headers = {}) => ({
  ok: status < 400, status, json: async () => body, text: async () => JSON.stringify(body),
  headers: { get: (k) => headers[k.toLowerCase()] ?? null },
});

const ALERT_URL = 'https://hooks.slack.test/services/T000/B000/XXXX';

// Stand-in GHL (plus the alert webhook). Options choose the canned answers:
// fail: { step: status } always fails that step; seq: { step: [entry, ...] } answers in order first, where an entry
// is a status, 'net' (network error) or { status, headers, body }; open: open opportunities, or a function
// (searchCount) => list; alert: 'net' or a status for the webhook. Returns GHL calls, alerts and a restore function.
function stubGhl({ isNew = true, open = [], fail = {}, seq = {}, alert = 200 } = {}) {
  const real = globalThis.fetch;
  const calls = [];
  const alerts = [];
  const queues = Object.fromEntries(Object.entries(seq).map(([k, v]) => [k, [...v]]));
  let searches = 0;
  globalThis.fetch = async (url, opts = {}) => {
    const u = new URL(String(url));
    if (String(url) === ALERT_URL) {
      alerts.push({ headers: opts.headers || {}, rawBody: opts.body, body: JSON.parse(opts.body), signal: opts.signal });
      if (alert === 'net') throw new Error('webhook down');
      return json({}, alert);
    }
    const call = { url: String(url), path: u.pathname, method: opts.method || 'GET', headers: opts.headers || {}, rawBody: opts.body, body: opts.body ? JSON.parse(opts.body) : null, query: u.searchParams };
    calls.push(call);
    assert.equal(u.origin, 'https://services.leadconnectorhq.com', 'only GHL is called');
    const step = u.pathname === '/contacts/upsert' ? 'upsert' : u.pathname.endsWith('/tags') ? 'tags' : u.pathname.endsWith('/notes') ? 'notes'
      : u.pathname === '/opportunities/search' ? 'search' : u.pathname === '/opportunities/' ? 'create' : 'other';
    if (step === 'search') searches++;
    const next = queues[step] && queues[step].shift();
    if (next === 'net') throw new Error('ECONNRESET');
    if (typeof next === 'number' && next >= 400) return json({ statusCode: next, message: 'error body with secrets' }, next);
    if (next && typeof next === 'object') return json(next.body || { message: 'error body with secrets' }, next.status, next.headers || {});
    if (fail[step]) return json({ statusCode: fail[step], message: 'error body with secrets' }, fail[step]);
    if (step === 'upsert') return json({ new: isNew, contact: { id: 'ct_123' }, traceId: 't' });
    if (step === 'tags') return json({ tags: ['lead-web-form'] }, 201);
    if (step === 'notes') return json({ note: { id: 'n1' } }, 201);
    if (step === 'search') { const list = typeof open === 'function' ? open(searches) : open; return json({ opportunities: list, meta: { total: list.length } }); }
    if (step === 'create') return json({ opportunity: { id: 'op1' } }, 201);
    return json({}, 404);
  };
  return { calls, alerts, restore: () => { globalThis.fetch = real; } };
}

function call(body, { origin = ORIGIN, method = 'POST', type = 'application/json', headers = {} } = {}) {
  const req = { method, headers: { origin, 'content-type': type, 'x-forwarded-for': `10.0.0.${++ipCount}`, ...headers }, body };
  const res = {
    statusCode: 200, headers: {}, body: undefined,
    setHeader(k, v) { this.headers[k.toLowerCase()] = v; },
    status(c) { this.statusCode = c; return this; },
    json(b) { this.body = b; return this; },
    end() { return this; },
  };
  return handler(req, res).then(() => res);
}

// Captures console output so tests can check nothing sensitive is logged.
function captureLogs() {
  const lines = [];
  const { log, error } = console;
  console.log = (...a) => lines.push(a.join(' '));
  console.error = (...a) => lines.push(a.join(' '));
  return { lines, restore: () => { console.log = log; console.error = error; } };
}

const LEAD = { name: 'Jane Q Doe', email: 'Jane@Example.com', town_zip: 'Waco, TX 76710', service: 'AC repair', message: 'Upstairs unit blowing warm air.' };

test('new contact: upsert, tag, note, search, then creates the opportunity', async () => {
  const g = stubGhl({ isNew: true });
  const logs = captureLogs();
  const res = await call(LEAD).finally(() => { logs.restore(); g.restore(); });
  assert.equal(res.statusCode, 200);
  assert.equal(res.body.ok, true);
  assert.equal(res.body.steps.opportunity, 'created');
  assert.equal(res.headers['access-control-allow-origin'], ORIGIN);
  assert.deepEqual(g.calls.map((c) => `${c.method} ${c.path}`), [
    'POST /contacts/upsert', 'POST /contacts/ct_123/tags', 'POST /contacts/ct_123/notes', 'GET /opportunities/search', 'POST /opportunities/',
  ]);
  for (const c of g.calls) {
    assert.equal(c.headers.Authorization, 'Bearer pit-test-token-not-real');
    assert.equal(c.headers.Version, '2021-07-28');
  }
  const [up, tags, note, search, create] = g.calls;
  assert.equal(up.body.locationId, 'loc_test');
  assert.equal(up.body.email, 'jane@example.com');
  assert.equal(up.body.firstName, 'Jane');
  assert.equal(up.body.lastName, 'Q Doe');
  assert.equal(up.body.city, 'Waco, TX');
  assert.equal(up.body.postalCode, '76710');
  assert.deepEqual(up.body.customFields, [
    { id: 'cf_lead_source', field_value: 'Website Form' },
    { id: 'cf_service', field_value: 'Repair' },
  ]);
  assert.equal(up.body.tags, undefined, 'upsert must not carry tags (it replaces them)');
  assert.deepEqual(tags.body, { tags: ['lead-web-form'] });
  assert.match(note.body.body, /Upstairs unit blowing warm air\./);
  assert.equal(search.query.get('location_id'), 'loc_test');
  assert.equal(search.query.get('pipeline_id'), 'pipe_test');
  assert.equal(search.query.get('contact_id'), 'ct_123');
  assert.equal(search.query.get('status'), 'open');
  assert.deepEqual(create.body, {
    locationId: 'loc_test', pipelineId: 'pipe_test', pipelineStageId: 'stage_new', contactId: 'ct_123', name: 'Jane Q Doe – Repair', status: 'open',
  });
  // Logs: step outcomes only, never the token or the person's details.
  const all = logs.lines.join('\n');
  for (const secret of ['pit-test-token-not-real', 'jane@example.com', 'Jane', 'Doe', '76710', 'warm air']) assert.ok(!all.toLowerCase().includes(secret.toLowerCase()), `log leaked ${secret}`);
  assert.match(all, /contact_upsert/);
});

test('existing contact with an open opportunity: no new opportunity', async () => {
  const g = stubGhl({ isNew: false, open: [{ id: 'op_old', status: 'open', pipelineId: 'pipe_test', contactId: 'ct_123' }] });
  const logs = captureLogs();
  const res = await call(LEAD).finally(() => { logs.restore(); g.restore(); });
  assert.equal(res.statusCode, 200);
  assert.equal(res.body.steps.opportunity, 'existing');
  assert.ok(!g.calls.some((c) => c.path === '/opportunities/'), 'must not create an opportunity');
  assert.ok(g.calls.some((c) => c.path.endsWith('/tags')), 'still tags the existing contact');
});

test('an open opportunity in another pipeline does not count', async () => {
  const g = stubGhl({ open: [{ id: 'op_x', status: 'open', pipelineId: 'other_pipe', contactId: 'ct_123' }] });
  const logs = captureLogs();
  const res = await call(LEAD).finally(() => { logs.restore(); g.restore(); });
  assert.equal(res.body.steps.opportunity, 'created');
});

test('service mapping lands on exactly the five options', () => {
  const cases = {
    'Repair': 'Repair', 'repair': 'Repair', 'AC Repair': 'Repair', 'furnace not heating': 'Repair', 'Emergency service': 'Repair',
    'Tune-Up/Maintenance': 'Tune-Up/Maintenance', 'tune up': 'Tune-Up/Maintenance', 'AC tune-up': 'Tune-Up/Maintenance', 'Maintenance plan': 'Tune-Up/Maintenance',
    'New System Estimate': 'New System Estimate', 'new system': 'New System Estimate', 'Replacement quote': 'New System Estimate', 'heat pump installation': 'New System Estimate',
    'Indoor Air Quality': 'Indoor Air Quality', 'IAQ': 'Indoor Air Quality', 'whole home air purifier': 'Indoor Air Quality',
    'Other': 'Other', '': 'Other', 'ductless?': 'Other', 'pool heater': 'Other', '<script>': 'Other',
  };
  for (const [raw, want] of Object.entries(cases)) assert.equal(mapService(raw), want, raw);
  for (const raw of Object.keys(cases)) assert.ok(SERVICES.includes(mapService(raw)));
  assert.deepEqual(SERVICES, ['Repair', 'Tune-Up/Maintenance', 'New System Estimate', 'Indoor Air Quality', 'Other']);
});

test('unknown service is sent to GHL as Other', async () => {
  const g = stubGhl();
  const logs = captureLogs();
  await call({ ...LEAD, service: 'something else entirely' }).finally(() => { logs.restore(); g.restore(); });
  assert.deepEqual(g.calls[0].body.customFields[1], { id: 'cf_service', field_value: 'Other' });
  assert.equal(g.calls.at(-1).body.name, 'Jane Q Doe – Other');
});

test('a phone number sent anyway is dropped, never forwarded', async () => {
  const g = stubGhl();
  const logs = captureLogs();
  const res = await call({ ...LEAD, phone: '(254) 555-0199', phoneNumber: '2545550199' }).finally(() => { logs.restore(); g.restore(); });
  assert.equal(res.statusCode, 200);
  for (const c of g.calls) {
    const raw = String(c.rawBody || '') + c.url;
    assert.ok(!/phone/i.test(raw), `${c.path} carried a phone key`);
    assert.ok(!raw.includes('555-0199') && !raw.includes('5550199'), `${c.path} carried the number`);
  }
});

test('form-encoded body works the same (and ignores phone)', async () => {
  const g = stubGhl();
  const logs = captureLogs();
  const raw = new URLSearchParams({ ...LEAD, phone: '2545550199' }).toString();
  const res = await call(raw, { type: 'application/x-www-form-urlencoded' }).finally(() => { logs.restore(); g.restore(); });
  assert.equal(res.statusCode, 200);
  assert.equal(g.calls[0].body.email, 'jane@example.com');
  assert.ok(!g.calls.some((c) => String(c.rawBody || '').includes('5550199')));
});

test('no outbound request ever carries SMS consent', async () => {
  for (const extra of [{}, { sms_consent: 'yes', 'sms-consent': 'on', smsConsent: true, tags: 'sms-consent' }]) {
    const g = stubGhl();
    const logs = captureLogs();
    await call({ ...LEAD, ...extra }).finally(() => { logs.restore(); g.restore(); });
    assert.ok(g.calls.length >= 4);
    for (const c of g.calls) {
      const raw = String(c.rawBody || '') + c.url;
      assert.ok(!/sms_consent/i.test(raw), `${c.path} contains sms_consent`);
      assert.ok(!/sms-consent/i.test(raw), `${c.path} contains sms-consent`);
      assert.ok(!/consent/i.test(raw), `${c.path} contains a consent field or tag`);
    }
    const tags = g.calls.find((c) => c.path.endsWith('/tags')).body.tags;
    assert.deepEqual(tags, ['lead-web-form']);
  }
});

test('bad email is rejected before any GHL call', async () => {
  const g = stubGhl();
  const res = await call({ ...LEAD, email: 'jane-at-example' }).finally(g.restore);
  assert.equal(res.statusCode, 400);
  assert.equal(res.body.ok, false);
  assert.match(res.body.error, /email/i);
  assert.equal(g.calls.length, 0);
});

test('honeypot: pretends success, sends nothing', async () => {
  const g = stubGhl();
  const logs = captureLogs();
  const res = await call({ ...LEAD, company_fax: 'http://spam.example' }).finally(() => { logs.restore(); g.restore(); });
  assert.equal(res.statusCode, 200);
  assert.deepEqual(res.body, { ok: true });
  assert.equal(g.calls.length, 0);
});

test('disallowed or missing origin is refused, no CORS header', async () => {
  const g = stubGhl();
  const logs = captureLogs();
  const bad = await call(LEAD, { origin: 'https://evil.example' });
  const none = await call(LEAD, { origin: '' });
  const pre = await call(undefined, { origin: 'https://evil.example', method: 'OPTIONS' });
  logs.restore(); g.restore();
  for (const r of [bad, none, pre]) {
    assert.equal(r.statusCode, 403);
    assert.equal(r.headers['access-control-allow-origin'], undefined);
  }
  assert.equal(g.calls.length, 0);
});

test('preflight from an allowed origin gets CORS headers', async () => {
  const res = await call(undefined, { origin: 'https://client-hvac.com/', method: 'OPTIONS' });
  assert.equal(res.statusCode, 204);
  assert.equal(res.headers['access-control-allow-origin'], 'https://client-hvac.com');
  assert.match(res.headers['access-control-allow-methods'], /POST/);
});

test('size limits: oversized body is refused, long fields are clipped', async () => {
  const g = stubGhl();
  const logs = captureLogs();
  const big = await call({ ...LEAD, message: 'x'.repeat(20000) });
  const ok = await call({ ...LEAD, message: 'y'.repeat(5000) });
  logs.restore(); g.restore();
  assert.equal(big.statusCode, 413);
  assert.equal(ok.statusCode, 200);
  const note = g.calls.find((c) => c.path.endsWith('/notes'));
  assert.ok(note.body.body.length < 2200);
});

test('GHL upsert error: friendly generic error, no further calls', async () => {
  const g = stubGhl({ fail: { upsert: 401 } });
  const logs = captureLogs();
  const res = await call(LEAD).finally(() => { logs.restore(); g.restore(); });
  assert.equal(res.statusCode, 502);
  assert.equal(res.body.ok, false);
  assert.match(res.body.error, /something went wrong/i);
  assert.ok(!/401|ghl|token/i.test(res.body.error));
  assert.equal(g.calls.length, 1);
  assert.match(logs.lines.join('\n'), /"step":"contact_upsert","ok":false,"status":401/);
});

test('GHL network failure on upsert is handled', async () => {
  const real = globalThis.fetch;
  globalThis.fetch = async () => { throw new Error('ECONNRESET'); };
  const logs = captureLogs();
  const res = await call(LEAD).finally(() => { logs.restore(); globalThis.fetch = real; });
  assert.equal(res.statusCode, 502);
  assert.equal(res.body.ok, false);
});

test('opportunity search failure: contact kept, no blind create', async () => {
  const g = stubGhl({ fail: { search: 500 } });
  const logs = captureLogs();
  const res = await call(LEAD).finally(() => { logs.restore(); g.restore(); });
  assert.equal(res.statusCode, 200);
  assert.equal(res.body.steps.opportunity, 'failed');
  assert.ok(!g.calls.some((c) => c.path === '/opportunities/'));
});

test('missing env: generic 503, no calls', async () => {
  delete process.env.GHL_TOKEN;
  const g = stubGhl();
  const logs = captureLogs();
  const res = await call(LEAD).finally(() => { logs.restore(); g.restore(); });
  assert.equal(res.statusCode, 503);
  assert.equal(g.calls.length, 0);
});

const UTM_ENV = { GHL_FIELD_UTM_SOURCE: 'cf_utm_source', GHL_FIELD_UTM_MEDIUM: 'cf_utm_medium', GHL_FIELD_UTM_CAMPAIGN: 'cf_utm_campaign', GHL_FIELD_UTM_TERM: 'cf_utm_term', GHL_FIELD_UTM_CONTENT: 'cf_utm_content' };
const UTMS = { utm_source: 'google', utm_medium: 'cpc', utm_campaign: 'spring-ac', utm_term: 'ac repair waco', utm_content: 'ad-a' };

test('UTMs: all five sent as custom fields by env ID when present', async () => {
  Object.assign(process.env, UTM_ENV);
  const g = stubGhl();
  const logs = captureLogs();
  await call({ ...LEAD, ...UTMS }).finally(() => { logs.restore(); g.restore(); });
  assert.deepEqual(g.calls[0].body.customFields, [
    { id: 'cf_lead_source', field_value: 'Website Form' },
    { id: 'cf_service', field_value: 'Repair' },
    { id: 'cf_utm_source', field_value: 'google' },
    { id: 'cf_utm_medium', field_value: 'cpc' },
    { id: 'cf_utm_campaign', field_value: 'spring-ac' },
    { id: 'cf_utm_term', field_value: 'ac repair waco' },
    { id: 'cf_utm_content', field_value: 'ad-a' },
  ]);
});

test('UTMs: missing values and unset env vars are skipped', async () => {
  Object.assign(process.env, UTM_ENV);
  delete process.env.GHL_FIELD_UTM_TERM;
  const g = stubGhl();
  const logs = captureLogs();
  await call({ ...LEAD, utm_source: 'google', utm_medium: '  ', utm_term: 'ac repair' }).finally(() => { logs.restore(); g.restore(); });
  assert.deepEqual(g.calls[0].body.customFields.slice(2), [{ id: 'cf_utm_source', field_value: 'google' }]);
});

test('UTMs: none sent when no UTM env vars are set', async () => {
  const g = stubGhl();
  const logs = captureLogs();
  await call({ ...LEAD, ...UTMS }).finally(() => { logs.restore(); g.restore(); });
  assert.equal(g.calls[0].body.customFields.length, 2);
  assert.ok(!/utm|google|cpc/i.test(g.calls[0].rawBody));
});

test('UTMs: a value mentioning consent is dropped', async () => {
  Object.assign(process.env, UTM_ENV);
  const g = stubGhl();
  const logs = captureLogs();
  await call({ ...LEAD, utm_source: 'sms-consent', utm_medium: 'sms_consent' }).finally(() => { logs.restore(); g.restore(); });
  assert.ok(!/consent/i.test(g.calls[0].rawBody));
});

test('gclid: forwarded only to the Google Click ID custom field when GHL_FIELD_GCLID is set', async () => {
  Object.assign(process.env, UTM_ENV, { GHL_FIELD_GCLID: 'cf_gclid' });
  const g = stubGhl();
  const logs = captureLogs();
  const res = await call({ ...LEAD, ...UTMS, gclid: 'EAIaIQobChMI-test' }).finally(() => { logs.restore(); g.restore(); });
  const [up, ...rest] = g.calls;
  assert.deepEqual(up.body.customFields.at(-1), { id: 'cf_gclid', field_value: 'EAIaIQobChMI-test' });
  assert.equal(up.body.customFields.filter((f) => f.field_value === 'EAIaIQobChMI-test').length, 1);
  // Only the upsert's customFields carry it: not the note, tag, search or opportunity, nor the logs or the response.
  for (const c of rest) assert.ok(!/gclid|EAIaIQ|google|cpc|spring-ac/i.test(String(c.rawBody || '') + c.url), `${c.path} carried tracking data`);
  assert.ok(!/EAIaIQ|google|cpc|spring-ac/i.test(logs.lines.join('\n')));
  assert.ok(!/EAIaIQ/.test(JSON.stringify(res.body)));
});

test('gclid: skipped when GHL_FIELD_GCLID is unset or the value is missing', async () => {
  for (const [envSet, body] of [[false, { ...LEAD, gclid: 'EAIaIQobChMI-test' }], [true, { ...LEAD, gclid: '  ' }], [true, LEAD]]) {
    if (envSet) process.env.GHL_FIELD_GCLID = 'cf_gclid'; else delete process.env.GHL_FIELD_GCLID;
    const g = stubGhl();
    const logs = captureLogs();
    await call(body).finally(() => { logs.restore(); g.restore(); });
    assert.equal(g.calls[0].body.customFields.length, 2);
    for (const c of g.calls) assert.ok(!/EAIaIQ|cf_gclid/.test(String(c.rawBody || '') + c.url));
  }
});

test('gclid: never sent as the built-in top-level contact field', async () => {
  for (const extra of [{}, { GHL_FIELD_GCLID: 'cf_gclid' }]) {
    Object.assign(process.env, extra);
    const g = stubGhl();
    const logs = captureLogs();
    await call({ ...LEAD, gclid: 'EAIaIQobChMI-test' }).finally(() => { logs.restore(); g.restore(); });
    for (const c of g.calls) {
      assert.equal(c.body ? c.body.gclid : undefined, undefined, `${c.path} has top-level gclid`);
      assert.equal(c.body ? c.body.attributionSource : undefined, undefined);
      assert.ok(!/"gclid"/.test(String(c.rawBody || '')), `${c.path} has a gclid key`);
    }
  }
});

test('lead-web-form tag is always added: new, existing, no message, and when later steps fail', async () => {
  const scenarios = [
    [{ isNew: true }, LEAD],
    [{ isNew: false, open: [{ id: 'op', status: 'open', pipelineId: 'pipe_test', contactId: 'ct_123' }] }, LEAD],
    [{ isNew: false }, { ...LEAD, message: '' }],
    [{ fail: { notes: 500, search: 500, create: 500 } }, LEAD],
    [{}, { ...LEAD, service: '', town_zip: '' }],
  ];
  for (const [opts, body] of scenarios) {
    const g = stubGhl(opts);
    const logs = captureLogs();
    const res = await call(body).finally(() => { logs.restore(); g.restore(); });
    assert.equal(res.statusCode, 200);
    const tagCalls = g.calls.filter((c) => c.path === '/contacts/ct_123/tags' && c.method === 'POST');
    assert.equal(tagCalls.length, 1, `tag call missing for ${JSON.stringify(opts)}`);
    assert.deepEqual(tagCalls[0].body, { tags: ['lead-web-form'] });
    assert.equal(g.calls[1].path, '/contacts/ct_123/tags', 'tag is added right after the upsert');
  }
});

test('tag failure is logged and reported in steps', async () => {
  const g = stubGhl({ fail: { tags: 500 } });
  const logs = captureLogs();
  const res = await call(LEAD).finally(() => { logs.restore(); g.restore(); });
  assert.equal(res.body.steps.tag, 'failed');
  assert.match(logs.lines.join('\n'), /"step":"add_tag","ok":false,"status":500/);
});

// ---- Retries and failure alerts ----
const count = (g, path, method) => g.calls.filter((c) => c.path === path && (!method || c.method === method)).length;
const OPP = { id: 'op_new', status: 'open', pipelineId: 'pipe_test', contactId: 'ct_123' };

test('retry: 429 then success on the upsert', async () => {
  const g = stubGhl({ seq: { upsert: [429] } });
  const logs = captureLogs();
  const res = await call(LEAD).finally(() => { logs.restore(); g.restore(); });
  assert.equal(res.statusCode, 200);
  assert.equal(res.body.ok, true);
  assert.equal(count(g, '/contacts/upsert'), 2);
  assert.deepEqual(sleeps, [500]);
  assert.match(logs.lines.join('\n'), /"step":"contact_upsert","ok":true,"status":200,"attempts":2/);
});

test('retry: a network error then success', async () => {
  const g = stubGhl({ seq: { tags: ['net'] } });
  const logs = captureLogs();
  const res = await call(LEAD).finally(() => { logs.restore(); g.restore(); });
  assert.equal(res.body.steps.tag, 'ok');
  assert.equal(count(g, '/contacts/ct_123/tags'), 2);
});

test('retry: upsert 5xx three times → friendly error and an alert', async () => {
  process.env.ALERT_WEBHOOK = ALERT_URL;
  const g = stubGhl({ fail: { upsert: 503 } });
  const logs = captureLogs();
  const res = await call(LEAD).finally(() => { logs.restore(); g.restore(); });
  assert.equal(res.statusCode, 502);
  assert.equal(res.body.ok, false);
  assert.match(res.body.error, /something went wrong/i);
  assert.equal(count(g, '/contacts/upsert'), 3);
  assert.equal(g.calls.length, 3, 'nothing after a failed upsert');
  assert.deepEqual(sleeps, [500, 1000]);
  assert.equal(g.alerts.length, 1);
  const { text } = g.alerts[0].body;
  assert.match(text, /contact_upsert/);
  assert.match(text, /503/);
  assert.match(text, /loc_test/, 'falls back to GHL_LOCATION_ID as the label');
  assert.match(text, /2026-10-18T16:30:01\.500Z/, 'timestamp');
  assert.match(text, /Jane Q Doe/);
  assert.match(text, /jane@example\.com/);
});

test('retry: later step 5xx three times → visitor still sees success, alert names the step', async () => {
  Object.assign(process.env, { ALERT_WEBHOOK: ALERT_URL, SITE_LABEL: 'Brazos Comfort (brazoscomfort.com)' });
  const g = stubGhl({ fail: { tags: 500 } });
  const logs = captureLogs();
  const res = await call(LEAD).finally(() => { logs.restore(); g.restore(); });
  assert.equal(res.statusCode, 200);
  assert.equal(res.body.ok, true);
  assert.equal(res.body.steps.tag, 'failed');
  assert.equal(count(g, '/contacts/ct_123/tags'), 3);
  assert.equal(g.alerts.length, 1);
  assert.match(g.alerts[0].body.text, /Brazos Comfort \(brazoscomfort\.com\)/);
  assert.match(g.alerts[0].body.text, /Step: add_tag, status 500/);
});

test('retry: no retry on 400 (or other 4xx)', async () => {
  for (const status of [400, 401, 404, 422]) {
    const g = stubGhl({ fail: { upsert: status } });
    const logs = captureLogs();
    sleeps = [];
    const res = await call(LEAD).finally(() => { logs.restore(); g.restore(); });
    assert.equal(res.statusCode, 502);
    assert.equal(count(g, '/contacts/upsert'), 1, `retried a ${status}`);
    assert.deepEqual(sleeps, []);
  }
});

test('retry: Retry-After is honored, and capped at 3 s', async () => {
  const g = stubGhl({ seq: { upsert: [{ status: 429, headers: { 'retry-after': '2' } }, { status: 429, headers: { 'retry-after': '120' } }] } });
  const logs = captureLogs();
  const res = await call(LEAD).finally(() => { logs.restore(); g.restore(); });
  assert.equal(res.statusCode, 200);
  assert.equal(count(g, '/contacts/upsert'), 3);
  assert.deepEqual(sleeps, [2000, 3000]);
});

test('retry: Retry-After as an HTTP date is honored', async () => {
  const when = new Date(Date.parse('2026-10-18T16:30:01.500Z')).toUTCString(); // ~1.5 s ahead (date has 1 s precision)
  const g = stubGhl({ seq: { tags: [{ status: 503, headers: { 'retry-after': when } }] } });
  const logs = captureLogs();
  await call(LEAD).finally(() => { logs.restore(); g.restore(); });
  assert.equal(sleeps.length, 1);
  assert.ok(sleeps[0] >= 500 && sleeps[0] <= 3000, String(sleeps[0]));
});

test('retry: total wait stays within the 8 s budget', async () => {
  const slow = { status: 429, headers: { 'retry-after': '60' } };
  const g = stubGhl({ seq: { upsert: [slow, slow], tags: [slow, slow], notes: [slow, slow], search: [slow, slow] } });
  const logs = captureLogs();
  const res = await call(LEAD).finally(() => { logs.restore(); g.restore(); });
  assert.equal(res.statusCode, 200);
  const total = sleeps.reduce((a, b) => a + b, 0);
  assert.ok(total <= 8000, `waited ${total} ms`);
  assert.ok(sleeps.every((ms) => ms <= 3000));
});

test('retry: opportunity create 5xx is retried only after a re-search shows nothing was created', async () => {
  const g = stubGhl({ seq: { create: [500] }, open: () => [] });
  const logs = captureLogs();
  const res = await call(LEAD).finally(() => { logs.restore(); g.restore(); });
  assert.equal(res.body.steps.opportunity, 'created');
  assert.deepEqual(g.calls.map((c) => `${c.method} ${c.path}`).slice(-4), [
    'GET /opportunities/search', 'POST /opportunities/', 'GET /opportunities/search', 'POST /opportunities/',
  ]);
});

test('retry: no duplicate opportunity when a failed-looking create actually went through', async () => {
  process.env.ALERT_WEBHOOK = ALERT_URL;
  // First search: none open. Create answers 502 but GHL made it anyway, so the re-search finds it.
  const g = stubGhl({ seq: { create: [502, 502] }, open: (n) => (n === 1 ? [] : [OPP]) });
  const logs = captureLogs();
  const res = await call(LEAD).finally(() => { logs.restore(); g.restore(); });
  assert.equal(res.body.steps.opportunity, 'created');
  assert.equal(count(g, '/opportunities/', 'POST'), 1, 'created only once');
  assert.equal(count(g, '/opportunities/search'), 2);
  assert.equal(g.alerts.length, 0, 'nothing actually failed');
});

test('retry: no duplicate opportunity when the re-search fails', async () => {
  process.env.ALERT_WEBHOOK = ALERT_URL;
  const g = stubGhl({ seq: { create: [500], search: [200, 500, 500, 500].map((s) => (s === 200 ? { status: 200, body: { opportunities: [] } } : s)) } });
  const logs = captureLogs();
  const res = await call(LEAD).finally(() => { logs.restore(); g.restore(); });
  assert.equal(res.statusCode, 200);
  assert.equal(res.body.steps.opportunity, 'failed');
  assert.equal(count(g, '/opportunities/', 'POST'), 1);
  assert.match(g.alerts[0].body.text, /opportunity_create, status 500/);
});

test('retry: opportunity create 4xx is not retried', async () => {
  const g = stubGhl({ fail: { create: 422 } });
  const logs = captureLogs();
  const res = await call(LEAD).finally(() => { logs.restore(); g.restore(); });
  assert.equal(res.body.steps.opportunity, 'failed');
  assert.equal(count(g, '/opportunities/', 'POST'), 1);
  assert.equal(count(g, '/opportunities/search'), 1);
});

test('alert payload: name and email only, no token, message, UTMs, gclid or error bodies', async () => {
  Object.assign(process.env, UTM_ENV, { GHL_FIELD_GCLID: 'cf_gclid', ALERT_WEBHOOK: ALERT_URL });
  const g = stubGhl({ fail: { tags: 500, notes: 500, search: 500 } });
  const logs = captureLogs();
  await call({ ...LEAD, ...UTMS, gclid: 'EAIaIQobChMI-test', town_zip: 'Waco 76710' }).finally(() => { logs.restore(); g.restore(); });
  assert.equal(g.alerts.length, 1, 'one alert per request');
  const a = g.alerts[0];
  assert.deepEqual(Object.keys(a.body), ['text']);
  assert.equal(a.headers['Content-Type'], 'application/json');
  assert.equal(a.headers.Authorization, undefined);
  assert.ok(a.signal, 'alert has a timeout');
  const raw = a.rawBody;
  for (const bad of ['pit-test-token-not-real', 'Bearer', 'warm air', 'Upstairs', 'google', 'cpc', 'spring-ac', 'ac repair waco', 'ad-a', 'utm', 'EAIaIQ', 'gclid', 'secrets', '76710', 'Waco', 'Repair', 'ct_123']) {
    assert.ok(!raw.toLowerCase().includes(bad.toLowerCase()), `alert leaked ${bad}`);
  }
  for (const step of ['add_tag', 'add_note', 'opportunity_search']) assert.match(a.body.text, new RegExp(step));
  assert.match(a.body.text, /Jane Q Doe/);
  assert.match(a.body.text, /jane@example\.com/);
});

test('alert payload: Slack control characters in the name are escaped', async () => {
  process.env.ALERT_WEBHOOK = ALERT_URL;
  const g = stubGhl({ fail: { tags: 500 } });
  const logs = captureLogs();
  await call({ ...LEAD, name: 'Bob <!channel> & Co' }).finally(() => { logs.restore(); g.restore(); });
  assert.ok(!g.alerts[0].body.text.includes('<!channel>'));
  assert.match(g.alerts[0].body.text, /Bob &lt;!channel&gt; &amp; Co/);
});

test('alert failure is swallowed: network error or bad status never breaks the request', async () => {
  for (const alert of ['net', 500]) {
    process.env.ALERT_WEBHOOK = ALERT_URL;
    const ok = stubGhl({ fail: { tags: 500 }, alert });
    const logs = captureLogs();
    const res = await call(LEAD).finally(() => { logs.restore(); ok.restore(); });
    assert.equal(res.statusCode, 200);
    assert.equal(res.body.ok, true);
    assert.equal(ok.alerts.length, 1);
    assert.match(logs.lines.join('\n'), /"step":"alert","ok":false/);
    assert.ok(!logs.lines.join('\n').includes('hooks.slack.test'), 'webhook URL is not logged');

    const bad = stubGhl({ fail: { upsert: 500 }, alert });
    const logs2 = captureLogs();
    const res2 = await call(LEAD).finally(() => { logs2.restore(); bad.restore(); });
    assert.equal(res2.statusCode, 502);
    assert.match(res2.body.error, /something went wrong/i);
  }
});

test('no alert when ALERT_WEBHOOK is unset, or when nothing failed', async () => {
  delete process.env.ALERT_WEBHOOK;
  const g = stubGhl({ fail: { upsert: 500 } });
  const logs = captureLogs();
  const res = await call(LEAD).finally(() => { logs.restore(); g.restore(); });
  assert.equal(res.statusCode, 502);
  assert.equal(g.alerts.length, 0);
  assert.ok(!/"step":"alert"/.test(logs.lines.join('\n')));

  process.env.ALERT_WEBHOOK = ALERT_URL;
  const fine = stubGhl();
  const logs2 = captureLogs();
  await call(LEAD).finally(() => { logs2.restore(); fine.restore(); });
  assert.equal(fine.alerts.length, 0);
});

test('missing GHL env with ALERT_WEBHOOK set: generic 503 and a config alert', async () => {
  process.env.ALERT_WEBHOOK = ALERT_URL;
  delete process.env.GHL_TOKEN;
  const g = stubGhl();
  const logs = captureLogs();
  const res = await call(LEAD).finally(() => { logs.restore(); g.restore(); });
  assert.equal(res.statusCode, 503);
  assert.equal(g.calls.length, 0);
  assert.match(g.alerts[0].body.text, /config/);
});
