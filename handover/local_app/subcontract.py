"""E10–E12 (D59): subcontract packages split from the owner BOQ (AB) into subcontract BOQs (BB).

Every BB line points at exactly one AB line and carries that line's WBS keys unchanged (ERP WBS code = boq.source_code,
MASTER work results and LBS of the line's WBS occurrences), so progress reported per BB line rolls back up to the owner's
WBS. Suggested subcontract prices come from three bases and are never filled in when an input is missing (D58: VL/NC/M
are never pro-rated out of the AB unit price). Award decisions are DRAFT, not approvals.
"""
import csv,io,re,uuid
from datetime import date
from decimal import Decimal
from domain import number,calculate,index,same_uom,status,meaningful

CODE_RE=re.compile(r'^GT-\d{2,3}$');SELF='CC1'
PARTS=('VL','NC','M');PART_CBS={'C10':'VL','C20':'NC','C30':'M'}
MODES=('GOP','TACH');PROVIDERS=('NTP','CC1');PRICE_FORMS=('DON_GIA_CO_DINH','DINH_MUC_DON_GIA_GIAO');ALLOCATIONS=('THEO_KHOI_LUONG','CO_DINH','KHONG_TINH')
HUNDRED=Decimal(100);EPS=Decimal('1e-9')
def s_(d):return None if d is None else format(d.normalize() if d==d.to_integral() else d,'f')
def _q(items,field,text):items.append({'field':field,'question':text})
def require_wbs_ready(s):
    st=status(s)
    if not st[2]['confirmed']:raise ValueError('Xác nhận bước 3 (WBS và các bộ mã) trước khi chia gói thầu: mã WBS là khóa xuyên suốt AB → BB.')
def measured(s):return {r['id']:r for r in s['boq'] if r.get('kind')=='MEASURED'}
def keys_ctx(s):
    """D87: indexes for wbs_keys built once per request (per-line rebuilding was O(n²) on a 17k-line BOQ)."""
    by={}
    for m in s['mapping']:by.setdefault(m.get('source_line_id'),[]).append(m.get('wbs_id'))
    return {'ab':index(s['boq']),'occ':index(s['wbs']),'by_line':by}
def wbs_keys(s,ab_id,ctx=None):
    """WBS keys of one AB line: ERP WBS code, MASTER work results and LBS of its WBS occurrences."""
    ctx=ctx or keys_ctx(s);ab=ctx['ab'].get(ab_id) or {};wr=set();lbs=set()
    for wid in ctx['by_line'].get(ab_id,[]):
        w=ctx['occ'].get(wid) or {}
        if meaningful(w.get('work_result_code')):wr.add(str(w['work_result_code']))
        if meaningful(w.get('lbs')):lbs.add(str(w['lbs']))
    return {'wbs_code':str(ab.get('source_code') or ''),'work_results':sorted(wr),'lbs':sorted(lbs)}
def snapshot(s,ab_id,ctx=None):
    ctx=ctx or keys_ctx(s);ab=ctx['ab'].get(ab_id) or {};return dict(wbs_keys(s,ab_id,ctx),quantity=ab.get('quantity'),uom=ab.get('uom'))
def has_wbs(snap):return bool(snap.get('wbs_code')) or bool(snap.get('work_results'))
def packages(s):return s.get('packages') or []
# ---------- structure (hard errors) ----------
def check_structure(s,pkgs):
    if not isinstance(pkgs,list) or len(pkgs)>500 or any(not isinstance(p,dict) for p in pkgs):raise ValueError('Danh sách gói thầu phải gồm các đối tượng (tối đa 500 gói).')
    codes=set();ids=set();bbs=set();ab=index(s['boq']);selfs=0
    for p in pkgs:
        code=str(p.get('code') or '').strip()
        if code==SELF:selfs+=1
        elif not CODE_RE.match(code):raise ValueError(f'Mã gói "{code}" sai mẫu GT-nn (hoặc CC1 cho phần CC1 tự làm).')
        if code in codes:raise ValueError('Mã gói trùng: '+code)
        if not p.get('id') or p['id'] in ids:raise ValueError('Gói thiếu id hoặc id trùng.')
        codes.add(code);ids.add(p['id'])
        lines=p.get('lines') or []
        if not isinstance(lines,list) or len(lines)>20000:raise ValueError('Các dòng của gói phải là danh sách (tối đa 20.000).')
        for l in lines:
            if not isinstance(l,dict):raise ValueError('Dòng BB phải là một đối tượng.')
            if l.get('ab_line_id') not in ab:raise ValueError(f'Dòng BB {l.get("bb_code")} không trỏ tới dòng BOQ AB hợp lệ (không có dòng BB mồ côi).')
            if not str(l.get('bb_code','')).startswith(code+'.'):raise ValueError(f'Mã dòng BB {l.get("bb_code")} phải bắt đầu bằng {code}.')
            if l['bb_code'] in bbs:raise ValueError('Mã dòng BB trùng: '+l['bb_code'])
            bbs.add(l['bb_code'])
    if selfs>1:raise ValueError('Chỉ có một gói CC1 (CC1 tự làm).')
