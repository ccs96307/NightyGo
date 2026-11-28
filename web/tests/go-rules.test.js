import test from 'node:test';
import assert from 'node:assert/strict';
import {estimateRulePosition} from '../go-rules.js';

test('an even area estimate with zero komi is a draw', () => {
  const estimate = estimateRulePosition(Array.from({length:9}, () => Array(9).fill(0)), 0);
  assert.equal(estimate.winner, '0');
  assert.equal(estimate.diff, 0);
});

test('separated groups exert local influence even when their opponent is distant', () => {
  const board = Array.from({length:19}, () => Array(19).fill(0));
  board[3][3] = 1;
  board[15][15] = 2;
  const {ownership} = estimateRulePosition(board);
  assert.equal(ownership[3 * 19 + 4], 2);
  assert.equal(ownership[15 * 19 + 14], -2);
  assert.equal(ownership[9 * 19 + 9], 0);
});

test('removes a trapped dead group before counting its surrounding liberties', () => {
  const board = Array.from({length:9}, () => Array(9).fill(1));
  board[0][0] = board[0][8] = 0; // Two independent corner eyes.
  board[4][4] = 2;
  board[4][5] = 0;
  const {deadGroupCount, black, ownership} = estimateRulePosition(board, 0);
  assert.equal(deadGroupCount, 1);
  assert.equal(black, 81);
  assert.equal(ownership[4*9+4], 1);
  assert.equal(ownership[4*9+5], 1);
  assert.equal(board[4][4], 2);
});
