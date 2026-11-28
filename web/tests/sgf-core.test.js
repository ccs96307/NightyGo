import test from 'node:test';
import assert from 'node:assert/strict';
import {layoutGameTree, parseSgf, parseSgfBytes, serializeSgf, variationMoveCounts} from '../sgf-core.js';

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

test('export normalizes CA to UTF-8 without changing source metadata', () => {
  const [game] = parseSgf('(;CA[ISO-8859-1]PB[Élodie]C[白棋])');
  const exported = new TextEncoder().encode(serializeSgf(game));
  assert.deepEqual(parseSgfBytes(exported)[0].props, {CA:['UTF-8'], PB:['Élodie'], C:['白棋']});
  assert.deepEqual(game.props.CA, ['ISO-8859-1']);
});

test('import uses the declared encoding for each game, including spaced CA properties', () => {
  const games = parseSgfBytes(Buffer.concat([
    Buffer.from('(;CA [ISO-8859-1]PB[Élodie])', 'latin1'),
    Buffer.from('(;CA[UTF-8]PB[白棋])'),
  ]));
  assert.deepEqual(games.map(game => game.props.PB[0]), ['Élodie', '白棋']);
});

test('import honors UTF-8 BOM and rejects invalid declared UTF-8', () => {
  const bytes = new TextEncoder().encode('\ufeff(;PB[白棋])');
  assert.deepEqual(parseSgfBytes(bytes)[0].props.PB, ['白棋']);
  assert.throws(() => parseSgfBytes(Buffer.from('(;CA[UTF-8]C[\xff])', 'latin1')));
});

test('parses Big5 text whose trailing byte is an SGF delimiter', () => {
  const pair = Buffer.from([0xa5, 0x5c]); // 功
  const data = Buffer.concat([Buffer.from('(;CA[Big5]C['), pair, Buffer.from('])')]);
  assert.deepEqual(parseSgfBytes(data)[0].props.C, ['功']);
});

test('nested forks occupy separate lanes and main continuations stay aligned', () => {
  const [root] = parseSgf('(;SZ[9](;B[aa](;W[ab])(;W[ac]))(;B[ba];W[bb]))');
  const {nodes, edges} = layoutGameTree(root);
  assert.equal(new Set(nodes.map(({x,y}) => x + ',' + y)).size, nodes.length);
  for (const {from,to} of edges) {
    if (from.node.children[0] === to.node) assert.equal(from.x, to.x);
    else assert.ok(to.x > from.x);
  }
  assert.deepEqual(layoutGameTree(root,true).nodes.map(({x}) => x), [0,0,0]);
});

test('branch-local totals and tree labels count stones and passes, including a root move', () => {
  const [root] = parseSgf('(;B[aa];C[notes](;W[];B[ba])(;W[bb]))');
  const note = root.children[0];
  assert.deepEqual(variationMoveCounts([root,note]), {played:1, total:3});
  assert.deepEqual(variationMoveCounts([root,note,note.children[1]]), {played:2, total:2});
  const {nodes} = layoutGameTree(root);
  assert.deepEqual(nodes.map(item => item.move), [1,1,2,3,2]);
});
