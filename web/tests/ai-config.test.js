import test from 'node:test';
import assert from 'node:assert/strict';
import {DEFAULT_AI_CONFIG, parseAiConfig, validateAiConfig} from '../ai-config.js';

test('accepts and normalizes a NightyGo AI profile', () => {
  assert.deepEqual(parseAiConfig(JSON.stringify(DEFAULT_AI_CONFIG)), DEFAULT_AI_CONFIG);
  assert.deepEqual(validateAiConfig({...DEFAULT_AI_CONFIG, ignored: true}), DEFAULT_AI_CONFIG);
});

test('rejects malformed, unsupported, and out-of-range profiles', () => {
  assert.throws(() => parseAiConfig('{'), /valid JSON/);
  assert.throws(() => validateAiConfig([]), /JSON object/);
  assert.throws(() => validateAiConfig({...DEFAULT_AI_CONFIG, version: 2}), /version/);
  assert.throws(() => validateAiConfig({...DEFAULT_AI_CONFIG, searchVisits: 64}), /searchVisits/);
  assert.throws(() => validateAiConfig({...DEFAULT_AI_CONFIG, maxSearchTimeMs: 100000}), /maxSearchTimeMs/);
});
