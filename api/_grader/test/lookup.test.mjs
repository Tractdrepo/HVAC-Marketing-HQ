// Fix for the Oct 14 Haddix case: a real Google profile reported as "No Google profile found".
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { findBusiness, pickPlace, sameBusinessName, lookupQueries, domainLabel } from '../collect/places.mjs';
import { getTrade } from '../trades/index.mjs';
import { place } from './helpers.mjs';

const hvac = getTrade('hvac');
const haddix = place({ name: 'Haddix Heating & Air', website: 'http://haddixhvac.com/', reviews: 277 });
const typed = { businessName: 'Haddix', website: 'haddixheatandair.com', town: 'Waco', state: 'TX' };

test('lookup adds a "<name> HVAC <town>, <state>" search after the plain one', () => {
  assert.deepEqual(lookupQueries(typed, hvac), ['Haddix, Waco, TX', 'Haddix HVAC Waco, TX', 'haddixheatandair.com', 'Haddix']);
  assert.deepEqual(lookupQueries({ businessName: 'Haddix', website: 'haddixheatandair.com', town: 'Waco' }, hvac)[1], 'Haddix HVAC Waco');
  assert.deepEqual(lookupQueries({ businessName: 'Haddix', website: 'haddixheatandair.com' }, hvac)[1], 'Haddix HVAC');
  // A name that already says HVAC doesn't get it twice.
  assert.ok(!lookupQueries({ businessName: 'Haddix HVAC', website: 'x.com', town: 'Waco' }, hvac).includes('Haddix HVAC HVAC Waco'));
});

test('typed "Haddix" matches Google "Haddix Heating & Air" (leftover words are trade words)', () => {
  assert.ok(sameBusinessName('Haddix Heating & Air', 'Haddix'));
  assert.ok(sameBusinessName('Haddix Heating & Air', 'Haddix Heat and Air'));
  assert.ok(sameBusinessName('Haddix Heating and Air, LLC', 'Haddix Heating & Air'));
  assert.ok(sameBusinessName('Haddix A/C & Heating Services', 'Haddix'));
  assert.equal(pickPlace([place({ name: 'Waco Air Pros', website: 'wacoairpros.com' }), haddix], typed, hvac), haddix);
});

test('different businesses are not matched', () => {
  assert.ok(!sameBusinessName('Haddix Plumbing Supply', 'Haddix'), 'supply is not a trade word');
  assert.ok(!sameBusinessName('Air Pros Heating', 'Air Pro'), 'pro is not pros');
  assert.ok(!sameBusinessName('Heating & Air Services Company LLC', 'Heating and Air'), 'nothing distinctive in common');
  assert.ok(!sameBusinessName('Smith Plumbing', 'Smith Heating & Air'), 'neither is a subset of the other');
  assert.ok(!sameBusinessName('Haddix Electric', 'Haddix Heating & Air'));
  const airPros = place({ name: 'Air Pros Heating', website: 'airproshvac.com' });
  assert.equal(pickPlace([airPros], { businessName: 'Air Pro', website: 'airpro-tx.com', town: 'Waco', state: 'TX' }, hvac), null);
});

test('a name-only match must be in the shop\'s state', () => {
  const okHaddix = place({ name: 'Haddix Heating & Air', website: null, state: 'OK', town: 'Tulsa' });
  const supply = place({ name: 'Haddix Plumbing Supply', website: 'haddixsupply.com', state: 'OK', town: 'Tulsa' });
  assert.equal(pickPlace([supply, okHaddix], typed, hvac), null);
  // The same Haddix in Texas is accepted.
  const txHaddix = place({ name: 'Haddix Heating & Air', website: null });
  assert.equal(pickPlace([supply, okHaddix, txHaddix], typed, hvac), txHaddix);
});

test('a website on the same registrable label matches anywhere, whatever the subdomain or path', () => {
  assert.equal(domainLabel('book.haddixheatandair.com'), 'haddixheatandair');
  assert.equal(domainLabel('haddixheatandair.co.uk'), 'haddixheatandair');
  assert.equal(domainLabel('haddix.business.site'), '', 'shared hosts have no label of their own');
  assert.equal(domainLabel('facebook.com'), '');
  const sub = place({ name: 'Daniel Haddix', website: 'https://book.haddixheatandair.com/schedule?utm=gbp', state: 'OK' });
  assert.equal(pickPlace([sub], typed, hvac), sub);
  // Two shops on Facebook pages are not the same shop.
  const fb = place({ name: 'Someone Else HVAC', website: 'https://facebook.com/someoneelse' });
  assert.equal(pickPlace([fb], { businessName: 'Haddix Plumbing Supply', website: 'https://facebook.com/haddix', town: 'Waco', state: 'TX' }, hvac), null);
});

