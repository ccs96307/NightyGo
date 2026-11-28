import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const source = readFileSync(new URL('../engine-worker.js', import.meta.url), 'utf8');

// Exercise the worker queue with CPU-style immediate promises. A deterministic
// fake clock delivers control messages at the next browser task boundary.
function workerFixture(afterMessage) {
  const messages = [];
  const timers = [];
  const self = {
    postMessage(data) {
      messages.push(data);
      afterMessage?.(data, self);
    },
  };
  const context = vm.createContext({self, importScripts() {}, setTimeout: fn => timers.push(fn)});
  vm.runInContext(source, context);
  vm.runInContext('searchMoves = async () => ({visits:3, winrate:0.2, pv:[]})', context);
  return {
    messages,
    post: data => self.onmessage({data}),
    async tick() {
      await new Promise(resolve => setImmediate(resolve));
      timers.shift()?.();
      await new Promise(resolve => setImmediate(resolve));
    },
    done: () => vm.runInContext('requestQueue', context),
  };
}

const request = requestId => ({
  type: 'analyzeCandidates', requestId, moves: [], toPlay: 1, komi: 6.5,
  candidateLocs: [10,20], continuous: true,
});

test('a stopped CPU analysis releases the queue and drops its unfinished candidate', async () => {
  const worker = workerFixture();
  worker.post(request(1));
  await worker.tick();
  worker.post({type: 'stopAnalysis', throughRequestId: 1});
  worker.post({...request(2), continuous: false});
  await worker.tick();
  await worker.done();
  const candidates = id => worker.messages.filter(m => m.requestId === id && m.type === 'analysisCandidate');
  assert.deepEqual(candidates(1).map(m => m.candidate.loc), [10]);
  assert.deepEqual(candidates(2).map(m => m.candidate.loc), [10,20]);
  assert.equal(candidates(2)[0].candidate.winrate, 0.8);
});

test('a cancellation arriving before dispatch also stops the queued request', async () => {
  const worker = workerFixture();
  worker.post(request(5));
  worker.post({type: 'stopAnalysis', throughRequestId: 5});
  await worker.done();
  assert.equal(worker.messages.at(-1).result.stopped, true);
  assert.equal(worker.messages.filter(m => m.type === 'analysisCandidate').length, 0);
});