def next_bb(p):
    used=[int(l['bb_code'].rsplit('.',1)[1]) for l in p.get('lines') or [] if str(l.get('bb_code','')).rsplit('.',1)[-1].isdigit()]
    return max(used+[p.get('bb_seq') or 0])+1
# ---------- save / add lines ----------
def save(s,body):
    """Replace packages (+ context.pm_model). Server-owned parts are kept: snapshots of existing lines, award, bb_seq."""
    require_wbs_ready(s);new=body.get('packages');check_structure(s,new);old={p['id']:p for p in packages(s)};kctx=keys_ctx(s)
    for pid,p in old.items():
        if p.get('award') and pid not in {x['id'] for x in new}:raise ValueError(f'Gói {p["code"]} đã có đề xuất giao thầu; không xóa được (gỡ đề xuất trước).')
    out=[]
    for p in new:
        prev=old.get(p['id']) or {};prev_lines={l['id']:l for l in prev.get('lines') or []};lines=[]
        for l in p.get('lines') or []:
            pl=prev_lines.get(l.get('id'))
            if pl and pl['ab_line_id']!=l['ab_line_id']:raise ValueError('Không đổi dòng AB của một dòng BB đã có; xóa và thêm dòng mới.')
            snap=pl['snapshot'] if pl else snapshot(s,l['ab_line_id'],kctx)
            if not has_wbs(snap):raise ValueError(f'Dòng AB của {l.get("bb_code")} chưa có mã WBS; hoàn tất bước 3.')
            lines.append({'id':l.get('id') or str(uuid.uuid4()),'bb_code':l['bb_code'],'ab_line_id':l['ab_line_id'],'alloc_pct':l.get('alloc_pct'),'snapshot':snap})
        keep={k:p.get(k) for k in ('id','code','name','scope_note','procurement_method','delivery','pricing')}
        keep.update(is_self=p['code']==SELF,lines=lines,award=prev.get('award'),bb_seq=max(prev.get('bb_seq') or 0,next_bb({'lines':lines})-1))
        out.append(keep)
    s['packages']=out
    if 'pm_model' in body:s['context']['pm_model']=body.get('pm_model')
    return s
def add_lines(s,body):
    """Add AB lines to a package by WBS branch, filter or explicit ids. alloc = a percentage or REMAINING (unallocated part)."""
    require_wbs_ready(s);p=next((x for x in packages(s) if x['id']==body.get('package_id')),None)
    if not p:raise ValueError('Không có gói thầu này; lưu gói trước.')
    by=body.get('by');rows=list(measured(s).values());skipped=[]
    if by=='WBS':
        pre=str(body.get('wbs_prefix') or '').strip();wr=str(body.get('work_result') or '').strip()
        if not pre and not wr:raise ValueError('Nhập tiền tố mã WBS (vd 1.2.1) hoặc mã kết quả công việc.')
        kctx=keys_ctx(s)
        def hit(r):
            k=wbs_keys(s,r['id'],kctx);code=k['wbs_code']
            return (pre and (code==pre or code.startswith(pre+'.'))) or (wr and any(x==wr or x.startswith(wr) for x in k['work_results']))
        rows=[r for r in rows if hit(r)]
    elif by=='FILTER':
        q=str(body.get('query') or '').strip().lower();u=str(body.get('uom') or '').strip()
        if not q and not u:raise ValueError('Nhập từ khóa mô tả hoặc đơn vị để lọc.')
        rows=[r for r in rows if (not q or q in str(r.get('description','')).lower()) and (not u or same_uom(r.get('uom'),u))]
    elif by=='IDS':
        ids=body.get('ids');allids=index(s['boq'])
        if not isinstance(ids,list) or not ids:raise ValueError('Chọn ít nhất một dòng BOQ AB.')
        skipped+=[{'ab_line_id':i,'reason':'Không phải dòng đo được (tiêu đề/ghi chú/loại trừ)'} for i in ids if i in allids and allids[i].get('kind')!='MEASURED']
        want=set(ids);rows=[r for r in rows if r['id'] in want]
    else:raise ValueError('Cách thêm dòng phải là theo WBS (WBS), theo bộ lọc (FILTER) hoặc theo danh sách chọn (IDS).')
    mode=body.get('alloc');pct=number(body.get('alloc_pct'))
    if mode!='REMAINING' and (pct is None or pct<=0 or pct>HUNDRED):raise ValueError('Tỷ lệ phân bổ phải >0 và ≤100, hoặc chọn phần còn lại.')
    cov=coverage(s);mine={l['ab_line_id'] for l in p['lines']};added=[]
    for r in rows:
        if r['id'] in mine:skipped.append({'ab_line_id':r['id'],'reason':'Đã có trong gói'});continue
        snap=snapshot(s,r['id'])
        if not has_wbs(snap):skipped.append({'ab_line_id':r['id'],'reason':'Dòng AB chưa có mã WBS'});continue
        a=HUNDRED-cov[r['id']]['allocated'] if mode=='REMAINING' else pct
        if a<=0:skipped.append({'ab_line_id':r['id'],'reason':'Đã phân bổ đủ 100%'});continue
        seq=next_bb(p);line={'id':str(uuid.uuid4()),'bb_code':f'{p["code"]}.{seq}','ab_line_id':r['id'],'alloc_pct':s_(a),'snapshot':snap}
        p['lines'].append(line);p['bb_seq']=seq;added.append(line['bb_code'])
    if not added and not skipped:raise ValueError('Không có dòng BOQ AB đo được khớp điều kiện.')
    return s,{'added':added,'skipped':skipped}
