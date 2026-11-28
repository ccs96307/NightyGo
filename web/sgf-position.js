/** Validate and replay a single path before changing the displayed game. */
const BLACK = 1, WHITE = 2;

export function sgfBoardSize(root) {
  const raw = root?.props.SZ?.[0] ?? '19';
  const match = /^(\d+)(?::(\d+))?$/.exec(raw);
  if (!match) throw Error('Invalid SGF board size');
  const n = Number(match[1]);
  if (n < 2 || n > 25 || (match[2] !== undefined && Number(match[2]) !== n)) {
    throw Error('Unsupported SGF board dimensions');
  }
  return n;
}

export function decodePoint(value, size) {
  if (value.length !== 2) throw Error('Invalid SGF coordinate');
  const x = value.charCodeAt(0) - 97, y = value.charCodeAt(1) - 97;
  if (x < 0 || y < 0 || x >= size || y >= size) throw Error('SGF coordinate outside board');
  return [x, y];
}

export function expandSetup(values, size) {
  const points = [];
  for (const range of values || []) {
    const ends = range.split(':');
    if (ends.length > 2) throw Error('Invalid SGF point range');
    const [x1, y1] = decodePoint(ends[0], size);
    const [x2, y2] = ends.length === 2 ? decodePoint(ends[1], size) : [x1, y1];
    for (let y = Math.min(y1, y2); y <= Math.max(y1, y2); y++) {
      for (let x = Math.min(x1, x2); x <= Math.max(x1, x2); x++) points.push([x, y]);
    }
  }
  return points;
}

export function isSgfPass(value, size) {
  return value === '' || (size <= 19 && value === 'tt');
}

export function replayPath(nodes, applyMove) {
  const root = nodes[0];
  const size = sgfBoardSize(root);
  let board = Array.from({length: size}, () => Array(size).fill(0));
  let toPlay = Number(root.props.HA?.[0]) >= 2 ? WHITE : BLACK;
  let last = null, positionHistory = [board];
  const captures = {[BLACK]: 0, [WHITE]: 0};
  for (const {props} of nodes) {
    if (props.AE || props.AB || props.AW) {
      board = board.map(row => row.slice());
      for (const [key, color] of [['AE', 0], ['AB', BLACK], ['AW', WHITE]]) {
        for (const [x, y] of expandSetup(props[key], size)) board[y][x] = color;
      }
      positionHistory = [board];
      last = null;
    }
    if (props.PL) {
      if (!['B', 'W'].includes(props.PL[0])) throw Error('Invalid SGF player');
      toPlay = props.PL[0] === 'W' ? WHITE : BLACK;
    }
    if (!props.B && !props.W) continue;
    if (props.B && props.W) throw Error('Two moves in one SGF node');
    const color = props.B ? BLACK : WHITE;
    const [value] = props.B || props.W;
    if (isSgfPass(value, size)) {
      last = {color, x: null, y: null, pass: true};
    } else {
      const [x, y] = decodePoint(value, size);
      const result = applyMove(board, color, x, y);
      board = result.grid;
      captures[color] += result.captured.length;
      last = {color, x, y};
    }
    toPlay = 3 - color;
    positionHistory.push(board);
  }
  return {board, toPlay, last, captures, positionHistory};
}
