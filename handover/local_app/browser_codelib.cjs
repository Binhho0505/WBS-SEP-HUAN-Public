// QA only (TEST ONLY project on a copy of the runtime DB): code library dialog -> add AF.65120 -> compose -> save
// (resources must persist) -> resource step -> automatic prices by CC1 master code.
const fs=require('fs'),path=require('path');
const {chromium}=require(process.env.CC1_PLAYWRIGHT_ROOT||'D:/Code/agent code pilot BMAD/CC1_Enterprise_Agentic_SDLC_Kit_v0_3_0/node_modules/playwright');
const T='TEST ONLY';
(async()=>{
 const out=process.env.CC1_QA_OUT||path.resolve(__dirname,'../runs_brian/norm_library_20261017/qa'),base=process.env.CC1_TEST_URL||'http://127.0.0.1:8767';fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});const page=await browser.newPage({viewport:{width:1440,height:1100}});let errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base);await page.waitForFunction(()=>typeof boot==='object'&&boot.token);
 const pid=await page.evaluate(async T=>{let p=(await api('/api/projects',{name:'QA TEST ONLY · thư viện mã AF.65120'})).project;const ctx=Object.fromEntries(['project_code','legal_entity','contract_ref','baseline','owner','reviewer','legal_ref','rounding_ref'].map(k=>[k,T]));Object.assign(ctx,{location:'Hưng Yên - Vùng II',period:'2026-09',currency:'VND',cost_basis:'ESTIMATE',money_places:2,estimate_purpose:'STATE_NORM_CHECK',relation_profile:'ESTIMATE_MIN',rounding_level:'TOTAL'});
  const boq=[{id:'qa-steel',source_code:'TEST',description:'TEST ONLY cốt thép bệ trụ',quantity:'156.1',uom:'tấn',kind:'MEASURED',source_ref:T,source_hash:'a'.repeat(64)}];
  for(const [i,data] of [[0,ctx],[1,boq]]){const d=await api('/api/projects/'+p.id+'/stage/'+i,{revision:p.revision,data,confirm:true});if(!d.confirmed)throw Error(JSON.stringify(d.questions));p=d.project;}
  const wr=master.find(r=>r.code.startsWith('H')&&r.status!=='HOLD').code,item={...p.mapping[0],wbs_id:'WP-001',mapping_ref:T};
  const d=await api('/api/projects/'+p.id+'/stage/2',{revision:p.revision,data:[item],wbs:[{id:'WP-001',work_result_code:wr,lbs:T,scope:T,acceptance:T,ca:T,cam:T}],confirm:true});if(!d.confirmed)throw Error(JSON.stringify(d.questions));return p.id;},T);
 await page.evaluate(id=>openProject(id),pid);await page.waitForFunction(()=>document.querySelector('#stage-title').textContent==='Chọn định mức');
 await page.locator('#open-codelib').click();await page.locator('#cl-q').fill('AF.65120');await page.locator('#cl-go').click();
 await page.locator('[data-norm="TT38-2026:AF.65120"]').click();await page.locator('#cl-add').waitFor();await page.screenshot({path:path.join(out,'11_code_library_detail.png'),fullPage:true});
 await page.locator('#cl-add').click();await page.waitForFunction(()=>project.norms.length===1&&project.resources.length===7);
 await page.evaluate(()=>{const n=project.norms[0];Object.assign(n,{selection_ref:'TEST ONLY QS check simulated',table_verified:true});project.mapping.forEach(m=>Object.assign(m,{technical_spec:'TEST Ø≤18',method:'TEST cần cẩu',norm_match_ref:'TEST'}));project.applications=[{id:'qa-app',item_id:project.mapping[0].id,norm_id:n.id,qty_factor:'1'}];dirty=true;});
 await page.locator('#confirm').click();await page.waitForFunction(()=>document.querySelector('#stage-title').textContent==='Phân tích hao phí');
 const persisted=await page.evaluate(async()=>(await api('/api/projects/'+project.id)).project.resources.map(r=>r.resource_code));
 if(persisted.length!==7||!persisted.includes('NC.N2')||!persisted.includes('M112.4003'))throw Error('resources not persisted with master codes: '+persisted);
 await page.evaluate(()=>{const spec={'Thép tròn':'TEST thép CB300 Ø14+','Dây thép':'TEST dây buộc 1 ly','Que hàn':'TEST que hàn','Máy hàn 23 kW':'M112.4003','Máy cắt uốn 5 kW':'M112.2601','Cần cẩu 16 t':'TEST cần cẩu'};project.resources.forEach(r=>{if(!r.spec)r.spec=spec[r.name]||'TEST';});project.resource_completeness_ref='TEST ONLY';dirty=true;});
 await page.locator('#confirm').click();await page.waitForFunction(()=>document.querySelector('#stage-title').textContent==='Đơn giá CC1');
 await page.locator('#auto-prices').click();await page.waitForFunction(()=>document.querySelector('#message').textContent.includes('Đã đề xuất'));
 const auto=await page.evaluate(()=>project.prices.map(p=>[p.resource_code,p.unit_price,p.period,p.mapped_from&&p.mapped_from.match]));
 await page.screenshot({path:path.join(out,'12_auto_prices.png'),fullPage:true});
 const want={'NC.N2':'298012','M112.4003':'474409','M112.2601':'322903'};
 for(const [c,v] of Object.entries(want)){const hit=auto.find(a=>a[0]===c);if(!hit||hit[1]!==v)throw Error('auto price '+c+' expected '+v+' got '+JSON.stringify(hit));}
 fs.writeFileSync(path.join(out,'browser-codelib.json'),JSON.stringify({status:errors.length?'FAIL':'PASS',persisted_resource_codes:persisted,auto_prices:auto,errors},null,2));await browser.close();if(errors.length)throw Error(errors.join('\n'));
 console.log('Code library browser PASS; resources persisted',persisted.length,'; auto prices',auto.length,JSON.stringify(auto));
})().catch(e=>{console.error(e);process.exit(1);});
