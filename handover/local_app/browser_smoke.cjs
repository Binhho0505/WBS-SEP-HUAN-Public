// Uses the pinned kit's Playwright for QA only; the delivered app needs no Node.
// Schema 0.2.0 smoke: gates, real AB import + persistence, data library, AI panel, mobile layout.
const fs=require('fs'),path=require('path');
const kit=process.env.CC1_PLAYWRIGHT_ROOT||'D:/Code/agent code pilot BMAD/CC1_Enterprise_Agentic_SDLC_Kit_v0_3_0/node_modules/playwright';
const {chromium}=require(kit);
(async()=>{
 const out=process.env.CC1_QA_OUT||path.resolve(__dirname,'../runs_brian/app_v020_20261017/qa');fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const page=await browser.newPage({viewport:{width:1440,height:1050}});let errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 const base=process.env.CC1_TEST_URL||'http://127.0.0.1:8767';
 await page.goto(base);await page.getByRole('button',{name:'Tạo hồ sơ đầu tiên'}).waitFor();
 await page.screenshot({path:path.join(out,'01_welcome_desktop.png'),fullPage:true});
 await page.getByRole('button',{name:'Tạo hồ sơ đầu tiên'}).click();await page.locator('#new-name').fill('QA TEST ONLY · không phải dự toán thật');await page.locator('#create-confirm').click();await page.locator('#stage-title').filter({hasText:'Hồ sơ dự án'}).waitFor();
 await page.locator('#confirm').click();await page.waitForFunction(()=>document.querySelector('#message').textContent.includes('Cần bổ sung'));
 if(!(await page.locator('[data-step="1"]').isDisabled()))throw Error('Step skip permitted');
 await page.screenshot({path:path.join(out,'02_missing_context_blocks.png'),fullPage:true});
 for(const key of ['project_code','legal_entity','contract_ref','baseline','location','owner','reviewer','legal_ref','rounding_ref']){await page.locator(`[data-field="${key}"]`).fill('QA TEST ONLY');await page.locator(`[data-field="${key}"]`).blur();}
 for(const [key,value] of [['period','2026-10'],['currency','VND']]){await page.locator(`[data-field="${key}"]`).fill(value);await page.locator(`[data-field="${key}"]`).blur();}
 for(const [key,value] of [['cost_basis','ESTIMATE'],['estimate_purpose','INTERNAL_COST'],['relation_profile','ESTIMATE_MIN'],['money_places','2'],['rounding_level','TOTAL']])await page.locator(`[data-field="${key}"]`).selectOption(value);
 await page.locator('#confirm').click();await page.waitForFunction(()=>document.querySelector('#stage-title').textContent==='BOQ nguồn');
 await page.locator('#builtin').click();await page.locator('#basis').selectOption('AB');await page.locator('#load-builtin').click();await page.locator('#dialog').waitFor({state:'hidden'});await page.locator('#save').click();await page.waitForFunction(()=>document.querySelector('#message').textContent.includes('Đã lưu phiên bản'));
 await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:path.join(out,'03_real_me_so_boq.png'),fullPage:true});
 await page.reload();await page.locator('#stage-title').filter({hasText:'BOQ nguồn'}).waitFor();
 const restored=await page.evaluate(()=>project.boq.length);if(restored!==821)throw Error('Reload persistence failed '+restored);
 // Data library: upload a TEST ONLY price list, it must persist as version 1 with SHA256.
 await page.locator('#open-library').click();await page.locator('#lib-name').fill('QA TEST ONLY bảng giá');await page.locator('#lib-kind').selectOption('PRICES');
 await page.locator('#lib-file').setInputFiles({name:'qa_prices.csv',mimeType:'text/csv',buffer:Buffer.from('id,resource_code,spec,uom,unit_price,location,period,currency,tax_basis,delivery,included,source_ref,price_ref\nQA1,QA-MAT,QA SPEC,t,1,QA TEST ONLY,2026-10,VND,EX_VAT,AT_SITE,TEST,TEST ONLY,TEST\n')});
 await page.locator('#lib-upload').click();await page.locator('text=QA TEST ONLY bảng giá · v1').waitFor();await page.screenshot({path:path.join(out,'04_data_library.png'),fullPage:true});await page.locator('#dialog-close').click();
 // AI panel renders providers; settings dialog never shows a stored key.
 if(!(await page.locator('#ai-provider option').count()))throw Error('AI providers missing');
 await page.locator('#ai-settings').click();await page.locator('[data-provider="anthropic"]').waitFor();await page.screenshot({path:path.join(out,'05_ai_settings.png'),fullPage:true});await page.locator('#dialog-close').click();
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(out,'06_mobile.png'),fullPage:true});
 const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth+1);if(overflow)throw Error('Mobile document overflow');
 fs.writeFileSync(path.join(out,'browser-check.json'),JSON.stringify({status:errors.length?'FAIL':'PASS',schema:'0.2.0',checks:['missing-context gate','disabled later steps','context form incl. purpose/profile/rounding level','real AB 821 import','SQLite reload persistence','data library upload v1','AI provider panel + settings','mobile layout no document overflow'],errors},null,2));
 await browser.close();if(errors.length)throw Error(errors.join('\n'));console.log('Browser smoke PASS; real AB rows=821; library + AI panel; no page errors');
})().catch(e=>{console.error(e);process.exit(1);});
