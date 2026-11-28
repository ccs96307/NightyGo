// Exercise the single-thread API used by NightyGo with a real model.
// node scripts/check-web-eval.cjs <model.bin.gz>
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

async function check() {
  const assets = path.resolve(__dirname, '../web/assets/engine');
  const scratch = fs.mkdtempSync(path.join(os.tmpdir(), 'nightygo-eval-'));
  try {
    // The browser classic script supports CommonJS. Our web/ package uses ESM.
    const commonJs = path.join(scratch, 'kataeval.cjs');
    fs.copyFileSync(path.join(assets, 'kataeval.js'), commonJs);
    const m = await require(commonJs)({locateFile: filename => path.join(assets, filename)});
    m.ccall('kgeSetForceCpu', null, ['number'], [1]);
    m.FS.writeFile('/model.bin.gz', fs.readFileSync(process.argv[2]));
    assert.equal(await m.ccall('kgeLoad', 'number', ['string', 'number'], ['/model.bin.gz', 9], {async: true}), 1);
    const policy = m._malloc(82 * 4);
    const value = m._malloc(5 * 4);
    const owner = m._malloc(81 * 4);
    // Make immediate reuse visible even when the owner allocation is at the top of the heap.
    const guard = m._malloc(24);
    for (const toPlay of [1, 2]) {
      const args = [0, 0, 0, toPlay, 30, 0, policy, value, owner];
      assert.equal(await m.ccall('kgeEvalSeq', 'number', args.map(() => 'number'), args, {async: true}), 1);
      const other = m._malloc(81 * 4);
      assert.notEqual(other, owner, 'kgeEvalSeq freed its caller-owned ownership buffer');
      m._free(other);
      const [whiteLogit, blackLogit] = m.HEAPF32.subarray(value >> 2, (value >> 2) + 2);
      assert.ok(whiteLogit > blackLogit, 'white should be favored at +30 komi for either side to move');
      for (const point of m.HEAPF32.subarray(owner >> 2, (owner >> 2) + 81)) {
        assert.ok(Number.isFinite(point) && Math.abs(point) <= 1, 'ownership must be normalized');
      }
    }
    [guard, owner, value, policy].forEach(ptr => m._free(ptr));
    console.log('PASS real model: black and white perspective, ownership range and buffer lifetime');
  } finally {
    fs.rmSync(scratch, {recursive: true, force: true});
  }
}
check().catch(error => { console.error(error); process.exitCode = 1; });
