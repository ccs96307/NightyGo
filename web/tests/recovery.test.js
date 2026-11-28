import assert from 'node:assert/strict';
import test from 'node:test';
import {makeRecovery, readRecovery} from '../recovery.js';
import {parseSgf} from '../sgf-core.js';

const sgf = '(;SZ[9])(;SZ[13];B[aa](;W[bc])(;W[cd];B[gg]))';
test('recovery restores the selected game and variation, even mid-line', () => {
  const games = parseSgf(sgf);
  const firstMove = games[1].children[0];
  const path = [games[1], firstMove, firstMove.children[1]];
  const restored = readRecovery(JSON.stringify(makeRecovery(sgf, games, path, false)), parseSgf);
  assert.equal(restored.root.props.SZ[0], '13');
  assert.deepEqual(restored.current.props.W, ['cd']);
  assert.equal(restored.path.length, 3);
  assert.equal(restored.dirty, false);
});
test('both historical snapshot encodings recover the moves', () => {
  const game = '(;SZ[9];B[bc];W[])';
  for (const raw of [game, JSON.stringify(game)]) {
    const restored = readRecovery(raw, parseSgf);
    assert.deepEqual(restored.current.props.W, ['']);
    assert.equal(restored.path.length, 3);
  }
});
