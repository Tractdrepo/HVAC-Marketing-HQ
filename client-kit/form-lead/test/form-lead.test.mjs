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
beforeEach(() => { saved = { ...process.env }; Object.assign(process.env, ENV); });
afterEach(() => { process.env = saved; });

const json = (body, status = 200) => ({ ok: status < 400, status, json: async () => body, text: async () => JSON.stringify(body) });

// Stand-in GHL. Options choose the canned answers; returns the calls and a restore function.
function stubGhl({ isNew = true, open = [], fail = {} } = {}) {
  const real = globalThis.fetch;
  const calls = [];
  globalThis.fetch = async (url, opts = {}) => {
    const u = new URL(String(url));
    const call = { url: String(url), path: u.pathname, method: opts.method || 'GET', headers: opts.headers || {}, rawBody: opts.body, body: opts.body ? JSON.parse(opts.body) : null, query: u.searchParams };
    calls.push(call);
    assert.equal(u.origin, 'https://services.leadconnectorhq.com', 'only GHL is called');
    const step = u.pathname === '/contacts/upsert' ? 'upsert' : u.pathname.endsWith('/tags') ? 'tags' : u.pathname.endsWith('/notes') ? 'notes'
      : u.pathname === '/opportunities/search' ? 'search' : u.pathname === '/opportunities/' ? 'create' : 'other';
    if (fail[step]) return json({ statusCode: fail[step], message: 'error' }, fail[step]);
    if (step === 'upsert') return json({ new: isNew, contact: { id: 'ct_123' }, traceId: 't' });
    if (step === 'tags') return json({ tags: ['lead-web-form'] }, 201);
    if (step === 'notes') return json({ note: { id: 'n1' } }, 201);
    if (step === 'search') return json({ opportunities: open, meta: { total: open.length } });
    if (step === 'create') return json({ opportunity: { id: 'op1' } }, 201);
    return json({}, 404);
  };
  return { calls, restore: () => { globalThis.fetch = real; } };
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