# ---------- coverage / gate ----------
def coverage(s):
    cov={i:{'allocated':Decimal(0),'parts':[],'invalid':False} for i in measured(s)}
    for p in packages(s):
        for l in p.get('lines') or []:
            c=cov.get(l['ab_line_id'])
            if c is None:continue
            a=number(l.get('alloc_pct'))
            if a is None or a<=0 or a>HUNDRED:c['invalid']=True;continue
            c['allocated']+=a;c['parts'].append({'package':p['code'],'bb_code':l['bb_code'],'alloc_pct':s_(a)})
    for c in cov.values():
        c['state']='INVALID' if c['invalid'] else 'OK' if abs(c['allocated']-HUNDRED)<=EPS else 'UNDER' if c['allocated']<HUNDRED else 'OVER'
    return cov
def stale_lines(s):
    out=[]
    kctx=keys_ctx(s)
    for p in packages(s):
        for l in p.get('lines') or []:
            now=snapshot(s,l['ab_line_id'],kctx);old=l.get('snapshot') or {}
            diff=[k for k in ('wbs_code','work_results','lbs','quantity','uom') if now.get(k)!=old.get(k)]
            if l['ab_line_id'] not in index(s['boq']):diff=['ab_line_deleted']
            if diff:out.append({'package':p['code'],'bb_code':l['bb_code'],'changed':diff})
    return out
def questions(s,models=None):
    q=[];pk=packages(s)
    if not pk:_q(q,'packages','Chưa có gói thầu con nào.');return q
    pm=s['context'].get('pm_model')
    if not meaningful(pm):_q(q,'context.pm_model','Chọn mô hình quản lý dự án cho hồ sơ (quyết định nhãn hình thức chọn thầu và danh mục hồ sơ).')
    elif models and pm not in models:
        import pmmodels
        _q(q,'context.pm_model',f'Mô hình "{pm}" không còn dùng ({pmmodels.RETIRED.get(pm,"không có trong danh mục")}) — chọn lại mô hình QLDA.')
    elif models and not models[pm].get('procurement_methods'):
        _q(q,'context.pm_model',f'Mô hình {pm} chưa có danh mục hình thức chọn nhà thầu phụ (CẦN BỔ SUNG từ văn bản gốc) — PMO bổ sung qua bộ dữ liệu "Mô hình QLDA CC1" hoặc chọn mô hình khác.')
    methods=set((models or {}).get(pm,{}).get('procurement_methods',{}).keys()) if models else set()
    for p in pk:
        c=p['code'];f='packages.'+c
        if not meaningful(p.get('name')):_q(q,f+'.name',f'Gói {c}: nhập tên gói.')
        if not p.get('lines'):_q(q,f+'.lines',f'Gói {c}: chưa có dòng BB.')
        if p.get('is_self'):continue
        if methods and p.get('procurement_method') not in methods:_q(q,f+'.procurement_method',f'Gói {c}: chọn hình thức chọn nhà thầu phụ theo mô hình {pm}.')
        d=p.get('delivery') or {}
        if d.get('mode') not in MODES:_q(q,f+'.delivery.mode',f'Gói {c}: chọn hình thức giao thầu GỘP hay TÁCH.')
        elif d['mode']=='TACH':
            for part in PARTS:
                if d.get(part) not in PROVIDERS:_q(q,f'{f}.delivery.{part}',f'Gói {c}: {part} do nhà thầu phụ (NTP) hay CC1 cung cấp?')
            if all(d.get(x)=='CC1' for x in PARTS):_q(q,f+'.delivery',f'Gói {c}: TÁCH mà CC1 cấp cả VL, NC, M thì nhà thầu phụ không còn phạm vi.')
        if d.get('price_form') not in PRICE_FORMS:_q(q,f+'.delivery.price_form',f'Gói {c}: hình thức giá là đơn giá cố định hay định mức + đơn giá giao?')
        fee=number(d.get('fee_pct'))
        if fee is None or fee<0:_q(q,f+'.delivery.fee_pct',f'Gói {c}: nhập phí (%) — ghi 0 nếu không có phí.')
        elif not meaningful(d.get('fee_ref')):_q(q,f+'.delivery.fee_ref',f'Gói {c}: căn cứ của mức phí?')
        for i,r in enumerate(d.get('shared') or []):
            if not meaningful(r.get('resource_code')) or r.get('provider') not in ('CC1','NTP') or r.get('allocation') not in ALLOCATIONS or not meaningful(r.get('ref')):
                _q(q,f'{f}.delivery.shared[{i}]',f'Gói {c}: nguồn lực dùng chung dòng {i+1} thiếu mã/bên cấp/cách phân bổ/căn cứ.')
        a=p.get('award')
        if a:
            if not meaningful(a.get('vendor')) or not meaningful(a.get('reason')) or not meaningful(a.get('proposed_by')):_q(q,f+'.award',f'Gói {c}: đề xuất giao thầu thiếu nhà thầu, lý do hoặc người đề xuất.')
            bad=[l['bb_code'] for l in p['lines'] if (number((a.get('prices') or {}).get(l['bb_code'])) or 0)<=0]
            if bad:_q(q,f+'.award.prices',f'Gói {c}: {len(bad)} dòng chưa có giá giao > 0 (vd {bad[0]}).')
    cov=coverage(s);bad={k:[i for i,c in cov.items() if c['state']==k] for k in ('UNDER','OVER','INVALID')}
    ab=index(s['boq'])
    for k,label in (('UNDER','chưa phân bổ đủ 100%'),('OVER','phân bổ vượt 100%'),('INVALID','có tỷ lệ phân bổ không hợp lệ (≤0, >100 hoặc trống)')):
        if bad[k]:_q(q,'coverage.'+k,f'{len(bad[k])} dòng BOQ AB {label} — vd {ab[bad[k][0]].get("source_code") or ""} {str(ab[bad[k][0]].get("description",""))[:60]}. Giao thêm, giảm tỷ lệ hoặc đưa vào gói CC1 tự làm.')
    st=stale_lines(s)
    if st:_q(q,'packages.stale',f'{len(st)} dòng BB cần xem lại vì dòng AB đã đổi ({", ".join(st[0]["changed"])} ở {st[0]["bb_code"]}). Xóa và thêm lại dòng để nhận dữ liệu mới.')
    for p in packages(s):
        if award_stale(s,p):_q(q,f'award.{p["code"]}.stale',f'Gói {p["code"]}: đề xuất giao thầu đã cũ (dòng gói / khối lượng / giá AB / báo giá đổi sau khi đề xuất) — lưu lại đề xuất (FR28).')
    return q
