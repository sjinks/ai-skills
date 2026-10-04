import test from 'node:test';
import assert from 'node:assert/strict';
import { readCelsius } from '../sensor.js';

test('reads the calibrated chamber', async () => {
  assert.equal(await readCelsius(), 20);
});
