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
const ASSETS = join(HERE, '..', 'clients', 'practice-hvac-co', 'assets');
const BASE = JSON.parse(readFileSync(PRACTICE, 'utf8'));

function run(cfg) {
  const dir = mkdtempSync(join(tmpdir(), 'clientsite-'));
  const cfgPath = join(dir, 'client.json');
  writeFileSync(cfgPath, JSON.stringify(cfg));
  const out = join(dir, 'out');
  const r = spawnSync('python3', [GEN, cfgPath, '--out', out, '--assets', ASSETS], { encoding: 'utf8' });
  return { ...r, out };
}
const htmlFiles = (out) => readdirSync(out, { recursive: true }).map(String).filter((f) => f.endsWith('.html'));
const read = (out, f) => readFileSync(join(out, f), 'utf8');
const cspOf = (out) => JSON.parse(read(out, 'vercel.json')).headers[0].headers.find((h) => h.key === 'Content-Security-Policy').value;

test('practice config builds a site', () => {
  const r = run(BASE);
  assert.equal(r.status, 0, r.stderr);
  for (const f of ['index.html', 'services.html', 'service-areas.html', 'contact.html', 'privacy.html', 'terms.html', '404.html', 'areas/waco.html', 'areas/hewitt.html', 'img/logo-test.svg', 'img/photo-test-1.svg', 'vercel.json', 'robots.txt', 'api/form-lead.js']) {
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
  for (const f of htmlFiles(r.out)) assert.doesNotMatch(readFileSync(join(r.out, f), 'utf8'), /widgets\.leadconnectorhq|data-widget-id/, f);
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
  for (const f of [...htmlFiles(r.out), 'vercel.json', 'robots.txt', 'site.js', 'styles.css', 'api/form-lead.js', 'img/logo-test.svg']) {
    assert.equal(readFileSync(join(committed, f), 'utf8'), readFileSync(join(r.out, f), 'utf8'), f);
  }
});

// ---------- full template features ----------
const NOFACTS = BASE.service_areas.map((a) => (typeof a === 'string' ? a : a.name));

test('city pages only for cities with facts; facts are rendered verbatim and nothing else is invented', () => {
  const r = run(BASE);
  assert.ok(existsSync(join(r.out, 'areas/waco.html')));
  assert.ok(existsSync(join(r.out, 'areas/hewitt.html')));
  for (const c of ['woodway', 'robinson', 'china-spring']) assert.ok(!existsSync(join(r.out, `areas/${c}.html`)), c);
  const hewitt = read(r.out, 'areas/hewitt.html');
  const facts = [...hewitt.matchAll(/<ul class="facts">([\s\S]*?)<\/ul>/g)][0][1].match(/<li>(.*?)<\/li>/g).map((x) => x.slice(4, -5));
  assert.deepEqual(facts, BASE.service_areas.find((a) => a.name === 'Hewitt').facts);
  const areasPage = read(r.out, 'service-areas.html');
  assert.match(areasPage, /href="\/areas\/hewitt"/);
  assert.doesNotMatch(areasPage, /href="\/areas\/woodway"/);
  const none = run({ ...BASE, service_areas: NOFACTS });
  assert.equal(none.status, 0, none.stderr);
  assert.ok(!existsSync(join(none.out, 'areas')), 'no facts anywhere = no city pages');
});

test('city facts go through the copy check', () => {
  const bad = run({ ...BASE, service_areas: [{ name: 'Waco', facts: ['Rated the best HVAC shop in Waco'] }] });
  assert.notEqual(bad.status, 0);
  assert.match(bad.stderr, /copy check failed/);
});

test('logo and photo slots: rendered when set (with alt text), absent when not', () => {
  const r = run(BASE);
  const home = read(r.out, 'index.html');
  assert.match(home, /<img src="\/img\/logo-test\.svg" alt="[^"]+"/);
  assert.match(home, /<img src="\/img\/photo-test-1\.svg" alt="[^"]+"/);
  const { logo, photos, ...plain } = BASE;
  const p = run(plain);
  assert.equal(p.status, 0, p.stderr);
  assert.doesNotMatch(read(p.out, 'index.html'), /<img /);
  assert.notEqual(run({ ...BASE, logo: { src: 'missing.png', alt: 'x' } }).status, 0, 'missing file refused');
  assert.notEqual(run({ ...BASE, logo: { src: 'logo-test.svg', alt: '' } }).status, 0, 'alt text required');
  assert.notEqual(run({ ...BASE, photos: [{ src: '../etc/passwd', alt: 'x' }] }).status, 0, 'no paths');
  assert.notEqual(run({ ...BASE, photos: [{ src: 'photo-test-1.svg', alt: '5 star job' }] }).status, 0, 'alt text is linted');
});

test('footer has hours and license on every page', () => {
  const r = run(BASE);
  for (const f of htmlFiles(r.out)) {
    const foot = read(r.out, f).split('<footer')[1];
    assert.ok(foot.includes(`Hours: ${BASE.hours}`), f);
    assert.ok(foot.includes(`License: ${BASE.license}`), f);
  }
});

test('booking link from config, and none when unset', () => {
  const r = run(BASE);
  assert.match(read(r.out, 'index.html'), new RegExp(`href="${BASE.booking_url}"[^>]*>Book online`));
  const n = run({ ...BASE, booking_url: '' });
  for (const f of htmlFiles(n.out)) assert.doesNotMatch(read(n.out, f), /Book online/, f);
  assert.notEqual(run({ ...BASE, booking_url: 'http://example.com/x' }).status, 0, 'https only');
});

test('Google review link: straight to the review URL on every page, no gating; real sites must use Google', () => {
  const r = run(BASE);
  for (const f of htmlFiles(r.out)) {
    const h = read(r.out, f);
    assert.match(h, new RegExp(`<a class="review-link" href="${BASE.review_url}" target="_blank" rel="noopener">Leave us a Google review</a>`), f);
    assert.doesNotMatch(h, /how did we do|rate us|unhappy|star picker/i, f);
  }
  const real = { ...BASE, TEST_SITE: false, NOINDEX: true, phone: '254-753-0142' };
  assert.notEqual(run({ ...real, review_url: 'https://example.com/feedback' }).status, 0, 'non-Google review URL refused');
  assert.equal(run({ ...real, review_url: 'https://g.page/r/CabcDEF123/review' }).status, 0);
  const none = run({ ...BASE, review_url: '' });
  for (const f of htmlFiles(none.out)) assert.doesNotMatch(read(none.out, f), /Google review/, f);
});

test('GA4 only when ga4_id is set (script, ga.js, CSP)', () => {
  const off = run(BASE);
  for (const f of htmlFiles(off.out)) assert.doesNotMatch(read(off.out, f), /googletagmanager|ga\.js/, f);
  assert.ok(!existsSync(join(off.out, 'ga.js')));
  assert.doesNotMatch(cspOf(off.out), /googletagmanager|google-analytics/);
  const on = run({ ...BASE, ga4_id: 'G-TEST12345' });
  assert.equal(on.status, 0, on.stderr);
  assert.match(read(on.out, 'index.html'), /googletagmanager\.com\/gtag\/js\?id=G-TEST12345/);
  assert.match(read(on.out, 'ga.js'), /gtag\('config', "G-TEST12345"\)/);
  assert.match(cspOf(on.out), /script-src [^;]*https:\/\/www\.googletagmanager\.com/);
  assert.match(cspOf(on.out), /connect-src [^;]*google-analytics\.com/);
  assert.notEqual(run({ ...BASE, ga4_id: 'UA-123' }).status, 0);
});

test('call-tracking script only when set, only from GHL hosts, and allowed in CSP', () => {
  const off = run(BASE);
  for (const f of htmlFiles(off.out)) assert.doesNotMatch(read(off.out, f), /msgsndr|number-pool/, f);
  const url = 'https://link.msgsndr.com/js/TEST-number-pool.js';
  const on = run({ ...BASE, call_tracking_script_url: url });
  assert.equal(on.status, 0, on.stderr);
  assert.match(read(on.out, 'index.html'), new RegExp(`<script src="${url.replace(/\./g, '\\.')}" async>`));
  assert.match(cspOf(on.out), /script-src [^;]*https:\/\/link\.msgsndr\.com/);
  assert.notEqual(run({ ...BASE, call_tracking_script_url: 'https://evil.example/x.js' }).status, 0);
});

test('Turnstile: widget + api.js on the form page and CSP allows challenges.cloudflare.com; nothing when unset', () => {
  const r = run(BASE);
  const contact = read(r.out, 'contact.html');
  assert.match(contact, /<div class="cf-turnstile" data-sitekey="1x00000000000000000000AA"/);
  assert.match(contact, /challenges\.cloudflare\.com\/turnstile\/v0\/api\.js/);
  assert.doesNotMatch(read(r.out, 'index.html'), /turnstile/, 'api.js only where there is a form');
  assert.match(cspOf(r.out), /script-src [^;]*https:\/\/challenges\.cloudflare\.com/);
  assert.match(cspOf(r.out), /frame-src [^;]*https:\/\/challenges\.cloudflare\.com/);
  const off = run({ ...BASE, turnstile_site_key: '' });
  assert.doesNotMatch(read(off.out, 'contact.html'), /turnstile/);
  assert.doesNotMatch(cspOf(off.out), /cloudflare/);
});

test('privacy and terms are generated as DRAFT – needs lawyer review', () => {
  const r = run(BASE);
  for (const f of ['privacy.html', 'terms.html']) {
    const h = read(r.out, f);
    assert.match(h, /DRAFT – needs lawyer review/);
    assert.match(h, /STOP/);
  }
  assert.match(read(r.out, 'privacy.html'), /does not ask for a phone number/);
});
