// D73 end-to-end through the UI on an EMPTY isolated QA server (never :8765), TEST ONLY data generated here:
// CC1 norms / resources / prices loaded into the data library → new project with contract AB context → BOQ AB CSV import with
// column mapping → manual edits (description, BOQ price, quantity, work code) + a typed line → WBS → CC1 norms pulled from the
// library + manual recipe edit → resource coefficient edited → CC1 prices pulled + one price edited → CBS rules → hand-checked
// total 750,778,875 → Excel export → subcontract split (PMBOK 6, GT-01 60% / CC1 40%, GT-02, typed line to CC1) with manual
// award prices → packs → reload: every manual value persisted.
// Usage: CC1_TEST_URL=http://127.0.0.1:8768/ CC1_QA_OUT=<dir> node local_app/browser_full_chain.cjs
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium}=require(process.env.CC1_PLAYWRIGHT_ROOT||'D:/Code/agent code pilot BMAD/CC1_Enterprise_Agentic_SDLC_Kit_v0_3_0/node_modules/playwright');
const T='TEST ONLY',LOC='TEST Hà Nội';
const csv=rows=>rows.map(r=>r.map(v=>/[",\n]/.test(String(v))?'"'+String(v).replace(/"/g,'""')+'"':v).join(',')).join('\n')+'\n';
(async()=>{
 const base=process.env.CC1_TEST_URL,out=process.env.CC1_QA_OUT;if(!base||base.includes(':8765'))throw Error('Set CC1_TEST_URL to an EMPTY isolated QA server.');assert.ok(out,'set CC1_QA_OUT');fs.mkdirSync(out,{recursive:true});
 const f=n=>path.join(out,n);
 fs.writeFileSync(f('boq_ab.csv'),'\ufeff'+csv([['Ma','MoTa','KL','DV','DonGia','Loai'],['1','PHẦN MÓNG (TEST ONLY)','','','','heading'],['1.1','Bê tông móng B25 (TEST ONLY)','120','m3','1800000','line'],
   ['1.2','Cốt thép móng (TEST ONLY)','15','tấn','22000000','line'],['1.3','Ván khuôn móng (TEST ONLY)','300','m2','180000','line']]));
 const NH=['id','code','kind','edition','uom','denominator','conditions','source_ref','selection_ref','table_verified','tt37_ref'];
 fs.writeFileSync(f('cc1_norms.csv'),csv([NH,['CC1-N1','CC1.BT.25','CC1_APPROVED_CUSTOM','CC1 TEST 2026','m3','1','TEST bê tông B25 đổ bằng bơm','TEST bộ CC1','TEST QS chọn','TRUE','TEST QĐ CC1'],
   ['CC1-N2','CC1.CT.01','CC1_APPROVED_CUSTOM','CC1 TEST 2026','tấn','1','TEST cốt thép móng','TEST bộ CC1','TEST QS chọn','TRUE','TEST QĐ CC1'],
   ['CC1-N3','CC1.VK.01','CC1_APPROVED_CUSTOM','CC1 TEST 2026','m2','100','TEST ván khuôn gỗ','TEST bộ CC1','TEST QS chọn','TRUE','TEST QĐ CC1']]));
 const RH=['id','norm_id','line_type','resource_code','name','spec','uom','coefficient','percent','percent_of','cbs','source_ref'];
 const R=[['R1','CC1-N1','QTY','CC1-VL-BT25','Bê tông B25','TEST B25','m3','1.025','','','C10','TEST'],['R2','CC1-N1','QTY','CC1-NC-35','Nhân công 3.5/7','TEST 3.5/7','công','1.5','','','C20','TEST'],
   ['R3','CC1-N1','QTY','CC1-M-DAM','Máy đầm dùi','TEST 1.5kW','ca','0.1','','','C30','TEST'],['R4','CC1-N2','QTY','CC1-VL-THEP','Thép CB400','TEST CB400','tấn','1.02','','','C10','TEST'],
   ['R5','CC1-N2','QTY','CC1-NC-35','Nhân công 3.5/7','TEST 3.5/7','công','10','','','C20','TEST'],['R6','CC1-N3','QTY','CC1-VL-VAN','Ván khuôn gỗ','TEST gỗ','m2','30','','','C10','TEST'],
   ['R7','CC1-N3','QTY','CC1-NC-35','Nhân công 3.5/7','TEST 3.5/7','công','25','','','C20','TEST']];
 fs.writeFileSync(f('cc1_resources.csv'),csv([RH,...R]));
 const PH=['id','resource_code','spec','uom','unit_price','location','period','currency','tax_basis','delivery','included','source_ref','price_ref'];
 const P=[['P1','CC1-VL-BT25','TEST B25','m3','1200000'],['P2','CC1-NC-35','TEST 3.5/7','công','300000'],['P3','CC1-M-DAM','TEST 1.5kW','ca','500000'],['P4','CC1-VL-THEP','TEST CB400','tấn','20000000'],['P5','CC1-VL-VAN','TEST gỗ','m2','150000']]
   .map(r=>[...r.slice(0,5),LOC,'2026-10','VND','EX_VAT','AT_SITE','TEST tại chân công trình','TEST bảng giá CC1','TEST QS kiểm']);
 fs.writeFileSync(f('cc1_prices.csv'),csv([PH,...P]));
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true}),errors=[],steps=[];
 const page=await browser.newPage({viewport:{width:1440,height:1100},acceptDownloads:true});page.setDefaultTimeout(20000);
 page.on('pageerror',e=>errors.push('pageerror '+e.message));page.on('console',m=>{if(m.type()==='error')errors.push('console '+m.text());});
 const title=t=>page.waitForFunction(t=>document.querySelector('#stage-title').textContent===t,t);
 const msg=re=>page.waitForFunction(r=>new RegExp(r).test(document.querySelector('#message').textContent),re.source);
 async function fill(group,values){for(const [key,value] of Object.entries(values)){const el=page.locator(`[data-group="${group}"][data-field="${key}"]`).last();if(!(await el.count()))throw Error('no field '+group+'.'+key);const tag=await el.evaluate(e=>e.tagName),type=await el.getAttribute('type');if(type==='checkbox')await el.setChecked(value===true);else if(tag==='SELECT')await el.selectOption(String(value));else{await el.fill(String(value??''));await el.blur();}}}
 async function confirm(next){await page.locator('#confirm').click();await page.waitForFunction(([t,n])=>document.querySelector('#stage-title').textContent===t||/Cần bổ sung/.test(document.querySelector('#message').textContent),[next,0]);
  const t=await page.locator('#stage-title').textContent();if(t!==next)throw Error('Không qua được bước: '+(await page.locator('#message').textContent())+' | '+JSON.stringify(await page.evaluate(()=>project&&status&&0)));}
 async function editRow(q){await page.locator('#row-search').fill(q);await page.locator('#row-search').dispatchEvent('change');await page.locator('.row-edit').first().click();}
 async function bulk(field,value){await page.locator('#bulk-fill').click();await page.locator('#bulk-field').selectOption(field);const el=page.locator('#bulk-value [data-field]');if((await el.evaluate(e=>e.tagName))==='SELECT')await el.selectOption(value);else await el.fill(value);await page.locator('#bulk-confirm').click();}
 try{
  await page.goto(base);await page.getByRole('button',{name:'Tạo hồ sơ đầu tiên'}).click();await page.locator('#new-name').fill('QA TOÀN CHUỖI · TEST ONLY · không phải dự toán thật');await page.locator('#create-confirm').click();await title('Hồ sơ dự án');
  // CC1 data first: norms, resources and prices into the shared data library (versioned, SHA256)
  for(const [kind,name,file] of [['NORMS','CC1 TEST định mức','cc1_norms.csv'],['RESOURCES','CC1 TEST hao phí','cc1_resources.csv'],['PRICES','CC1 TEST bảng giá','cc1_prices.csv']]){
   await page.locator('#open-library').click();await page.locator('#lib-name').fill(name);await page.locator('#lib-kind').selectOption(kind);await page.locator('#lib-file').setInputFiles(f(file));await page.locator('#lib-upload').click();
   await page.locator(`text=${name} · v1`).waitFor();await page.locator('#dialog-close').click();}
  steps.push('CC1 norms/resources/prices loaded into the data library');
  for(const k of ['project_code','legal_entity','baseline','owner','reviewer','legal_ref','rounding_ref'])await fill('context',{[k]:T});
  await fill('context',{contract_ref:'HĐ AB TEST-01 (Chủ đầu tư A – CC1), phụ lục BOQ',location:LOC,period:'2026-10',currency:'VND',cost_basis:'ESTIMATE',estimate_purpose:'INTERNAL_COST',relation_profile:'ESTIMATE_MIN',money_places:'0',rounding_level:'TOTAL'});
  await confirm('BOQ nguồn');steps.push('1 Hồ sơ + hợp đồng AB');
  await page.locator('#import').click();await page.locator('#upload-file').setInputFiles(f('boq_ab.csv'));await page.locator('#preview-file').click();await page.locator('[data-column="description"]').waitFor();
  for(const [k,v] of [['source_code','Ma'],['description','MoTa'],['quantity','KL'],['uom','DV'],['unit_price','DonGia'],['kind','Loai']])await page.locator(`[data-column="${k}"]`).selectOption(v);
  await page.locator('#import-confirm').click();await msg(/Đã nạp file vào nháp/);assert.equal(await page.evaluate(()=>project.boq.length),4);
  await editRow('1.1');await fill('boq',{description:'Bê tông móng B25 đá 1x2 (sửa tay)',quantity:'125',unit_price:'1850000',disposition_ref:'TEST phụ lục 01 tăng khối lượng'});
  await editRow('Ván khuôn');await fill('boq',{source_code:'1.3.1',disposition_ref:'TEST đổi mã công việc theo WBS chi tiết'});
  await page.locator('#row-search').fill('');await page.locator('#row-search').dispatchEvent('change');
  await page.locator('#add-row').click();await fill('boq',{source_code:'1.4',description:'Bê tông lót móng B10 (dòng thêm tay)',kind:'MEASURED',quantity:'10',uom:'m3',unit_price:'1200000',disposition_ref:'TEST biên bản bổ sung khối lượng'});
  await confirm('WBS và các bộ mã');
  const boq=await page.evaluate(()=>project.boq.map(r=>({c:r.source_code,d:r.description,q:r.quantity,p:r.unit_price,oc:r.original_source_code,oq:r.original_quantity,op:r.original_unit_price,src:r.source_ref,raw:!!r.raw})));
  const b11=boq.find(r=>r.c==='1.1'),b13=boq.find(r=>r.c==='1.3.1'),b14=boq.find(r=>r.c==='1.4');
  assert.deepEqual([b11.q,b11.p,b11.oq,b11.op],['125','1850000','120','1800000']);assert.equal(b13.oc,'1.3');assert.ok(b14.src.startsWith('MANUAL')&&b14.raw);
  steps.push('2 BOQ AB nạp CSV + sửa tay mô tả/giá/khối lượng/mã + dòng thêm tay (gốc giữ ở original_*)');
  const wr=await page.evaluate(()=>master.find(r=>r.code.startsWith('H')&&r.status!=='HOLD').code);
  await page.locator('#add-row').click();await fill('wbs',{work_result_code:wr,lbs:'TEST-MONG',scope:'TEST móng',acceptance:'TEST nghiệm thu móng',ca:'TEST-CA',cam:'TEST-CAM'});
  await page.locator('[data-sub="mapping"]').click();await bulk('wbs_id','WP-001');await bulk('mapping_ref','TEST mapping móng');await confirm('Chọn định mức');steps.push('3 WBS');
  await page.locator('#library-norms').click();await page.locator('#ln-norms').waitFor();
  await page.locator('#ln-norms').selectOption({label:await page.locator('#ln-norms option').filter({hasText:'CC1 TEST định mức'}).first().innerText()});
  await page.locator('#ln-res').selectOption({label:await page.locator('#ln-res option').filter({hasText:'CC1 TEST hao phí'}).first().innerText()});
  await page.locator('#ln-confirm').click();await msg(/Đã thêm 3 tổ hợp định mức và 7 dòng hao phí/);
  await editRow('CC1.BT.25');await fill('norms',{conditions:'TEST bê tông B25 đổ bằng bơm, đá 1x2 (QS sửa tay)',selection_ref:'TEST QS chọn theo biện pháp bơm'});
  const ids=await page.evaluate(()=>{const b=Object.fromEntries(project.boq.map(r=>[r.id,r.source_code]));return {items:project.mapping.map(m=>[b[m.source_line_id],m.id]),norms:Object.fromEntries(project.norms.map(n=>[n.code,n.id]))};});
  const item=Object.fromEntries(ids.items),use={'1.1':'CC1.BT.25','1.2':'CC1.CT.01','1.3.1':'CC1.VK.01','1.4':'CC1.BT.25'};
  await page.locator('[data-sub="applications"]').click();
  for(const [code,norm] of Object.entries(use)){await page.locator('#add-row').click();await fill('applications',{item_id:item[code],norm_id:ids.norms[norm],qty_factor:'1'});}
  await page.locator('[data-sub="assign"]').click();await bulk('technical_spec','TEST quy cách theo hồ sơ');await bulk('method','TEST biện pháp thi công');await bulk('norm_match_ref','TEST đối chiếu điều kiện');
  await confirm('Phân tích hao phí');steps.push('4 Định mức CC1 lấy từ thư viện + sửa tay recipe + ghép từng hạng mục');
  await editRow('CC1-VL-THEP');  // locate the steel norm lines; edit labour coefficient of norm CC1-N2
  await page.locator('#row-search').fill('');await page.locator('#row-search').dispatchEvent('change');
  const r5=await page.evaluate(()=>project.resources.findIndex(r=>r.id==='R5'));assert.ok(r5>=0);
  await page.evaluate(i=>{selected=i;render();},r5);await fill('resources',{coefficient:'11',source_ref:'TEST QS tăng hao phí nhân công cốt thép'});
  await page.locator('#completeness').fill('TEST đủ dòng hao phí');await page.locator('#completeness').blur();await confirm('Đơn giá CC1');steps.push('5 Hao phí (sửa tay hệ số)');
  await page.locator('#library-prices').click();await page.locator('#lp-set').waitFor();
  await page.locator('#lp-set').selectOption({label:await page.locator('#lp-set option').filter({hasText:'CC1 TEST bảng giá'}).first().innerText()});
  await page.locator('#lp-confirm').click();await msg(/Đã thêm 5 dòng giá; phủ 5\/5/);
  await editRow('CC1-VL-BT25');await fill('prices',{unit_price:'1250000',price_ref:'TEST báo giá NCC 10/2026 thay bảng CC1'});
  await confirm('CBS và tổng dự toán');steps.push('6 Giá CC1 lấy từ thư viện + sửa tay một giá');
  await fill('adjustments',{cbs_scheme_ref:T,cost_boundary_ref:T,tax_ref:T,completeness_ref:T,allocation_driver:'DIRECT_PRORATA'});
  for(const rule of [{nature:'COST',cbs:'C50',id:'TEST_OH',name:'TEST chi phí chung',method:'PERCENT',basis:'DIRECT',value:'10',source_ref:'TEST'},{nature:'TAX',id:'TEST_VAT',name:'TEST VAT',method:'PERCENT',basis:'DIRECT+TEST_OH',value:'8',source_ref:'TEST'}]){await page.locator('#add-row').click();await fill('rules',rule);}
  await page.locator('#save').click();await msg(/Đã lưu phiên bản/);
  const calc=await page.evaluate(()=>({total:project._calculation.total,direct:project._calculation.direct}));
  // hand check: N1 1.025×1,250,000+1.5×300,000+0.1×500,000=1,781,250/m3 × (125+10); N2 (1.02×20,000,000+11×300,000)×15; N3 (30×150,000+25×300,000)/100×300
  assert.equal(calc.total,'750778875','total '+JSON.stringify(calc));await confirm('Kiểm tra và xuất');steps.push('7 CBS: tổng 750.778.875 khớp tính tay');
  await fill('export',{prepared_by:T,checked_by:T,review_ref:T,template_id:'TPL03_COMPOSITION',local_draft_ack:true});await page.locator('#confirm').click();
  await page.waitForFunction(()=>document.querySelector('#stage-state').textContent==='ĐÃ XÁC NHẬN TRÊN MÁY');
  const dl=page.waitForEvent('download');await page.locator('#export-xlsx').click();await(await dl).saveAs(f('DU_TOAN_TOAN_CHUOI_TEST_ONLY.xlsx'));steps.push('8 Kiểm tra + xuất Excel');
  // subcontract split for subcontractors (NTP)
  await page.click('#open-subcontract');await page.locator('#subcontract-view').waitFor();
  const smsg=re=>page.waitForFunction(r=>new RegExp(r).test(document.querySelector('#sv-msg')?.textContent||''),re.source).catch(async e=>{throw Error(`waiting ${re}: #sv-msg = "${await page.locator('#sv-msg').textContent().catch(()=>'?')}"`);});
  await page.selectOption('#sv-model','PMBOK6');await smsg(/Đã lưu gói thầu/);
  for(const [code,name] of [['GT-01','TEST bê tông + ván khuôn móng'],['GT-02','TEST cốt thép móng']]){await page.fill('#np-code',code);await page.fill('#np-name',name);await page.click('#np-add');}
  await page.click('#np-self');await page.click('#pk-save');await smsg(/Đã lưu gói thầu/);
  const setPkg=async code=>{await page.locator('tr[data-pkg]').filter({hasText:code}).first().click();};
  const delivery=async()=>{await page.selectOption('[data-f="procurement_method"]','QUALITY_AND_COST');await page.selectOption('[data-d="mode"]','GOP');await page.selectOption('[data-d="price_form"]','DON_GIA_CO_DINH');
   await page.fill('[data-d="fee_pct"]','5');await page.fill('[data-d="fee_ref"]','TEST phí quản lý');await page.fill('[data-p="k_all"]','0.9');await page.locator('[data-p="k_all"]').blur();await page.click('#pk-save');await smsg(/Đã lưu gói thầu/);};
  const add=async(by,q,pct,n)=>{await page.selectOption('#al-by',by);await page.fill('#al-q',q);await page.fill('#al-pct',pct);await page.click('#al-add');await smsg(new RegExp('Đã thêm '+n+' dòng'));};
  await setPkg('GT-01');await delivery();await add('WBS','1.1','60',1);await add('WBS','1.3','100',1);
  await setPkg('GT-02');await delivery();await add('WBS','1.2','100',1);
  await setPkg('CC1');await page.selectOption('#al-by','IDS');for(const c of ['1.1','1.4']){const id=await page.evaluate(c=>project.boq.find(r=>r.source_code===c).id,c);await page.locator(`[data-pick="${id}"]`).check();}
  await page.check('#al-rem');await page.click('#al-add');await smsg(/Đã thêm 2 dòng/);
  await page.click('[data-svtab="coverage"]');assert.match(await page.locator('#subcontract-view .badge').innerText(),/Đủ điều kiện/);steps.push('Chia thầu: GT-01 (1.1 60% + 1.3.1), GT-02 (1.2), CC1 (1.1 40% + 1.4 dòng tay) — phủ 100%');
  await page.click('[data-svtab="award"]');
  for(const [code,vendor,prices] of [['GT-01','TEST NTP Bê tông A',['1700000','170000']],['GT-02','TEST NTP Thép B',['21500000']]]){
   const pid=await page.evaluate(c=>project.packages.find(p=>p.code===c).id,code);const inputs=page.locator(`[data-ap="${pid}"]`);assert.equal(await inputs.count(),prices.length);
   for(let i=0;i<prices.length;i++){await inputs.nth(i).fill(prices[i]);await inputs.nth(i).blur();}
   await page.fill(`[data-av="${pid}"]`,vendor);await page.fill(`[data-aby="${pid}"]`,'TEST QS');await page.fill(`[data-ar="${pid}"]`,'TEST giá giao nhập tay theo thương thảo');await page.click(`[data-asave="${pid}"]`);await smsg(/nháp/);}
  steps.push('Giá giao nhập tay từng dòng BB + đề xuất DRAFT');
  // E17 PAKD · BM01 (D76), hand check: B = 125×1,850,000 + 15×22,000,000 + 300×180,000 + 10×1,200,000 = 627,250,000
  // C.1.5 = 1,700,000×125×60% + 170,000×300 + 21,500,000×15 = 501,000,000; C.1.4 = CC1 VL (40% of 1.1 + 1.4) = 64,062,500 + 12,812,500 = 76,875,000
  // C.1.6b = CC1 NC+M = 25,000,000 + 5,000,000 = 30,000,000; C.1.1 = 5,000,000; C.2 = 2% × B = 12,545,000 → D = 1,830,000 (0.29%)
  await page.click('[data-svtab="pakd"]');await page.locator('#pk-sel').waitFor();
  assert.match(await page.locator('#sv-body').innerText(),/chọn căn cứ giá giao/);  // no basis chosen yet → missing, not zero
  for(const code of ['GT-01','GT-02']){const id=await page.evaluate(c=>project.packages.find(p=>p.code===c).id,code);await page.selectOption(`[data-pkb="${id}"]`,'AWARD');}
  for(const [code,method,base,value,ref] of [['C.1.1','AMOUNT',null,'5000000','TEST báo giá thiết kế BVTC'],['C.2','PERCENT','DT','2','TEST quy chế chi phí gián tiếp']]){
   await page.selectOption('#pl-code',code);await page.click('#pl-add');const i=await page.locator('[data-pldel]').count()-1;
   if(method==='PERCENT'){await page.selectOption(`[data-pl="${i}"][data-k="method"]`,'PERCENT');await page.selectOption(`[data-pl="${i}"][data-k="base"]`,base);}
   await page.fill(`[data-pl="${i}"][data-k="value"]`,value);await page.locator(`[data-pl="${i}"][data-k="value"]`).blur();
   await page.fill(`[data-pl="${i}"][data-k="source_ref"]`,ref);await page.locator(`[data-pl="${i}"][data-k="source_ref"]`).blur();}
  // D86: Quy trình PAKD v1.0 — baseline (chốt) cần dòng tiền, nên lập dòng tiền 2 kỳ ngay trên Kịch bản 1 (bản sao A kế thừa)
  const fillB=async(sel,v)=>{await page.fill(sel,v);await page.locator(sel).blur();};
  await page.click('#cf-start');await fillB('#cf-n','2');await fillB('#cf-start-m','2027-01');await fillB('#cf-sref','TEST tiến độ 2 tháng');
  for(const [k,vals] of [['revenue_pct',['50','50']],['ntp_pct',['50','50']],['own_pct',['100','0']]])for(let i=0;i<2;i++)await fillB(`[data-cfs="${k}|${i}"]`,vals[i]);
  for(const [side,vals] of [['ab',{advance_pct:'0',retention_pct:'0',delay:'1',ref:'TEST HĐ AB điều khoản thanh toán'}],['ntp',{advance_pct:'0',retention_pct:'0',delay:'1',ref:'TEST dự thảo HĐ NTP'}],['own',{delay:'0',ref:'TEST trả ngay'}]])
   for(const [k,v] of Object.entries(vals))await fillB(`[data-cft="${side}|${k}"]`,v);
  await page.click('#pk-save-s');await smsg(/Đã lưu kịch bản PAKD/);
  const pk=await page.evaluate(async()=>{const v=await api('/api/projects/'+project.id+'/subcontract');const c=v.pakd.scenarios.find(x=>x.id===v.pakd.current);return {t:c.result.totals,rows:Object.fromEntries(c.result.rows.map(r=>[r.code,r.value])),m:c.result.rows.find(r=>r.code==='D').margin_pct,miss:c.result.missing,q:c.questions};});
  assert.deepEqual(pk.miss,[]);assert.deepEqual(pk.q,[]);
  assert.deepEqual([pk.t.B,pk.rows['C.1.4'],pk.rows['C.1.5'],pk.rows['C.1.6b'],pk.rows['C.1.7'],pk.rows['C.2'],pk.t.D,pk.m],['627250000','76875000','501000000','30000000','0','12545000','1830000','0.29']);
  steps.push('PAKD · BM01: B 627.250.000 − C = LN gộp 1.830.000 (0,29%) khớp tính tay');
  await page.fill('#pk-newname','TEST căn cứ A');await page.click('#pk-copy');await smsg(/Đã nhân bản/);
  assert.match(await page.locator('#sv-body').innerText(),/So sánh kịch bản/);
  await page.selectOption('#pk-sel',{label:'Kịch bản 1'});await smsg(/Đã chọn kịch bản/);
  await page.fill('#pf-name','TEST PAKD lần 1');await page.fill('#pf-by','TEST QS');await page.click('#pf-go');await smsg(/Đã chốt phiên bản PAKD/);
  assert.match(await page.locator('#sv-body').innerText(),/TEST PAKD lần 1[\s\S]*Khớp/);
  const vx=await page.evaluate(async()=>{const v=await api('/api/projects/'+project.id+'/subcontract');return v.pakd.versions[0].id;});
  for(const u of [`/pakd.xlsx`,`/pakd.xlsx?version=${vx}`]){const r=await page.request.get(base.replace(/\/$/,'')+`/api/projects/${await page.evaluate(()=>project.id)}`+u);assert.equal(r.status(),200,u);}
  await page.screenshot({path:f('pakd-bm01.png'),fullPage:true});
  steps.push('PAKD: nhân bản kịch bản, so sánh, chốt phiên bản bất biến, tải Excel');
  // BL100 (D77): split GT-01 into parts (prompt 6.11) + cash flow (FR22) on scenario "TEST căn cứ A", hand check:
  // part "TEST ván khuôn" = line 1.3.1 (ván khuôn, code edited by hand) on basis A: 180,000 × 0.9 × 300 = 48,600,000 instead of AWARD 51,000,000 → C.1.5 498,600,000, D 4,230,000 (0.67%)
  // cash flow 2 periods, AB 50/50 paid 1 period late, NTP 50/50 paid 1 period late, CC1 own 124,420,000 in T1 (C 623,020,000 − NTP 498,600,000)
  // cumulative: −124,420,000 / −60,095,000 / 4,230,000 → peak funding 124,420,000 in 2027-01
  await page.selectOption('#pk-sel',{label:'TEST căn cứ A'});await smsg(/Đã chọn kịch bản/);
  const g1=await page.evaluate(()=>project.packages.find(p=>p.code==='GT-01').id);
  await page.click(`[data-psplit="${g1}"]`);await page.click(`[data-padd="${g1}"]`);
  await fillB(`[data-pp="${g1}|0|name"]`,'TEST ván khuôn');await page.selectOption(`[data-pp="${g1}|0|mode"]`,'GOP');await page.selectOption(`[data-pp="${g1}|0|basis"]`,'A');
  const bb13=await page.evaluate(()=>{const p=project.packages.find(p=>p.code==='GT-01');return p.lines.find(l=>project.boq.find(r=>r.id===l.ab_line_id).source_code!=='1.1').bb_code;});
  await page.locator('.subpanel details summary').first().click();await page.selectOption(`[data-pln="${g1}|${bb13}"]`,{label:'TEST ván khuôn'});
  await page.click('#pk-save-s');await smsg(/Đã lưu kịch bản PAKD/);  // dòng tiền kế thừa từ Kịch bản 1 khi nhân bản
  const sp=await page.evaluate(async()=>{const v=await api('/api/projects/'+project.id+'/subcontract');const c=v.pakd.scenarios.find(x=>x.id===v.pakd.current);
   return {name:c.name,c15:c.result.rows.find(r=>r.code==='C.1.5').value,D:c.result.totals.D,m:c.result.rows.find(r=>r.code==='D').margin_pct,parts:c.result.packages.find(p=>p.code==='GT-01').parts.map(x=>[x.name,x.lines,x.cost]),
     cum:c.cashflow.periods.map(r=>r.cum),peak:[c.cashflow.totals.peak_funding,c.cashflow.totals.peak_period],fin:c.cashflow.totals.financing,cfc:c.cashflow.complete,q:c.questions};});
  assert.deepEqual([sp.name,sp.c15,sp.D,sp.m],['TEST căn cứ A','498600000','4230000','0.67']);assert.deepEqual(sp.q,[]);
  assert.deepEqual(sp.parts,[['Phần chung',1,'127500000'],['TEST ván khuôn',1,'48600000']]);
  assert.deepEqual([sp.cum,sp.peak,sp.fin,sp.cfc],[['-124420000','-60095000','4230000'],['124420000','2027-01'],null,true]);
  const body=await page.locator('#sv-body').innerText();assert.match(body,/TEST ván khuôn/);assert.match(body,/Nhu cầu vốn đỉnh/);assert.match(body,/chưa có lãi suất/);
  await page.screenshot({path:f('pakd-parts-cashflow.png'),fullPage:true});
  steps.push('PAKD chia phần GT-01 theo dòng (căn cứ A) + dòng tiền 2 kỳ: LN gộp 4.230.000 (0,67%), vốn đỉnh 124.420.000 khớp tính tay');
  {const r=await page.request.get(base.replace(/\/$/,'')+`/api/projects/${await page.evaluate(()=>project.id)}/procurement-pack.zip`);const z=(await r.body()).toString('latin1');
   assert.ok(z.includes('PAKD/PAKD_BM01_DANG_LAP_')&&z.includes('PAKD/PAKD_BM01_CHOT_TEST_PAKD'),'PAKD Excel in the procurement ZIP');steps.push('ZIP Chào thầu có Excel PAKD đang lập + phiên bản chốt');}
  // E18 (D78) hồ sơ hợp đồng BB′ for GT-02 (TEST ONLY): 15 FR29 headings + form + back-to-back + authority → review → READY (snapshot
  // 21,500,000 × 15 = 322,500,000) → signed evidence → award API refuses to change the signed package → change request → AB acceptance
  await page.click('[data-svtab="contracts"]');await page.locator('#ct-by').waitFor();
  await page.fill('#ct-by','TEST QS');const g2=await page.evaluate(()=>project.packages.find(p=>p.code==='GT-02').id);
  await page.selectOption('#ct-pkg',g2);await page.click('#ct-new');await smsg(/Đã lập hồ sơ hợp đồng/);await page.fill('#ct-by','TEST QS');
  const keys=await page.evaluate(()=>[...document.querySelectorAll('[data-ctt$="|text"]')].map(e=>e.dataset.ctt.split('|')[0]));assert.equal(keys.length,15);
  for(const k of keys){await fillB(`[data-ctt="${k}|text"]`,'TEST nội dung '+k);await fillB(`[data-ctt="${k}|ref"]`,'TEST căn cứ');}
  await page.fill('#ct-form-ref','TEST mẫu nội bộ (OQ07 chưa chốt)');await page.setInputFiles('#ct-form',{name:'TEST_ONLY_form_HD_NTP.pdf',mimeType:'application/pdf',buffer:Buffer.from('%PDF TEST ONLY form')});await smsg(/Đã cố định mẫu hợp đồng/);
  await page.click('#ct-b2b-add');await fillB('[data-ctb="0|clause"]','TEST Điều 8 bảo hành');await fillB('[data-ctb="0|ab_ref"]','HĐ AB Đ8');await page.selectOption('[data-ctb="0|decision"]','APPLY');await fillB('[data-ctb="0|rationale"]','TEST back-to-back 24 tháng');
  await page.fill('#ct-by','TEST QS');await fillB('#ct-auth-name','TEST Giám đốc');await fillB('#ct-auth-ref','TEST UQ-01');
  await page.click('#ct-submit');await smsg(/Đã chuyển xem xét/);await page.fill('#ct-by','TEST QS');
  await page.click('#ct-ready');await smsg(/Sẵn sàng trình ký/);await page.fill('#ct-by','TEST QS');
  await page.setInputFiles('#sg-file',{name:'TEST_ONLY_HD_ky.pdf',mimeType:'application/pdf',buffer:Buffer.from('%PDF TEST ONLY signed')});
  for(const [id,v] of [['#sg-p1','TEST CC1'],['#sg-p2','TEST NTP Thép B'],['#sg-ref','TEST-HĐ-GT02'],['#sg-date','2026-10-21'],['#sg-ver','TEST đối chiếu bản gốc']])await page.fill(id,v);
  await page.click('#sg-go');await smsg(/Đã ghi bằng chứng ký/);
  const ct=await page.evaluate(async()=>{const v=await api('/api/projects/'+project.id+'/subcontract');const c=v.contracts.contracts.find(x=>x.package_code==='GT-02');return {st:c.status,total:c.snapshot.total,sha:c.signed.sha256,form:c.form.sha256,rev:v.revision};});
  assert.deepEqual([ct.st,ct.total,ct.sha.length,ct.form.length],['SIGNED_EVIDENCE_RECORDED','322500000',64,64]);
  {const r=await page.request.post(base.replace(/\/$/,'')+`/api/projects/${await page.evaluate(()=>project.id)}/award`,{headers:{'X-CC1-Session':await page.evaluate(()=>boot.token),'Content-Type':'application/json'},data:{revision:ct.rev,package_id:g2,vendor:'TEST NTP Thép B',prices:{'GT-02.1':'1'}}});
   assert.equal(r.status(),400,'signed package locked against award changes');}
  await page.fill('#ct-by','TEST QS');await page.selectOption('#ch-src','NTP');await page.fill('#ch-title','TEST NTP đề nghị bù trượt giá thép');await page.fill('#ch-ref','TEST CV NTP-01');await page.fill('#ch-ntp','5000000');
  await page.click('#ch-add');await smsg(/Đã lập yêu cầu thay đổi/);
  const chid=await page.evaluate(async()=>{const v=await api('/api/projects/'+project.id+'/subcontract');return v.contracts.changes[0].id;});
  await page.fill('#ct-by','TEST QS');await page.selectOption(`[data-chs="${chid}|ntp_status"]`,'AGREED');await smsg(/Đã cập nhật trạng thái thay đổi/);
  assert.match(await page.locator('#sv-body').innerText(),/Chi phí NTP chưa có nguồn thu\s*5\.000\.000/);
  await page.fill('#ct-by','TEST QS');await page.selectOption('#fc-kind','AB_ACCEPTED');await page.fill('#fc-per','2026-10');await page.selectOption('#fc-basis','CUMULATIVE');await page.fill('#fc-val','7');await page.fill('#fc-ev','TEST BB nghiệm thu CĐT');
  await page.click('#fc-add');await smsg(/Đã ghi số liệu/);
  const tr=await page.evaluate(async()=>{const v=await api('/api/projects/'+project.id+'/subcontract');return v.contracts.trace.ab.filter(a=>a.ab_accepted!=null).map(a=>a.ab_accepted);});
  assert.equal(tr.length,1);
  await page.screenshot({path:f('contract-bb-prime.png'),fullPage:true});
  steps.push('Hợp đồng BB′ GT-02: 15 mục + form + back-to-back + thẩm quyền → trình ký 322.500.000 → ghi bằng chứng ký; API giá giao bị chặn (400); thay đổi NTP chưa có nguồn thu 5.000.000; CĐT nghiệm thu ghi riêng');
  const pid=await page.evaluate(()=>project.id);
  for(const u of [`/api/projects/${pid}/procurement-pack.zip`,`/api/projects/${pid}/tender-pack.zip`,`/api/projects/${pid}/bb/GT-01.xlsx`]){const r=await page.request.get(base.replace(/\/$/,'')+u);assert.equal(r.status(),200,u);}
  steps.push('Tải BOQ BB + ZIP Đấu thầu/Chào thầu');
  await page.reload();await page.waitForFunction(()=>typeof boot==='object'&&!!boot.token);await page.evaluate(id=>openProject(id),pid);await page.waitForFunction(()=>!!project&&project.id);
  const back=await page.evaluate(()=>({b11:project.boq.find(r=>r.source_code==='1.1'),b14:project.boq.find(r=>r.source_code==='1.4'),price:project.prices.find(p=>p.resource_code==='CC1-VL-BT25').unit_price,coef:project.resources.find(r=>r.id==='R5').coefficient,
    award:project.packages.find(p=>p.code==='GT-01').award,pm:project.context.pm_model,total:project._calculation&&project._calculation.total}));
  assert.deepEqual([back.b11.description,back.b11.quantity,back.b11.unit_price,back.b14.description,back.price,back.coef,back.pm],['Bê tông móng B25 đá 1x2 (sửa tay)','125','1850000','Bê tông lót móng B10 (dòng thêm tay)','1250000','11','PMBOK6']);
  assert.deepEqual(Object.values(back.award.prices).map(Number).sort((a,b)=>a-b),[170000,1700000]);steps.push('Tải lại: mọi giá trị sửa tay còn nguyên');
  await page.screenshot({path:f('full-chain-end.png'),fullPage:false});
  assert.deepEqual(errors,[]);fs.writeFileSync(f('browser-full-chain.json'),JSON.stringify({status:'PASS',steps,total:calc.total},null,1));console.log('PASS\n - '+steps.join('\n - '));
 }catch(e){try{await page.screenshot({path:f('full-chain-FAIL.png'),fullPage:true});}catch(_){}fs.writeFileSync(f('browser-full-chain.json'),JSON.stringify({status:'FAIL',steps,errors,error:String(e.stack||e)},null,1));console.error('FAIL after:\n - '+steps.join('\n - ')+'\n',e,errors);process.exitCode=1;}
 finally{await browser.close();}
})();