# ---------- suggested price ----------
def line_costs(s,calc=None):
    """Per AB line: CC1 direct cost by part (VL/NC/M) from the estimate lines, and whether the line is fully priced."""
    calc=calc or calculate(s);out={};missing={m.get('source_line_id') for m in calc['missing'] if m.get('source_line_id')}
    items=index(s['mapping']);miss_items={m.get('item_id') for m in calc['missing']}
    for i in miss_items:
        if i in items:missing.add(items[i].get('source_line_id'))
    if calc.get('missing_count',0)>len(calc['missing']):missing=None  # truncated list: cannot tell which lines are complete
    for l in calc['lines']:
        part=PART_CBS.get(l.get('cbs'));sid=l.get('source_line_id')
        if part is None and l.get('line_type')=='PERCENT':part=PART_CBS.get(l.get('percent_of'))
        d=out.setdefault(sid,{'VL':Decimal(0),'NC':Decimal(0),'M':Decimal(0),'other':Decimal(0)})
        d[part or 'other']+=Decimal(l['amount'])
    for sid,d in out.items():d['complete']=missing is not None and sid not in missing
    return out
def basis_values(s,p,costs,quotes_ok):
    """Suggested unit price per BB line on bases A, B and C. Missing input → value None with the reason."""
    ab=index(s['boq']);pr=p.get('pricing') or {};d=p.get('delivery') or {};out={}
    k_all=number(pr.get('k_all'));ks={x:number(pr.get('k_'+x)) for x in PARTS};fee=number(d.get('fee_pct'))
    nt=[x for x in PARTS if d.get('mode')=='GOP' or (d.get('mode')=='TACH' and d.get(x)=='NTP')]
    for l in p.get('lines') or []:
        a=ab.get(l['ab_line_id']) or {};up=number(a.get('unit_price'));qty=number(a.get('quantity'))
        if up is None:A={'value':None,'reason':'Dòng AB không có đơn giá hợp đồng'}
        elif k_all is not None and k_all>0:A={'value':s_(up*k_all),'reason':f'Đơn giá AB × K chung {s_(k_all)}'}
        elif any(v is not None for v in ks.values()):A={'value':None,'reason':'Đơn giá AB không tách VL/NC/M; không chia tỷ lệ (D58) — nhập K chung hoặc dùng căn cứ B'}
        else:A={'value':None,'reason':'Chưa nhập hệ số giao K chung'}
        c=costs.get(l['ab_line_id'])
        if d.get('mode') not in MODES:B={'value':None,'reason':'Chưa chọn hình thức giao thầu'}
        elif not nt:B={'value':None,'reason':'Nhà thầu phụ không chịu thành phần VL/NC/M nào'}
        elif not c or not c.get('complete'):B={'value':None,'reason':'Dự toán CC1 của dòng AB chưa đủ hao phí/giá (bước 4–6)'}
        elif not qty:B={'value':None,'reason':'Dòng AB không có khối lượng'}
        elif any(ks[x] is None or ks[x]<=0 for x in nt):B={'value':None,'reason':'Thiếu hệ số K cho thành phần nhà thầu phụ chịu: '+', '.join(x for x in nt if ks[x] is None or ks[x]<=0)}
        elif fee is None or fee<0:B={'value':None,'reason':'Chưa nhập phí (%)'}
        elif not any(c[x] for x in nt):B={'value':None,'reason':'Dự toán CC1 không có chi phí cho thành phần nhà thầu phụ chịu ('+', '.join(nt)+'); không định giá 0'}
        else:
            base=sum((c[x]*ks[x] for x in nt),Decimal(0))/qty
            B={'value':s_((base*(1+fee/HUNDRED)).quantize(Decimal('0.01'))),'reason':'Chi phí CC1 ('+'+'.join(f'{x}×{s_(ks[x])}' for x in nt)+f') × (1+{s_(fee)}%)'}
        vals=[number(r.get('unit_price')) for q in quotes_ok for r in q['rows'] if r.get('bb_code')==l['bb_code']]
        vals=[v for v in vals if v is not None and v>0]
        C={'value':s_(min(vals)),'reason':f'Thấp nhất trong {len(quotes_ok)} báo giá hợp lệ'} if vals else {'value':None,'reason':'Chưa có báo giá hợp lệ'}
        nums=[number(x['value']) for x in (A,B,C) if x['value'] is not None]
        out[l['bb_code']]={'A':A,'B':B,'C':C,'spread_pct':s_(((max(nums)-min(nums))/min(nums)*HUNDRED).quantize(Decimal('0.1'))) if len(nums)>1 and min(nums)>0 else None}
    return out
