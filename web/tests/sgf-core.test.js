import test from 'node:test';
import assert from 'node:assert/strict';
import {parseSgf, serializeSgf} from '../sgf-core.js';

test('parses a main line and sibling variations', () => {
  const [root] = parseSgf('(;FF[4];B[aa](;W[bb])(;W[cc]))');
  assert.equal(root.children[0].children.length, 2);
  assert.deepEqual(root.children[0].children.map(n => n.props.W[0]), ['bb', 'cc']);
});

test('parses SGF collections and preserves their games on serialization', () => {
  const games = parseSgf('(;SZ[9];B[aa])\n(;SZ[13];W[bb])');
  assert.equal(games.length, 2);
  const serialized = games.map(serializeSgf).join('\n');
  assert.equal(parseSgf(serialized).length, 2);
});

test('handles escaped delimiters and escaped newlines', () => {
  const [root] = parseSgf('(;C[closing \\] bracket\\\nnext])');
  assert.equal(root.props.C[0], 'closing ] bracketnext');
  assert.equal(parseSgf(serializeSgf(root))[0].props.C[0], root.props.C[0]);
});

test('rejects malformed SGF instead of silently truncating', () => {
  assert.throws(() => parseSgf('(;C[unterminated]'));
  assert.throws(() => parseSgf(''));
});
