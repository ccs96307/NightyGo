// Earlier releases stored either a JSON string or raw SGF without a cursor.
export function readRecovery(raw, parse) {
  const saved = raw.trimStart().startsWith('(') ? raw : JSON.parse(raw);
  const legacy = typeof saved === 'string';
  const trees = parse(legacy ? saved : saved.sgf);
  const root = trees[legacy ? 0 : saved.gameIndex];
  if (!root) throw new Error('Missing game in recovery snapshot');
  const path = [root];
  if (legacy) {
    while (path.at(-1).children.length) path.push(path.at(-1).children[0]);
  } else {
    for (const index of saved.path) {
      const child = path.at(-1).children[index];
      if (!child) throw new Error('Missing variation in recovery snapshot');
      path.push(child);
    }
  }
  return {trees, root, path, current: path.at(-1), dirty: legacy || saved.dirty};
}

export function makeRecovery(sgf, trees, path, dirty) {
  return {
    sgf,
    gameIndex: trees.indexOf(path[0]),
    path: path.slice(1).map((node, i) => path[i].children.indexOf(node)),
    dirty,
  };
}
