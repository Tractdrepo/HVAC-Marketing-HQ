import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { parseHomepage, ruleTitleVerdict } from '../collect/homepage.mjs';
import { placeFacts } from '../collect/places.mjs';
import { nameMatches, nameWords } from '../names.mjs';
import { isPublicSite } from '../report.mjs';
import { getTrade } from '../trades/index.mjs';

const hvac = getTrade('hvac');
const html = readFileSync(new URL('./fixtures/sample-home.html', import.meta.url), 'utf8');

test('home page facts', () => {
  const f = parseHomepage(html, 'https://example-brazoscomfort.com/', hvac);
  assert.equal(f.https, true);
  assert.equal(f.mobileViewport, true);
  assert.equal(f.booking, true);
  assert.equal(f.chat, true);
  assert.equal(f.emergency, true);
  assert.equal(f.financing, true);
  assert.equal(f.license, true);
  assert.equal(f.tapToCall, true);
  assert.equal(f.facebookLinked, true);
  assert.equal(f.placeholderPhone, '(555) 555-5555');
  assert.deepEqual(f.phones, ['2547770142']);
  assert.deepEqual(f.serviceTopics.sort(), ['AC repair', 'heating', 'installation', 'maintenance plan']);
  assert.ok(f.areaPages.includes('hewitt') && f.areaPages.includes('woodway'));
  assert.equal(f.pageCount, 10);
  assert.equal(f.h1, "Waco's trusted heating and air team");
  assert.equal(ruleTitleVerdict(f, hvac, { town: 'Waco', state: 'TX' }), 'clear');
  assert.equal(ruleTitleVerdict(f, hvac, { town: 'Mesa', state: 'AZ' }), 'vague');
});

test('bare page: nothing found, title vague', () => {
  const f = parseHomepage('<html><title>Home</title><body>Welcome</body></html>', 'http://example.com/', hvac);
  assert.equal(f.https, false);
  assert.equal(f.booking, false);
  assert.equal(f.license, false);
  assert.equal(f.pageCount, 0);
  assert.equal(ruleTitleVerdict(f, hvac), 'vague');
});

test('directory name matching ignores town and trade words', () => {
  assert.deepEqual(nameWords('Brazos Comfort Heating & Air, LLC', hvac, 'Waco'), ['brazos']);
  assert.ok(nameMatches('Brazos Comfort Heating and Air - Waco, TX - Yelp', 'Brazos Comfort Heating & Air', hvac, 'Waco'));
  assert.ok(!nameMatches('Waco Heating and Air - Yelp', 'Brazos Comfort Heating & Air', hvac, 'Waco'));
  // Nothing distinctive left: whole name must appear as a phrase.
  assert.ok(nameMatches('Waco Heating & Air | BBB', 'Waco Heating and Air', hvac, 'Waco'));
  assert.ok(!nameMatches('Best Heating and Air in Waco', 'Waco Heating and Air', hvac, 'Waco'));
  // URL slugs count.
  assert.ok(nameMatches('/biz/brazos-comfort-heating-and-air-waco', 'Brazos Comfort Heating & Air', hvac, 'Waco'));
});

test('Places record becomes profile and review facts', () => {
  const now = Date.parse('2026-10-11T00:00:00Z');
  const place = {
    id: 'p1', displayName: { text: 'Brazos Comfort Heating & Air' }, primaryType: 'hvac_contractor',
    primaryTypeDisplayName: { text: 'HVAC contractor' }, rating: 4.6, userRatingCount: 140,
    websiteUri: 'https://www.example-brazoscomfort.com/?utm_source=gbp', nationalPhoneNumber: '(254) 777-0142',
    businessStatus: 'OPERATIONAL', regularOpeningHours: { weekdayDescriptions: ['Monday: 8 AM–5 PM'] },
    paymentOptions: { acceptsCreditCards: true },
    photos: Array.from({ length: 10 }, (_, i) => ({ authorAttributions: [{ displayName: i < 6 ? 'Brazos Comfort Heating & Air' : 'A Customer' }] })),
    reviews: [
      { rating: 5, publishTime: '2026-10-01T00:00:00Z' }, { rating: 2, publishTime: '2026-08-01T00:00:00Z' },
      { rating: 5, publishTime: '2026-07-01T00:00:00Z' },
    ],
  };
  const searches = [{ query: 'HVAC near Waco, TX', rank: 3, marketSize: 20, results: [
    { id: 'c1', rating: 4.9, userRatingCount: 900 }, { id: 'c2', rating: 4.7, userRatingCount: 300 },
    place, { id: 'c3', rating: 4.8, userRatingCount: 600 }, { id: 'c4', rating: 3.0, userRatingCount: 4 }] }];
  const f = placeFacts(place, searches, hvac, { now, website: 'example-brazoscomfort.com' });
  assert.equal(f.profile.photos.byBusiness, 6);
  assert.equal(f.profile.linksToSite, true);
  assert.equal(f.profile.hasHours, true);
  assert.equal(f.profile.paymentListed, true);
  assert.equal(f.reviews.newestDays, 10);
  assert.equal(f.reviews.lowInShown, 1);
  assert.equal(f.reviews.competitors.n, 3);
  assert.equal(Math.round(f.reviews.competitors.avgCount), 600);
});

