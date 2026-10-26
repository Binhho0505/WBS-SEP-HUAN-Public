// QA only (TEST ONLY projects on a copy of the runtime DB): BL63 — project A confirms AF.65110 for a line, project B with
// the identical line gets it from the 'Áp dụng lựa chọn QS đã nhớ' button; item facts stay empty; save persists.
const fs=require('fs'),path=require('path');
const {chromium}=require(process.env.CC1_PLAYWRIGHT_ROOT||'D:/Code/agent code pilot BMAD/CC1_Enterprise_Agentic_SDLC_Kit_v0_3_0/node_modules/playwright');
const T='TEST ONLY';
(async()=>{
 const out=process.env.CC1_QA_OUT||path.resolve(__dirname,'../runs_brian/norm_library_20261017/qa'),base=process.env.CC1_TEST_URL||'http://127.0.0.1:8767';fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});const page=await browser.newPage({viewport:{width:1440,height:1100}});let errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base);await page.waitForFunction(()=>typeof boot==='object'&&boot.token);
 const desc='TEST ONLY cốt thép bệ trụ BL63 '+Date.now();
 const ids=await page.evaluate(async({T,desc})=>{
  const mk=async name=>{let p=(await api('/api/projects',{name})).project;const ctx=Object.fromEntries(['project_code','legal_entity','contract_ref','baseline','owner','reviewer','legal_ref','rounding_ref'].map(k=>[k,T]));Object.assign(ctx,{location:'Hưng Yên - Vùng II',period:'2026-09',currency:'VND',cost_basis:'ESTIMATE',money_places:2,estimate_purpose:'STATE_NORM_CHECK',relation_profile:'ESTIMATE_MIN',rounding_level:'TOTAL'});
   const boq=[{id:'qa-steel',source_code:'1',description:desc,quantity:'10',uom:'tấn',kind:'MEASURED',source_ref:T,source_hash:'a'.repeat(64)}];
   for(const [i,data] of [[0,ctx],[1,boq]]){const d=await api('/api/projects/'+p.id+'/stage/'+i,{revision:p.revision,data,confirm:true});if(!d.confirmed)throw Error(JSON.stringify(d.questions));p=d.project;}
   const wr=master.find(r=>r.code.startsWith('H')&&r.status!=='HOLD').code;const d=await api('/api/projects/'+p.id+'/stage/2',{revision:p.revision,data:p.mapping.map(m=>({...m,wbs_id:'WP-001',mapping_ref:T})),wbs:[{id:'WP-001',work_result_code:wr,lbs:T,scope:T,acceptance:T,ca:T,cam:T}],confirm:true});if(!d.confirmed)throw Error(JSON.stringify(d.questions));return d.project;};
  let a=await mk('QA TEST ONLY · BL63 hồ sơ A');const x=await api('/api/projects/'+a.id+'/code-norm',{id:'TT38-2026:AF.65110'});
  const d=await api('/api/projects/'+a.id+'/stage/3',{revision:a.revision,data:[{...x.norm,selection_ref:'TEST ONLY QS A đã kiểm',table_verified:true}],confirm:true,applications:[{id:'qa-a',item_id:a.mapping[0].id,norm_id:x.norm.id,qty_factor:'1'}],resources:x.resources,assignments:a.mapping.map(m=>({id:m.id,technical_spec:'TEST Ø≤10',method:'TEST cần cẩu',norm_match_ref:T}))});
  if(!d.confirmed)throw Error('A not confirmed '+JSON.stringify(d.questions));
  const b=await mk('QA TEST ONLY · BL63 hồ sơ B');return {a:a.id,b:b.id};},{T,desc});
 await page.evaluate(id=>openProject(id),ids.b);await page.waitForFunction(()=>document.querySelector('#stage-title').textContent==='Chọn định mức');
 await page.locator('[data-sub="applications"]').click();await page.locator('#apply-memory').click();
 await page.waitForFunction(()=>document.querySelector('#message').textContent.includes('Đã áp dụng lựa chọn QS đã nhớ'));
 const msg=await page.locator('#message').textContent();await page.screenshot({path:path.join(out,'14_apply_memory.png'),fullPage:true});
 const local=await page.evaluate(()=>({apps:project.applications.map(a=>a.norm_id),sel:(project.norms[0]||{}).selection_ref,res:project.resources.length,spec:project.mapping[0].technical_spec||''}));
 if(local.apps.join()!=='TT38-2026:AF.65110'||!String(local.sel).includes('hồ sơ «QA TEST ONLY · BL63 hồ sơ A»')||local.res<3||local.spec)throw Error('apply-memory unexpected '+JSON.stringify(local));
 const saved=await page.evaluate(async()=>{await save(false);const p=(await api('/api/projects/'+project.id)).project;return {apps:p.applications.length,res:p.resources.length,confirmed:p.confirmed}});
 if(saved.apps!==1||saved.res!==local.res||saved.confirmed.includes(3))throw Error('save unexpected '+JSON.stringify(saved));
 fs.writeFileSync(path.join(out,'browser-memory.json'),JSON.stringify({status:errors.length?'FAIL':'PASS',message:msg,local,saved,errors},null,2));await browser.close();if(errors.length)throw Error(errors.join('\n'));
 console.log('QS memory browser PASS;',msg.slice(0,90),JSON.stringify(saved));
})().catch(e=>{console.error(e);process.exit(1);});
