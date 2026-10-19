#!/usr/bin/env node
// LIVE end-to-end check of api/form-lead.js against a real GHL sub-account (practice location first).
// It runs the real handler in-process with a fake req/res, then reads GHL back and checks:
//   1. the contact exists (looked up by email)            4. an open opportunity exists in GHL_PIPELINE_ID
//   2. it has the lead-web-form tag                          at GHL_STAGE_ID (HVAC Jobs / New Lead)
//   3. lead_source = "Website Form" and service_needed     5. SMS consent is NOT set: no sms-consent tag, and BOTH
//      = the service sent                                     consent fields (sms_consent, sms_marketing_consent) empty
// Optional --twice submits again and checks there is still exactly one open opportunity (dedupe).
// Also sends TEST_TRACKING (UTMs + fake gclid) and checks each mapped field; reads conversations (if the token can)
// to prove nothing was sent. Field ids must come from the GHL handoff: the form-lead token has no
// locations/customFields.readonly scope, so it can't look them up itself.
//
// Secrets: NEVER put the token in this file, the repo, chat or a shell history line. Load env from a secret store:
//   op run --env-file=practice.op.env -- node client-kit/form-lead/scripts/live-check.mjs --live --email you@example.com
// or a file OUTSIDE the repo with 600 perms, deleted after:  node --env-file=/secure/practice.env ...
// Prints only check names, pass/fail, HTTP statuses and GHL ids. Never the token.
//
// Env (same as the function):  GHL_TOKEN GHL_LOCATION_ID GHL_FIELD_LEAD_SOURCE GHL_FIELD_SERVICE GHL_PIPELINE_ID
//   GHL_STAGE_ID ALLOWED_ORIGINS   (+ optional GHL_FIELD_UTM_* GHL_FIELD_GCLID ALERT_WEBHOOK SITE_LABEL)
// Harness only (optional, but set both for a real test): the template has TWO consent fields that must BOTH stay empty:
//   GHL_FIELD_SMS_CONSENT           = id of contact.sms_consent
//   GHL_FIELD_SMS_MARKETING_CONSENT = id of contact.sms_marketing_consent
// Without an id, that field's check is skipped with a WARN (the sms-consent tag check still runs).
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);
const GHL = 'https://services.leadconnectorhq.com';
// Realistic test UTMs + a fake gclid, so the tracking field mapping is exercised.
export const TEST_TRACKING = { utm_source: 'practice-test', utm_medium: 'cpc', utm_campaign: 'practice-run-oct26', utm_term: 'ac repair waco', utm_content: 'harness', gclid: 'TEST-GCLID-practice' };
const TRACKING_ENV = { utm_source: 'GHL_FIELD_UTM_SOURCE', utm_medium: 'GHL_FIELD_UTM_MEDIUM', utm_campaign: 'GHL_FIELD_UTM_CAMPAIGN', utm_term: 'GHL_FIELD_UTM_TERM', utm_content: 'GHL_FIELD_UTM_CONTENT', gclid: 'GHL_FIELD_GCLID' };
const CONSENT_FIELDS = [['GHL_FIELD_SMS_CONSENT', 'SMS Consent (contact.sms_consent)'], ['GHL_FIELD_SMS_MARKETING_CONSENT', 'SMS Marketing Consent (contact.sms_marketing_consent)']];
const REQUIRED = ['GHL_TOKEN', 'GHL_LOCATION_ID', 'GHL_FIELD_LEAD_SOURCE', 'GHL_FIELD_SERVICE', 'GHL_PIPELINE_ID', 'GHL_STAGE_ID', 'ALLOWED_ORIGINS'];

export function missingEnv(env) {
  return REQUIRED.filter((k) => !String(env[k] || '').trim());
}

// Call the handler like Vercel would. Returns { status, body }.
async function invoke(handler, origin, payload) {
  const raw = JSON.stringify(payload);
  const req = {
    method: 'POST',
    headers: { origin, 'content-type': 'application/json', 'content-length': String(Buffer.byteLength(raw)), 'x-forwarded-for': `203.0.113.${Math.floor(Math.random() * 200) + 1}` },
    body: payload,
  };
  return new Promise((resolve) => {
    const res = {
      statusCode: 200, headers: {},
      setHeader(k, v) { this.headers[k] = v; },
      status(c) { this.statusCode = c; return this; },
      json(b) { resolve({ status: this.statusCode, body: b }); return this; },
      end() { resolve({ status: this.statusCode, body: null }); return this; },
    };
    Promise.resolve(handler(req, res)).catch((e) => resolve({ status: 0, body: { ok: false, error: String(e && e.message) } }));
  });
}

