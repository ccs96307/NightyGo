export function resolveTouchPlacement(preview, point) {
  if (preview?.touchPreview && preview.x === point.x && preview.y === point.y) {
    return {confirm: true, preview: null};
  }
  return {
    confirm: false,
    preview: {x: point.x, y: point.y, touchPreview: true},
  };
}
