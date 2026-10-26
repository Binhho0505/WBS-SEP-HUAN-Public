// QA only (TEST ONLY project on a copy of the runtime DB): BOQ heading path -> "Gợi ý mã TT38" dialog -> pick one
// column -> norm + resource lines pulled from the library -> save (step 3 not confirmed: selection_ref still required).
const fs=require('fs'),path=require('path');
const {chromium}=require(process.env.CC1_PLAYWRIGHT_ROOT||'D:/Code/agent code pilot BMAD/CC1_Enterprise_Agentic_SDLC_Kit_v0_3_0/node_modules/playwright');
const T='TEST ONLY';
(async()=>{
 const out=process.env.CC1_QA_OUT||path.resolve(__dirname,'../runs_brian/norm_library_20261017/qa'),base=process.env.CC1_TEST_URL||'http://127.0.0.1:8767';fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});const page=await browser.newPage({viewport:{width:1440,height:1100}});let errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base);await page.waitForFunction(()=>typeof boot==='object'&&boot.token);
 const pid=await page.evaluate(async T=>{let p=(await api('/api/projects',{name:'QA TEST ONLY · gợi ý mã TT38'})).project;const ctx=Object.fromEntries(['project_code','legal_entity','contract_ref','baseline','owner','reviewer','legal_ref','rounding_ref'].map(k=>[k,T]));Object.assign(ctx,{location:'Hưng Yên - Vùng II',period:'2026-09',currency:'VND',cost_basis:'ESTIMATE',money_places:2,estimate_purpose:'STATE_NORM_CHECK',relation_profile:'ESTIMATE_MIN',rounding_level:'TOTAL'});
  const boq=[{id:'qa-h1',source_code:'1',description:'TEST ONLY Kết cấu phần dưới',kind:'HEADING',source_ref:T,source_hash:'a'.repeat(64)},{id:'qa-h2',source_code:'1.1',description:'Trụ cầu trên cạn',kind:'HEADING',source_ref:T,source_hash:'a'.repeat(64)},
   {id:'qa-steel',source_code:'1.1.1',description:'Cốt thép bệ trụ',quantity:'156.1',uom:'tấn',kind:'MEASURED',source_ref:T,source_hash:'a'.repeat(64)},{id:'qa-cap',source_code:'1.1.2',description:'Bê tông xà mũ',quantity:'80',uom:'m3',kind:'MEASURED',source_ref:T,source_hash:'a'.repeat(64)},{id:'qa-wp',source_code:'1.1.3',description:'Lớp phòng nước mặt cầu',quantity:'500',uom:'m2',kind:'MEASURED',source_ref:T,source_hash:'a'.repeat(64)}];
  for(const [i,data] of [[0,ctx],[1,boq]]){const d=await api('/api/projects/'+p.id+'/stage/'+i,{revision:p.revision,data,confirm:true});if(!d.confirmed)throw Error(JSON.stringify(d.questions));p=d.project;}
  const wr=master.find(r=>r.code.startsWith('H')&&r.status!=='HOLD').code,items=p.mapping.map(m=>({...m,wbs_id:'WP-001',mapping_ref:T}));
  const d=await api('/api/projects/'+p.id+'/stage/2',{revision:p.revision,data:items,wbs:[{id:'WP-001',work_result_code:wr,lbs:T,scope:T,acceptance:T,ca:T,cam:T}],confirm:true});if(!d.confirmed)throw Error(JSON.stringify(d.questions));return p.id;},T);
 await page.evaluate(id=>openProject(id),pid);await page.waitForFunction(()=>document.querySelector('#stage-title').textContent==='Chọn định mức');
 await page.locator('[data-sub="applications"]').click();const t0=Date.now();await page.locator('#suggest-norms').click();await page.locator('[data-pick]').first().waitFor({timeout:120000});const ms=Date.now()-t0;
 const shown=await page.evaluate(()=>[...document.querySelectorAll("#dialog-content .editor")].map(e=>({item:e.querySelector('b').textContent,path:e.querySelector('small').textContent,top:[...e.querySelectorAll('.question > b')].map(b=>b.textContent)})));
 await page.screenshot({path:path.join(out,'13_suggest_norms.png'),fullPage:true});
 const steel=shown.find(s=>s.item.includes('Cốt thép bệ trụ'));if(!steel||!steel.path.includes('Trụ cầu trên cạn')||!steel.top.slice(0,2).some(c=>c.startsWith('AF.651')))throw Error('steel suggestion unexpected '+JSON.stringify(shown));
 await page.locator('#sg-method').selectOption('BOM');await page.waitForFunction(()=>{const e=[...document.querySelectorAll('#dialog-content .editor')].find(x=>x.textContent.includes('Bê tông xà mũ'));return e&&e.querySelector('.question > b')&&e.querySelector('.question > b').textContent.startsWith('AF.33')},null,{timeout:60000});
 const capTop=await page.evaluate(()=>[...document.querySelectorAll('#dialog-content .editor')].find(x=>x.textContent.includes('Bê tông xà mũ')).querySelector('.question > b').textContent);
 const badge=await page.evaluate(()=>{const e=[...document.querySelectorAll('#dialog-content .editor')].find(x=>x.textContent.includes('Lớp phòng nước mặt cầu'));return e?e.textContent:''});
 const hasDict=await page.evaluate(async()=>(await api('/api/library')).datasets.some(d=>d.status==='ACTIVE'&&d.name.startsWith('Từ điển BOQ→TT38')));
 if(hasDict&&!badge.includes('Từ điển NT01 · NO_TT38'))throw Error('dictionary badge missing: '+badge.slice(0,200));
 const btn=page.locator('[data-pick*="AF.651"]').first();const nid=(await btn.getAttribute('data-pick')).split('|')[1];await btn.click();
 await page.waitForFunction(()=>document.querySelector('#message').textContent.includes('Đã ghép'));
 if(!(await btn.isDisabled()))throw Error('picked button must be disabled');
 const local=await page.evaluate(nid=>({apps:project.applications.filter(a=>a.norm_id===nid).length,norm:!!project.norms.find(n=>n.id===nid),res:project.resources.filter(r=>r.norm_id===nid).length}),nid);
 if(local.apps!==1||!local.norm||local.res<3)throw Error('pick did not compose '+JSON.stringify(local));
 const saved=await page.evaluate(async()=>{await save(false);const p=(await api('/api/projects/'+project.id)).project;return {apps:p.applications.length,norms:p.norms.length,res:p.resources.length,confirmed:p.confirmed}});
 if(saved.apps!==1||saved.res!==local.res||saved.confirmed.includes(3))throw Error('save/gate unexpected '+JSON.stringify(saved));
 fs.writeFileSync(path.join(out,'browser-suggest.json'),JSON.stringify({status:errors.length?'FAIL':'PASS',dialog_ms:ms,cap_top_with_BOM:capTop,dictionary_badge:hasDict?'NT01 · NO_TT38 shown':'no dictionary loaded',shown,picked:nid,local,saved,errors},null,2));await browser.close();if(errors.length)throw Error(errors.join('\n'));
 console.log('Suggest browser PASS in',ms,'ms; BOM xà mũ top',capTop,'; picked',nid,JSON.stringify(saved),JSON.stringify(shown.map(s=>[s.item,s.top.slice(0,3)])));
})().catch(e=>{console.error(e);process.exit(1);});
