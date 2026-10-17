import test from 'node:test';
import assert from 'node:assert/strict';
import { newestReviewNote } from '../grade.mjs';

test('service-area shops get a plain note, not "turn on Places API"', () => {
  const n = newestReviewNote({ days: null, serviceArea: true });
  assert.match(n, /service-area business/);
  assert.doesNotMatch(n, /turn on/);
});

test('NOT_FOUND from the older endpoint is not blamed on the key', () => {
  const n = newestReviewNote({ days: null, error: 'NOT_FOUND: The provided Place ID is no longer valid.' });
  assert.doesNotMatch(n, /turn on/);
  assert.match(n, /5 reviews Google shows/);
});

test('REQUEST_DENIED still says to turn on Places API', () => {
  assert.match(newestReviewNote({ days: null, error: 'REQUEST_DENIED: not enabled' }), /turn on "Places API"/);
});
