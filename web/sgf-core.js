/** Small, dependency-free SGF collection parser and serializer. */
function parseCollection(text, onTree) {
  let i = 0;
  const skip = () => { while (/\s/.test(text[i] || '') && i < text.length) i++; };
  const value = () => {
    i++; let v = '';
    while (i < text.length) {
      const c = text[i++];
      if (c === ']') return v;
      if (c === '\\' && i < text.length) {
        const e = text[i++];
        if (e === '\r') { if (text[i] === '\n') i++; continue; }
        if (e === '\n') continue;
        v += e;
      } else v += c;
    }
    throw Error('Unterminated SGF value');
  };
  function parseNode() {
    i++; const node = {props: {}, children: []}; skip();
    while (/[A-Z]/.test(text[i] || '')) {
      const start = i; while (/[A-Z]/.test(text[i] || '')) i++;
      const key = text.slice(start, i); skip(); const vals = [];
      while (text[i] === '[') { vals.push(value()); skip(); }
      if (!vals.length) throw Error('Property without value');
      node.props[key] = [...(node.props[key] || []), ...vals];
    }
    return node;
  }
  function tree() {
    if (text[i++] !== '(') throw Error('Expected game tree');
    skip(); const seq = [];
    while (text[i] === ';') { seq.push(parseNode()); skip(); }
    if (!seq.length) throw Error('Game tree has no nodes');
    for (let k = 0; k < seq.length - 1; k++) seq[k].children.push(seq[k + 1]);
    const tail = seq.at(-1);
    while (text[i] === '(') { tail.children.push(tree()); skip(); }
    if (text[i++] !== ')') throw Error('Unclosed game tree');
    return seq[0];
  }
  const games = []; skip();
  while (i < text.length) {
    const start = i;
    const game = tree();
    games.push(game);
    onTree?.(game, start, i);
    skip();
  }
  if (!games.length) throw Error('Empty SGF');
  return games;
}

export function parseSgf(text) {
  return parseCollection(text);
}

// The supported ASCII-compatible encodings preserve ')'. Decode through each
// possible boundary before counting parentheses. This distinguishes a genuine
// SGF escape from a backslash that is part of a Big5 or Shift-JIS character.
function readEncodedGame(bytes, start, charset) {
  const decoder = new TextDecoder(charset, {fatal: true});
  const chunks = [];
  let depth = 0, inValue = false, escaped = false;
  let offset = start;
  while (offset < bytes.length) {
    const close = bytes.indexOf(0x29, offset);
    if (close === -1) break;
    const chunk = decoder.decode(bytes.subarray(offset, close + 1), {stream: true});
    chunks.push(chunk);
    offset = close + 1;
    for (const ch of chunk) {
      if (escaped) escaped = false;
      else if (inValue && ch === '\\') escaped = true;
      else if (inValue && ch === ']') inValue = false;
      else if (!inValue && ch === '[') inValue = true;
      else if (!inValue && ch === '(') depth++;
      else if (!inValue && ch === ')') {
        if (--depth < 0) throw Error('Unexpected SGF tree delimiter');
        if (depth === 0) return {game: parseSgf(chunks.join(''))[0], end: offset};
      }
    }
  }
  throw Error('Unclosed SGF game');
}

// Use byte offsets to decode each game with its own root CA declaration.
// A UTF-8 BOM is a signature and is outside the SGF document.
export function parseSgfBytes(input) {
  let bytes = new Uint8Array(input);
  const hasBom = bytes[0] === 0xef && bytes[1] === 0xbb && bytes[2] === 0xbf;
  if (hasBom) bytes = bytes.subarray(3);
  const byteText = new TextDecoder('windows-1252').decode(bytes);
  const games = [];
  try {
    parseCollection(byteText, (game, start, end) => {
      const charset = game.props.CA?.[0] || (hasBom ? 'utf-8' : 'iso-8859-1');
      const decoded = new TextDecoder(charset, {fatal: true}).decode(bytes.subarray(start, end));
      games.push(parseSgf(decoded)[0]);
    });
    return games;
  } catch (error) {
    // A multibyte encoding can use a closing bracket or backslash as a trail
    // byte. In that case find the declared codec and parse its decoded text.
    const declarations = byteText.matchAll(/\bCA\s*\[([a-zA-Z0-9_.:-]+)\]/g);
    const charsets = new Set([hasBom ? 'utf-8' : 'iso-8859-1', ...Array.from(declarations, m => m[1])]);
    const decodedGames = [];
    let start = 0;
    while (start < bytes.length) {
      while (start < bytes.length && /\s/.test(byteText[start])) start++;
      if (start === bytes.length) break;
      const previous = start;
      for (const charset of charsets) {
        try {
          const {game, end} = readEncodedGame(bytes, start, charset);
          const expected = game.props.CA?.[0] || (hasBom ? 'utf-8' : 'iso-8859-1');
          if (new TextDecoder(expected).encoding !== new TextDecoder(charset).encoding) continue;
          decodedGames.push(game);
          start = end;
          break;
        } catch { /* Try the next declared encoding. */ }
      }
      if (start === previous) throw error;
    }
    if (decodedGames.length) return decodedGames;
    throw error;
  }
}

const escapeValue = value => String(value).replaceAll('\\', '\\\\').replaceAll(']', '\\]');
export function serializeSgf(root) {
  const nodeText = node => ';' + Object.entries(node === root ? {...node.props, CA: ['UTF-8']} : node.props || {})
    .filter(([key]) => /^[A-Z]+$/.test(key))
    .map(([key, values]) => key + (values || []).map(v => `[${escapeValue(v)}]`).join('')).join('');
  const treeText = start => {
    let out = '('; let node = start;
    while (true) {
      out += nodeText(node); const children = node.children || [];
      if (!children.length) break;
      if (children.length === 1) { node = children[0]; continue; }
      for (const child of children) out += treeText(child);
      break;
    }
    return out + ')';
  };
  return treeText(root);
}

function hasMove(node) {
  return Boolean(node.props.B || node.props.W);
}

export function variationMoveCounts(path) {
  const played = path.filter(hasMove).length;
  let total = played;
  for (let next = path.at(-1)?.children[0]; next; next = next.children[0]) {
    if (hasMove(next)) total++;
  }
  return {played, total};
}

export function layoutGameTree(root, mainOnly = false) {
  const nodes = [], edges = [];
  function place(node, x, y, precedingMoves, from) {
    const item = {node, x, y, move: precedingMoves + Number(hasMove(node))};
    nodes.push(item);
    if (from) edges.push({from, to: item});
    let nextLane = x;
    for (const child of (mainOnly ? node.children.slice(0, 1) : node.children)) {
      nextLane = place(child, nextLane, y + 1, item.move, item);
    }
    return Math.max(nextLane, x + 1);
  }
  place(root, 0, 0, 0, null);
  return {nodes, edges};
}
