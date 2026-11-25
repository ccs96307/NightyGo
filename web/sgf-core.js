/** Small, dependency-free SGF collection parser and serializer. */
export function parseSgf(text) {
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
  while (i < text.length) { games.push(tree()); skip(); }
  if (!games.length) throw Error('Empty SGF');
  return games;
}

const escapeValue = value => String(value).replaceAll('\\', '\\\\').replaceAll(']', '\\]');
export function serializeSgf(root) {
  if (!root.props.CA) root.props.CA = ['UTF-8'];
  const nodeText = node => ';' + Object.entries(node.props || {})
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