test('only public hostnames are accepted', () => {
  assert.ok(isPublicSite('brazoscomfort.com'));
  assert.ok(isPublicSite('https://www.example.com/path'));
  for (const bad of ['localhost', 'http://127.0.0.1', 'http://169.254.169.254/latest', 'file:///etc/passwd',
    'http://user:pw@example.com', 'http://example.com:8080', 'printer.local', '']) {
    assert.ok(!isPublicSite(bad), bad);
  }
});

test('town field: state read from the end, nationwide', async () => {
  const { splitTown } = await import('../trades/region.mjs');
  assert.deepEqual(splitTown('Waco, TX'), { town: 'Waco', state: 'TX' });
  assert.deepEqual(splitTown('Salt Lake City Utah'), { town: 'Salt Lake City', state: 'UT' });
  assert.deepEqual(splitTown('mesa, az'), { town: 'mesa', state: 'AZ' });
  assert.deepEqual(splitTown('Fort Worth'), { town: 'Fort Worth', state: null });
});

test('area pages found outside Texas', () => {
  const page = '<a href="/locations/mesa-az">Mesa</a><a href="/x">Gilbert, AZ</a><a href="/y">AC repair in Chandler</a>';
  const f = parseHomepage(page, 'https://example.com/', hvac);
  assert.deepEqual(f.areaPages.sort(), ['chandler', 'gilbert', 'mesa-az']);
});

test('report email shows grades and fixes, not points', async () => {
  const { renderReport } = await import('../report.mjs');
  const { scoreFacts } = await import('../grade.mjs');
  const facts = JSON.parse(readFileSync(new URL('./fixtures/hvac-mid.json', import.meta.url)));
  const report = scoreFacts(facts);
  const r = renderReport({ facts: { ...facts, town: 'Waco', state: 'TX' }, report }, { firstName: 'Sam', bookingUrl: 'https://cal.example/x', siteUrl: 'https://hvacmarketinghq.com' });
  assert.match(r.subject, /^Your (report card: .+ gets an? [A-F]|HVAC report card for .+ is ready)/);
  assert.ok(r.html.includes('Hi Sam') && r.html.includes('https://cal.example/x'));
  assert.ok(!/\/ ?\d+ points|\bpts\b/i.test(r.html));
  assert.ok(r.text.includes('Overall:') && r.text.includes('Top fix:'));
  assert.ok(r.html.includes('/ 100'));
  const m = r.link.match(/\/your-report#z=([A-Za-z0-9_-]+)$/);
  assert.ok(m, 'results link');
  const { inflateRawSync } = await import('node:zlib');
  const back = JSON.parse(inflateRawSync(Buffer.from(m[1], 'base64url')).toString());
  assert.equal(back.n, facts.businessName);
  assert.equal(back.a.length, 4);
  assert.ok(r.html.includes('How we fix it:'), 'each top fix comes with how we fix it');
  assert.ok(back.a.some((a) => Array.isArray(a.fx[0]) && a.fx[0][1]), 'fixes carry how');
  assert.ok(back.s.length > 20, 'summary present without AI');
  assert.ok(r.link.length < 6000, `link length ${r.link.length}`);
});

test('listings are not graded when there is no Google profile and no directory search', async () => {
  const { scoreListings } = await import('../score.mjs');
  const a = scoreListings({ phoneMatch: undefined, googleLinksSite: undefined, facebookLinked: true }, hvac);
  assert.equal(a.score, null);
});

test('town pages match real place names, and a contact link counts as a way to book', async () => {
  const { parseHomepage, townPages } = await import('../collect/homepage.mjs');
  const html = '<a href="/coolidge/">Coolidge</a><a href="/fairfield-hvac/">Fairfield</a><a href="/ac-services-mexia/">Mexia</a><a href="/navarro-county-hvac-services/">Navarro County</a><a href="/about/">About Us</a><a href="/contact/">Contact Us</a><a href="/blog/">Blog</a>';
  const f = parseHomepage(html, 'https://www.example.com/', hvac);
  assert.equal(f.bookingKind, 'form');
  assert.equal(f.blogUrl, 'https://www.example.com/blog/');
  assert.deepEqual(townPages(f, 'TX', hvac).sort(), ['coolidge', 'fairfield', 'mexia', 'navarro county']);
});

test('blog freshness reads the newest post date', async () => {
  const { parseNewestDate } = await import('../collect/blog.mjs');
  const t = parseNewestDate('<p>Posted March 3, 2025</p><time datetime="2024-01-02">x</time><p>Jan 9, 2026</p>', Date.parse('2026-10-14'));
  assert.equal(new Date(t).toISOString().slice(0, 10), '2026-01-09');
});
