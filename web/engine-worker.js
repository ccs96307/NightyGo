/* KataGo WASM runs off the UI thread. Model bytes are sent by the page and never uploaded. */
importScripts('assets/engine/kataeval.js');
let moduleInstance, boardSize = 19, moveLocPtr, moveColorPtr;
let lastStoppedAnalysis = 0;
function allocateMoves(moves) {
  if (moveLocPtr) moduleInstance._free(moveLocPtr);
  if (moveColorPtr) moduleInstance._free(moveColorPtr);
  const max = Math.max(1, moves.length);
  moveLocPtr = moduleInstance._malloc(max * 4); moveColorPtr = moduleInstance._malloc(max * 4);
  const locs = moveLocPtr >> 2, cols = moveColorPtr >> 2;
  moves.forEach((m, i) => { moduleInstance.HEAP32[locs + i] = m.loc; moduleInstance.HEAP32[cols + i] = m.color; });
  return moves.length;
}
async function load({bytes, size}, onProgress = () => {}) {
  boardSize = size;
  moduleInstance = await createKata({locateFile: name => new URL(`assets/engine/${name}`, self.location.href).href});
  onProgress('loadingNetwork');
  moduleInstance.FS.writeFile('/nightygo-model.bin.gz', new Uint8Array(bytes));
  const ok = await moduleInstance.ccall('kgeLoad','number',['string','number'],['/nightygo-model.bin.gz',boardSize],{async:true});
  if (!ok) throw new Error(moduleInstance.ccall('kgeError','string',[],[]));
  return {version:moduleInstance.ccall('kgeModelVersion','number',[],[]),gpu:!!moduleInstance.ccall('kgeBackendIsGpu','number',[],[])};
}
async function evaluateMoves(moves,toPlay,komi) {
  const count = allocateMoves(moves), hw = boardSize * boardSize;
  const policy = moduleInstance._malloc((hw + 1) * 4), value = moduleInstance._malloc(5 * 4), owner = moduleInstance._malloc(hw * 4);
  try {
    const ok = await moduleInstance.ccall('kgeEvalSeq','number',Array(9).fill('number'),[moveLocPtr,moveColorPtr,count,toPlay,komi,0,policy,value,owner],{async:true});
    if (!ok) throw new Error(moduleInstance.ccall('kgeError','string',[],[]));
    const vals = Array.from(moduleInstance.HEAPF32.subarray(value >> 2,(value >> 2)+5));
    // KataGo returns win/loss/no-result logits; normalize before exposing percentages.
    const maxLogit=Math.max(vals[0],vals[1],vals[2]);
    const probs=[vals[0],vals[1],vals[2]].map(x=>Math.exp(x-maxLogit));
    const probSum=probs.reduce((sum,x)=>sum+x,0);
    vals[0]=probs[0]/probSum;vals[1]=probs[1]/probSum;vals[2]=probs[2]/probSum;
    const logits = Array.from(moduleInstance.HEAPF32.subarray(policy >> 2,(policy >> 2)+hw+1));
    const ownership = Array.from(moduleInstance.HEAPF32.subarray(owner >> 2,(owner >> 2)+hw));
    const best = logits.map((v,loc)=>({loc,score:v})).filter(x=>x.loc===hw||Number.isFinite(x.score)).sort((a,b)=>b.score-a.score);
    const out = {value:vals,candidates:best,ownership};
    return out;
  } finally {
    for (const ptr of [policy, value, owner]) moduleInstance._free(ptr);
  }
}
async function searchMoves({moves,toPlay,komi,visits,maxSearchTimeMs=15000}) {
  const count = allocateMoves(moves), best=moduleInstance._malloc(4), wr=moduleInstance._malloc(4), pvCap=12, pv=moduleInstance._malloc(pvCap*4), pvLen=moduleInstance._malloc(4), done=moduleInstance._malloc(4);
  try {
    const ok=await moduleInstance.ccall('kgeSearch','number',Array(13).fill('number'),[moveLocPtr,moveColorPtr,count,toPlay,komi,visits,maxSearchTimeMs,best,wr,pv,pvCap,pvLen,done],{async:true});
    if(!ok)throw new Error(moduleInstance.ccall('kgeError','string',[],[]));
    const result={best:moduleInstance.HEAP32[best>>2],winrate:moduleInstance.HEAPF32[wr>>2],visits:moduleInstance.HEAP32[done>>2],pv:Array.from(moduleInstance.HEAP32.subarray(pv>>2,(pv>>2)+moduleInstance.HEAP32[pvLen>>2]))};
    return result;
  } finally {
    for (const ptr of [best, wr, pv, pvLen, done]) moduleInstance._free(ptr);
  }
}
async function analyzeCandidates({moves,toPlay,komi,candidateLocs,visits=128,maxSearchTimeMs=15000,continuous=false},onUpdate=()=>{}, shouldStop=()=>false){
  const candidates=new Map(),opponent=toPlay===1?2:1,total=Math.max(1,candidateLocs.length),perCandidateTime=Math.max(250,Math.floor(maxSearchTimeMs/total));
  if (!candidateLocs.length) return {candidates: [], rounds: 0};
  let round=0;
  do{
    round++;
    for(let index=0;index<candidateLocs.length;index++){
      if(shouldStop()) break;
      const loc=candidateLocs[index],moveLoc=loc===boardSize*boardSize?-1:loc;
      onUpdate({type:'analysisProgress',current:index+1,total,loc,round});
      const result=await searchMoves({moves:[...moves,{loc:moveLoc,color:toPlay}],toPlay:opponent,komi,visits,maxSearchTimeMs:perCandidateTime});
      // A CPU/WASM call can resolve synchronously. Return to the worker's event
      // loop between candidates so a stop or position change can be delivered.
      if (continuous) await new Promise(resolve => setTimeout(resolve, 0));
      if (shouldStop()) break;
      const previous=candidates.get(loc),sample=Math.max(1,result.visits),sampleWinrate=Math.max(0,Math.min(1,1-result.winrate));
      const candidate={loc,visits:(previous?.visits||0)+result.visits,winrate:previous?((previous.winrate*previous.visits+sampleWinrate*sample)/(previous.visits+sample)):sampleWinrate,pv:result.pv};
      candidates.set(loc,candidate);onUpdate({type:'analysisCandidate',candidate});
    }
    onUpdate({type:'analysisRound',round});
  }while(continuous&&!shouldStop());
  return {candidates:[...candidates.values()].sort((a,b)=>b.winrate-a.winrate),rounds:round,stopped:shouldStop()};
}
let requestQueue=Promise.resolve();
self.onmessage=({data})=>{
  if (data.type === 'stopAnalysis') {
    lastStoppedAnalysis = Math.max(lastStoppedAnalysis, data.throughRequestId);
    return;
  }
  const run=async()=>{
    try{
      let result;
      if(data.type==='load')result=await load(data,stage=>self.postMessage({requestId:data.requestId,type:'progress',stage}));
      else if(data.type==='analyze')result=await evaluateMoves(data.moves,data.toPlay,data.komi);
      else if(data.type==='analyzeCandidates')result=await analyzeCandidates(data, message => self.postMessage({requestId:data.requestId, ...message}), () => data.requestId <= lastStoppedAnalysis);
      else if(data.type==='search')result=await searchMoves(data);
      else throw new Error(`Unknown worker request: ${data.type}`);
      self.postMessage({requestId:data.requestId,type:data.type==='load'?'loaded':data.type,result});
    }catch(error){self.postMessage({requestId:data.requestId,type:'error',message:error.message||String(error)});}
  };
  requestQueue=requestQueue.then(run,run);
};
