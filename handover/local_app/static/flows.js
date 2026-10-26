'use strict';
/* E21 (D85) · Một giao diện cho dự toán (8765) và bóc khối lượng (CERP-QTO 8770):
   - "Luồng làm việc": 5 luồng của một hồ sơ, trạng thái và việc kế tiếp, dẫn vào đúng màn hình.
   - "Bản vẽ & bóc khối lượng": CERP-QTO nhúng trong khung này (token do 8765 gắn, dự án theo hồ sơ) + thẩm định khối lượng
     bản vẽ ↔ BOQ của Tư vấn (nhập takeoff đã duyệt → QS gán vào dòng AB → lệch %). BOQ nguồn không bị sửa.
   Dùng api/esc/showDialog/project/stages/message/openProject/SV/navRecord của app.js và subcontract.js. */
(()=>{
const q=s=>document.querySelector(s),qa=s=>[...document.querySelectorAll(s)];
const num=v=>v==null||v===''?'—':Number(v).toLocaleString('vi-VN',{maximumFractionDigits:4});
let view=null,qtab='draw',qst=null,review=null,thr='1',busy=false;
const CODE={STATE_DRAFT:1};
function hideAll(){['#workspace','#subcontract-view','#flows-view','#qto-view'].forEach(s=>{const e=q(s);if(e)e.hidden=true;});q('#welcome').hidden=true;}
function stageDone(i){return !!(stages&&stages[i]&&stages[i].confirmed);}
function count(a){return (a||[]).length;}
/* ---------- Luồng làm việc: Quy trình PAKD Thi công v1.0 (11/10/2026) — 7 pha, 18 bước; mỗi bước nối vào màn hình của app ---------- */
const chip=(ok,t)=>`<span class="${ok==null?'chip-wait':ok?'chip-ok':'chip-block'}">${esc(t)}</span>`;
function facts(){const P=project,boq=count(P.boq.filter(r=>r.kind==='MEASURED')),ctx=P.context||{},qt=(P.takeoffs||[]).filter(t=>String(t.id).startsWith('qto:')),conf=qt.filter(t=>(t.assign||{}).status==='CONFIRMED').length,
 pk=P.packages||[],aw=pk.filter(p=>p.award).length,ct=P.contracts||[],signed=ct.filter(c=>['SIGNED_EVIDENCE_RECORDED','AMENDED','CLOSED'].includes(c.status)).length,pakd=P.pakd||{},
 scen=count(pakd.scenarios)||(pk.length?1:0),frozen=count(pakd.versions),cf=(pakd.scenarios||[]).some(s=>s.cashflow),rules=((P.adjustments||{}).rules||[]),
 wbs=count(P.wbs),lbs=(P.wbs||[]).filter(w=>w.lbs).length,ca=(P.wbs||[]).filter(w=>w.ca||w.cam).length,items=count(P.mapping),apps=count(P.applications),prices=count(P.prices),
 facts=(P.facts||[]).length,prog=(P.progress||[]).length,total=P._calculation&&P._calculation.total,firstOpen=[2,3,4,5,6,7].find(i=>!stageDone(i));
 const er=(P.erp_reference||{}),bb=er.bb_contracts||[],gt=er.pakd_gt||null,tt=er.pakd_tt||null,bbDone=pk.filter(p=>p.erp_ref).length;
 return {P,boq,ctx,qt,conf,pk,aw,ct,signed,scen,frozen,cf,rules,wbs,lbs,ca,items,apps,prices,facts,prog,total,firstOpen,qp:ctx.qto_project,scope:!!(ctx.scope_in||ctx.scope_out||ctx.assumptions_log),erp:{has:!!(bb.length||gt||tt),bb:bb.length,bbDone,gt,tt,exported:er.exported}};}
/* Mỗi bước: tên theo quy trình, đầu ra chính, owner/gate theo quy trình, mức app đáp ứng (app: ĐẠT / MỘT PHẦN / CHƯA CÓ), trạng thái sống, nút */
function steps18(F){const S=[
 {ph:1,n:1,name:'Tiếp nhận hợp đồng AB và hồ sơ gốc',out:'Contract Intake; BOQ AB chuẩn hóa',owner:'Commercial/QS/Pháp chế/PMO',app:'part',
  chips:[chip(stageDone(0),stageDone(0)?'Hồ sơ & hợp đồng: đã xác nhận':'Hồ sơ & hợp đồng: chưa'),chip(stageDone(1),F.boq?`BOQ AB: ${F.boq} dòng${stageDone(1)?' · đã xác nhận':''}`:'BOQ AB: chưa nạp'),chip(F.qp?true:null,F.qp?`Dự án CERP-QTO: ${F.qp}`:'Bản vẽ: chưa nối dự án CERP-QTO')],
  gap:'Document checklist, Contract Risk Note: chưa có trong app',acts:[['step:0','Hồ sơ & hợp đồng CĐT'],['step:1','Nạp BOQ AB','primary'],['qto:draw','Bản vẽ (CERP-QTO)']]},
 {ph:1,n:2,name:'Bóc doanh thu AB và Revenue Baseline',out:'Revenue Baseline; mốc thanh toán',owner:'QS/Commercial/Finance',app:'part',
  chips:[chip(F.boq&&stageDone(1)?true:null,'Doanh thu B = Σ KL × đơn giá AB (PAKD)'),chip(F.cf?true:null,F.cf?'Điều khoản thanh toán: đã nhập ở dòng tiền':'Điều khoản thanh toán: nhập ở dòng tiền PAKD')],
  gap:'Sổ mốc thanh toán và trạng thái variation: chưa có',acts:[['sv:pakd','Doanh thu & dòng tiền (PAKD)']]},
 {ph:1,n:'2b',name:'Thẩm định khối lượng bản vẽ ↔ BOQ Tư vấn',out:'Bảng lệch KL bản vẽ / BOQ AB',owner:'QS/BIM',app:'ok',extra:true,
  chips:[chip(F.qt.length?true:null,F.qt.length?`${F.qt.length} khối lượng đã nhập`:'Chưa nhập khối lượng'),chip(F.conf?true:null,`${F.conf} đã gán vào dòng AB`)],
  gap:'Bước bổ sung theo yêu cầu người dùng (không có trong quy trình v1.0)',acts:[['qto:review','Thẩm định khối lượng','primary']]},
 {ph:2,n:3,name:'Scope Register và ranh giới phạm vi',out:'Scope In/Out; Assumption & Exclusion Log',owner:'PMO/QS/BQLDA',app:'part',
  chips:[chip(F.scope?true:null,F.scope?'Phạm vi vào/ra cấp hồ sơ: đã khai':'Phạm vi vào/ra cấp hồ sơ: chưa khai (bước 1)'),chip(F.wbs?true:null,`Phạm vi theo phần tử WBS: ${F.wbs}`)],
  gap:'',acts:[['step:0','Khai phạm vi (Hồ sơ)','primary']]},
 {ph:2,n:4,name:'Lập WBS thi công',out:'WBS Dictionary; Work Package',owner:'PMO/Planner/QS/BQLDA',app:'ok',
  chips:[chip(stageDone(2),`${F.wbs} phần tử WBS · ${F.items} hạng mục chuẩn hóa${stageDone(2)?' · đã xác nhận':''}`)],gap:'',acts:[['step:2','WBS và các bộ mã','primary']]},
 {ph:2,n:5,name:'Gắn LBS vị trí thi công',out:'LBS Register; WBS–LBS',owner:'BIM/CDE/BQLDA/Planner',app:'ok',
  chips:[chip(F.wbs?F.lbs===F.wbs:null,`${F.lbs}/${F.wbs} phần tử có LBS`)],gap:'',acts:[['step:2','WBS · LBS']]},
 {ph:2,n:6,name:'Gắn OBS, RACI và owner kiểm soát',out:'OBS Register; RACI; Approval Matrix',owner:'PMO/BQLDA/Finance/IT',app:'gap',
  chips:[chip(F.ctx.owner&&F.ctx.reviewer?true:null,'Người lập / người kiểm: '+(F.ctx.owner&&F.ctx.reviewer?'đã khai':'chưa đủ')),chip(F.ca?true:null,`${F.ca} phần tử có CA/CAM`)],
  gap:'OBS/RACI/DOA: chưa có (OQ02 PRD); app chỉ giữ owner, reviewer, CA, CAM',acts:[['step:0','Người lập / kiểm'],['step:2','CA / CAM theo WBS']]},
 {ph:3,n:7,name:'Tạo CBS Cost Code',out:'CBS Dictionary; Finance Mapping',owner:'Finance/QS/IT Data',app:'part',
  chips:[chip(true,'CBS C10–C70 (tài liệu 09/10)'),chip(null,'C90 Dự phòng của quy trình: chưa có trong bộ mã — chờ quyết định')],gap:'C50–C57 tương thích với C50 của app; C90 cần Từ điển mã quyết định',acts:[['step:6','CBS & khoản bổ sung'],['dict','Từ điển mã']]},
 {ph:3,n:8,name:'Cost Center và Budget Item (chi phí gián tiếp)',out:'Cost Center / Budget Item Register',owner:'Finance/PMO/BQLDA',app:'gap',
  chips:[chip(null,'Chi phí gián tiếp hiện nhập theo khoản ở PAKD C.2, chưa theo cost center / tháng')],gap:'Cost Center, Budget Item, period: chưa có',acts:[['sv:pakd','Khoản C.2 trong PAKD']]},
 {ph:3,n:9,name:'Mapping BOQ AB → WBS, LBS, OBS, CBS',out:'Crosswalk; Allocation Rule (Σ = 100%)',owner:'QS/Finance/PMO/IT Data',app:'part',
  chips:[chip(stageDone(2),`${F.items} hạng mục gán WBS/LBS (trọng số phân bổ)`),chip(null,'OBS: chưa; CBS: theo dòng hao phí')],gap:'',acts:[['step:2','Gán hạng mục → WBS','primary']]},
 {ph:4,n:10,name:'Lập BOQ Tổng thầu (Internal BOQ)',out:'Internal BOQ; Method-linked BOQ',owner:'QS/BQLDA/Planner',app:'ok',
  chips:[chip(stageDone(3),`${F.apps} ghép định mức · quy cách & biện pháp${stageDone(3)?' · đã xác nhận':''}`)],gap:'',acts:[['step:3','Chọn định mức & biện pháp','primary']]},
 {ph:4,n:11,name:'Nạp định mức và khung giá',out:'Norm / Price / Source Register',owner:'QS/Procurement/Finance',app:'ok',
  chips:[chip(stageDone(4),`Hao phí${stageDone(4)?': đã xác nhận':': chưa'}`),chip(stageDone(5),`${F.prices} dòng giá${stageDone(5)?' · đã xác nhận':''}`)],gap:'',acts:[['step:4','Hao phí'],['step:5','Đơn giá CC1','primary']]},
 {ph:4,n:12,name:'Tính Direct Cost Budget',out:'Direct Cost theo WBS/CBS',owner:'QS/Finance/PMO',app:'part',
  chips:[F.total!=null?chip(true,`Tổng dự toán ${num(F.total)}`):chip(null,'Chưa tính được tổng'),chip(null,'Phân bổ theo tháng: chưa')],gap:'Phân kỳ tháng chưa có',acts:[['step:6','CBS & tổng dự toán','primary']]},
 {ph:4,n:13,name:'Tính Indirect Cost Budget',out:'Indirect Budget; Monthly Overhead Curve',owner:'Finance/PMO/BQLDA',app:'gap',
  chips:[chip(F.rules.length?true:null,`${F.rules.length} khoản bổ sung (bước 7)`)],gap:'Site overhead theo cost center / tháng: chưa có',acts:[['step:6','Khoản bổ sung'],['sv:pakd','C.2 trong PAKD']]},
 {ph:4,n:14,name:'Contingency và Risk Budget',out:'Contingency Budget; Risk Register',owner:'PMO/QS/Finance',app:'gap',
  chips:[chip(F.rules.some(r=>r.nature==='CONTINGENCY')?true:null,'Dự phòng: khoản bổ sung / PAKD C.1.10'),chip(null,'Risk Register: chưa có')],gap:'Risk Register, EMV: chưa có (FR19 PRD)',acts:[['step:6','Khoản dự phòng'],['sv:pakd','C.1.10 trong PAKD']]},
 {ph:5,n:15,name:'BOQ giao thầu phụ (BB′) và giá giao thầu',out:'BOQ BB′; gói thầu; giá giao; đề xuất',owner:'Procurement/QS/Finance/PMO',app:'ok',
  chips:[chip(F.pk.length?true:false,`${F.pk.length} gói`),chip(F.aw?true:null,`${F.aw} đề xuất giao thầu`),chip(F.signed?true:null,`${F.ct.length} hồ sơ HĐ · ${F.signed} đã ký`),...(F.erp.bb?[chip(F.erp.bbDone?true:null,`ERP: ${F.erp.bb} hợp đồng BB′ · ${F.erp.bbDone} đã tạo gói`)]:[])],
  gap:'Target / ceiling price: dùng căn cứ A/B/C; chưa có trường riêng',acts:[['sv:packages','Gói thầu'],['sv:award','Giá giao & đề xuất'],['sv:contracts','Hợp đồng BB′','primary'],...(F.erp.bb&&F.erp.bbDone<F.erp.bb?[[stageDone(2)?'erp:packages':'step:2',stageDone(2)?`Tạo gói từ BB′ ERP (${F.erp.bb-F.erp.bbDone})`:`BB′ ERP: ${F.erp.bb} hợp đồng — xác nhận WBS trước`]]:[])]},
 {ph:6,n:16,name:'Milestone tháng: tiến độ, sản lượng, giá trị',out:'Monthly Milestone Baseline; PV; Cashflow Plan',owner:'Planner/PMO/QS/Finance',app:'part',
  chips:[chip(F.cf?true:null,F.cf?'Dòng tiền theo kỳ: đã lập':'Dòng tiền theo kỳ: chưa lập')],gap:'PV/EV theo WBS-tháng: chưa có; app mới có % thu/chi theo kỳ',acts:[['sv:pakd','Dòng tiền (PAKD)','primary']]},
 {ph:6,n:17,name:'Tổng hợp PAKD Thi công',out:'PAKD (BM01 + cấu trúc A–I); Margin; Cashflow',owner:'PMO/QS/Finance/Sponsor',app:'ok',
  chips:[chip(F.scen?true:null,`${F.scen} kịch bản`),chip(F.frozen?true:null,`${F.frozen} phiên bản đã chốt`),...(F.erp.gt?[chip(null,`ERP PAKD_GT: ${(F.erp.gt.sections||[]).length} khoản gián tiếp`)]:[]),...(F.erp.tt?[chip(null,`ERP PAKD_TT chi phí trực tiếp: ${num(F.erp.tt.total)} (đối chiếu)`)]:[])],gap:'',acts:[['sv:pakd','PAKD · BM01 / A–I','primary'],...(F.erp.gt?[['erp:pakd','Nhập gián tiếp từ PAKD_GT ERP']]:[])]},
 {ph:7,n:18,name:'Phê duyệt baseline và theo dõi hiệu quả',out:'Approved Baseline; Monthly Control; EAC',owner:'Sponsor/PMO/Finance/QS/IT Data',app:'part',
  chips:[chip(F.frozen?true:null,F.frozen?'Baseline cục bộ: đã chốt (chưa phải phê duyệt công ty)':'Chưa chốt baseline'),chip(F.facts||F.prog?true:null,`${F.prog} ghi nhận KL · ${F.facts} số liệu nghiệm thu / thanh toán`)],
  gap:'EAC, EVM, Monthly Control Report: chưa có (FR23 P1)',acts:[['sv:progress','Hoàn thành theo WBS'],['sv:contracts','Nghiệm thu / thanh toán']]}];
 return S;}
const PHASES={1:'Pha 1 · Tiếp nhận',2:'Pha 2 · Phân rã quản trị',3:'Pha 3 · Cấu trúc chi phí',4:'Pha 4 · Tính giá thành',5:'Pha 5 · Giao thầu phụ',6:'Pha 6 · PAKD Thi công',7:'Pha 7 · Theo dõi hiệu quả'};
const APPLBL={ok:['chip-ok','App: đạt'],part:['chip-wait','App: một phần'],gap:['chip-block','App: chưa có']};
const QUICK=[['step:1','1 · Nạp BOQ AB & bản vẽ'],['qto:review','2 · Thẩm định khối lượng'],['step:2','3 · Lập dự toán'],['sv:packages','4 · Chia thầu & gói BB′'],['sv:pakd','5 · PAKD']];
function drawFlows(){if(!project)return;hideAll();const v=q('#flows-view');v.hidden=false;const F=facts(),S=steps18(F),byPh={};S.forEach(s=>(byPh[s.ph]=byPh[s.ph]||[]).push(s));
 const next=S.find(s=>s.app!=='gap'&&s.chips.some(c=>c.includes('chip-block')))||S.find(s=>s.app!=='gap'&&s.chips.some(c=>c.includes('chip-wait')));
 v.innerHTML=`<div class="stage-heading"><div><span class="eyebrow">${esc(project.name)} · Quy trình PAKD Thi công v1.0</span><h2>Luồng làm việc</h2></div><span class="badge">PB ${project.revision}</span></div>
 <p class="help">Theo "Quy trình từ hợp đồng AB đến PAKD Thi công" (7 pha, 18 bước, 11/10/2026): bước sau chỉ dùng dữ liệu bước trước đã có phiên bản, người phụ trách và xác nhận. Mỗi bước nối vào màn hình tương ứng; bước app chưa có được ghi rõ, không làm thay.</p>
 <div class="toolbar quick-flows"><span class="eyebrow">Vào nhanh</span>${QUICK.map(([a,l])=>`<button data-fact="${a}" class="quiet">${esc(l)}</button>`).join('')}</div>
 ${next?`<div class="note"><b>Việc kế tiếp theo quy trình:</b> Bước ${esc(next.n)} — ${esc(next.name)}.</div>`:''}
 ${Object.keys(byPh).map(ph=>`<h3 class="phase-h">${esc(PHASES[ph])}</h3><div class="flow-grid">${byPh[ph].map(s=>`<article class="flow-card ${s.app}" data-flow="b${s.n}"><div class="flow-n">${esc(s.n)}</div><h3>${esc(s.name)}${s.extra?' <small>(bổ sung)</small>':''}</h3><p><b>Đầu ra:</b> ${esc(s.out)} · <b>Owner/gate:</b> ${esc(s.owner)}</p><div class="chips"><span class="${APPLBL[s.app][0]}">${APPLBL[s.app][1]}</span>${s.chips.join('')}</div>${s.gap?`<p class="flow-gap">${esc(s.gap)}</p>`:''}<div class="toolbar">${s.acts.map(([a,l,cls])=>`<button data-fact="${a}" class="${cls||'quiet'}">${esc(l)}</button>`).join('')}</div></article>`).join('')}</div>`).join('')}`;
 qa('[data-fact]').forEach(b=>b.onclick=()=>go(b.dataset.fact));view='flows';if(window.navRecord)navRecord();}
async function go(a){const [k,x]=a.split(':');
 if(k==='step'){if(!stages[+x]||!stages[+x].available){message('Bước này chưa mở — hoàn tất bước trước.',true);return;}step=+x;selected=-1;page=0;search='';errorOnly=false;view=null;render();return;}
 if(k==='sv'){view=null;await SV.open(x);return;}
 if(k==='dict'){const b=q('#open-dictionaries');if(b)b.click();return;}
 if(k==='erp'){await erpImport(x);return;}
 if(k==='qto'){await openQto(x);}}
/* ---------- D87 · nhập từ khối tham chiếu ERP (BB′ → gói thầu; PAKD_GT → C.2) qua đúng cổng của app ---------- */
async function erpImport(what){if(!project)return;if(dirty)await save(false);
 try{const d=await api('/api/projects/'+project.id+'/'+(what==='packages'?'erp-packages':'erp-pakd'),{revision:project.revision});
  project.revision=d.revision;for(const k of ['packages','quotes','progress','drawings','takeoffs'])project[k]=d.project[k];project.pakd=d.project.pakd;project.context=d.project.context;q('#revision').textContent='PB '+project.revision+' · TRÊN MÁY';
  const r=d.result;if(what==='packages'){const sk=r.imported.reduce((a,x)=>a+x.skipped.length,0);message(`Đã tạo ${r.imported.length} gói từ hợp đồng BB′ ERP (${r.imported.map(x=>x.code+' ← '+x.ref).join('; ')}); ${sk} dòng không ghép được (xem phần Việc còn mở của gói thầu)${r.skipped_contracts.length?`; ${r.skipped_contracts.length} hợp đồng không ghép được dòng nào`:''}.`);await SV.open('packages');}
  else{message(`Đã thêm ${r.added} khoản C.2 từ PAKD_GT ERP vào kịch bản "${r.scenario}" (kèm căn cứ). PAKD_TT ERP tổng ${r.tt_total||'—'} chỉ để đối chiếu, không nhập.`);await SV.open('pakd');}
 }catch(e){message(e.message,true);}}
window.erpImport=erpImport;
/* ---------- Bản vẽ & bóc khối lượng (CERP-QTO nhúng + thẩm định) ---------- */
async function status(){try{qst=await api('/api/qto/status');}catch(e){qst={service:'DOWN',token_set:false,me:null,error:e.message};}return qst;}
function theme(){const r=document.documentElement;return r.dataset.theme||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');}
function iframeSrc(t){const p=(project.context||{}).qto_project||'';return `/qto/ui/?embedded=1&project=${encodeURIComponent(p)}&theme=${theme()}&view=${t||'drawings'}`;}
async function openQto(tab){if(!project){message('Mở một hồ sơ trước.',true);return;}if(dirty)await save(false);qtab=tab||qtab;await status();if(qtab==='review')await loadReview();drawQto();}
async function loadReview(){try{const d=await api('/api/projects/'+project.id+'/qto-review',{threshold_pct:thr});review=d.review;}catch(e){review=null;message(e.message,true);}}
function drawQto(){hideAll();const v=q('#qto-view');v.hidden=false;const ctx=project.context||{},qp=ctx.qto_project||'',me=qst&&qst.me,ok=qst&&qst.service==='UP'&&qst.token_set&&me,
 projs=me?(me.projects.includes('*')?[]:me.projects):[];
 const head=`<div class="stage-heading"><div><span class="eyebrow">${esc(project.name)} · CERP-QTO</span><h2>Bản vẽ &amp; bóc khối lượng</h2></div><span class="badge ${ok?'':'badge-warn'}">${qst?qst.service==='UP'?(qst.token_set?(me?'Đã nối · '+esc(me.user):'Token không hợp lệ'):'Chưa có token'):'Service chưa chạy':'…'}</span></div>
 <div class="toolbar"><label>Dự án CERP-QTO ${projs.length?`<select id="qp-sel">${['',...projs].map(p=>`<option value="${esc(p)}" ${p===qp?'selected':''}>${p||'— chọn —'}</option>`).join('')}${qp&&!projs.includes(qp)?`<option value="${esc(qp)}" selected>${esc(qp)}</option>`:''}</select>`:`<input id="qp-sel" value="${esc(qp)}" placeholder="Mã dự án, vd ${esc(ctx.project_code||'DEMO')}" class="w-m">`}</label><button id="qp-link" class="quiet">Lưu dự án</button><span class="topbar-sep"></span><button id="qp-settings" class="quiet">Cài đặt bóc khối lượng</button>${qst&&qst.error?`<span class="error">${esc(qst.error)}</span>`:''}</div>
 <div class="tabs"><button class="tab ${qtab==='draw'?'current':''}" data-qtab="draw">Bản vẽ &amp; bóc khối lượng</button><button class="tab ${qtab==='review'?'current':''}" data-qtab="review">Thẩm định khối lượng ↔ BOQ Tư vấn</button></div>`;
 let body='';
 if(qtab==='draw'){body=!ok?`<div class="note">${esc(!qst||qst.service!=='UP'?'Service CERP-QTO (cổng 8770) chưa chạy. Khởi động bằng D:\\Code\\cerp-qto\\start-api.cmd và start-worker.cmd rồi tải lại.':'Chưa có token CERP-QTO hợp lệ. Bấm "Cài đặt bóc khối lượng" và dán token (tools\\copy-token.cmd). Token được lưu trên máy này, không hiện lại.')}</div>`
  :!qp?'<div class="note">Chọn dự án CERP-QTO cho hồ sơ này rồi bấm "Lưu dự án". Bản vẽ, rule profile và takeoff của CERP-QTO đều theo mã dự án đó.</div>'
  :`<iframe id="qto-frame" src="${iframeSrc('drawings')}" title="CERP-QTO · bóc khối lượng có truy vết" class="qto-frame"></iframe><p class="help">Khung trên là CERP-QTO chạy trong ứng dụng này (token do ứng dụng gắn). Mọi khối lượng là ứng viên cho tới khi QS duyệt; sau khi "Tổng hợp" ở thẻ Takeoff → BOQ, sang thẻ Thẩm định để nhập về hồ sơ.</p>`;}
 else{const R=review;body=`<div class="toolbar"><button id="qi-import" class="primary" ${ok&&qp?'':'disabled'}>Nhập takeoff đã duyệt từ CERP-QTO</button><label>Ngưỡng lệch % <input id="qi-thr" class="w-xs" value="${esc(thr)}" inputmode="decimal"></label><span class="help">Chỉ nhập khối lượng đã duyệt (approved / pushed), phiên bản mới nhất của mỗi hạng mục.</span></div>`;
  if(!R)body+='<p class="help">Chưa có dữ liệu thẩm định.</p>';
  else{const ab=project.boq.filter(r=>r.kind==='MEASURED');const opt=(sel)=>ab.map(r=>`<option value="${esc(r.id)}" ${r.id===sel?'selected':''}>${esc(r.source_code)} · ${esc((r.description||'').slice(0,60))} (${esc(r.uom)})</option>`).join('');
   body+=`<div class="metric-row m4"><div class="metric">Khối lượng từ bản vẽ<strong>${R.counts.candidates}</strong><small>${R.counts.confirmed} đã gán · ${R.counts.rejected} loại · ${R.counts.open} chờ</small></div><div class="metric">Dòng AB có đối chiếu<strong>${R.compare.length}</strong><small>${R.counts.no_takeoff} dòng chưa có khối lượng bản vẽ</small></div><div class="metric">Lệch quá ngưỡng${R.threshold_pct?' '+esc(R.threshold_pct)+'%':''}<strong>${R.counts.flagged}</strong><small>chỉ báo, không sửa BOQ</small></div></div>
   <h3>Khối lượng bóc từ bản vẽ → gán vào dòng BOQ AB</h3><div class="table-wrap"><table><thead><tr><th>Hạng mục (CERP-QTO)</th><th>WBS · định mức</th><th class="num">Khối lượng</th><th>ĐVT</th><th>Nguồn</th><th>Gán vào dòng AB</th><th></th></tr></thead><tbody>${R.candidates.map(t=>{const a=t.assign||{},s=t.source||{},sg=t.suggestion||{};
    return `<tr><td>${esc(t.text)}</td><td>${esc(s.wbs_code||'—')}${s.norm_code?' · '+esc(s.norm_code):''}</td><td class="num">${num(t.value)}</td><td>${esc(t.uom||'')}</td><td><small>v${esc(s.version)} · ${esc(s.measurements)} phép đo</small></td>
     <td>${a.status==='CONFIRMED'?`<span class="chip-ok">Đã gán</span> ${esc((project.boq.find(r=>r.id===a.ab_line_id)||{}).source_code||'')} ×${esc(a.factor)}${a.updated_from!=null?' <span class="chip-wait" title="Khối lượng đổi sau khi gán (từ v'+esc(a.updated_from)+')">đã đổi</span>':''}`:a.status==='REJECTED'?`<span class="chip-block">Loại</span> <small>${esc(a.reason||'')}</small>`:
      `<select data-qab="${esc(t.id)}"><option value="">— dòng AB —</option>${opt(sg.ab_line_id)}</select> <input data-qf="${esc(t.id)}" class="w-xs" value="1" inputmode="decimal" title="Hệ số quy đổi"> <input data-qr="${esc(t.id)}" placeholder="Căn cứ" value="${esc(sg.ab_line_id?sg.reason:'')}">${sg.reason&&!sg.ab_line_id?`<br><small>${esc(sg.reason)}</small>`:''}`}</td>
     <td>${a.status?`<button class="quiet" data-qclr="${esc(t.id)}">Gỡ</button>`:`<button data-qok="${esc(t.id)}" class="primary">Gán</button> <button class="quiet" data-qno="${esc(t.id)}">Loại</button>`}</td></tr>`;}).join('')||'<tr><td colspan="7">Chưa nhập khối lượng nào. Bấm "Nhập takeoff đã duyệt từ CERP-QTO".</td></tr>'}</tbody></table></div>
   <h3>Đối chiếu với BOQ của Tư vấn</h3><div class="table-wrap"><table><thead><tr><th>Mã WBS</th><th>Hạng mục (BOQ AB)</th><th>ĐVT</th><th class="num">KL BOQ Tư vấn</th><th class="num">KL bản vẽ</th><th class="num">Lệch %</th><th>Đánh giá</th></tr></thead><tbody>${R.compare.map(c=>`<tr><td>${esc(c.wbs_code)}</td><td>${esc(c.description)}</td><td>${esc(c.uom)}</td><td class="num">${num(c.boq_quantity)}</td><td class="num">${num(c.drawing_quantity)}</td><td class="num">${c.deviation_pct==null?'—':esc(c.deviation_pct)}</td><td>${c.flag==='FLAG'?'<span class="chip-block">Vượt ngưỡng</span>':c.flag==='OK'?'<span class="chip-ok">Trong ngưỡng</span>':''}</td></tr>`).join('')||'<tr><td colspan="7">Chưa có dòng AB nào được gán khối lượng bản vẽ.</td></tr>'}</tbody></table></div>
   ${R.no_takeoff.length?`<details class="editor"><summary>Dòng BOQ AB chưa có khối lượng bản vẽ (${R.no_takeoff.length})</summary><div class="table-wrap"><table><tbody>${R.no_takeoff.slice(0,300).map(r=>`<tr><td>${esc(r.wbs_code)}</td><td>${esc(r.description)}</td><td>${esc(r.uom)}</td><td class="num">${num(r.boq_quantity)}</td></tr>`).join('')}</tbody></table></div></details>`:''}`;}}
 v.innerHTML=head+body+'<div id="qto-msg" role="status" aria-live="polite"></div>';bindQto();view='qto';if(window.navRecord)navRecord();}
const say=(t,err)=>{const m=q('#qto-msg');if(m){m.textContent=t;m.className=err?'error':'';}};
function bindQto(){qa('[data-qtab]').forEach(b=>b.onclick=async()=>{qtab=b.dataset.qtab;if(qtab==='review')await loadReview();drawQto();});
 const b=(id,fn)=>{const el=q(id);if(el)el.onclick=fn;};
 b('#qp-link',async()=>{try{const d=await api('/api/projects/'+project.id+'/qto-project',{revision:project.revision,qto_project:q('#qp-sel').value.trim()});project.revision=d.project.revision;project.context=d.project.context;q('#revision').textContent='PB '+project.revision+' · TRÊN MÁY';drawQto();say('Đã lưu dự án CERP-QTO cho hồ sơ.');}catch(e){say(e.message,true);}});
 b('#qp-settings',settings);
 b('#qi-import',async()=>{if(busy)return;busy=true;const btn=q('#qi-import');btn.disabled=true;btn.textContent='Đang nhập…';
  try{thr=q('#qi-thr').value.trim();const d=await api('/api/projects/'+project.id+'/qto-import',{revision:project.revision,threshold_pct:thr});project.revision=d.project.revision;project.takeoffs=d.project.takeoffs;project.drawings=d.project.drawings;q('#revision').textContent='PB '+project.revision+' · TRÊN MÁY';review=d.review;drawQto();
   const r=d.result;say(`Đã nhập ${r.items} khối lượng đã duyệt: ${r.added} mới, ${r.updated} đổi phiên bản, ${r.unchanged} không đổi; ${r.suggested} gợi ý dòng AB cùng mã WBS và đơn vị.`);}
  catch(e){say(e.message,true);busy=false;drawQto();return;}busy=false;});
 const th=q('#qi-thr');if(th)th.onchange=async()=>{thr=th.value.trim();await loadReview();drawQto();};
 const assign=async(body,ok)=>{try{const d=await api('/api/projects/'+project.id+'/takeoff-assign',Object.assign({revision:project.revision},body));project.revision=d.revision;project.takeoffs=d.project.takeoffs;q('#revision').textContent='PB '+project.revision+' · TRÊN MÁY';await loadReview();drawQto();say(ok);}catch(e){say(e.message,true);}};
 qa('[data-qok]').forEach(x=>x.onclick=()=>{const id=x.dataset.qok,ab=q(`[data-qab="${id}"]`).value,f=q(`[data-qf="${id}"]`).value,r=q(`[data-qr="${id}"]`).value.trim();
  if(!ab)return say('Chọn dòng BOQ AB để gán.',true);if(!r)return say('Ghi căn cứ gán (cùng mã WBS, quy đổi đơn vị…).',true);assign({takeoff_id:id,status:'CONFIRMED',ab_line_id:ab,factor:f,factor_ref:r,by:(project.context||{}).owner||''},'Đã gán khối lượng vào dòng AB.');});
 qa('[data-qno]').forEach(x=>x.onclick=()=>{const why=prompt('Lý do loại khối lượng này?');if(why)assign({takeoff_id:x.dataset.qno,status:'REJECTED',reason:why},'Đã loại khối lượng.');});
 qa('[data-qclr]').forEach(x=>x.onclick=()=>assign({takeoff_id:x.dataset.qclr,status:'CLEAR'},'Đã gỡ quyết định.'));}
function settings(){const s=qst||{};showDialog(`<h2>Cài đặt bóc khối lượng (CERP-QTO)</h2><p class="help">Service CERP-QTO chạy riêng trên máy này; ứng dụng dự toán gắn token thay bạn. Token lưu ở runtime/qto_settings.json, không hiện lại và không gửi đi đâu khác.</p>
 <div class="form-grid"><label>Địa chỉ service (loopback)<input id="qs-url" value="${esc(s.url||'http://127.0.0.1:8770')}"></label><label>Token CERP-QTO ${s.token_set?'<small>(đã có — để trống nếu giữ nguyên)</small>':''}<input id="qs-tok" type="password" autocomplete="off" placeholder="Dán token từ tools\\copy-token.cmd"></label></div>
 <p class="help">Trạng thái: ${esc(s.service==='UP'?'service đang chạy':'service chưa chạy')}${s.me?` · đăng nhập ${esc(s.me.user)} · quyền ${esc(s.me.roles.join(', '))} · dự án ${esc(s.me.projects.includes('*')?'tất cả':s.me.projects.join(', '))}`:''}${s.error?` · <span class="error">${esc(s.error)}</span>`:''}</p>
 <p id="qs-err" class="error" role="alert"></p><div class="toolbar"><button id="qs-ok" class="primary">Lưu và kiểm tra</button><button id="qs-cancel" class="quiet">Đóng</button></div>`);
 q('#qs-cancel').onclick=()=>q('#dialog').close();q('#qs-ok').onclick=async()=>{try{const body={url:q('#qs-url').value.trim()};const t=q('#qs-tok').value.trim();if(t)body.token=t;qst=await api('/api/qto/settings',body);
  if(qst.error){q('#qs-err').textContent=qst.error;return;}q('#dialog').close();drawQto();say(qst.me?`Đã nối CERP-QTO: ${qst.me.user}.`:'Đã lưu địa chỉ service.');}catch(e){q('#qs-err').textContent=e.message;}};}
/* ---------- nối với vỏ app: điều hướng, lịch sử, theme ---------- */
window.FL={open:drawFlows,openQto,close:()=>{view=null;},isOpen:()=>!!view,state:()=>view?{v:view,pid:project&&project.id,tab:view==='qto'?qtab:null}:null,
 restore:async s=>{if(s.v==='flows')drawFlows();else await openQto(s.tab||'draw');}};
window.addEventListener('DOMContentLoaded',()=>{const f=q('#open-flows'),g=q('#open-qto');if(f)f.onclick=()=>project?drawFlows():message('Mở một hồ sơ trước.',true);if(g)g.onclick=()=>project?openQto('draw'):message('Mở một hồ sơ trước.',true);
 const tt=q('#theme-toggle');if(tt)tt.addEventListener('click',()=>{const fr=q('#qto-frame');if(fr)setTimeout(()=>{fr.src=iframeSrc('drawings');},50);});});
})();
