"""E23 (D87): ERP reference data attached to a project (`s['erp_reference']`) and the two imports that turn it into app objects
through the normal gates.

The demo builder (runs_brian/erp_demo_20261022/build_erp_demo.py) stores, per project, what the ERP export holds besides the AB
BOQ: the subcontractor contracts (HĐ BB′) and the PAKD plans (PAKD_GT = direct overheads, PAKD_TT = direct labours), every row with
its workbook SHA-256 and row number. Nothing here is loaded silently:
  * packages_from_erp — one package per BB′ contract, lines matched to AB lines by WBS code + same UOM (allocation = BB′ qty /
    AB qty, capped at 100 %), award DRAFT with the BB′ unit prices as price basis. Needs the WBS step confirmed (sc.save gate).
    Ambiguous / unmatched / over-quantity rows are reported, never guessed. Re-running skips contracts already imported.
  * pakd_from_erp — the PAKD_GT indirect sections become C.2 lines (amount, source, process group C) of the current scenario.
    PAKD_TT (ERP direct-cost plan) is NOT imported into BM01 (it would double count the estimate); it is shown as a comparator.
"""
import uuid
from decimal import Decimal
from domain import number,index,same_uom,meaningful
import subcontract as sc,pakd
HUNDRED=Decimal(100)
def ref(s):return s.get('erp_reference') or {}
def summary(s):
    """Counts for the UI (flows overview, package / PAKD tabs)."""
    r=ref(s);bb=r.get('bb_contracts') or [];gt=r.get('pakd_gt') or {};tt=r.get('pakd_tt') or {}
    done={p.get('erp_ref') for p in sc.packages(s) if p.get('erp_ref')}
    tot=lambda rows:sum((number(x.get('quantity')) or 0)*(number(x.get('unit_price')) or 0) for x in rows)
    return {'present':bool(bb or gt or tt),'exported':r.get('exported'),'bb_contracts':len(bb),'bb_imported':sum(1 for c in bb if c['ref'] in done),'bb_lines':sum(len(c['lines']) for c in bb),
            'bb_total':str(sum((tot(c['lines']) for c in bb),Decimal(0))),'pakd_gt_sections':len(gt.get('sections') or []),'pakd_gt_total':str(sum((number(x.get('amount')) or 0 for x in gt.get('sections') or []),Decimal(0))),
            'pakd_tt_total':tt.get('total'),'pakd_tt_rows':tt.get('rows'),'pakd_gt_imported':any((l.get('source_ref') or '').startswith('PAKD_GT ERP') for c in (s.get('pakd') or {}).get('scenarios') or [] for l in c.get('lines') or [])}