test('findBusiness: the "<name> HVAC <town>" search finds Haddix when the plain search does not', async () => {
  const seen = [];
  const search = async (q) => { seen.push(q); return q === 'Haddix HVAC Waco, TX' ? [place({ name: 'Brazos Comfort Heating & Air' }), haddix] : []; };
  const found = await findBusiness(typed, 'key', hvac, { search });
  assert.equal(found, haddix);
  assert.deepEqual(seen, ['Haddix, Waco, TX', 'Haddix HVAC Waco, TX']);
});

test('findBusiness: one Places error does not stop the other searches; an error with no match is thrown', async () => {
  const flaky = async (q) => { if (q === 'Haddix, Waco, TX') throw new Error('Places 503'); return q === 'Haddix HVAC Waco, TX' ? [haddix] : []; };
  assert.equal(await findBusiness(typed, 'key', hvac, { search: flaky }), haddix);
  const down = async () => { throw new Error('Places 503'); };
  await assert.rejects(findBusiness(typed, 'key', hvac, { search: down }), /Places 503/);
  assert.equal(await findBusiness(typed, 'key', hvac, { search: async () => [] }), null);
});

// Service-area shops (address hidden on Google). Places gives no address, or only "Waco, TX" / "Texas".
const sab = (opts, extra = {}) => ({ ...place(opts), addressComponents: [], pureServiceAreaBusiness: true, ...extra });

test('a service-area shop with no address is found by name plus its trade category', () => {
  const noAddr = sab({ name: 'Haddix Heating & Air' }, { types: ['hvac_contractor', 'service', 'point_of_interest'] });
  assert.equal(pickPlace([place({ name: 'Waco Air Pros', state: 'TX' }), noAddr], typed, hvac), noAddr);
  // Name alone isn't enough with no address: no town, no website, not a trade category.
  const bare = sab({ name: 'Haddix Heating & Air' }, { primaryType: null, primaryTypeDisplayName: null, types: ['point_of_interest'] });
  assert.equal(pickPlace([bare], typed, hvac), null);
  // A trade category only backs a strict name match, not a loose one ("Haddix Bros Plumbing Supply").
  const loose = sab({ name: 'Haddix Bros' }, { primaryType: 'plumber' });
  assert.equal(pickPlace([loose], typed, hvac), null);
});

test('a service-area shop showing only "Waco, TX" (or just the town) is found', () => {
  const cityOnly = sab({ name: 'Haddix Heating & Air' }, { formattedAddress: 'Waco, TX, USA', shortFormattedAddress: 'Waco, TX', primaryType: null, primaryTypeDisplayName: null });
  assert.equal(pickPlace([cityOnly], typed, hvac), cityOnly);
  const townOnly = sab({ name: 'Haddix Heating & Air' }, { shortFormattedAddress: 'Waco', primaryType: null, primaryTypeDisplayName: null });
  assert.equal(pickPlace([townOnly], typed, hvac), townOnly, 'the typed town in the address backs the name');
  const regionOnly = sab({ name: 'Haddix Heating & Air' }, { formattedAddress: 'Texas, USA' });
  assert.equal(pickPlace([regionOnly], typed, hvac), regionOnly);
});

test('a candidate whose address is in another state is still rejected, even as a service-area shop', () => {
  const tulsa = sab({ name: 'Haddix Heating & Air', website: 'haddixhvac.com' }, { formattedAddress: '410 S Main St, Tulsa, OK 74103, USA' });
  assert.equal(pickPlace([tulsa], typed, hvac), null);
  const okRegion = sab({ name: 'Haddix Heating & Air' }, { formattedAddress: 'Oklahoma, USA' });
  assert.equal(pickPlace([okRegion], typed, hvac), null);
  assert.equal(pickPlace([okRegion], { ...typed, state: 'OK' }, hvac), okRegion);
});

test('an alt domain carrying the shop\'s name word (haddixhvac.com) backs a name match, never replaces one', () => {
  const alt = sab({ name: 'Haddix Heating & Air', website: 'https://www.haddixhvac.com/' }, { primaryType: null, primaryTypeDisplayName: null });
  assert.equal(pickPlace([alt], typed, hvac), alt);
  const other = sab({ name: 'Brazos Comfort Heating & Air', website: 'https://haddixcomfort.com/' });
  assert.equal(pickPlace([other], typed, hvac), null, 'the domain word alone is not a name match');
});

test('findBusiness asks Places for what the service-area match needs', async () => {
  let fields;
  await findBusiness(typed, 'key', hvac, { search: async (q, f) => { fields = f; return []; } });
  for (const f of ['types', 'primaryType', 'websiteUri', 'formattedAddress', 'shortFormattedAddress', 'addressComponents', 'pureServiceAreaBusiness']) {
    assert.ok(fields.includes(f), f);
  }
});
