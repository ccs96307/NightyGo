import test from 'node:test';
import assert from 'node:assert/strict';
import {parseSgf} from '../sgf-core.js';
import {replayPath, sgfBoardSize} from '../sgf-position.js';

test('ordinary handicap starts with White and explicit PL takes precedence', () => {
  const [root] = parseSgf('(;SZ[9]HA[2]AB[gc][cg])');
  const pos = replayPath([root]);
  assert.equal(pos.toPlay, 2);
  assert.equal(pos.board[2][6], 1);
  assert.equal(pos.board[6][2], 1);
  root.props.PL = ['B'];
  assert.equal(replayPath([root]).toPlay, 1);
});

test('non-square, fractional and unsupported sizes cannot be truncated during import', () => {
  for (const size of ['9:13', '9.5', '0', '26', 'abc']) {
    assert.throws(() => sgfBoardSize({props:{SZ:[size]}}));
  }
  assert.equal(sgfBoardSize({props:{SZ:['13:13']}}), 13);
});

test('rejects malformed moves before calling the rules engine', () => {
  for (const move of ['W[zz]', 'W[aa]B[aa]']) {
    const [game] = parseSgf('(;SZ[9];' + move + ')');
    assert.throws(() => replayPath([game, game.children[0]]), /SGF/);
  }
});
