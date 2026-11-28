export function resolveTouchPlacement(preview, point) {
  if (preview?.touchPreview && preview.x === point.x && preview.y === point.y) {
    return {confirm: true, preview: null};
  }
  return {
    confirm: false,
    preview: {x: point.x, y: point.y, touchPreview: true},
  };
}

// Confirm on release so a drag away from an already previewed intersection
// cannot place the stone the moment the finger touches the board.
export function bindBoardPointers(canvas, {pointAt, previewAt, getPreview, position, mark, play}) {
  let gesture = null;
  const same = (a, b) => a && b && a.x === b.x && a.y === b.y;
  canvas.onpointerdown = event => {
    if (event.button !== 0 || event.isPrimary === false) return;
    const point = pointAt(event);
    if (!point || mark(point)) return;
    if (event.pointerType !== 'touch') {
      play(point);
      return;
    }
    const {confirm} = resolveTouchPlacement(getPreview(), point);
    gesture = {pointerId: event.pointerId, board: position(), start: point, confirm};
    canvas.setPointerCapture(event.pointerId);
    previewAt(point, true);
  };
  canvas.onpointermove = event => {
    const point = pointAt(event);
    if (event.pointerType !== 'touch') {
      if (!gesture) previewAt(point, false);
    } else if (gesture?.pointerId === event.pointerId && gesture.board === position()) {
      if (!same(point, gesture.start)) gesture.confirm = false;
      previewAt(point, true);
    }
  };
  canvas.onpointerup = event => {
    if (gesture?.pointerId !== event.pointerId) return;
    const previous = gesture;
    gesture = null;
    if (previous.board !== position()) return;
    const point = pointAt(event);
    if (previous.confirm && same(point, previous.start)) {
      previewAt(null, true);
      play(point);
    } else {
      previewAt(point, true);
    }
  };
  canvas.onpointerleave = event => {
    if (!gesture && event.pointerType !== 'touch') previewAt(null, false);
  };
  canvas.onpointercancel = canvas.onlostpointercapture = event => {
    if (gesture?.pointerId === event.pointerId) {
      gesture = null;
      previewAt(null, true);
    }
  };
}
