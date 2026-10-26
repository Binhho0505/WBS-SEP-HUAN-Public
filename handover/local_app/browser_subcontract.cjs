// D59 browser checks for E10–E16 (gói thầu → báo giá → đề xuất → hoàn thành → bản vẽ → xuất; từ điển). Isolated QA server only.
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium}=require(process.env.CC1_PLAYWRIGHT_ROOT||'D:/Code/agent code pilot BMAD/CC1_Enterprise_Agentic_SDLC_Kit_v0_3_0/node_modules/playwright');
(async()=>{
 const base=process.env.CC1_TEST_URL;if(!base||base.includes(':8765'))throw Error('Set CC1_TEST_URL to an isolated QA server.');
 const out=process.env.CC1_QA_OUT;if(!out)throw Error('Set CC1_QA_OUT (seed_qa.py output).');
 const [id]=JSON.parse(fs.readFileSync(path.join(out,'ids.json'))),browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const errors=[],steps=[];
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000},colorScheme:'light'});page.setDefaultTimeout(15000);
  page.on('pageerror',e=>errors.push('pageerror '+e.message));page.on('console',m=>{if(m.type()==='error')errors.push('console '+m.text());});
  const msg=async re=>{await page.waitForFunction(r=>new RegExp(r).test(document.querySelector('#sv-msg')?.textContent||''),re.source);};
  await page.goto(base);await page.waitForFunction(()=>typeof boot==='object'&&!!boot.token);
  await page.evaluate(id=>openProject(id),id);await page.waitForFunction(()=>!!project);
  await page.click('#open-subcontract');await page.locator('#subcontract-view').waitFor();steps.push('open view');
  await page.selectOption('#sv-model','VN_ND175');await msg(/Đã lưu gói thầu/);
  await page.fill('#np-code','GT-01');await page.fill('#np-name','TEST cọc và bê tông');await page.click('#np-add');await page.click('#pk-save');await msg(/Đã lưu gói thầu/);
  await page.selectOption('[data-f="procurement_method"]','CHI_DINH_THAU');await page.selectOption('[data-d="mode"]','GOP');await page.selectOption('[data-d="price_form"]','DON_GIA_CO_DINH');
  await page.fill('[data-d="fee_pct"]','5');await page.fill('[data-d="fee_ref"]','TEST phí');await page.fill('[data-p="k_all"]','0.9');await page.locator('[data-p="k_all"]').blur();
  await page.click('#pk-save');await msg(/Đã lưu gói thầu/);
  await page.selectOption('#al-by','WBS');await page.fill('#al-q','1');await page.fill('#al-pct','100');await page.click('#al-add');await msg(/Đã thêm 2 dòng/);
  assert.match(await page.locator('#sv-body').innerText(),/GT-01\.1[\s\S]*1\.1/);steps.push('GT-01 lines keep WBS 1.1');
  await page.click('#np-self');await page.click('#pk-save');await msg(/Đã lưu gói thầu/);
  await page.locator('tr[data-pkg]').filter({hasText:'CC1'}).click();await page.selectOption('#al-by','IDS');await page.locator('[data-pick="ab3"]').check();await page.check('#al-rem');await page.click('#al-add');await msg(/Đã thêm 1 dòng/);
  await page.click('[data-svtab="coverage"]');assert.match(await page.locator('.metric-row').innerText(),/phủ đủ 100%\s*3/i);assert.match(await page.locator('#subcontract-view .badge').innerText(),/Đủ điều kiện/);steps.push('coverage 3/3, gate clear');
  await page.click('[data-svtab="quotes"]');const pid=await page.evaluate(()=>project.packages.find(p=>p.code==='GT-01').id);
  const bb=await page.request.get(`${base}/api/projects/${id}/bb/GT-01.xlsx`);assert.equal(bb.status(),200);
  await page.fill(`[data-qv="${pid}"]`,'TEST NTP A');await page.setInputFiles(`[data-qf="${pid}"]`,path.join(out,'quote.csv'));await page.click(`[data-qup="${pid}"]`);await msg(/thẩm định báo giá/);
  assert.match(await page.locator('#sv-body').innerText(),/TEST NTP A[\s\S]*Hợp lệ/);steps.push('quote reviewed valid');
  await page.click('[data-svtab="award"]');assert.match(await page.locator('#sv-body').innerText(),/88/);
  const qid=await page.evaluate(()=>project.quotes[0].id);await page.selectOption(`[data-aq="${pid}"]`,qid);await page.fill(`[data-ar="${pid}"]`,'TEST thấp nhất hợp lệ');await page.fill(`[data-aby="${pid}"]`,'TEST QS');
  await page.click(`[data-asave="${pid}"]`);await msg(/nháp/);assert.match(await page.locator('#sv-body').innerText(),/ĐỀ XUẤT NHÁP/);steps.push('award draft');
  await page.click('[data-svtab="progress"]');await page.selectOption('#pg-bb','GT-01.2');await page.fill('#pg-qty','10');await page.fill('#pg-ref','TEST biên bản');await page.click('#pg-add');await msg(/hoàn thành/);
  assert.match(await page.locator('#pg-wbs').innerText(),/1\.2[\s\S]*Xong/);steps.push('WBS 1.2 done for owner');
  await page.click('[data-svtab="drawings"]');await page.setInputFiles('#dw-file',path.join(out,'mong.dxf'));await page.click('#dw-up');await msg(/bóc ứng viên/);
  const tid=await page.evaluate(()=>project.takeoffs.find(t=>t.kind==='DXF_TEXT').id);await page.selectOption(`[data-tab="${tid}"]`,'ab3');await page.fill(`[data-tref="${tid}"]`,'TEST cùng đơn vị');await page.click(`[data-tok="${tid}"]`);await msg(/Đã gán/);
  assert.match(await page.locator('#sv-body').innerText(),/Đối chiếu bản vẽ/);steps.push('drawing candidate assigned');
  await page.click('[data-svtab="export"]');for(const u of [`/api/projects/${id}/procurement-pack.zip`,`/api/projects/${id}/tender-pack.zip`,`/api/dictionaries.xlsx?project=${id}`]){const r=await page.request.get(base+u);assert.equal(r.status(),200,u);}
  assert.match(await page.locator('#sv-body').innerText(),/GT-01[\s\S]*Đủ/);steps.push('packs downloadable');
  await page.screenshot({path:path.join(out,'subcontract-light.png')});
  await page.click('#theme-toggle');await page.click('[data-svtab="award"]');await page.screenshot({path:path.join(out,'subcontract-dark.png')});
  await page.click('#open-dictionaries');await page.locator('#dc-check').waitFor();assert.match(await page.locator('#dialog').innerText(),/Tải từ điển mã/);await page.screenshot({path:path.join(out,'dictionaries.png')});
  await page.click('#dialog-close');await page.click('#sv-back');await page.locator('#workspace').waitFor();steps.push('back to 8 steps');
  const m=await browser.newPage({viewport:{width:390,height:844},colorScheme:'light'});m.on('pageerror',e=>errors.push('mobile '+e.message));m.on('console',x=>{if(x.type()==='error')errors.push('mobile console '+x.text());});
  await m.goto(base);await m.waitForFunction(()=>typeof boot==='object'&&!!boot.token);await m.evaluate(id=>openProject(id),id);await m.waitForFunction(()=>!!project);
  await m.evaluate(()=>document.querySelector('#open-subcontract').click());await m.locator('#subcontract-view').waitFor();
  for(const t of ['packages','award','pakd','progress']){await m.click(`[data-svtab="${t}"]`);const w=await m.evaluate(()=>[document.scrollingElement.scrollWidth,innerWidth]);assert.ok(w[0]<=w[1]+1,'no horizontal page scroll on '+t+': '+w);}
  await m.screenshot({path:path.join(out,'subcontract-mobile.png')});steps.push('mobile 390 no horizontal scroll');
  assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(out,'browser-subcontract.json'),JSON.stringify({status:'PASS',steps,errors},null,1));console.log('PASS',steps.join(' · '));
 }catch(e){fs.writeFileSync(path.join(out,'browser-subcontract.json'),JSON.stringify({status:'FAIL',steps,errors,error:String(e.stack||e)},null,1));console.error('FAIL after',steps.join(' · '),'\n',e,errors);process.exitCode=1;}
 finally{await browser.close();}
})();
