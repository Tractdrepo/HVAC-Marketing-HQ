// Tests for scripts/live-check.mjs with a fake handler + fake GHL. No network.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { runLiveCheck, missingEnv } from '../scripts/live-check.mjs';

const ENV = { GHL_TOKEN: 'pit-fake', GHL_LOCATION_ID: 'loc', GHL_FIELD_LEAD_SOURCE: 'cf_ls', GHL_FIELD_SERVICE: 'cf_svc', GHL_PIPELINE_ID: 'pipe', GHL_STAGE_ID: 'stage_new', ALLOWED_ORIGINS: 'https://practice.test', GHL_FIELD_SMS_CONSENT: 'cf_sms', GHL_FIELD_SMS_MARKETING_CONSENT: 'cf_sms_mkt' };
const okHandler = async (req, res) => res.status(200).json({ ok: true, steps: { contact: 'ok' } });
const resp = (data, status = 200) => ({ ok: status < 400, status, json: async () => data });
function fakeGhl({ tags = ['lead-web-form'], fields = [{ id: 'cf_ls', value: 'Website Form' }, { id: 'cf_svc', value: 'Tune-Up/Maintenance' }], opps = [{ id: 'o1', status: 'open', pipelineId: 'pipe', pipelineStageId: 'stage_new', contactId: 'c1' }] } = {}) {
  const seen = [];
  const f = async (url, opts) => {
    seen.push({ url: String(url), auth: opts.headers.Authorization });
    const u = new URL(url);
    if (u.pathname === '/contacts/search/duplicate') return resp({ contact: { id: 'c1' } });
    if (u.pathname === '/contacts/c1') return resp({ contact: { id: 'c1', tags, customFields: fields } });
    if (u.pathname === '/opportunities/search') return resp({ opportunities: opps });
    return resp({}, 404);
  };
  f.seen = seen;
  return f;
}
const quiet = () => {};

test('missingEnv lists required vars', () => {
  assert.deepEqual(missingEnv({}), ['GHL_TOKEN', 'GHL_LOCATION_ID', 'GHL_FIELD_LEAD_SOURCE', 'GHL_FIELD_SERVICE', 'GHL_PIPELINE_ID', 'GHL_STAGE_ID', 'ALLOWED_ORIGINS']);
});

test('all checks pass on a correct lead', async () => {
  const r = await runLiveCheck({ env: ENV, email: 'me@example.com', fetchImpl: fakeGhl(), handler: okHandler, log: quiet });
  assert.equal(r.ok, true, JSON.stringify(r.results));
});

test('fails when lead-web-form tag missing or sms-consent tag present', async () => {
  assert.equal((await runLiveCheck({ env: ENV, email: 'me@example.com', fetchImpl: fakeGhl({ tags: [] }), handler: okHandler, log: quiet })).ok, false);
  assert.equal((await runLiveCheck({ env: ENV, email: 'me@example.com', fetchImpl: fakeGhl({ tags: ['lead-web-form', 'sms-consent'] }), handler: okHandler, log: quiet })).ok, false);
});

test('fails when SMS Consent field is set, or lead_source/service wrong', async () => {
  const base = [{ id: 'cf_ls', value: 'Website Form' }, { id: 'cf_svc', value: 'Tune-Up/Maintenance' }];
  assert.equal((await runLiveCheck({ env: ENV, email: 'me@example.com', fetchImpl: fakeGhl({ fields: [...base, { id: 'cf_sms', value: 'Yes' }] }), handler: okHandler, log: quiet })).ok, false);
  assert.equal((await runLiveCheck({ env: ENV, email: 'me@example.com', fetchImpl: fakeGhl({ fields: [{ id: 'cf_ls', value: 'Chat' }, base[1]] }), handler: okHandler, log: quiet })).ok, false);
  assert.equal((await runLiveCheck({ env: ENV, email: 'me@example.com', fetchImpl: fakeGhl({ fields: [base[0]] }), handler: okHandler, log: quiet })).ok, false);
});

test('fails with no open opportunity at the New Lead stage', async () => {
  const r = await runLiveCheck({ env: ENV, email: 'me@example.com', fetchImpl: fakeGhl({ opps: [{ id: 'o1', status: 'open', pipelineId: 'pipe', pipelineStageId: 'other', contactId: 'c1' }] }), handler: okHandler, log: quiet });
  assert.equal(r.ok, false);
});

test('never prints the token', async () => {
  const lines = [];
  await runLiveCheck({ env: ENV, email: 'me@example.com', fetchImpl: fakeGhl(), handler: okHandler, log: (l) => lines.push(l) });
  assert.ok(!lines.join('\n').includes('pit-fake'));
});

test('refuses to run without env or email', async () => {
  assert.equal((await runLiveCheck({ env: {}, email: 'me@example.com', fetchImpl: fakeGhl(), handler: okHandler, log: quiet })).ok, false);
  const f = fakeGhl();
  assert.equal((await runLiveCheck({ env: ENV, email: '', fetchImpl: f, handler: okHandler, log: quiet })).ok, false);
  assert.equal(f.seen.length, 0);
});

// The template has two consent fields: contact.sms_consent and contact.sms_marketing_consent. Both must stay empty.
test('fails when SMS Marketing Consent field is set', async () => {
  const base = [{ id: 'cf_ls', value: 'Website Form' }, { id: 'cf_svc', value: 'Tune-Up/Maintenance' }];
  const r = await runLiveCheck({ env: ENV, email: 'me@example.com', fetchImpl: fakeGhl({ fields: [...base, { id: 'cf_sms_mkt', value: ['Yes'] }] }), handler: okHandler, log: quiet });
  assert.equal(r.ok, false);
  assert.ok(r.results.some((x) => /Marketing Consent/.test(x.label) && !x.pass));
});

test('both consent checks run, and WARN (not fail) when their ids are not given', async () => {
  const lines = [];
  const { GHL_FIELD_SMS_CONSENT, GHL_FIELD_SMS_MARKETING_CONSENT, ...noIds } = ENV;
  const r = await runLiveCheck({ env: noIds, email: 'me@example.com', fetchImpl: fakeGhl(), handler: okHandler, log: (l) => lines.push(l) });
  assert.equal(r.ok, true);
  assert.equal(lines.filter((l) => /^WARN .*Consent/.test(l)).length, 2);
  const all = await runLiveCheck({ env: ENV, email: 'me@example.com', fetchImpl: fakeGhl(), handler: okHandler, log: quiet });
  assert.ok(all.results.some((x) => /sms_consent\)/.test(x.label) && x.pass && x.level === 'PASS'));
  assert.ok(all.results.some((x) => /sms_marketing_consent/.test(x.label) && x.pass && x.level === 'PASS'));
});
