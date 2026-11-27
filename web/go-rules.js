const BLACK = 1, WHITE = 2;
const neighbors = (x, y, n) => [[x - 1, y], [x + 1, y], [x, y - 1], [x, y + 1]].filter(([a, b]) => a >= 0 && b >= 0 && a < n && b < n);

export function estimateRulePosition(board, komi = 6.5) {
  const n = board.length, groups = [], groupAt = Array.from({length: n}, () => Array(n).fill(-1));
  for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) {
    if (!board[y][x] || groupAt[y][x] >= 0) continue;
    const color = board[y][x], id = groups.length, stones = [], liberties = new Set(), stack = [[x, y]];
    groupAt[y][x] = id;
    while (stack.length) {
      const [cx, cy] = stack.pop(); stones.push([cx, cy]);
      for (const [nx, ny] of neighbors(cx, cy, n)) {
        if (!board[ny][nx]) liberties.add(ny * n + nx);
        else if (board[ny][nx] === color && groupAt[ny][nx] < 0) { groupAt[ny][nx] = id; stack.push([nx, ny]); }
      }
    }
    groups.push({id, color, stones, liberties});
  }

  const regions = [], regionAt = Array.from({length: n}, () => Array(n).fill(-1));
  for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) {
    if (board[y][x] || regionAt[y][x] >= 0) continue;
    const id = regions.length, points = [], border = new Set(), stack = [[x, y]];
    let boundarySides = 0, stoneBoundarySides = 0;
    regionAt[y][x] = id;
    while (stack.length) {
      const [cx, cy] = stack.pop(); points.push([cx, cy]);
      const adjacent = neighbors(cx, cy, n); boundarySides += 4 - adjacent.length;
      for (const [nx, ny] of adjacent) {
        if (board[ny][nx]) { border.add(groupAt[ny][nx]); boundarySides++; stoneBoundarySides++; }
        else if (regionAt[ny][nx] < 0) { regionAt[ny][nx] = id; stack.push([nx, ny]); }
      }
    }
    const colors = new Set([...border].map(groupId => groups[groupId].color));
    const enclosedColor = colors.size === 1 && stoneBoundarySides / boundarySides >= .65 ? [...colors][0] : 0;
    regions.push({id, points, border, color: enclosedColor});
  }

  // Benson's iterative vital-eye test identifies groups alive regardless of
  // the opponent's moves. Ambiguous seki and unsettled groups stay unclassified.
  const alive = new Set();
  for (const color of [BLACK, WHITE]) {
    const activeGroups = new Set(groups.filter(g => g.color === color).map(g => g.id));
    const activeRegions = new Set(regions.filter(r => r.color === color).map(r => r.id));
    let changed = true;
    while (changed) {
      changed = false;
      for (const regionId of [...activeRegions]) {
        const region = regions[regionId];
        if ([...region.border].some(groupId => !activeGroups.has(groupId))) { activeRegions.delete(regionId); changed = true; }
      }
      for (const groupId of [...activeGroups]) {
        const vitalCount = [...activeRegions].filter(regionId => regions[regionId].points.every(([x, y]) => neighbors(x, y, n).some(([nx, ny]) => groupAt[ny][nx] === groupId))).length;
        if (vitalCount < 2) { activeGroups.delete(groupId); changed = true; }
      }
    }
    for (const groupId of activeGroups) alive.add(groupId);
  }

  const deadStones = Array(n * n).fill(false), deadGroups = [];
  for (const group of groups) {
    if (alive.has(group.id) || !group.liberties.size || group.liberties.size > 2) continue;
    const opponent = 3 - group.color;
    const enclosedLiberties = [...group.liberties].every(point => {
      const x = point % n, y = Math.floor(point / n), adjacent = neighbors(x, y, n).map(([nx, ny]) => groupAt[ny][nx]).filter(id => id >= 0);
      return adjacent.some(id => groups[id].color === opponent && alive.has(id)) && !adjacent.some(id => groups[id].color === group.color && alive.has(id));
    });
    if (enclosedLiberties) { deadGroups.push(group); for (const [x, y] of group.stones) deadStones[y * n + x] = true; }
  }

  const ownership = Array(n * n).fill(0); let black = 0, white = komi;
  for (const group of groups) {
    if (deadGroups.includes(group)) {
      if (group.color === BLACK) white += group.stones.length; else black += group.stones.length;
      continue;
    }
    if (group.color === BLACK) black += group.stones.length; else white += group.stones.length;
  }
  for (const region of regions) {
    if (region.color === BLACK) { black += region.points.length; for (const [x, y] of region.points) ownership[y * n + x] = 1; }
    else if (region.color === WHITE) { white += region.points.length; for (const [x, y] of region.points) ownership[y * n + x] = -1; }
  }

  // Fill in only open points with a clear, nearby influence advantage. These
  // are marked separately from enclosed territory and never treated as certain.
  if (groups.some(g => g.color === BLACK && !deadGroups.includes(g)) && groups.some(g => g.color === WHITE && !deadGroups.includes(g))) {
    const distances = [null, Array(n * n).fill(Infinity), Array(n * n).fill(Infinity)];
    for (const color of [BLACK, WHITE]) {
      const distance = distances[color], queue = [];
      for (const group of groups) if (group.color === color && !deadGroups.includes(group)) for (const [x, y] of group.stones) { const point = y * n + x; if (distance[point] !== 0) { distance[point] = 0; queue.push(point); } }
      for (let i = 0; i < queue.length; i++) { const point = queue[i], x = point % n, y = Math.floor(point / n); for (const [nx, ny] of neighbors(x, y, n)) { const next = ny * n + nx; if (distance[next] > distance[point] + 1) { distance[next] = distance[point] + 1; queue.push(next); } } }
    }
    const reach = Math.max(3, Math.floor(n / 3));
    for (let point = 0; point < n * n; point++) {
      const x = point % n, y = Math.floor(point / n);
      if (board[y][x] || ownership[point]) continue;
      const b = distances[BLACK][point], w = distances[WHITE][point];
      if (b <= reach && w <= reach && Math.abs(b - w) >= 2) {
        const owner = b < w ? BLACK : WHITE; ownership[point] = owner === BLACK ? 2 : -2;
        if (owner === BLACK) black++; else white++;
      }
    }
  }

  const diff = Math.abs(black - white);
  return {ownership, deadStones, deadGroupCount: deadGroups.length, black, white, komi, diff, winner: black > white ? 'B' : 'W'};
}