# ---------- delete draft packages (D81) ----------
def delete_packages(s,body):
    """Delete saved packages that are still drafts, with what hangs on them: their quotes, the DRAFT award and the PAKD
    scenario references (basis / parts). Refused when a package has a contract dossier (E18) or recorded progress /
    acceptance on its lines — those are evidence, never deleted silently. Returns (project, report)."""
    ids=body.get('package_ids') or ([body['package_id']] if body.get('package_id') else [])
    if not ids or not isinstance(ids,list):raise ValueError('Chọn gói cần xóa.')
    byid={p['id']:p for p in packages(s)};report=[]
    for pid in ids:
        p=byid.get(pid)
        if not p:raise ValueError('Gói không còn trong hồ sơ (tải lại).')
        if any(c.get('package_id')==pid for c in s.get('contracts') or []):raise ValueError(f'Gói {p["code"]} đã có hồ sơ hợp đồng — không xóa (hồ sơ là bằng chứng).')
        codes={l['bb_code'] for l in p.get('lines') or []}
        if any(e.get('bb_code') in codes for e in (s.get('progress') or [])+(s.get('facts') or [])):raise ValueError(f'Gói {p["code"]} đã có khối lượng hoàn thành / nghiệm thu — không xóa.')
        q=[x for x in s.get('quotes') or [] if x['package_id']==pid]
        report.append({'code':p['code'],'lines':len(p.get('lines') or []),'quotes':len(q),'award':bool(p.get('award'))})
    drop=set(ids)
    s['packages']=[p for p in packages(s) if p['id'] not in drop]
    s['quotes']=[x for x in s.get('quotes') or [] if x['package_id'] not in drop]
    pk=s.get('pakd') or {}
    for c in pk.get('scenarios') or []:
        c['basis']={k:v for k,v in (c.get('basis') or {}).items() if k not in drop}
        c['parts']={k:v for k,v in (c.get('parts') or {}).items() if k not in drop}
    return s,report
def package_usage(s):
    """Per package: what deleting it would remove or what blocks it (shown in the confirmation dialog)."""
    out={}
    for p in packages(s):
        codes={l['bb_code'] for l in p.get('lines') or []}
        block=('hồ sơ hợp đồng' if any(c.get('package_id')==p['id'] for c in s.get('contracts') or []) else
               'khối lượng hoàn thành / nghiệm thu' if any(e.get('bb_code') in codes for e in (s.get('progress') or [])+(s.get('facts') or [])) else None)
        out[p['id']]={'lines':len(p.get('lines') or []),'quotes':sum(1 for x in s.get('quotes') or [] if x['package_id']==p['id']),'award':bool(p.get('award')),
                      'pakd':sum(1 for c in (s.get('pakd') or {}).get('scenarios') or [] if p['id'] in (c.get('basis') or {}) or p['id'] in (c.get('parts') or {})),'blocked_by':block}
    return out
