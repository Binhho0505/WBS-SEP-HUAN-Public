// QA only: library price search + machine crosswalk hints + assignment on the E2E copy DB (TEST ONLY project).
const fs=require('fs'),path=require('path');
const {chromium}=require(process.env.CC1_PLAYWRIGHT_ROOT||'D:/Code/agent code pilot BMAD/CC1_Enterprise_Agentic_SDLC_Kit_v0_3_0/node_modules/playwright');
(async()=>{
 const out=process.env.CC1_QA_OUT||path.resolve(__dirname,'../runs_brian/state_market_prices_20261017/qa/browser'),base=process.env.CC1_TEST_URL||'http://127.0.0.1:8767';fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});const page=await browser.newPage({viewport:{width:1440,height:1100}});let errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base);await page.waitForFunction(()=>typeof boot==='object'&&boot.projects.length>0);
 const pid=await page.evaluate(()=>boot.projects.find(p=>p.name.includes('AF.65120')).id);await page.evaluate(id=>openProject(id),pid);
 await page.waitForFunction(()=>project&&project.name.includes('AF.65120'));await page.locator('[data-step="5"]').click();await page.locator('#price-search').click();
 const idx=await page.evaluate(()=>neededKeys().sort((a,b)=>a.priced-b.priced).findIndex(k=>k.name==='Cần cẩu 16 t'));await page.locator('#ps-key').selectOption(String(idx));
 await page.locator('[data-hint]').first().waitFor();const hints=await page.locator('[data-hint]').allTextContents();
 await page.locator('[data-hint="M102.0202"]').click();await page.locator('[data-assign]').first().waitFor();
 await page.screenshot({path:path.join(out,'10_price_search_crosswalk.png'),fullPage:true});
 const first=await page.locator('#ps-results .question').first().textContent();
 await page.locator('[data-assign]').first().click();await page.waitForFunction(()=>document.querySelector('#message').textContent.includes('Đã gán giá'));
 // D73 fix: since the code library maps resources to CC1 master codes (D30), the crane key is no longer 'CAN_CAU_16_T';
 // find the price row of the key that was selected (same resource_code/spec/uom/location) instead of a hard-coded name.
 const want=await page.evaluate(()=>{const k=neededKeys().find(k=>k.name==='Cần cẩu 16 t');return k&&[k.code,k.spec,k.uom,k.zone];});
 const assigned=await page.evaluate(w=>project.prices.find(p=>w&&p.resource_code===w[0]&&p.spec===w[1]&&p.uom===w[2]&&p.location===w[3]),want);
 if(!assigned||!assigned.mapped_from||assigned.price_ref!=='')throw Error('assignment lineage missing '+JSON.stringify(assigned));
 fs.writeFileSync(path.join(out,'browser-price-search.json'),JSON.stringify({status:errors.length?'FAIL':'PASS',hints,first_result:first.slice(0,200),assigned:{unit_price:assigned.unit_price,period:assigned.period,location:assigned.location,mapped_from:assigned.mapped_from},errors},null,2));
 await browser.close();if(errors.length)throw Error(errors.join('\n'));console.log('Price search PASS; hints',hints.length,'; assigned',assigned.unit_price,'from',assigned.mapped_from.name);
})().catch(e=>{console.error(e);process.exit(1);});
