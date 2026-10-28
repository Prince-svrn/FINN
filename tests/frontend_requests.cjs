// Request behavior tests; no network or browser is needed.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const context = vm.createContext({
  URL, console, setTimeout, clearTimeout,
  location: {href:'http://localhost:8000/'},
  localStorage:{getItem:()=>null}, sessionStorage:{getItem:()=>null},
  document:{addEventListener(){},querySelector:()=>({addEventListener(){}})},
  AbortSignal:{timeout:ms=>({timeout:ms})},
});
let source=fs.readFileSync(path.join(__dirname,'../frontend/app.js'),'utf8');
vm.runInContext(source.replace(/init\(\);\s*$/,''),context);
vm.runInContext('render=()=>{}; toast=message=>globalThis.lastMessage=message;',context);
async function run(){
  let timeout;
  context.fetch=async(_,options)=>{timeout=options.signal.timeout;return {ok:true,json:async()=>({status:'ok'})}};
  await vm.runInContext("api('/api/company/PIDILITIND')",context);
  assert.ok(timeout>=60000,'Company discovery must allow both backend URL attempts');
  await vm.runInContext("api('/api/prices/PIDILITIND')",context);
  assert.ok(timeout>30000,'Price request must outlast the provider timeout');
  context.fetch=async()=>{const e=new Error();e.name='TimeoutError';throw e};
  await assert.rejects(vm.runInContext("api('/api/company/PIDILITIND')",context),/saved briefing/);
  vm.runInContext("busy=true; state.symbol='KPITTECH';",context);
  await vm.runInContext("searchSymbol('TCS')",context);
  assert.equal(vm.runInContext('state.symbol',context),'KPITTECH','A second request must not orphan the active request');
  assert.match(context.lastMessage,/already running/);
  vm.runInContext('backend=true;busy=false;',context);
  context.fetch=async()=>{throw Error('Network unavailable')};
  await vm.runInContext('refresh()',context);
  assert.equal(vm.runInContext('busy',context),false,'Failed refresh must restore controls');
  const errorMarkup=vm.runInContext("renderModelAnalysis({analysis_status:'error',analysis_reason:'Free quota reached. <unsafe>'})",context);
  assert.match(errorMarkup,/Free quota reached/);
  assert.ok(!errorMarkup.includes('<unsafe>'),'Provider explanations must be HTML escaped');
  console.log('6 frontend checks passed');
}
run().catch(error=>{console.error(error);process.exitCode=1});