async function ghlGet(fetchImpl, env, path) {
  const r = await fetchImpl(`${GHL}${path}`, { headers: { Authorization: `Bearer ${env.GHL_TOKEN}`, Version: '2021-07-28', Accept: 'application/json' } });
  let data = null;
  try { data = await r.json(); } catch { /* ignore */ }
  return { ok: r.ok, status: r.status, data };
}

const fieldValue = (contact, id) => {
  const f = (contact.customFields || contact.customField || []).find((x) => x.id === id);
  if (!f) return undefined;
  return f.value ?? f.field_value ?? f.fieldValue;
};
// GHL logs activity entries (e.g. "Opportunity created", messageType TYPE_ACTIVITY_OPPORTUNITY, direction "outbound")
// in the conversation. They are internal timeline items, not messages to the lead, so they don't count.
export const isRealOutbound = (m) => m && m.direction === 'outbound' && !/^TYPE_ACTIVITY/.test(String(m.messageType || '')) && !m.activity && m.messageType !== 'TYPE_INTERNAL_COMMENT';
const isEmpty = (v) => v === undefined || v === null || v === '' || (Array.isArray(v) && v.length === 0);

export async function runLiveCheck({ env = process.env, email, name = 'Practice Test Lead', service = 'Tune-Up/Maintenance', twice = false, tracking = TEST_TRACKING, settleMs = 0, fetchImpl = globalThis.fetch, handler = require('../api/form-lead.js'), log = console.log } = {}) {
  const results = [];
  const check = (label, pass, detail = '', level = pass ? 'PASS' : 'FAIL') => { results.push({ label, pass, level }); log(`${level}  ${label}${detail ? `  (${detail})` : ''}`); };

  const missing = missingEnv(env);
  if (missing.length) { check('env present', false, `missing: ${missing.join(', ')}`); return { ok: false, results }; }
  if (!email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { check('test email given', false, 'pass --email <your own address>'); return { ok: false, results }; }
  const origin = env.ALLOWED_ORIGINS.split(',')[0].trim().replace(/\/+$/, '');
  // No phone anywhere (forms are email-only). Consent keys ARE sent, to prove the function drops them.
  const payload = { name, email, service, town_zip: 'Hewitt 76643', message: 'Practice run test lead (TEST). Safe to delete.', sms_consent: 'yes', sms_marketing_consent: 'yes', ...tracking };

  const first = await invoke(handler, origin, payload);
  check('handler returned ok', first.status === 200 && first.body && first.body.ok === true, `HTTP ${first.status} steps=${JSON.stringify(first.body && first.body.steps)}`);
  if (twice) {
    const second = await invoke(handler, origin, payload);
    check('second submit returned ok', second.status === 200 && second.body && second.body.ok === true, `HTTP ${second.status} steps=${JSON.stringify(second.body && second.body.steps)}`);
    // The intended dedupe path is opportunity search -> "existing". GHL's opportunity search lags right after a
    // create (live run Oct 19: search returned 0, create then got 400), so a quick resubmit may end "failed" and only
    // GHL's own duplicate rejection prevents a 2nd deal. Since the Oct 19 fix the function re-searches after a 400 and
    // should report "existing"; anything else is flagged. The opportunity count check below is the real gate.
    const oppStep = second.body && second.body.steps && second.body.steps.opportunity;
    if (oppStep !== 'existing') check('second submit deduped via search (steps.opportunity = existing)', true, `got "${oppStep}"`, 'WARN');
  }

  const q = new URLSearchParams({ locationId: env.GHL_LOCATION_ID, email });
  const dup = await ghlGet(fetchImpl, env, `/contacts/search/duplicate?${q}`);
  const contactId = dup.data && dup.data.contact && dup.data.contact.id;
  check('contact exists (by email)', Boolean(contactId), `HTTP ${dup.status}${contactId ? ` id=${contactId}` : ''}`);
  if (!contactId) return { ok: false, results };

  const got = await ghlGet(fetchImpl, env, `/contacts/${encodeURIComponent(contactId)}`);
  const c = (got.data && got.data.contact) || {};
  const tags = (c.tags || []).map((t) => String(t).toLowerCase());
  check('tag lead-web-form present', tags.includes('lead-web-form'), `tags=${JSON.stringify(c.tags || [])}`);
  check('lead_source = "Website Form"', fieldValue(c, env.GHL_FIELD_LEAD_SOURCE) === 'Website Form', `value=${JSON.stringify(fieldValue(c, env.GHL_FIELD_LEAD_SOURCE))}`);
  check(`service_needed = "${service}"`, fieldValue(c, env.GHL_FIELD_SERVICE) === service, `value=${JSON.stringify(fieldValue(c, env.GHL_FIELD_SERVICE))}`);
  check('no sms-consent tag', !tags.some((t) => /sms[-_ ]?consent/.test(t)));
  // The HVAC Client Template has TWO consent fields. Both must stay empty for a website-form lead:
  // contact.sms_consent (transactional) and contact.sms_marketing_consent (promotional).
  for (const [envName, label] of CONSENT_FIELDS) {
    if (env[envName]) {
      const v = fieldValue(c, env[envName]);
      check(`${label} field NOT set`, isEmpty(v), `value=${JSON.stringify(v)}`);
    } else {
      check(`${label} field NOT set`, true, `${envName} not given, field not checked`, 'WARN');
    }
  }
  check('no phone on the contact', !c.phone, c.phone ? 'contact has a phone (was it already on the contact?)' : '');
  for (const [key, envName] of Object.entries(TRACKING_ENV)) {
    if (!tracking[key]) continue;
    if (!env[envName]) { check(`${key} field populated`, true, `${envName} not given, not checked`, 'WARN'); continue; }
    const v = fieldValue(c, env[envName]);
    check(`${key} field populated`, v === tracking[key], `value=${JSON.stringify(v)}`);
  }

  const oq = new URLSearchParams({ location_id: env.GHL_LOCATION_ID, pipeline_id: env.GHL_PIPELINE_ID, contact_id: contactId, status: 'open', limit: '20' });
  const opp = await ghlGet(fetchImpl, env, `/opportunities/search?${oq}`);
  const open = ((opp.data && opp.data.opportunities) || []).filter((o) => o.status === 'open' && o.pipelineId === env.GHL_PIPELINE_ID && (!o.contactId || o.contactId === contactId));
  const atStage = open.filter((o) => o.pipelineStageId === env.GHL_STAGE_ID);
  check('open opportunity in HVAC Jobs at New Lead', atStage.length >= 1, `HTTP ${opp.status} open=${open.length} atNewLead=${atStage.length}${atStage[0] ? ` id=${atStage[0].id}` : ''}`);
  if (twice) check('still exactly one open opportunity after 2 submits', open.length === 1, `open=${open.length}`);

  // Outbound messages: needs conversations.readonly, which the minimum form-lead token does NOT have. If the read is
  // refused, the check WARNs ("can't check with these scopes"); check it another way (GHL UI or a read-only connector).
  if (settleMs) await new Promise((r) => setTimeout(r, settleMs)); // give any (wrongly) live workflow time to fire
  const cq = new URLSearchParams({ locationId: env.GHL_LOCATION_ID, contactId });
  const conv = await ghlGet(fetchImpl, env, `/conversations/search?${cq}`);
  if (conv.status === 401 || conv.status === 403) {
    check('no outbound messages', true, `HTTP ${conv.status}: token can't read conversations, NOT CHECKED`, 'WARN');
  } else if (!conv.ok) {
    check('no outbound messages', false, `HTTP ${conv.status} reading conversations`);
  } else {
    let outbound = 0;
    let readFail = 0;
    for (const cv of (conv.data && conv.data.conversations) || []) {
      const m = await ghlGet(fetchImpl, env, `/conversations/${encodeURIComponent(cv.id)}/messages`);
      if (!m.ok) { readFail++; continue; }
      const list = (m.data && m.data.messages && m.data.messages.messages) || (m.data && m.data.messages) || [];
      outbound += (Array.isArray(list) ? list : []).filter(isRealOutbound).length;
    }
    check('no outbound messages', outbound === 0 && readFail === 0, `conversations=${((conv.data && conv.data.conversations) || []).length} outbound=${outbound}${readFail ? ` unreadable=${readFail}` : ''}`);
  }

  const ok = results.every((r) => r.pass);
  log(ok ? '\nALL CHECKS PASSED. Delete the test contact/opportunity in GHL afterwards (with Logan\'s OK).' : '\nSOME CHECKS FAILED.');
  return { ok, results, contactId };
}

function parseArgs(argv) {
  const a = { live: false, twice: false };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    if (k === '--live') a.live = true;
    else if (k === '--twice') a.twice = true;
    else if (k === '--email') a.email = argv[++i];
    else if (k === '--name') a.name = argv[++i];
    else if (k === '--service') a.service = argv[++i];
  }
  return a;
}

if (import.meta.url === pathToFileURL(process.argv[1] || '').href) {
  const a = parseArgs(process.argv.slice(2));
  if (!a.live) {
    console.log('Dry run: this script writes a real contact + opportunity to GHL. Re-run with --live --email <your own address>.');
    const missing = missingEnv(process.env);
    console.log(missing.length ? `Missing env: ${missing.join(', ')}` : 'All required env vars are present.');
    process.exit(0);
  }
  const { ok } = await runLiveCheck({ email: a.email, name: a.name, service: a.service, twice: a.twice, settleMs: 15000 });
  process.exit(ok ? 0 : 1);
}