# ---------- BB′ contracts → packages + award drafts ----------
def packages_from_erp(s,body):
    """Returns (project, report). Only contracts listed in body['refs'] (default: all not yet imported)."""
    bb=ref(s).get('bb_contracts') or []
    if not bb:raise ValueError('Hồ sơ không có hợp đồng BB′ tham chiếu từ ERP.')
    sc.require_wbs_ready(s)
    want=set(body.get('refs') or [c['ref'] for c in bb]);done={p.get('erp_ref') for p in sc.packages(s) if p.get('erp_ref')}
    ab=[r for r in s['boq'] if r.get('kind')=='MEASURED'];by_code={}
    for r in ab:by_code.setdefault(str(r.get('source_code') or '').strip(),[]).append(r)
    pkgs=list(sc.packages(s));seq=max([int(p['code'].split('-')[1]) for p in pkgs if p['code'].startswith('GT-')]+[0]);report=[]
    exported=ref(s).get('exported') or 'ERP'
    for c in bb:
        if c['ref'] not in want or c['ref'] in done:continue
        seq+=1;code=f'GT-{seq:02d}';pid=str(uuid.uuid4());lines=[];prices={};price_refs={};skipped=[];n=0
        for row in c['lines']:
            if row.get('kind')!='MEASURED':continue
            wc=str(row.get('wbs_code') or '').strip();cands=by_code.get(wc,[]);q=number(row.get('quantity'));up=number(row.get('unit_price'))
            if not cands:skipped.append({'row':row.get('row'),'wbs_code':wc,'why':'không có dòng AB cùng mã WBS'});continue
            same=[a for a in cands if same_uom(a.get('uom'),row.get('uom'))]
            if len(same)!=1:skipped.append({'row':row.get('row'),'wbs_code':wc,'why':'nhiều dòng AB cùng mã' if len(same)>1 else f'khác đơn vị ({row.get("uom")} ≠ {", ".join(str(a.get("uom")) for a in cands)})'});continue
            a=same[0];aq=number(a.get('quantity'))
            if q is None or q<=0 or aq is None or aq<=0:skipped.append({'row':row.get('row'),'wbs_code':wc,'why':'thiếu khối lượng BB′ hoặc AB'});continue
            pct=(q/aq*HUNDRED);note=None
            if pct>HUNDRED:note=f'KL BB′ {sc.s_(q)} > KL AB {sc.s_(aq)}: phân bổ 100 %, phần vượt ghi nhận';pct=HUNDRED
            n+=1;bb_code=f'{code}.{n}';lines.append({'id':str(uuid.uuid4()),'bb_code':bb_code,'ab_line_id':a['id'],'alloc_pct':sc.s_(pct.quantize(Decimal('0.0001')))})
            if up is not None:prices[bb_code]=sc.s_(up);price_refs[bb_code]=f'HĐ BB′ {c["ref"]} dòng {row.get("row")} ({exported})'+(' · '+note if note else '')
            elif note:skipped.append({'row':row.get('row'),'wbs_code':wc,'why':note})
        if not lines:report.append({'ref':c['ref'],'code':None,'lines':0,'skipped':skipped,'note':'Không ghép được dòng nào — bỏ qua hợp đồng'});continue
        pkgs.append({'id':pid,'code':code,'name':f'{c["ref"]} · {c.get("label") or ""}'[:200],'scope_note':f'Nhập từ hợp đồng thầu phụ ERP {c["ref"]} ({exported}); phạm vi theo dòng BB′ ghép mã WBS.','procurement_method':None,'delivery':{},'pricing':{},'lines':lines,'erp_ref':c['ref']})
        report.append({'ref':c['ref'],'code':code,'lines':len(lines),'skipped':skipped,'prices':len(prices),'_award':{'package_id':pid,'vendor':(c.get('vendor') or c['ref'])[:200],'prices':prices,'price_refs':price_refs}})
    if not any(r.get('code') for r in report):raise ValueError('Không hợp đồng BB′ nào ghép được với dòng AB theo mã WBS + đơn vị.'+(' Chi tiết: '+'; '.join(f"{r['ref']}: {len(r['skipped'])} dòng bỏ qua" for r in report) if report else ''))
    s=sc.save(s,{'packages':pkgs})
    for r in report:
        aw=r.pop('_award',None)
        if aw and aw['prices']:
            s=sc.save_award(s,dict(aw,reason=f'Đơn giá theo hợp đồng thầu phụ trong ERP ({exported}). Trong app là đề xuất NHÁP: chưa có bằng chứng ký trong hồ sơ.',proposed_by='ERP import'))
            r['award']='DRAFT'
        elif aw:r.pop('_award',None)
    for p in s['packages']:  # erp_ref survives sc.save (it only keeps known keys) → re-attach
        m=next((r for r in report if r.get('code')==p['code']),None)
        if m:p['erp_ref']=m['ref']
    return s,{'imported':[r for r in report if r.get('code')],'skipped_contracts':[r for r in report if not r.get('code')],'already':sorted(done&want)}
# ---------- PAKD_GT → C.2 lines ----------
def pakd_from_erp(s,body):
    gt=ref(s).get('pakd_gt') or {}
    if not gt.get('sections'):raise ValueError('Hồ sơ không có PAKD_GT (chi phí gián tiếp) tham chiếu từ ERP.')
    st=pakd.state(s);c=pakd._scen(st,body.get('scenario_id') or st['current']);exported=ref(s).get('exported') or 'ERP'
    have={l.get('source_ref') for l in c.get('lines') or []};lines=list(c.get('lines') or []);added=0
    for sec in gt['sections']:
        src=f'PAKD_GT ERP {gt.get("id") or ""} · {sec["code"]} {sec["name"]} · {sec["rows"]} dòng ({exported})'[:1000]
        if src in have or number(sec.get('amount')) is None:continue
        lines.append({'code':'C.2','name':f'{sec["code"]} {sec["name"]}'[:200],'method':'AMOUNT','value':sec['amount'],'source_ref':src,'process_group':'C','on':True});added+=1
    if not added:raise ValueError('Các khoản PAKD_GT đã được nhập vào kịch bản này.')
    s=pakd.act(s,{'action':'save','scenario_id':c['id'],'lines':lines})
    return s,{'added':added,'scenario':c['name'],'tt_total':(ref(s).get('pakd_tt') or {}).get('total')}
