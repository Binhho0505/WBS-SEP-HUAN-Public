// D81 UX checks (isolated QA server only, TEST ONLY data from seed_ux_qa.py):
// windows (back / minimise / maximise / Esc), page back (header button + browser Back), quick edits on the grid,
// manual BOQ item, bulk price update with history (persisted), delete draft packages; light, dark and 390 px.
// Usage: python local_app/seed_ux_qa.py <new.sqlite> <dir>; server on another port; CC1_TEST_URL=… CC1_QA_OUT=<dir> node local_app/browser_ux.cjs
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium}=require(process.env.CC1_PLAYWRIGHT_ROOT||'D:/Code/agent code pilot BMAD/CC1_Enterprise_Agentic_SDLC_Kit_v0_3_0/node_modules/playwright');
(async()=>{
 const base=process.env.CC1_TEST_URL,out=process.env.CC1_QA_OUT;if(!base||base.includes(':8765'))throw Error('Set CC1_TEST_URL to an isolated QA server.');
 const [id]=JSON.parse(fs.readFileSync(path.join(out,'ids.json'))),browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const errors=[],steps=[];
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000},colorScheme:'light'});page.setDefaultTimeout(15000);
  page.on('pageerror',e=>errors.push('pageerror '+e.message));page.on('console',m=>{if(m.type()==='error')errors.push('console '+m.text());});
  const msg=re=>page.waitForFunction(r=>new RegExp(r).test(document.querySelector('#message')?.textContent||''),re.source);
  const svmsg=re=>page.waitForFunction(r=>new RegExp(r).test(document.querySelector('#sv-msg')?.textContent||''),re.source);
  const stepNo=()=>page.locator('#step-number').innerText();
  await page.goto(base);await page.waitForFunction(()=>typeof boot==='object'&&!!boot.token);
  await page.evaluate(id=>openProject(id),id);await page.waitForFunction(()=>!!project);
  // 1 · page back: header button and the browser's Back walk through steps and the package screen
  await page.click('[data-step="1"]');await page.click('[data-step="5"]');assert.match(await stepNo(),/BƯỚC 6/);
  assert.equal(await page.locator('#nav-back').isDisabled(),false);
  await page.click('#nav-back');await page.waitForFunction(()=>/BƯỚC 2/.test(document.querySelector('#step-number').textContent));
  await page.goForward();await page.waitForFunction(()=>/BƯỚC 6/.test(document.querySelector('#step-number').textContent));
  await page.goBack();await page.waitForFunction(()=>/BƯỚC 2/.test(document.querySelector('#step-number').textContent));
  steps.push('Trang trước: nút ← header + Back/Forward trình duyệt qua các bước');
  // 3 · prices: quick edit records history; bulk update with preview, reference and rounding; persisted
  await page.click('[data-step="5"]');await page.locator('#price-update').waitFor();
  const p0=await page.evaluate(()=>project.prices[0].unit_price);
  await page.fill('#q-prices-0-unit_price','12');await page.locator('#q-prices-0-unit_price').blur();
  assert.deepEqual(await page.evaluate(()=>project.prices[0].price_history.map(h=>[h.from,h.to,h.how])),[[p0,'12','sửa tay']]);
  await page.click('#price-update');await page.locator('#pu-val').waitFor();assert.equal(await page.locator('#pu-ok').isDisabled(),true);
  await page.fill('#pu-val','10');await page.selectOption('#pu-round','none');assert.match(await page.locator('#pu-prev').innerText(),/13,2/);
  await page.click('#pu-ok');assert.match(await page.locator('#pu-err').innerText(),/căn cứ/);
  await page.fill('#pu-ref','TEST thông báo giá quý 4');await page.click('#pu-ok');await msg(/Đã cập nhật 1 giá/);
  await page.click('#save');await page.waitForFunction(()=>!dirty);
  await page.evaluate(id=>openProject(id),id);await page.waitForFunction(()=>!!project);
  const pr=await page.evaluate(()=>project.prices[0]);assert.equal(pr.unit_price,'13.2');assert.equal(pr.price_history.length,2);assert.match(pr.price_ref,/Cập nhật \+10% .*TEST thông báo giá quý 4/);
  await page.click('[data-step="5"]');await page.click('.row-edit');assert.match(await page.locator('.editor').innerText(),/Lịch sử giá/);
  await page.click('#close-row');assert.equal(await page.locator('#close-row').count(),0);
  steps.push('Giá: sửa ngay trên bảng có lịch sử; cập nhật hàng loạt +10% có xem trước, bắt buộc căn cứ; lưu và tải lại còn nguyên');
  // 4 · windows: stack, back, Esc, maximise, minimise (page usable underneath), restore
  await page.evaluate(()=>showDialog('<h2>TEST cửa sổ A</h2><p>A</p><input id="t-a">'));
  await page.fill('#t-a','giữ nguyên');assert.equal(await page.locator('#dialog-back').isHidden(),true);
  await page.evaluate(()=>showDialog('<h2>TEST cửa sổ B</h2><p>B</p>'));assert.equal(await page.locator('#dialog-title').innerText(),'TEST cửa sổ B');
  await page.click('#dialog-back');assert.equal(await page.locator('#dialog-title').innerText(),'TEST cửa sổ A');assert.equal(await page.inputValue('#t-a'),'giữ nguyên');  // content and input kept
  await page.evaluate(()=>showDialog('<h2>TEST cửa sổ B</h2><p>B</p>'));await page.keyboard.press('Escape');assert.equal(await page.locator('#dialog-title').innerText(),'TEST cửa sổ A');
  await page.click('#dialog-max');assert.equal(await page.evaluate(()=>document.querySelector('#dialog').classList.contains('max')),true);
  const box=await page.locator('#dialog').boundingBox();assert.ok(box.width>=1430,'maximised width '+box.width);
  await page.waitForTimeout(400);await page.screenshot({path:path.join(out,'ux-dialog-max.png')});
  await page.click('#dialog-max');await page.click('#dialog-min');
  assert.deepEqual(await page.evaluate(()=>{const d=document.querySelector('#dialog');return [d.open,d.classList.contains('min'),d.matches(':modal')];}),[true,true,false]);
  await page.click('[data-step="1"]');assert.match(await stepNo(),/BƯỚC 2/);   // page usable while minimised
  await page.waitForTimeout(400);await page.screenshot({path:path.join(out,'ux-dialog-min.png')});
  await page.click('#dialog-min');assert.deepEqual(await page.evaluate(()=>{const d=document.querySelector('#dialog');return [d.classList.contains('min'),d.matches(':modal')];}),[false,true]);
  assert.equal(await page.inputValue('#t-a'),'giữ nguyên');await page.click('#dialog-close');assert.equal(await page.evaluate(()=>document.querySelector('#dialog').open),false);
  steps.push('Cửa sổ: ← quay lại giữ nội dung, Esc lùi một cấp, phóng to toàn màn, thu nhỏ xuống góc (trang vẫn thao tác), mở lại, đóng');
  // 5 · delete draft packages
  await page.click('#open-subcontract');await page.locator('#subcontract-view').waitFor();
  await page.selectOption('#sv-model','PMBOK6');await svmsg(/Đã lưu gói thầu/);
  for(const [c,n] of [['GT-01','TEST gói giữ lại'],['GT-02','TEST gói nháp tạo nhầm'],['GT-03','TEST gói rỗng']]){await page.fill('#np-code',c);await page.fill('#np-name',n);await page.click('#np-add');}
  await page.click('#pk-save');await svmsg(/Đã lưu gói thầu/);
  const g2=await page.evaluate(()=>project.packages.find(p=>p.code==='GT-02').id);
  await page.click(`[data-pkdel="${g2}"]`);await page.locator('#del-ok').waitFor();assert.match(await page.locator('#dialog-content').innerText(),/GT-02/);
  await page.click('#del-cancel');assert.equal(await page.evaluate(()=>project.packages.length),3);
  await page.click(`[data-pkdel="${g2}"]`);await page.click('#del-ok');await svmsg(/Đã xóa GT-02/);
  assert.deepEqual(await page.evaluate(()=>project.packages.map(p=>p.code)),['GT-01','GT-03']);
  assert.match(await page.locator('#pk-del-empty').innerText(),/Xóa 2 gói rỗng/);await page.click('#pk-del-empty');assert.match(await page.locator('#dialog-title').innerText(),/Xóa 2 gói thầu/);await page.click('#del-ok');await svmsg(/Đã xóa GT-01, GT-03/);
  assert.deepEqual(await page.evaluate(()=>project.packages.map(p=>p.code)),[]);
  steps.push('Xóa gói nháp: nút thùng rác từng gói + "Xóa N gói rỗng", hộp xác nhận nêu hậu quả, Hủy không xóa');
  // 6 · page back from the package screen to the step view
  await page.click('[data-svtab="pakd"]');await page.click('#nav-back');await page.waitForFunction(()=>window.SV&&SV.tab()==='packages');
  await page.click('#sv-back');await page.waitForFunction(()=>!document.querySelector('#workspace').hidden);
  await page.click('#nav-back');await page.waitForFunction(()=>!document.querySelector('#subcontract-view').hidden);
  steps.push('Trang trước qua màn Gói thầu (tab → tab, gói thầu ↔ 8 bước)');
  // 6b · project menu ⋮ (D84): keyboard + rename, duplicate (opens the copy), hide, bin, restore, purge with typed name
  await page.click('#sv-back');
  const menu=async pid=>{await page.click(`[data-pmenu="${pid}"]`);await page.locator('#project-menu').waitFor();};
  const act=async a=>{await page.click(`#project-menu [data-pact="${a}"]`);};
  await page.focus(`[data-pmenu="${id}"]`);await page.keyboard.press('Enter');await page.locator('#project-menu').waitFor();
  assert.equal(await page.evaluate(()=>document.activeElement.dataset.pact),'open');await page.keyboard.press('ArrowDown');assert.equal(await page.evaluate(()=>document.activeElement.dataset.pact),'rename');
  await page.keyboard.press('Escape');assert.equal(await page.locator('#project-menu').count(),0);assert.equal(await page.evaluate(()=>document.activeElement.dataset.pmenu),id);
  await menu(id);await page.waitForTimeout(150);await page.screenshot({path:path.join(out,'ux-project-menu.png')});await act('rename');await page.fill('#pr-name','TEST ONLY · UX QA đổi tên');await page.keyboard.press('Enter');await msg(/Đã đổi tên hồ sơ/);
  assert.equal(await page.locator('#project-title').innerText(),'TEST ONLY · UX QA đổi tên');
  await menu(id);await act('duplicate');await page.fill('#pd-name','TEST ONLY · bản sao UX');await page.click('#pd-ok');await msg(/Đã tạo bản sao/);
  const cp=await page.evaluate(()=>project.id);assert.notEqual(cp,id);assert.equal(await page.evaluate(()=>project.confirmed.length),0);
  await menu(cp);await act('hide');await msg(/Đã ẩn/);assert.match(await page.locator('#projects').innerText(),/Đã ẩn \(1\)/);
  await page.click('[data-pgroup="hidden"] summary');await menu(cp);await act('delete');await page.click('#pdel-ok');await msg(/thùng rác/);
  assert.equal(await page.locator('#welcome').isHidden(),false);assert.match(await page.locator('#projects').innerText(),/Thùng rác \(1\)/);   // active copy closed
  await page.click('[data-pgroup="bin"] summary');assert.equal(await page.locator(`[data-project="${cp}"]`).isDisabled(),true);
  await menu(cp);await act('restore');await msg(/Đã khôi phục/);await menu(cp);await act('delete');await page.click('#pdel-ok');await msg(/thùng rác/);
  assert.equal(await page.locator('[data-pgroup="bin"]').getAttribute('open'),'');  // the bin stays open (remembered)
  await menu(cp);await act('purge');assert.equal(await page.locator('#pp-ok').isDisabled(),true);
  await page.fill('#pp-name','sai');assert.equal(await page.locator('#pp-ok').isDisabled(),true);await page.fill('#pp-name','TEST ONLY · bản sao UX');await page.click('#pp-ok');await msg(/Đã xóa vĩnh viễn/);
  assert.deepEqual(await page.evaluate(()=>boot.projects.map(p=>p.id)),[id]);
  await page.evaluate(id=>openProject(id),id);await page.waitForFunction(()=>!!project);
  steps.push('Menu ⋮ hồ sơ: bàn phím (Enter, ↓, Esc trả focus), đổi tên, nhân bản và mở bản sao, ẩn, thùng rác (đóng hồ sơ đang mở), khôi phục, xóa vĩnh viễn phải gõ đúng tên');
  // 7 · manual BOQ item (step 2 = BOQ); saving it reopens the dependent steps (by design)
  await page.click('[data-step="1"]');
  await page.click('#add-manual');await page.locator('#mi-desc').waitFor();
  await page.click('#mi-ok');assert.match(await page.locator('#mi-err').innerText(),/tên hạng mục/);  // inline validation, dialog stays
  await page.fill('#mi-code','9.1');await page.fill('#mi-desc','TEST ONLY hạng mục tay');await page.fill('#mi-qty','12,5');await page.fill('#mi-uom','m3');await page.fill('#mi-price','150000');await page.fill('#mi-ref','TEST biên bản bổ sung');
  await page.click('#mi-ok');await msg(/Đã thêm hạng mục tay/);
  const man=await page.evaluate(()=>project.boq.find(r=>r.description==='TEST ONLY hạng mục tay'));assert.deepEqual([man.quantity,man.unit_price,man.kind,man.source_ref.startsWith('MANUAL')],['12.5','150000','MEASURED',true]);
  assert.match(await page.locator('#stage-content').innerText(),/nhập tay/);
  // quick edit of a BOQ quantity on the grid row
  const qi=await page.evaluate(()=>project.boq.findIndex(r=>r.description==='TEST ONLY hạng mục tay'));
  await page.fill(`#q-boq-${qi}-quantity`,'13');await page.locator(`#q-boq-${qi}-quantity`).blur();
  assert.equal(await page.evaluate(i=>project.boq[i].quantity,qi),'13');assert.equal(await page.inputValue(`#boq-${qi}-quantity`),'13');  // detail form in step
  await page.click('#save');await page.waitForFunction(()=>!dirty);await page.waitForFunction(()=>document.querySelector('[data-step="5"]').disabled).catch(async()=>{throw Error('price step still open after BOQ save: '+JSON.stringify(await page.evaluate(()=>({msg:document.querySelector('#message').textContent,stages:stages.map(s=>[s.available,s.confirmed])}))));});  // BOQ changed → price step reopens for review
  steps.push('Hạng mục tay (hộp thoại, kiểm lỗi tại chỗ) + sửa KL ngay trên bảng, đồng bộ form, lưu; các bước sau mở lại để kiểm');
  // 8 · dark theme + 390 px
  const d=await browser.newPage({viewport:{width:1440,height:1000},colorScheme:'dark'});d.on('pageerror',e=>errors.push('dark '+e.message));
  await d.goto(base);await d.waitForFunction(()=>typeof boot==='object'&&!!boot.token);await d.evaluate(id=>openProject(id),id);await d.waitForFunction(()=>!!project);
  await d.evaluate(()=>{step=5;render();});await d.click('#price-update');await d.fill('#pu-val','5');await d.waitForTimeout(400);await d.screenshot({path:path.join(out,'ux-dark-price-update.png')});
  const m=await browser.newPage({viewport:{width:390,height:844},colorScheme:'light'});m.on('pageerror',e=>errors.push('mobile '+e.message));
  await m.goto(base);await m.waitForFunction(()=>typeof boot==='object'&&!!boot.token);await m.evaluate(id=>openProject(id),id);await m.waitForFunction(()=>!!project);
  await m.evaluate(()=>{step=5;render();});await m.click('#price-update');await m.fill('#pu-val','5');
  const w=await m.evaluate(()=>[document.scrollingElement.scrollWidth,innerWidth,document.querySelector('#dialog').getBoundingClientRect().width]);assert.ok(w[0]<=w[1]+1&&w[2]<=w[1],'390: '+w);
  await m.click('#dialog-min');const mb=await m.locator('#dialog').boundingBox();assert.ok(mb.width<=390&&mb.y>500,'minimised dock on mobile '+JSON.stringify(mb));
  await m.waitForTimeout(400);await m.screenshot({path:path.join(out,'ux-mobile.png')});steps.push('Tối + 390 px: không cuộn ngang, cửa sổ thu nhỏ nằm đáy màn');
  assert.deepEqual(errors,[]);console.log('PASS\n - '+steps.join('\n - '));
 }catch(e){console.log('FAIL after:\n - '+steps.join('\n - ')+'\n',e,errors);process.exitCode=1;}finally{await browser.close();}
})();
