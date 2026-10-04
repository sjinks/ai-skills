import test from 'node:test';
import assert from 'node:assert/strict';
import { clamp } from '../clamp.js';

test('keeps an in-range value', () => {
  assert.equal(clamp(5, 0, 10), 5);
});

test('clamps below range', () => {
  assert.equal(clamp(-1, 0, 10), 0);
});

test('clamps above range', () => {
  assert.equal(clamp(11, 0, 10), 10);
});
