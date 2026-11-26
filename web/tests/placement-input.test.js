import test from 'node:test';
import assert from 'node:assert/strict';
import {resolveTouchPlacement} from '../placement-input.js';

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
