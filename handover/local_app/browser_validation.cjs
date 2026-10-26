// Regression checks for actionable server validation. Use only an isolated fixture server.
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium}=require(process.env.CC1_PLAYWRIGHT_ROOT||'D:/Code/agent code pilot BMAD/CC1_Enterprise_Agentic_SDLC_Kit_v0_3_0/node_modules/playwright');
(async()=>{
 const base=process.env.CC1_TEST_URL;if(!base||base.includes(':8765'))throw Error('Set CC1_TEST_URL to an isolated QA server.');
 const out=process.env.CC1_QA_OUT;if(!out)throw Error('Set a new CC1_QA_OUT evidence directory.');fs.mkdirSync(out,{recursive:true});
 const ids=JSON.parse(fs.readFileSync(path.join(out,'ids.json'))),browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 try{
 const page=await browser.newPage({viewport:{width:1440,height:1000},colorScheme:'light'}),errors=[];page.setDefaultTimeout(10000);page.setDefaultNavigationTimeout(10000);page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base);await page.waitForFunction(()=>typeof boot==='object'&&!!boot.token);
 await page.evaluate(async id=>{let p=(await api('/api/projects/'+id)).project;p.context.period='invalid';await api('/api/projects/'+id+'/stage/0',{revision:p.revision,data:p.context,confirm:false});},ids[0]);
 async function open(n){console.log('Checking step',n);await page.evaluate(id=>openProject(id),ids[n]);await page.waitForFunction(n=>step===n,n,{timeout:10000});}
 async function jump(field){const button=page.locator('.validation-question').filter({has:page.locator('code',{hasText:field})}).locator('button').first();await button.click();}
 const checked=[];
 for(const [n,field,selector] of [
  [0,'context.period','#context--1-period'],[1,'boq[0].quantity','#boq-0-quantity'],
  [2,'wbs[17].cam','#wbs-17-cam'],[3,'mapping.test-item.method','#assign-0-method'],
  [4,'resources[0].coefficient','#resources-0-coefficient'],[5,'prices[0].unit_price','#prices-0-unit_price'],
  [6,'adjustments.rules[0].basis','#rules-0-basis'],[7,'export.local_draft_ack','#export--1-local_draft_ack']]){
  await open(n);await jump(field);await page.locator(selector).waitFor();assert.equal(await page.locator(selector).getAttribute('aria-invalid'),'true',field);assert.equal(await page.locator(selector).evaluate(e=>e===document.activeElement),true,field+' focused');assert.ok(await page.locator(selector).getAttribute('aria-describedby'));checked.push(field);
  if(n===2){assert.match(await page.locator('.pagination').innerText(),/2\/2/);assert.equal(await page.locator('.validation-row-error').count(),1);await page.locator('#error-only').check();assert.equal(await page.locator('tbody tr').count(),1);assert.match(await page.locator('tbody').innerText(),/18/);}
  if(n===4){await jump('resources');assert.equal(await page.locator('#completeness').getAttribute('aria-invalid'),'true');}
  if(n===5){assert.equal(await page.locator('.validation-row-error').count(),2);}
 }
 // Cross-step field routing and dirty data: errors remain until actual server revalidation.
 await open(3);await jump('context.norm_mix_ref');assert.equal(await page.locator('#context--1-norm_mix_ref').getAttribute('aria-invalid'),'true');assert.equal(await page.evaluate(()=>step),0);
 await open(0);await page.locator('#context--1-period').fill('2026-10');await page.locator('#context--1-period').blur();assert.equal(await page.locator('#context--1-period').getAttribute('aria-invalid'),'true');await page.locator('.validation-pending').waitFor();await page.locator('#save').click();await page.waitForFunction(()=>!dirty&&!stages[0].questions.length&&!document.querySelector('#stage-content [aria-invalid=true]'));assert.equal(await page.locator('[aria-invalid=true]').count(),0);assert.equal(await page.locator('#stage-state').innerText(),'ĐỦ ĐẦU VÀO · CHỜ XÁC NHẬN');assert.equal(await page.evaluate(()=>project.confirmed.includes(0)),false);
 // Server gate remains active, even with error filtering/navigation in the client.
 await open(1);await page.locator('#confirm').click();await page.waitForFunction(()=>!dirty&&stages[1].questions.length>0);assert.equal(await page.evaluate(()=>step),1);await jump('boq[0].quantity');assert.equal(await page.locator('#boq-0-quantity').getAttribute('aria-invalid'),'true');
 await page.screenshot({path:path.join(out,'validation-light.png'),fullPage:true});await page.locator('#theme-toggle').click();await page.screenshot({path:path.join(out,'validation-dark.png'),fullPage:true});
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(out,'validation-mobile.png'),fullPage:true});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'mobile page must not overflow');
 // Hostile strings stay text, and lists longer than the previous 35-error cap remain actionable.
 await page.evaluate(()=>{stages[step].questions=Array.from({length:42},(_,i)=>({field:'boq[0].quantity',question:'<img src=x onerror=alert(1)> '+i}));renderQuestions();});assert.equal(await page.locator('.issue-jump').count(),42);assert.equal(await page.locator('#questions img').count(),0);
 assert.deepEqual(errors,[]);fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify({status:'PASS',checked,checks:['all eight steps','row 18 pagination','error-only filter','cross-step field','dirty pending','server revalidation','confirmation gate','duplicate price keys','light dark mobile','42 errors and HTML escaping'],pageErrors:errors},null,2));console.log('PASS: actionable validation across 8 steps, server gates, light/dark/mobile.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
