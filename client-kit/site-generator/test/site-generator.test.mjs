// Client site generator tests. Runs generate.py into temp folders; no network.
// Run: node --test client-kit/site-generator/test/
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, readdirSync, writeFileSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const GEN = join(HERE, '..', 'generate.py');
const PRACTICE = join(HERE, '..', 'clients', 'practice-hvac-co', 'client.json');
const BASE = JSON.parse(readFileSync(PRACTICE, 'utf8'));

function run(cfg) {
  const dir = mkdtempSync(join(tmpdir(), 'clientsite-'));
  const cfgPath = join(dir, 'client.json');
  writeFileSync(cfgPath, JSON.stringify(cfg));
  const out = join(dir, 'out');
  const r = spawnSync('python3', [GEN, cfgPath, '--out', out], { encoding: 'utf8' });
  return { ...r, out };
}
const htmlFiles = (out) => readdirSync(out).filter((f) => f.endsWith('.html'));

test('practice config builds a site', () => {
  const r = run(BASE);
  assert.equal(r.status, 0, r.stderr);
  for (const f of ['index.html', 'services.html', 'service-areas.html', 'contact.html', 'privacy.html', '404.html', 'vercel.json', 'robots.txt', 'api/form-lead.js']) {
    assert.ok(existsSync(join(r.out, f)), f);
  }
});

test('every page has robots noindex,nofollow and the TEST banner', () => {
  const r = run(BASE);
  const files = htmlFiles(r.out);
  assert.ok(files.length >= 5);
  for (const f of files) {
    const h = readFileSync(join(r.out, f), 'utf8');
    assert.match(h, /<meta name="robots" content="noindex,nofollow">/, f);
    assert.match(h, /TEST SITE – not a real business/, f);
  }
});

test('vercel.json sends X-Robots-Tag noindex on every path; robots.txt disallows all', () => {
  const r = run(BASE);
  const vj = JSON.parse(readFileSync(join(r.out, 'vercel.json'), 'utf8'));
  const all = vj.headers.find((h) => h.source === '/(.*)');
  const xr = all.headers.find((h) => h.key === 'X-Robots-Tag');
  assert.ok(xr && /noindex/.test(xr.value));
  assert.equal(readFileSync(join(r.out, 'robots.txt'), 'utf8'), 'User-agent: *\nDisallow: /\n');
});

test('a TEST_SITE cannot turn NOINDEX off', () => {
  const r = run({ ...BASE, NOINDEX: false });
  assert.notEqual(r.status, 0);
  assert.match(r.stderr, /NOINDEX/);
});

test('forms are email-only: no phone input, no SMS opt-in, post to form-lead', () => {
  const r = run(BASE);
  for (const f of htmlFiles(r.out)) {
    const h = readFileSync(join(r.out, f), 'utf8');
    assert.doesNotMatch(h, /type="tel"|name="phone"|name="sms|sms[-_ ]?consent|opt-?in/i, f);
    for (const form of h.match(/<form[\s\S]*?<\/form>/g) || []) {
      assert.match(form, /action="\/api\/form-lead"/);
      assert.match(form, /name="email"/);
      assert.match(form, /name="company_fax"/);
      assert.doesNotMatch(form, /checkbox/i);
    }
  }
  assert.match(readFileSync(join(r.out, 'contact.html'), 'utf8'), /<form/);
});

test('chat widget loader is skipped while CHAT_WIDGET_ID is empty', () => {
  const r = run(BASE);
  assert.equal(BASE.CHAT_WIDGET_ID, '');
  for (const f of htmlFiles(r.out)) assert.doesNotMatch(readFileSync(join(r.out, f), 'utf8'), /leadconnectorhq|data-widget-id/, f);
  const csp = JSON.parse(readFileSync(join(r.out, 'vercel.json'), 'utf8')).headers[0].headers.find((h) => h.key === 'Content-Security-Policy').value;
  assert.doesNotMatch(csp, /leadconnectorhq/);
});

test('chat widget loader appears (and CSP allows it) once CHAT_WIDGET_ID is set', () => {
  const r = run({ ...BASE, CHAT_WIDGET_ID: 'abc123def456' });
  assert.equal(r.status, 0, r.stderr);
  assert.match(readFileSync(join(r.out, 'index.html'), 'utf8'), /data-widget-id="abc123def456"/);
  const csp = JSON.parse(readFileSync(join(r.out, 'vercel.json'), 'utf8')).headers[0].headers.find((h) => h.key === 'Content-Security-Policy').value;
  assert.match(csp, /script-src 'self' https:\/\/\*\.leadconnectorhq\.com/);
});

test("HMHQ's own chat widget id is refused", () => {
  const r = run({ ...BASE, CHAT_WIDGET_ID: '6ad452bad3ae3b035c14772f' });
  assert.notEqual(r.status, 0);
  assert.match(r.stderr, /HMHQ/);
});

test('a TEST_SITE must use a fictional 555-01xx phone', () => {
  assert.notEqual(run({ ...BASE, phone: '254-555-1234' }).status, 0);
  assert.notEqual(run({ ...BASE, phone: '254-753-0142' }).status, 0);
  assert.equal(run({ ...BASE, phone: '254-555-0199' }).status, 0);
});

test('copy lint blocks reviews, stats, promises and miss scenarios', () => {
  for (const bad of ['Our customers love us: testimonials inside', 'We answer 100% of calls', 'Guaranteed same-day service', 'What if we miss your call?', '5 stars on Google']) {
    const cfg = { ...BASE, tagline: bad };
    const r = run(cfg);
    assert.notEqual(r.status, 0, bad);
    assert.match(r.stderr, /copy check failed/, bad);
  }
});

test('no review/rating markup in schema', () => {
  const r = run(BASE);
  for (const f of htmlFiles(r.out)) assert.doesNotMatch(readFileSync(join(r.out, f), 'utf8'), /AggregateRating|"review"/i, f);
});

test('committed practice output matches the generator (regenerate after editing client.json)', () => {
  const r = run(BASE);
  const committed = join(HERE, '..', '..', 'sites', 'practice-hvac-co');
  for (const f of [...htmlFiles(r.out), 'vercel.json', 'robots.txt', 'site.js', 'styles.css', 'api/form-lead.js']) {
    assert.equal(readFileSync(join(committed, f), 'utf8'), readFileSync(join(r.out, f), 'utf8'), f);
  }
});