# ---------- quotes ----------
HEAD={'bb_code':('ma dong bb','bb code','ma bb'),'wbs_code':('ma wbs','wbs code','wbs'),'description':('mo ta','noi dung','ten cong viec','description'),
      'uom':('don vi','dvt','uom','unit'),'quantity':('khoi luong','kl','quantity','qty'),'unit_price':('don gia','unit price','price')}
def _fold(x):
    import unicodedata
    return ' '.join(''.join(c for c in unicodedata.normalize('NFD',str(x or '').lower().replace('đ','d')) if unicodedata.category(c)!='Mn').split())
def parse_quote(filename,data):
    """Read a subcontractor quote (XLSX/CSV); the header row is found by its column names (template from the BB export)."""
    name=str(filename or '').lower()
    if name.endswith('.csv'):
        text=data.decode('utf-8-sig',errors='replace');table=list(csv.reader(io.StringIO(text)))
    elif name.endswith('.xlsx'):
        from openpyxl import load_workbook
        wb=load_workbook(io.BytesIO(data),read_only=True,data_only=True);ws=next((w for w in wb.worksheets if w.title.startswith('BOQ')),wb.worksheets[0])
        table=[list(r) for r in ws.iter_rows(values_only=True)]
    else:raise ValueError('Báo giá phải là .xlsx hoặc .csv.')
    for hi,row in enumerate(table[:30]):
        cols={}
        for ci,cell in enumerate(row):
            f=_fold(cell)
            for key,names in HEAD.items():
                if key not in cols and any(f==n or f.startswith(n+' ') or f.startswith(n+'(') for n in names):cols[key]=ci
        if 'unit_price' in cols and ('bb_code' in cols or 'wbs_code' in cols):break
    else:raise ValueError('Không tìm thấy dòng tiêu đề có cột Đơn giá và Mã dòng BB/Mã WBS (dùng mẫu BOQ BB xuất từ app).')
    rows=[]
    for row in table[hi+1:]:
        get=lambda k:(row[cols[k]] if k in cols and cols[k]<len(row) else None)
        if not any(get(k) not in (None,'') for k in cols):continue
        rows.append({k:(None if get(k) is None else str(get(k)).strip()) for k in HEAD})
    if not rows:raise ValueError('Báo giá không có dòng dữ liệu.')
    return rows
def review(s,p,quote,basis,tol_qty=None,tol_price=None):
    """Findings for one quote vs the package BB lines. Blocking findings make the quote invalid for basis C."""
    pr=p.get('pricing') or {};tq=number(pr.get('qty_tol_pct'));tp=number(pr.get('price_tol_pct'))
    tq=tq if tq is not None else Decimal(5);tp=tp if tp is not None else Decimal(10)
    ab=index(s['boq']);lines={l['bb_code']:l for l in p.get('lines') or []};found=[];seen=set()
    by_bb={r.get('bb_code'):r for r in quote['rows'] if r.get('bb_code')}
    total=Decimal(0)
    for code,l in lines.items():
        a=ab.get(l['ab_line_id']) or {};r=by_bb.get(code)  # AC16 (D79): match by BB line id only, never by description
        if not r:found.append({'bb_code':code,'type':'MISSING','blocking':True,'text':'Báo giá thiếu dòng này'});continue
        seen.add(id(r));bq=number(a.get('quantity'));al=number(l.get('alloc_pct'))
        bbq=bq*al/HUNDRED if bq is not None and al is not None else None
        if r.get('uom') and not same_uom(r.get('uom'),a.get('uom')):found.append({'bb_code':code,'type':'UOM_MISMATCH','blocking':True,'text':f'Đơn vị {r.get("uom")} ≠ {a.get("uom")}'})
        price=number(r.get('unit_price'))
        if price is None:found.append({'bb_code':code,'type':'PRICE_EMPTY','blocking':True,'text':'Đơn giá trống / không phải số (không coi là 0)'})
        elif price<=0:found.append({'bb_code':code,'type':'PRICE_NOT_POSITIVE','blocking':True,'text':f'Đơn giá {s_(price)} ≤ 0'})
        q=number(r.get('quantity'))
        if q is not None and bbq and abs(q-bbq)/bbq*HUNDRED>tq:found.append({'bb_code':code,'type':'QTY_DIFF','blocking':False,'text':f'Khối lượng {s_(q)} lệch BB {s_(bbq.quantize(Decimal("0.001")))} quá {s_(tq)}%'})
        ref=[number(basis.get(code,{}).get(k,{}).get('value')) for k in ('A','B')];ref=[x for x in ref if x is not None]
        if price and price>0 and ref:
            m=min(ref);dev=(price-m)/m*HUNDRED
            if abs(dev)>tp:found.append({'bb_code':code,'type':'PRICE_HIGH' if dev>0 else 'PRICE_LOW','blocking':False,'text':f'Đơn giá lệch {s_(dev.quantize(Decimal("0.1")))}% so giá gợi ý {s_(m)}'})
        if price and price>0 and bbq:total+=price*bbq
    for r in quote['rows']:
        if id(r) not in seen:found.append({'bb_code':r.get('bb_code'),'type':'EXTRA','blocking':False,'text':('Dòng không có trong BOQ BB: ' if r.get('bb_code') else 'Dòng thiếu mã dòng BB (không ghép theo mô tả): ')+str(r.get('description') or '')[:60]})
    return {'quote_id':quote['id'],'vendor':quote['vendor'],'valid':not any(f['blocking'] for f in found),'findings':found,'total':s_(total.quantize(Decimal('0.01'))),
            'counts':{t:sum(1 for f in found if f['type']==t) for t in ('MISSING','UOM_MISMATCH','PRICE_EMPTY','PRICE_NOT_POSITIVE','EXTRA','QTY_DIFF','PRICE_HIGH','PRICE_LOW')}}
