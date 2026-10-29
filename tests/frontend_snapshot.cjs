// Regressions for static-host startup, blocked browser storage, and recovery.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync(__dirname+'/../frontend/app.js','utf8').replace(/init\(\);\s*$/,'');
const snapshot=JSON.parse(fs.readFileSync(__dirname+'/../dist/data/snapshot.json'));
function harness(blocked=false){
 const nodes={}; const node=s=>nodes[s]??=( {value:'',textContent:'',innerHTML:'',addEventListener(){},close(){this.closed=true},classList:{add(){},remove(){}}});
 const storage={getItem(){if(blocked)throw Error('Storage denied');return null},setItem(){if(blocked)throw Error('Storage denied')},removeItem(){if(blocked)throw Error('Storage denied')}};
 const calls=[];
 const ctx=vm.createContext({URL,console,setTimeout,clearTimeout,AbortSignal,AbortController,location:{hostname:'demo.example',href:'https://demo.example/'},localStorage:storage,sessionStorage:storage,document:{addEventListener(){},querySelector:node,getElementById(){return null}},window:{scrollTo(){}},navigator:{},fetch:async url=>{calls.push(url);return {ok:true,json:async()=>JSON.parse(JSON.stringify(snapshot))}}});
 vm.runInContext(source,ctx);vm.runInContext('render=()=>{globalThis.renders=(globalThis.renders||0)+1};toast=m=>globalThis.message=m;',ctx);
 return {ctx,nodes,node,calls};
}
(async()=>{
 for(const blocked of [false,true]){
  const h=harness(blocked);await vm.runInContext('init()',h.ctx);
  assert.equal(h.ctx.renders,1);assert.deepEqual(h.calls,['./data/snapshot.json']);
  h.node('#api-origin');h.node('#connection-error');await vm.runInContext('connect()',h.ctx);
  assert.equal(h.calls.length,1,'Blank hosted origin must never issue an API request');
  assert.match(h.nodes['#connection-error'].textContent,/saved demo/);
  vm.runInContext("data.filings=[];liveResearch={stale:true};state.tab='research';useSnapshot()",h.ctx);
  assert.equal(vm.runInContext('data.filings.length',h.ctx),snapshot.filings.length);
  assert.equal(vm.runInContext('liveResearch',h.ctx),null);
  assert.equal(vm.runInContext('state.tab',h.ctx),'feed');assert.ok(h.nodes['#drawer'].closed);
 }
 const h=harness();h.ctx.AbortSignal={};assert.ok(vm.runInContext('timeoutSignal(1)',h.ctx));
 console.log('Static startup, blocked storage, inline errors, snapshot reset and timeout fallback passed');
})().catch(e=>{console.error(e);process.exitCode=1});
