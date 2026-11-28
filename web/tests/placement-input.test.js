import test from 'node:test';
import assert from 'node:assert/strict';
import {bindBoardPointers, resolveTouchPlacement} from '../placement-input.js';

test('first tap previews and second tap at the same intersection confirms', () => {
  const first = resolveTouchPlacement(null, {x: 3, y: 5});
  assert.equal(first.confirm, false);
  assert.deepEqual(first.preview, {x: 3, y: 5, touchPreview: true});

  const second = resolveTouchPlacement(first.preview, {x: 3, y: 5});
  assert.equal(second.confirm, true);
  assert.equal(second.preview, null);
});

test('tapping another intersection moves the preview and still requires confirmation', () => {
  const first = resolveTouchPlacement(null, {x: 3, y: 5});
  const moved = resolveTouchPlacement(first.preview, {x: 4, y: 5});
  assert.equal(moved.confirm, false);
  assert.deepEqual(moved.preview, {x: 4, y: 5, touchPreview: true});
});

function boardInput() {
  const canvas = {setPointerCapture() {}};
  let preview, context = {};
  const moves = [];
  bindBoardPointers(canvas, {
    pointAt: event => ({x:event.x,y:event.y}),
    previewAt: (p, touchPreview) => { preview = p && {...p, touchPreview}; },
    getPreview: () => preview,
    position: () => context,
    mark: () => false,
    play: point => moves.push(point),
  });
  const send = (kind, x, y, pointerType='touch') =>
    canvas['onpointer'+kind]({pointerId: 1, pointerType, button: 0, isPrimary: true, x, y});
  return {send, moves, navigate() { context = {}; preview = null; }};
}

test('drag then tap the visible preview once places at the release point', () => {
  const {send, moves} = boardInput();
  send('down',2,2); send('move',3,4); send('up',3,4);
  assert.equal(moves.length, 0);
  send('down',3,4);
  assert.equal(moves.length, 0);
  send('up',3,4);
  assert.deepEqual(moves, [{x:3,y:4}]);
});

test('dragging from a preview, cancelling and navigating cannot confirm an old point', () => {
  const {send, moves, navigate} = boardInput();
  send('down',1,2); send('up',1,2);
  send('down',1,2); send('move',2,3); send('up',2,3);
  send('down',2,3); send('cancel',2,3);
  send('down',2,3); send('up',2,3);
  send('down',2,3); navigate(); send('up',2,3);
  assert.equal(moves.length, 0);
  send('down',4,5,'mouse');
  assert.deepEqual(moves, [{x:4,y:5}]);
});
