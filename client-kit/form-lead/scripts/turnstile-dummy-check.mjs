#!/usr/bin/env node
// Runs api/form-lead.js against the REAL Cloudflare siteverify endpoint with Cloudflare's published dummy keys
// (https://developers.cloudflare.com/turnstile/troubleshooting/testing/). GHL is NOT called: every non-Cloudflare
// fetch is answered by a local stub. Free, no keys of ours involved.
//   node client-kit/form-lead/scripts/turnstile-dummy-check.mjs
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const handler = require('../api/form-lead.js');
const CF = 'https://challenges.cloudflare.com/turnstile/v0/siteverify';
const realFetch = globalThis.fetch;
let ghlCalls = 0;
globalThis.fetch = async (url, opts) => {
  if (String(url) === CF) return realFetch(url, opts);
  ghlCalls++;
  const path = new URL(String(url)).pathname;
  const body = path === '/contacts/upsert' ? { contact: { id: 'stub' }, new: true } : path === '/opportunities/search' ? { opportunities: [] } : {};
  return new Response(JSON.stringify(body), { status: path === '/opportunities/search' ? 200 : 201, headers: { 'content-type': 'application/json' } });
};
Object.assign(process.env, { GHL_TOKEN: 'stub', GHL_LOCATION_ID: 'stub', GHL_FIELD_LEAD_SOURCE: 'stub', GHL_FIELD_SERVICE: 'stub', GHL_PIPELINE_ID: 'stub', GHL_STAGE_ID: 'stub', ALLOWED_ORIGINS: 'https://test.invalid' });
const run = (secret, token, i) => new Promise((resolve) => {
  process.env.TURNSTILE_SECRET_KEY = secret;
  const body = { name: 'Dummy Test', email: 'dummy@example.com', service: 'Repair', ...(token ? { 'cf-turnstile-response': token } : {}) };
  const res = { statusCode: 200, setHeader() {}, status(c) { this.statusCode = c; return this; }, json(b) { resolve({ status: this.statusCode, ok: b && b.ok }); return this; }, end() { resolve({ status: this.statusCode }); return this; } };
  handler({ method: 'POST', headers: { origin: 'https://test.invalid', 'content-type': 'application/json', 'x-forwarded-for': `198.51.100.${i}` }, body }, res);
});
const cases = [
  ['always-pass secret + dummy token', '1x0000000000000000000000000000000AA', 'XXXX.DUMMY.TOKEN.XXXX', 200],
  ['always-fail secret + dummy token', '2x0000000000000000000000000000000AA', 'XXXX.DUMMY.TOKEN.XXXX', 403],
  ['token-already-spent secret', '3x0000000000000000000000000000000AA', 'XXXX.DUMMY.TOKEN.XXXX', 403],
];
let fails = 0;
for (const [i, [label, secret, token, want]] of cases.entries()) {
  const before = ghlCalls;
  const r = await run(secret, token, i + 1);
  const pass = r.status === want && (want === 200 ? ghlCalls > before : ghlCalls === before);
  if (!pass) fails++;
  console.log(`${pass ? 'PASS' : 'FAIL'}  ${label}: HTTP ${r.status} (want ${want}), stubbed GHL calls ${ghlCalls - before}`);
}
// Observed Oct 19, 2026: the real endpoint's always-pass secret ALSO accepted a non-dummy token (the docs say test
// secrets only accept the dummy token). Reported, not asserted, so this check doesn't depend on that detail.
{
  const r = await run('1x0000000000000000000000000000000AA', 'not-a-real-token', 9);
  console.log(`INFO  always-pass secret + non-dummy token: HTTP ${r.status} (docs suggest 403; informational only)`);
}
process.exit(fails ? 1 : 0);
