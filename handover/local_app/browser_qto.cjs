// E21 (D85) one UI for 8765 + CERP-QTO, on ISOLATED servers only (8765 QA with seed_qto_qa.py; CERP-QTO QA instance tests/qa_server.py):
// settings (token stored server-side) → link project → CERP-QTO embedded (profile, golden DXF upload, units gate, run rules, approve,
// aggregate) → import take-off into the estimate → QS assigns to the consultant's BOQ line → deviation flagged → flows overview → history.
// Env: CC1_TEST_URL (8765 QA), CC1_QA_OUT (ids.json), CC1_QTO_TEST_URL, CC1_QTO_TEST_TOKEN, CERP_QTO_GOLDEN.
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium}=require(process.env.CC1_PLAYWRIGHT_ROOT||'D:/Code/agent code pilot BMAD/CC1_Enterprise_Agentic_SDLC_Kit_v0_3_0/node_modules/playwright');
(async()=>{
 const base=process.env.CC1_TEST_URL,out=process.env.CC1_QA_OUT,qurl=process.env.CC1_QTO_TEST_URL,qtok=process.env.CC1_QTO_TEST_TOKEN,golden=process.env.CERP_QTO_GOLDEN;
 if(!base||base.includes(':8765')||!qurl||qurl.includes(':8770'))throw Error('Isolated QA servers only (never :8765 / :8770).');assert.ok(qtok&&golden&&out);
 const [id]=JSON.parse(fs.readFileSync(path.join(out,'ids.json'))),browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const errors=[],steps=[],project='E2E-'+Date.now(),profile=fs.readFileSync(path.join(path.dirname(golden),'../../profiles/cc1-kc-default.toml'),'utf8');
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000},colorScheme:'light'});page.setDefaultTimeout(30000);
  page.on('pageerror',e=>errors.push('pageerror '+e.message));page.on('console',m=>{if(m.type()==='error')errors.push('console '+m.text());});
  const qmsg=re=>page.waitForFunction(r=>new RegExp(r).test(document.querySelector('#qto-msg')?.textContent||''),re.source).catch(async()=>{throw Error(`waiting ${re}: #qto-msg="${await page.locator('#qto-msg').textContent().catch(()=>'?')}"`);});
  await page.goto(base);await page.waitForFunction(()=>typeof boot==='object'&&!!boot.token);await page.evaluate(id=>openProject(id),id);await page.waitForFunction(()=>!!project);
  // 1 · settings: service + token stored on the 8765 side; the page never sees the token again
  await page.click('#open-qto');await page.locator('#qto-view').waitFor();assert.match(await page.locator('#qto-view .badge').innerText(),/Service chưa chạy|Chưa có token/);
  await page.click('#qp-settings');await page.fill('#qs-url',qurl);await page.fill('#qs-tok',qtok);await page.click('#qs-ok');await qmsg(/Đã nối CERP-QTO: e2e/);
  assert.match(await page.locator('#qto-view .badge').innerText(),/Đã nối · e2e/);
  const st=await page.evaluate(()=>api('/api/qto/status'));assert.equal(st.token_set,true);assert.ok(!JSON.stringify(st).includes('tok-e2e'));steps.push('Cài đặt: token lưu phía 8765, trạng thái nối e2e');
  // 2 · link the CERP-QTO project to this estimate → embedded CERP-QTO appears (no token / project typing inside)
  await page.fill('#qp-sel',project);await page.click('#qp-link');await qmsg(/Đã lưu dự án CERP-QTO/);
  const fr=page.frameLocator('#qto-frame');await fr.locator('[data-view="drawings"]').waitFor();
  assert.equal(await fr.locator('#project').inputValue(),project);assert.equal(await fr.locator('#token').isVisible(),false);assert.equal(await fr.locator('aside').isVisible(),false);
  steps.push('CERP-QTO nhúng trong khung 8765: dự án theo hồ sơ, không ô token, không thanh bên riêng');
  // 3 · the CERP-QTO flow inside the frame (same steps as cerp-qto tests/e2e_ui.cjs)
  const fmsg=re=>page.waitForFunction(r=>{const f=document.querySelector('#qto-frame');return f&&new RegExp(r).test(f.contentDocument?.querySelector('#msg')?.textContent||'');},re.source,{timeout:90000});
  await fr.locator('[data-view="profiles"]').click();await fr.locator('#toml').waitFor();
  if(!(await fr.locator('tbody').innerText()).includes('cc1-kc-default')){await fr.locator('#toml').fill(profile);await fr.locator('#tsave').click();await fmsg(/Đã lưu draft/);}
  if(await fr.locator('[data-ap]').count()){await fr.locator('[data-ap]').first().click();await page.waitForFunction(()=>!document.querySelector('#qto-frame').contentDocument.querySelector('[data-ap]'));}
  await fr.locator('[data-view="drawings"]').click();await fr.locator('#dup').waitFor();
  await fr.locator('#dcode').fill('KC-01');await fr.locator('#dtitle').fill('TEST ONLY golden GC-QTO-01');await fr.locator('#dfile').setInputFiles(golden);await fr.locator('#dup').click();
  await fr.locator('[data-rev]').first().waitFor();await page.waitForFunction(()=>/ready/.test(document.querySelector('#qto-frame').contentDocument.querySelector('tbody').innerText),null,{timeout:90000});
  await fr.locator('[data-rev]').first().click();await fr.locator('[data-sheet]').first().click();await fr.locator('#calh').click();await fmsg(/Đã xác nhận tỷ lệ/);
  await fr.locator('[data-sheet]').first().click();await fr.locator('#prof').selectOption({label:'cc1-kc-default @ 2026.10'});await fr.locator('#run').click();await fmsg(/Xong: \d+ ứng viên/);
  await page.waitForFunction(()=>document.querySelector('#qto-frame').contentDocument.querySelectorAll('tr[data-m]').length>=10);
  await fr.locator('tr[data-m]').filter({hasText:'KT-SAN-01'}).locator('[data-a="approve"]').click();await fmsg(/Đã cập nhật/);
  await fr.locator('[data-view="takeoff"]').click();await fr.locator('#agg').click();await fmsg(/hạng mục có phiên bản mới/);
  await page.waitForTimeout(300);await page.screenshot({path:path.join(out,'qto-embedded.png')});steps.push('Trong khung: duyệt profile, tải DXF golden, xác nhận tỷ lệ, chạy rule, duyệt KT-SAN-01, tổng hợp takeoff');
  // 4 · back in the estimate: import approved take-off → candidates; assign the 23 m2 hatch to the consultant's 24 m2 line → −4.2 % flagged at 1 %
  await page.click('[data-qtab="review"]');await page.locator('#qi-import').waitFor();await page.click('#qi-import');await qmsg(/Đã nhập \d+ khối lượng đã duyệt: \d+ mới/);
  const cand=page.locator('#qto-view tbody tr').filter({hasText:'m2'}).filter({has:page.locator('[data-qok]')}).first();const cid=await cand.locator('[data-qok]').getAttribute('data-qok');
  assert.match(await cand.innerText(),/23/);await page.selectOption(`[data-qab="${cid}"]`,'test-san');await page.fill(`[data-qr="${cid}"]`,'TEST cùng hạng mục sàn, bản vẽ KC-01');await page.click(`[data-qok="${cid}"]`);await qmsg(/Đã gán khối lượng vào dòng AB/);
  const rv=await page.evaluate(()=>api('/api/projects/'+project.id+'/qto-review',{threshold_pct:'1'}).then(d=>d.review));
  const c=rv.compare.find(x=>x.ab_line_id==='test-san');assert.deepEqual([c.boq_quantity,c.drawing_quantity,c.deviation_pct,c.flag,rv.counts.confirmed],['24','23.0000','-4.2','FLAG',1]);
  assert.equal(await page.evaluate(()=>project.boq.find(r=>r.id==='test-san').quantity),'24');      // the consultant's BOQ is never changed
  assert.match(await page.locator('#qto-view').innerText(),/Vượt ngưỡng/);await page.screenshot({path:path.join(out,'qto-review.png'),fullPage:true});
  steps.push('Thẩm định: nhập takeoff, QS gán 23 m2 vào dòng Tư vấn 24 m2 → lệch −4,2 % vượt ngưỡng 1 %, BOQ không đổi');
  // 5 · flows overview reflects it; history walks qto → flows → step
  await page.click('#open-flows');await page.locator('#flows-view').waitFor();const fl=await page.locator('#flows-view').evaluate(e=>e.textContent);
  assert.match(fl,/Dự án CERP-QTO: E2E-/);assert.match(fl,/1 khối lượng đã nhập/);assert.match(fl,/1 đã gán vào dòng AB/);assert.match(fl,/Pha 5 · Giao thầu phụ[\s\S]*BOQ giao thầu phụ \(BB′\)/);assert.match(fl,/Pha 7 · Theo dõi hiệu quả/);
  await page.waitForTimeout(200);await page.screenshot({path:path.join(out,'flows.png')});
  await page.click('[data-flow="b4"] [data-fact^="step:"]');await page.waitForFunction(()=>!document.querySelector('#workspace').hidden);
  await page.click('#nav-back');await page.waitForFunction(()=>!document.querySelector('#flows-view').hidden);await page.click('#nav-back');await page.waitForFunction(()=>!document.querySelector('#qto-view').hidden);
  steps.push('Luồng làm việc: 5 luồng với trạng thái thật; trang trước đi qua bước → luồng → bản vẽ');
  const d=await browser.newPage({viewport:{width:1440,height:1000},colorScheme:'dark'});d.on('pageerror',e=>errors.push('dark '+e.message));
  await d.goto(base);await d.waitForFunction(()=>typeof boot==='object'&&!!boot.token);await d.evaluate(id=>openProject(id),id);await d.waitForFunction(()=>!!project);await d.click('#open-flows');await d.locator('#flows-view').waitFor();await d.screenshot({path:path.join(out,'flows-dark.png')});
  const m=await browser.newPage({viewport:{width:390,height:844}});await m.goto(base);await m.waitForFunction(()=>typeof boot==='object'&&!!boot.token);await m.evaluate(id=>openProject(id),id);await m.waitForFunction(()=>!!project);await m.click('#open-flows');await m.locator('#flows-view').waitFor();
  const w=await m.evaluate(()=>[document.scrollingElement.scrollWidth,innerWidth]);assert.ok(w[0]<=w[1]+1,'390: '+w);await m.screenshot({path:path.join(out,'flows-mobile.png')});steps.push('Tối + 390 px');
  const expected=errors.filter(e=>/status of (409|401)/.test(e));assert.deepEqual(errors.filter(e=>!/status of (409|401)/.test(e)),[]);console.log('PASS\n - '+steps.join('\n - '));
 }catch(e){console.log('FAIL after:\n - '+steps.join('\n - ')+'\n',e,errors);process.exitCode=1;}finally{await browser.close();}
})();