def add_quote(s,body,sha,rows):
    p=next((x for x in packages(s) if x['id']==body.get('package_id')),None)
    if not p or p.get('is_self'):raise ValueError('Chọn gói thầu con (không phải gói CC1 tự làm).')
    vendor=str(body.get('vendor') or '').strip()
    if not vendor:raise ValueError('Nhập tên nhà thầu phụ của báo giá.')
    s.setdefault('quotes',[]).append({'id':str(uuid.uuid4()),'package_id':p['id'],'vendor':vendor[:200],'filename':str(body.get('filename') or '')[:200],'sha256':sha,'received':str(date.today()),'rows':rows[:20000]})
    return s
def save_award(s,body):
    p=next((x for x in packages(s) if x['id']==body.get('package_id')),None)
    if not p or p.get('is_self'):raise ValueError('Chọn gói thầu con.')
    if body.get('clear'):p['award']=None;return s
    q=next((x for x in s.get('quotes') or [] if x['id']==body.get('quote_id') and x['package_id']==p['id']),None)
    if body.get('quote_id') and not q:raise ValueError('Báo giá không thuộc gói này.')
    prices=body.get('prices') or {}
    if not isinstance(prices,dict):raise ValueError('Bảng giá giao phải là đối tượng {mã dòng BB: đơn giá}.')
    if q and not prices:prices={r['bb_code']:r.get('unit_price') for r in q['rows'] if r.get('bb_code')}
    codes={l['bb_code'] for l in p['lines']}
    p['award']={'status':'DRAFT','inputs_sha256':award_digest(s,p,body.get('quote_id')),'quote_id':body.get('quote_id'),'vendor':str(body.get('vendor') or (q or {}).get('vendor') or '')[:200],'reason':str(body.get('reason') or '')[:2000],
                'proposed_by':str(body.get('proposed_by') or '')[:200],'date':str(date.today()),'prices':{k:v for k,v in prices.items() if k in codes},'price_refs':{k:v for k,v in (body.get('price_refs') or {}).items() if k in codes},
                'note':'Đề xuất NHÁP trong app trên máy — không phải phê duyệt giao thầu.'}
    return s
def award_digest(s,p,quote_id=None):
    """FR28 (D79): what an award priced — package lines, their AB quantity/UOM/price and the quote file. A change makes it stale."""
    import hashlib,json
    ab=index(s['boq']);q=next((x for x in s.get('quotes') or [] if x['id']==quote_id),None)
    payload={'lines':sorted((l['bb_code'],l['ab_line_id'],str(l.get('alloc_pct')),*(str((ab.get(l['ab_line_id']) or {}).get(k)) for k in ('quantity','uom','unit_price'))) for l in p.get('lines') or []),
             'quote':(q or {}).get('sha256')}
    return hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def award_stale(s,p):
    aw=p.get('award') or {}
    return bool(aw) and aw.get('inputs_sha256') is not None and aw['inputs_sha256']!=award_digest(s,p,aw.get('quote_id'))
# ---------- progress ----------
def add_progress(s,body):
    lines={l['bb_code']:l for p in packages(s) for l in p.get('lines') or []}
    code=body.get('bb_code');q=number(body.get('cum_qty'))
    if code not in lines:raise ValueError('Không có dòng BB này.')
    if q is None or q<0:raise ValueError('Khối lượng hoàn thành lũy kế phải ≥ 0.')
    d=str(body.get('date') or '')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',d):raise ValueError('Ngày theo dạng YYYY-MM-DD.')
    if not meaningful(body.get('ref')):raise ValueError('Nhập căn cứ (biên bản/nhật ký) của khối lượng hoàn thành.')
    s.setdefault('progress',[]).append({'id':str(uuid.uuid4()),'bb_code':code,'date':d,'cum_qty':s_(q),'ref':str(body['ref'])[:500],'by':str(body.get('by') or '')[:200]})
    return s
def rollup(s):
    """Completion per AB line and per WBS key, from the latest cumulative quantity of each BB line."""
    ab=index(s['boq']);latest={}
    for e in sorted(s.get('progress') or [],key=lambda e:(e['date'],e['id'])):latest[e['bb_code']]=e
    per_ab={};warn=[]
    for p in packages(s):
        for l in p.get('lines') or []:
            a=ab.get(l['ab_line_id']) or {};q=number(a.get('quantity'));al=number(l.get('alloc_pct'))
            alloc=q*al/HUNDRED if q is not None and al is not None else None;e=latest.get(l['bb_code']);done=number(e['cum_qty']) if e else Decimal(0)
            if alloc is not None and done>alloc:warn.append({'bb_code':l['bb_code'],'text':f'Hoàn thành {s_(done)} vượt phân bổ {s_(alloc)}'});done=alloc
            d=per_ab.setdefault(l['ab_line_id'],{'done':Decimal(0),'parts':[]});d['done']+=done;d['parts'].append({'bb_code':l['bb_code'],'package':p['code'],'done':s_(done),'alloc':s_(alloc),'date':e['date'] if e else None})
    rows=[];groups={};kctx=keys_ctx(s)
    for i,a in measured(s).items():
        q=number(a.get('quantity'));d=per_ab.get(i,{'done':Decimal(0),'parts':[]});pct=(d['done']/q*HUNDRED) if q else None
        k=wbs_keys(s,i,kctx);rows.append({'ab_line_id':i,'wbs_code':k['wbs_code'],'work_results':k['work_results'],'description':a.get('description'),'uom':a.get('uom'),'quantity':a.get('quantity'),'done':s_(d['done']),'pct':s_(pct.quantize(Decimal('0.1'))) if pct is not None else None,'parts':d['parts']})
        up=number(a.get('unit_price'));key=k['wbs_code'] or ','.join(k['work_results'])
        g=groups.setdefault(key,{'wbs':key,'value':Decimal(0),'done_value':Decimal(0),'pcts':[],'lines':0});g['lines']+=1
        if pct is not None:g['pcts'].append(pct)
        if up is not None and q:g['value']+=up*q;g['done_value']+=up*d['done']
        else:g['unpriced']=g.get('unpriced',0)+1
    out=[]
    for g in groups.values():
        if g['value']>0 and not g.get('unpriced'):pct=g['done_value']/g['value']*HUNDRED;method='Theo giá trị hợp đồng AB'
        else:pct=None;method='Chưa có trọng số: dòng AB thiếu đơn giá — không lấy trung bình % dòng (PRD §5.3)'
        out.append({'wbs':g['wbs'],'lines':g['lines'],'pct':s_(pct.quantize(Decimal('0.1'))) if pct is not None else None,'method':method,'state':'XONG' if pct is not None and pct>=HUNDRED else 'CHUA_BAT_DAU' if not pct else 'DANG_LAM'})
    out.sort(key=lambda g:[(0,int(x),'') if x.isdigit() else (1,0,x) for x in re.split(r'[.]',g['wbs'])] if g['wbs'] else [])  # D85: numeric and alphabetic WBS codes mix (type-stable key)
    return {'lines':rows,'wbs':out,'warnings':warn}
# ---------- reconciliation and summary ----------
def reconcile(s):
    """Per WBS code: AB quantity vs Σ BB allocations (incl. CC1 self-performed) per AB line; differences only."""
    cov=coverage(s);ab=measured(s);rows=[]
    for i,c in cov.items():
        a=ab[i];q=number(a.get('quantity'))
        rows.append({'ab_line_id':i,'wbs_code':str(a.get('source_code') or ''),'description':a.get('description'),'uom':a.get('uom'),'ab_quantity':a.get('quantity'),
                     'bb_quantity':s_((q*c['allocated']/HUNDRED).quantize(Decimal('0.0001'))) if q is not None else None,'allocated_pct':s_(c['allocated']),'state':c['state'],'parts':c['parts']})
    return rows
def summary(s,models=None):
    calc=calculate(s);costs=line_costs(s,calc);res=[];out=[]
    for p in packages(s):
        qs=[q for q in s.get('quotes') or [] if q['package_id']==p['id']]
        pre=basis_values(s,p,costs,[])
        reviews=[review(s,p,q,pre) for q in qs];ok=[q for q,r in zip(qs,reviews) if r['valid']]
        basis=basis_values(s,p,costs,ok)
        out.append({'id':p['id'],'code':p['code'],'reviews':reviews,'basis':basis})
    cov=coverage(s);counts={k:sum(1 for c in cov.values() if c['state']==k) for k in ('OK','UNDER','OVER','INVALID')}
    return {'packages':out,'coverage':counts,'reconcile':reconcile(s),'stale':stale_lines(s),'progress':rollup(s),'questions':questions(s,models)}
