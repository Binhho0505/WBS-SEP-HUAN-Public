"""Server-side workflow gates and Decimal estimate snapshots for local review (state schema 0.2.0).

0.2.0 separates partition (BOQ item -> WBS occurrence) from composition (item -> n norm applications),
supports PERCENT resource lines, resource-master price lists with price zones, known/coverage totals,
CBS-based rule bases, indirect allocation for contract comparison and LINE/TOTAL rounding (BL24-BL29).
"""
import hashlib,json,re,uuid
from functools import lru_cache
from decimal import Decimal,InvalidOperation,ROUND_HALF_UP
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCHEMA='0.2.0'
STEPS=['Hồ sơ dự án','BOQ nguồn','WBS và các bộ mã','Chọn định mức','Phân tích hao phí','Đơn giá CC1','CBS và tổng dự toán','Kiểm tra và xuất']
KEYS=['context','boq','mapping','norms','resources','prices','adjustments','export']
CATEGORIES={'C10':'Vật liệu','C20':'Nhân công','C30':'Máy thi công','C40':'Thầu phụ','C50':'Chi phí công trường','C60':'Kỹ thuật/thử nghiệm','C70':'Chi phí khác'}
PURPOSES={'STATE_NORM_CHECK':'Đối chiếu theo định mức nhà nước (TT38)','INTERNAL_COST':'Giá thành nội bộ CC1'}
PROFILES={'ESTIMATE_MIN':'Tối thiểu cho dự toán: kết quả công việc, LBS, phạm vi, nghiệm thu, CA, CAM','FULL':'Đầy đủ: thêm PBS/OBS/CTR/công tác/BIM/rủi ro/tài sản/GL'}
RELATIONS=['pbs','obs','ctr','activity','bim','risk','asset','gl']
WBS_ATTRS=['work_result_code','lbs','price_zone','scope','acceptance','ca','cam']+RELATIONS
RESERVED={'DIRECT',*CATEGORIES}
ALLOCATED_NATURES=['COST','CONTINGENCY']
@lru_cache(maxsize=1)
def catalog():
    p=ROOT/'runs_brian/enterprise_dictionary_20261017_01/dictionary.json'
    return json.loads(p.read_text(encoding='utf-8'))['tables']
def number(x):
    try:
        if x is None or isinstance(x,bool) or str(x).strip()=='':return None
        n=Decimal(str(x)); return n if n.is_finite() else None
    except (InvalidOperation,ValueError):return None
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def new_project(name):
    return {'id':str(uuid.uuid4()),'schema_version':SCHEMA,'name':name,'revision':0,'confirmed':[],'context':{},'boq':[],'wbs':[],'mapping':[],'applications':[],'norms':[],'resources':[],'prices':[],'adjustments':{'rules':[]},'export':{}}
def meaningful(x):return isinstance(x,str) and bool(x.strip()) and x.strip().upper() not in ['N/A','NA','UNKNOWN','OPEN','PENDING']
def ask(items,path,label):items.append({'field':path,'question':label})
def required(items,obj,fields,prefix):
    for key,label in fields:
        if not meaningful(obj.get(key)):ask(items,prefix+'.'+key,label)
def index(rows):return {r.get('id'):r for r in rows}
def upgrade(s):
    """Migrate a 0.1.0 state in place. Values are kept; confirmations reset because the model changed."""
    if s.get('schema_version')==SCHEMA:return s
    s.setdefault('wbs',[]);s.setdefault('applications',[]);seen={w.get('id') for w in s['wbs']}
    for item in s.get('mapping',[]):
        wid=item.get('wbs_id')
        if wid and wid not in seen and any(item.get(a) for a in WBS_ATTRS):s['wbs'].append({'id':wid,**{a:item.get(a) for a in WBS_ATTRS if item.get(a) is not None}});seen.add(wid)
        for a in WBS_ATTRS:item.pop(a,None)
        if item.get('norm_id'):s['applications'].append({'id':str(uuid.uuid4()),'item_id':item['id'],'norm_id':item.pop('norm_id'),'qty_factor':'1','factor_ref':'Chuyển từ cấu trúc 0.1.0 (mỗi hạng mục một tổ hợp định mức)'})
    lines={}
    for r in s.get('resources',[]):
        r.setdefault('line_type','QTY');r.setdefault('resource_code',r.get('id'));lines[r.get('id')]=r
    for p in s.get('prices',[]):
        if 'resource_code' not in p and p.get('resource_id') in lines:p['resource_code']=lines[p['resource_id']]['resource_code']
        p.pop('resource_id',None);p.setdefault('id',str(uuid.uuid4()))
    s['schema_version']=SCHEMA;s['confirmed']=[];s.setdefault('migrations',[]).append('0.1.0->0.2.0: WBS occurrence table, norm applications, resource_code prices; re-review required')
    return s
def zone(s,item,wbs=None):
    w=(wbs if wbs is not None else index(s['wbs'])).get(item.get('wbs_id'),{})
    return w.get('price_zone') if meaningful(w.get('price_zone')) else s['context'].get('location')
def price_key(r,z):return (r.get('resource_code'),r.get('spec'),r.get('uom'),z)
def needed_price_keys(s):
    """Resource-master keys (code, spec, uom, zone) the current applications need a price for."""
    items=index(s['mapping']);wbs=index(s['wbs']);keys=set()
    for app in s['applications']:
        item=items.get(app.get('item_id'))
        if not item:continue
        z=zone(s,item,wbs)
        for r in s['resources']:
            if r.get('norm_id')==app.get('norm_id') and r.get('line_type','QTY')!='PERCENT':keys.add(price_key(r,z))
    return keys
def period_ok(p,ctx):
    """Same period, or an earlier published period (annual labour/machine lists) carried forward with a stated basis."""
    if p.get('period')==ctx.get('period'):return True
    return meaningful(p.get('period_ref')) and str(p.get('period') or '')<=str(ctx.get('period') or '') and bool(p.get('period'))
def price_lookup(s):
    """Price rows in the project context, keyed by resource-master key; duplicates are ambiguous and excluded."""
    ctx=s['context'];found={}
    for p in s['prices']:
        if period_ok(p,ctx) and p.get('currency')==ctx.get('currency') and number(p.get('unit_price')) is not None:
            found.setdefault((p.get('resource_code'),p.get('spec'),p.get('uom'),p.get('location')),[]).append(p)
    return {k:v[0] for k,v in found.items() if len(v)==1}
def calculate(s):
    ctx=s['context'];places=ctx.get('money_places') if ctx.get('money_places') in [0,2] and not isinstance(ctx.get('money_places'),bool) else None
    line_round=ctx.get('rounding_level')=='LINE' and places is not None;quant=Decimal(1).scaleb(-places) if places is not None else None
    rnd=lambda v:v.quantize(quant,rounding=ROUND_HALF_UP) if line_round else v
    items=index(s['mapping']);norms=index(s['norms']);wbs=index(s['wbs']);prices=price_lookup(s);by_norm={}
    for r in s['resources']:by_norm.setdefault(r.get('norm_id'),[]).append(r)
    lines=[];missing=[];needed=0
    for app in s['applications']:
        item=items.get(app.get('item_id'));norm=norms.get(app.get('norm_id'));rows=by_norm.get(app.get('norm_id'),[])
        base=[number((item or {}).get('quantity')),number(app.get('qty_factor')),number((norm or {}).get('denominator'))]
        if not item or not norm or not rows or any(v is None for v in base) or base[2]<=0:
            needed+=max(1,len(rows));missing.append({'application_id':app.get('id'),'item_id':app.get('item_id'),'norm_id':app.get('norm_id'),'reason':'Thiếu hạng mục/tổ hợp định mức/hao phí, khối lượng, hệ số áp dụng hoặc mẫu số'});continue
        unit=base[0]*base[1]/base[2];w=wbs.get(item.get('wbs_id'),{});z=zone(s,item,wbs);group={};gap=set()
        common={'application_id':app['id'],'item_id':item['id'],'source_line_id':item.get('source_line_id'),'wbs_id':item.get('wbs_id'),'work_result_code':w.get('work_result_code'),'lbs':w.get('lbs'),'price_zone':z,'norm_id':norm['id'],'norm_code':norm.get('code'),'qty_factor':str(base[1]),'norm_source':norm.get('source_ref')}
        for r in rows:
            if r.get('line_type','QTY')=='PERCENT':continue
            needed+=1;coef=number(r.get('coefficient'));price=prices.get(price_key(r,z))
            if coef is None or price is None:
                gap.add(r.get('cbs'));missing.append(dict(common,resource_id=r.get('id'),resource_code=r.get('resource_code'),spec=r.get('spec'),uom=r.get('uom'),reason='Thiếu hệ số' if coef is None else 'Thiếu giá hoặc giá trùng trong hồ sơ/vùng giá'));continue
            quantity=unit*coef;unit_price=number(price['unit_price']);amount=rnd(quantity*unit_price);group[r.get('cbs')]=group.get(r.get('cbs'),Decimal(0))+amount
            lines.append(dict(common,line_type='QTY',resource_id=r['id'],resource_code=r.get('resource_code'),resource_name=r.get('name'),spec=r.get('spec'),cbs=r.get('cbs'),uom=r.get('uom'),quantity=str(quantity),unit_price=str(unit_price),percent=None,percent_of=None,amount=str(amount),price_id=price.get('id'),price_source=price.get('source_ref')))
        for r in rows:
            if r.get('line_type','QTY')!='PERCENT':continue
            needed+=1;pct=number(r.get('percent'));of=r.get('percent_of')
            if pct is None or of in gap or of not in group:
                missing.append(dict(common,resource_id=r.get('id'),resource_code=r.get('resource_code'),reason='Dòng % thiếu tỷ lệ hoặc nhóm '+str(of)+' chưa đủ giá'));continue
            amount=rnd(group[of]*pct/100)
            lines.append(dict(common,line_type='PERCENT',resource_id=r['id'],resource_code=r.get('resource_code'),resource_name=r.get('name'),spec=r.get('spec'),cbs=r.get('cbs'),uom='%',quantity=None,unit_price=None,percent=str(pct),percent_of=of,amount=str(amount),price_id=None,price_source=r.get('source_ref')))
    cbs={c:sum((Decimal(l['amount']) for l in lines if l['cbs']==c),Decimal(0)) for c in CATEGORIES};direct=sum(cbs.values(),Decimal(0))
    result={'complete':False,'total':None,'known_amount':str(direct),'coverage':{'needed':needed,'priced':len(lines)},'missing':missing[:200],'missing_count':len(missing),'lines':lines,'cbs':{k:str(v) for k,v in cbs.items()},'rules':[],'items':[],'status':'INCOMPLETE_KNOWN_AMOUNT_ONLY'}
    if missing or not lines or places is None:return result
    amounts={'DIRECT':direct,**cbs};rules=[]
    for rule in s['adjustments'].get('rules',[]):
        value=number(rule.get('value'));terms=[t.strip() for t in str(rule.get('basis','')).split('+')]
        if not rule.get('id') or rule.get('id') in amounts or rule.get('method') not in ['AMOUNT','PERCENT'] or value is None:return result
        if rule.get('method')=='PERCENT' and not all(t in amounts for t in terms):return result
        amount=rnd(value if rule['method']=='AMOUNT' else sum((amounts[t] for t in terms),Decimal(0))*value/100)
        amounts[rule['id']]=amount;rules.append(dict(rule,amount=str(amount)))
        if rule.get('nature')=='COST' and rule.get('cbs') in cbs:cbs[rule['cbs']]+=amount
    total=direct+sum((Decimal(r['amount']) for r in rules),Decimal(0))
    allocatable=sum((Decimal(r['amount']) for r in rules if r.get('nature') in ALLOCATED_NATURES),Decimal(0))
    prorata=s['adjustments'].get('allocation_driver')=='DIRECT_PRORATA' and direct>0;raw=index(s['boq']);rows=[]
    for item in s['mapping']:
        own=sum((Decimal(l['amount']) for l in lines if l['item_id']==item['id']),Decimal(0));allocated=allocatable*own/direct if prorata else Decimal(0);internal=own+allocated
        source=raw.get(item.get('source_line_id'),{});price=number(source.get('unit_price'));quantity=number(item.get('quantity'));contract=None
        if price is not None and quantity is not None:
            contract=quantity*price if item.get('uom')==source.get('uom') else (number(source.get('original_quantity',source.get('quantity'))) or Decimal(0))*price*(number(item.get('weight')) or Decimal(0))
        margin=None if contract is None else contract-internal
        rows.append({'item_id':item['id'],'source_line_id':item.get('source_line_id'),'wbs_id':item.get('wbs_id'),'quantity':str(quantity) if quantity is not None else None,'uom':item.get('uom'),'direct_cost':str(own),'allocated_indirect':str(allocated),'internal_cost':str(internal),'unit_internal_cost':str(internal/quantity) if quantity else None,'contract_unit_price':str(price) if price is not None else None,'contract_amount':str(contract) if contract is not None else None,'margin':str(margin) if margin is not None else None,'margin_pct':str((margin/contract*100).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)) if margin is not None and contract else None})
    final=total if line_round else total.quantize(quant,rounding=ROUND_HALF_UP)
    rounding=('Làm tròn 0,5 lên (HALF_UP) từng dòng hao phí và khoản bổ sung' if line_round else 'Làm tròn 0,5 lên (HALF_UP) chỉ ở tổng cuối; chi tiết giữ độ chính xác')+f'; {places} chữ số'
    result.update(complete=True,direct_cost=str(direct),total_unrounded=str(total),total=str(final),rounding=rounding,cbs={k:str(v) for k,v in cbs.items()},rules=rules,items=rows,allocation={'driver':s['adjustments'].get('allocation_driver'),'allocated_natures':ALLOCATED_NATURES,'allocatable':str(allocatable),'note':'Phân bổ chỉ để so sánh với đơn giá hợp đồng; thuế/lợi nhuận không vào giá thành nội bộ'},status='LOCAL_DRAFT_NOT_CORPORATE_RELEASE')
    return result

def same_uom(a,b):
    """D47: same unit written differently (m³/m3, M3, 'm 3', 'tấn.' …) — typography only, never a unit conversion."""
    f=lambda u:str(u or '').strip().lower().replace('²','2').replace('³','3').replace(' ','').rstrip('.')
    return f(a)==f(b)
def questions(s,step):
    q=[];ctx=s['context'];boq=s['boq'];parts=s['mapping'];norms=s['norms'];resources=s['resources'];prices=s['prices']
    if step==0:
        required(q,ctx,[('project_code','Mã dự án là gì?'),('legal_entity','Pháp nhân quản lý nào?'),('contract_ref','Nguồn hợp đồng và phiên bản nào?'),('location','Địa bàn giá mặc định?'),('period','Kỳ giá (YYYY-MM)?'),('currency','Tiền tệ?'),('cost_basis','Đây là Dự toán (ESTIMATE) hay Ngân sách (BUDGET)?'),('owner','Ai phụ trách lập dự toán?'),('reviewer','Ai kiểm tra/nghiệm thu?'),('legal_ref','Căn cứ áp dụng TT36/37/38 và chuyển tiếp hợp đồng nào?'),('baseline','Đường cơ sở/phiên bản phạm vi?')],'context')
        if ctx.get('cost_basis') not in ['ESTIMATE','BUDGET']:ask(q,'context.cost_basis','Chọn Dự toán (ESTIMATE) hoặc Ngân sách (BUDGET); không dùng số thực chi/đã thanh toán cho bản dự toán.')
        if ctx.get('estimate_purpose') not in PURPOSES:ask(q,'context.estimate_purpose','Mục đích dự toán: đối chiếu định mức nhà nước hay giá thành nội bộ CC1? Không trộn hai mục đích trong một bản số liệu khi chưa ghi căn cứ.')
        if ctx.get('relation_profile') not in PROFILES:ask(q,'context.relation_profile','Chọn bộ mã liên quan: Tối thiểu (ESTIMATE_MIN, cho dự toán) hoặc Đầy đủ (FULL, đủ 10 quan hệ).')
        if not re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])',str(ctx.get('period',''))):ask(q,'context.period','Nhập kỳ giá YYYY-MM hợp lệ.')
        if ctx.get('money_places') not in [0,2] or isinstance(ctx.get('money_places'),bool):ask(q,'context.money_places','Chọn số chữ số làm tròn tiền 0 hoặc 2.')
        if ctx.get('rounding_level') not in ['TOTAL','LINE']:ask(q,'context.rounding_level','Làm tròn ở tổng cuối (TOTAL) hay từng dòng (LINE) theo chính sách của Tài chính?')
        if not meaningful(ctx.get('rounding_ref')):ask(q,'context.rounding_ref','Căn cứ chính sách làm tròn 0,5 lên (HALF_UP) đã chọn là gì?')
    elif step==1:
        if not boq:ask(q,'boq','Nạp BOQ CSV/XLSX hoặc chọn dữ liệu Mễ Sở theo từng cơ sở (AB/BB/PAKD).')
        ids=set()
        for i,r in enumerate(boq):
            p=f'boq[{i}]'
            if not r.get('id') or r.get('id') in ids:ask(q,p+'.id','Mỗi dòng nguồn cần ID duy nhất; không gộp theo mã WBS trùng.')
            ids.add(r.get('id'))
            required(q,r,[('description','Dòng BOQ mô tả hạng mục nào?'),('source_ref','Nguồn/sheet/dòng nào?'),('source_hash','Mã băm của bản BOQ nào?')],p)
            if r.get('kind') not in ['MEASURED','HEADING','NOTE','EXCLUDED']:ask(q,p+'.kind','Phân loại dòng BOQ: có khối lượng, tiêu đề, ghi chú hay loại trừ có căn cứ?')
            if r.get('kind')=='MEASURED':
                if number(r.get('quantity')) is None or number(r.get('quantity'))<=0:ask(q,p+'.quantity','Nhập khối lượng dương; ghi giảm/đảo khối lượng cần hồ sơ riêng, không dùng bản dự toán này.')
                if not meaningful(r.get('uom')):ask(q,p+'.uom','Đơn vị đo của hạng mục là gì?')
            if r.get('kind')=='EXCLUDED' and not meaningful(r.get('disposition_ref')):ask(q,p+'.disposition_ref','Vì sao loại dòng khỏi dự toán? Cần căn cứ để không bỏ sót phạm vi.')
            changed=[f for f in ('source_code','description','unit_price','quantity','uom') if 'original_'+f in r and (number(r.get(f))!=number(r.get('original_'+f)) if f in ('quantity','unit_price') else str(r.get(f) or '')!=str(r.get('original_'+f) or ''))]
            if changed and not meaningful(r.get('disposition_ref')):ask(q,p+'.disposition_ref','Đã sửa tay '+', '.join(changed)+' so với dữ liệu nguồn; ghi căn cứ sửa (phụ lục/biên bản/làm rõ). Bản số liệu gốc giữ nguyên.')
            if str(r.get('source_ref') or '').startswith('MANUAL') and not meaningful(r.get('disposition_ref')):ask(q,p+'.disposition_ref','Dòng nhập tay: căn cứ thêm dòng (phụ lục hợp đồng, biên bản, chỉ dẫn)?')
        if boq and not any(r.get('kind')=='MEASURED' for r in boq):ask(q,'boq','Cần ít nhất một dòng có khối lượng; không thể tạo dự toán rỗng.')
    elif step==2:
        source={r['id']:r for r in boq if r.get('kind')=='MEASURED'};group={};seen=set();master={r['business_code']:r for r in catalog()['WORK_RESULTS']};occurrences={};full=ctx.get('relation_profile')=='FULL'
        for i,w in enumerate(s['wbs']):
            p=f'wbs[{i}]'
            if not meaningful(w.get('id')) or w.get('id') in occurrences:ask(q,p+'.id','ID phần tử WBS phải duy nhất.')
            occurrences[w.get('id')]=w
            required(q,w,[('work_result_code','Chọn mã kết quả công việc MASTER V1.20.'),('lbs','LBS/vị trí thực nào?'),('scope','Phạm vi vào/ra của kết quả là gì?'),('acceptance','Tiêu chí nghiệm thu nào?'),('ca','Tài khoản kiểm soát chi phí (CA) trong đường cơ sở?'),('cam','CAM chính của CA?')],p)
            node=master.get(w.get('work_result_code'))
            if w.get('work_result_code') and not node:ask(q,p+'.work_result_code','Mã kết quả công việc không có trong MASTER đã chốt phiên bản; cần bổ sung qua thay đổi có kiểm soát.')
            elif node and node['readiness']=='HOLD':ask(q,p+'.work_result_code','Mã MASTER đang tạm giữ (HOLD)/thiếu định nghĩa hoặc nhiều cha; chọn mã hợp lệ hoặc xử lý xung đột trước.')
            for rel in RELATIONS if full else []:
                value=w.get(rel)
                if not meaningful(value) or (str(value).startswith('N/A:') and len(str(value)[4:].strip())<5):ask(q,p+'.'+rel,f'{rel.upper()}: nhập mã liên quan hoặc N/A: kèm lý do (bộ mã Đầy đủ).')
        for i,r in enumerate(parts):
            p=f'mapping[{i}]';group.setdefault(r.get('source_line_id'),[]).append(r)
            if not r.get('id') or r.get('id') in seen:ask(q,p+'.id','ID hạng mục chuẩn hóa phải duy nhất.')
            seen.add(r.get('id'))
            if r.get('source_line_id') not in source:ask(q,p+'.source_line_id','Hạng mục chuẩn hóa phải tham chiếu dòng BOQ có khối lượng còn trong phạm vi.')
            required(q,r,[('mapping_ref','Căn cứ xác nhận gán/tách hạng mục?'),('uom','Đơn vị của hạng mục chuẩn hóa?')],p)
            if r.get('wbs_id') not in occurrences:ask(q,p+'.wbs_id','Gán hạng mục vào một phần tử WBS đã khai báo (dùng "Điền hàng loạt" cho các dòng đang lọc).')
            if number(r.get('quantity')) is None or number(r.get('quantity'))<=0:ask(q,p+'.quantity','Khối lượng hạng mục chuẩn hóa phải dương.')
            weight=number(r.get('weight'))
            if weight is None or not 0<weight<=1:ask(q,p+'.weight','Trọng số phân bổ giá trị nằm trong (0,1]; không dùng làm hệ số khối lượng.')
        for sid,raw in source.items():
            rows=group.get(sid,[])
            if not rows:ask(q,'mapping','Chưa phủ dòng BOQ '+str(raw.get('source_code') or sid)+': '+str(raw.get('description')));continue
            weights=[number(r.get('weight')) for r in rows]
            if None in weights or sum(weights)!=1:ask(q,'mapping','Phân bổ giá trị chưa đủ 100% cho dòng '+sid)
            if all(r.get('uom')==raw.get('uom') and number(r.get('quantity')) is not None for r in rows):
                if sum(number(r['quantity']) for r in rows)!=number(raw.get('quantity')):ask(q,'mapping','Tổng khối lượng sau tách khác BOQ '+sid)
            elif not all(meaningful(r.get('quantity_conversion_ref')) for r in rows):ask(q,'mapping','Khác đơn vị nguồn: cần quy đổi/tách khối lượng có căn cứ; không suy từ tỷ lệ tiền.')
        unused=set(occurrences)-{r.get('wbs_id') for r in parts}
        if unused:ask(q,'wbs','Có '+str(len(unused))+' phần tử WBS chưa có hạng mục; bỏ khỏi bản số liệu hoặc gán hạng mục.')
    elif step==3:
        ids=set();byid={r.get('id'):r for r in norms};items=index(parts);pairs=set();used=set()
        for i,r in enumerate(norms):
            p=f'norms[{i}]'
            if not r.get('id') or r.get('id') in ids:ask(q,p+'.id','ID tổ hợp định mức phải duy nhất.')
            ids.add(r.get('id'))
            required(q,r,[('code','Mã nguyên tử đầy đủ hoặc mã định mức nội bộ nào?'),('edition','Bộ/phụ lục/phiên bản định mức?'),('uom','Đơn vị đầu ra của định mức?'),('conditions','Quy cách, biện pháp và điều kiện áp dụng cụ thể?'),('source_ref','Trang/bảng nguồn nào?'),('selection_ref','Ai xác nhận việc lựa chọn và phạm vi áp dụng?')],p)
            if r.get('kind') not in ['TT38_ATOMIC','CC1_APPROVED_CUSTOM']:ask(q,p+'.kind','Chọn mã TT38 nguyên tử đã kiểm bảng hoặc định mức CC1 riêng có căn cứ TT37.')
            if r.get('kind')=='CC1_APPROVED_CUSTOM' and not meaningful(r.get('tt37_ref')):ask(q,p+'.tt37_ref','Căn cứ xây dựng/điều chỉnh định mức TT37 và quyết định nội bộ?')
            if r.get('kind')=='TT38_ATOMIC':
                if not re.fullmatch(r'[A-Z]{2}\.\d{5}',str(r.get('code',''))) or str(r.get('code','')).endswith('00'):ask(q,p+'.code','Mã này chưa chứng minh là mã chi tiết; mã tiêu đề nhóm không được dùng làm tổ hợp định mức.')
                if r.get('table_verified') is not True:ask(q,p+'.table_verified','Xác nhận đã kiểm mã, hậu tố, đơn vị, điều kiện và toàn bộ cột hao phí ở bảng nguồn.')
            if number(r.get('denominator')) is None or number(r.get('denominator'))<=0:ask(q,p+'.denominator','Mẫu số định mức là 1, 100 hay giá trị nào theo bảng nguồn?')
        kinds={r.get('kind') for r in norms};purpose=ctx.get('estimate_purpose')
        if ((purpose=='STATE_NORM_CHECK' and 'CC1_APPROVED_CUSTOM' in kinds) or (purpose=='INTERNAL_COST' and 'TT38_ATOMIC' in kinds)) and not meaningful(ctx.get('norm_mix_ref')):ask(q,'context.norm_mix_ref','Bản số liệu dùng loại định mức khác mục đích '+str(purpose)+'; ghi căn cứ trộn (ví dụ TT38 làm số đại diện cho giá thành nội bộ) ở Hồ sơ dự án.')
        for i,a in enumerate(s['applications']):
            p=f'applications[{i}]';item=items.get(a.get('item_id'));norm=byid.get(a.get('norm_id'))
            if not item:ask(q,p+'.item_id','Áp dụng định mức phải trỏ tới hạng mục chuẩn hóa hiện có.')
            if not norm:ask(q,p+'.norm_id','Áp dụng định mức phải trỏ tới tổ hợp định mức hiện có.')
            if (a.get('item_id'),a.get('norm_id')) in pairs:ask(q,p,'Cùng tổ hợp định mức đã áp dụng cho hạng mục này; gộp hệ số thay vì lặp dòng.')
            pairs.add((a.get('item_id'),a.get('norm_id')));used.add(a.get('norm_id'))
            factor=number(a.get('qty_factor'))
            if factor is None or factor<=0:ask(q,p+'.qty_factor','Hệ số khối lượng định mức trên 1 đơn vị hạng mục (ví dụ 1; 0,12 t thép/m³)?')
            elif factor!=1 and not meaningful(a.get('factor_ref')):ask(q,p+'.factor_ref','Hệ số khác 1 cần căn cứ (bản vẽ, bảng thống kê, quy đổi được duyệt).')
            if item and norm and not same_uom(item.get('uom'),norm.get('uom')) and not meaningful(a.get('conversion_ref')):ask(q,p+'.conversion_ref','Đơn vị hạng mục ('+str(item.get('uom'))+') khác định mức ('+str(norm.get('uom'))+'); ghi căn cứ quy đổi tương ứng với hệ số.')
        covered={a.get('item_id') for a in s['applications']}
        for r in parts:
            required(q,r,[('technical_spec','Quy cách thực của hạng mục (mác/đường kính/cường độ…) là gì?'),('method','Biện pháp thi công thực của hạng mục?'),('norm_match_ref','Căn cứ đối chiếu hạng mục thực với toàn bộ điều kiện định mức?')],'mapping.'+str(r.get('id')))
            if r.get('id') not in covered:ask(q,'applications','Hạng mục '+str(r.get('id'))[:8]+' chưa có định mức áp dụng nào.')
        if set(byid)-used:ask(q,'norms','Có tổ hợp định mức không dùng; bỏ khỏi bản số liệu này để tránh cộng nhầm phương án.')
    elif step==4:
        ids=set();nids={r.get('id') for r in norms};counts={}
        for i,r in enumerate(resources):
            p=f'resources[{i}]';percent=r.get('line_type')=='PERCENT'
            if r.get('line_type') not in ['QTY','PERCENT']:ask(q,p+'.line_type','Loại dòng: Theo khối lượng (QTY, hệ số × giá) hay Theo tỷ lệ % (PERCENT, % trên nhóm khác, ví dụ vật liệu khác)?')
            if not percent:counts[r.get('norm_id')]=counts.get(r.get('norm_id'),0)+1
            if not r.get('id') or r.get('id') in ids:ask(q,p+'.id','ID dòng hao phí của tổ hợp định mức phải duy nhất.')
            ids.add(r.get('id'))
            if r.get('norm_id') not in nids:ask(q,p+'.norm_id','Dòng hao phí tham chiếu tổ hợp định mức không tồn tại.')
            if r.get('cbs') not in CATEGORIES:ask(q,p+'.cbs','Chọn nhóm CBS theo hệ mã của tài liệu triển khai 09/10; không trộn hệ mã 30/08.')
            if percent:
                required(q,r,[('name','Tên dòng % (ví dụ Vật liệu khác)?'),('source_ref','Dòng/cột tỷ lệ trong bảng định mức?')],p)
                if number(r.get('percent')) is None or number(r.get('percent'))<0:ask(q,p+'.percent','Tỷ lệ % không âm theo bảng định mức.')
                if r.get('percent_of') not in CATEGORIES:ask(q,p+'.percent_of','Tỷ lệ tính trên nhóm CBS nào (C10 vật liệu, C30 máy…)?')
                elif not any(x.get('norm_id')==r.get('norm_id') and x.get('line_type','QTY')=='QTY' and x.get('cbs')==r.get('percent_of') for x in resources):ask(q,p+'.percent_of','Tổ hợp định mức chưa có dòng theo khối lượng (QTY) thuộc nhóm '+str(r.get('percent_of'))+' để tính %.')
            else:
                required(q,r,[('resource_code','Mã nguồn lực trong danh mục nguồn lực (khóa bảng giá)?'),('name','Tên nguồn lực?'),('spec','Quy cách/mác/chủng loại?'),('uom','Đơn vị hao phí?'),('source_ref','Dòng/cột hao phí và quyết định điều chỉnh nào?')],p)
                if number(r.get('coefficient')) is None or number(r.get('coefficient'))<0:ask(q,p+'.coefficient','Hệ số hao phí không âm, thiếu không được điền 0.')
        for nid in nids:
            if not counts.get(nid):ask(q,'resources','Tổ hợp định mức '+str(nid)+' chưa có dòng hao phí theo khối lượng (QTY).')
        for norm in norms:
            rr=[r for r in resources if r.get('norm_id')==norm.get('id')]
            if any(r.get('cbs')=='C40' for r in rr) and len(rr)>1 and not meaningful(norm.get('subcontract_boundary_ref')):ask(q,'resources','Thầu phụ đi cùng VL/NC/M cần ranh giới bao gồm/loại trừ để không bóc trùng.')
        if not meaningful(s.get('resource_completeness_ref')):ask(q,'resources','Xác nhận bảng hao phí đủ các dòng VL/NC/M theo tổ hợp định mức (ghi tại mục xác nhận hao phí).')
    elif step==5:
        need=needed_price_keys(s);byk={};ids=set()
        for i,p in enumerate(prices):
            path=f'prices[{i}]';k=(p.get('resource_code'),p.get('spec'),p.get('uom'),p.get('location'))
            if not p.get('id') or p.get('id') in ids:ask(q,path+'.id','ID dòng giá phải duy nhất.')
            ids.add(p.get('id'));byk.setdefault(k,[]).append(p)
            if k not in need:ask(q,path,'Giá '+str(p.get('resource_code'))+' / '+str(p.get('spec'))+' / '+str(p.get('location'))+' không thuộc nguồn lực hoặc vùng giá đang dùng; loại khỏi bản số liệu.');continue
            required(q,p,[('source_ref','Nguồn giá CC1/công bố/báo giá nào?'),('price_ref','Người kiểm tra và căn cứ sử dụng giá?'),('included','Giá đã gồm những gì (hao hụt, vận chuyển, máy/lái máy, thuế…)?')],path)
            v=number(p.get('unit_price'))
            if v is None or v<0:ask(q,path+'.unit_price','Giá phải là số không âm; thiếu giữ trống (null).')
            if v==0 and not meaningful(p.get('zero_ref')):ask(q,path+'.zero_ref','Giá bằng 0 cần căn cứ riêng, không thay cho thiếu giá.')
            if p.get('currency')!=ctx.get('currency'):ask(q,path+'.currency','Giá chưa khớp tiền tệ của hồ sơ; chọn lại tiền tệ ở Hồ sơ dự án hoặc cập nhật giá có căn cứ.')
            if not period_ok(p,ctx):ask(q,path+'.period_ref','Kỳ giá '+str(p.get('period'))+' khác kỳ hồ sơ '+str(ctx.get('period'))+'; dùng giá đúng kỳ hoặc ghi căn cứ áp dụng kỳ công bố trước (ví dụ nhân công/ca máy công bố theo năm). Kỳ sau kỳ hồ sơ không được dùng.')
            if p.get('tax_basis')!='EX_VAT' or p.get('delivery')!='AT_SITE':ask(q,path,'Cần giá chưa VAT tại công trường; quy đổi báo giá gốc bằng bảng tính có căn cứ trước khi nạp.')
        for k in sorted(need,key=lambda x:tuple(str(v) for v in x)):
            n=len(byk.get(k,[]))
            if n!=1:ask(q,'prices.'+str(k[0]),('Chưa có giá cho ' if n==0 else 'Có '+str(n)+' giá trùng cho ')+' / '.join(str(v) for v in k)+' (mã / quy cách / đơn vị / vùng giá).')
    elif step==6:
        a=s['adjustments'];required(q,a,[('cbs_scheme_ref','Chốt hệ mã CBS theo tài liệu triển khai và ánh xạ Tài chính nào?'),('cost_boundary_ref','Xác nhận ranh giới tránh tính trùng nguồn lực/thầu phụ/vận chuyển/chi phí chung?'),('tax_ref','Chính sách VAT/miễn thuế áp dụng và căn cứ nào?'),('completeness_ref','Các nhóm gián tiếp, lợi nhuận, dự phòng, thuế… đã được đưa vào hoặc loại trừ có căn cứ chưa?')],'adjustments')
        if a.get('allocation_driver') not in ['DIRECT_PRORATA','NONE']:ask(q,'adjustments.allocation_driver','Phân bổ khoản chi phí/dự phòng cấp dự án xuống hạng mục để so sánh hợp đồng: Phân bổ theo tỷ lệ chi phí trực tiếp (DIRECT_PRORATA) hay Không phân bổ (NONE)?')
        known=set(RESERVED)
        for i,r in enumerate(a.get('rules',[])):
            path=f'adjustments.rules[{i}]';required(q,r,[('id','Mã khoản bổ sung?'),('name','Tên khoản chi phí/thuế?'),('source_ref','Công thức/tỷ lệ và căn cứ CC1 nào?')],path)
            if r.get('id') in known:ask(q,path+'.id','Mã khoản bổ sung trùng hoặc dùng tên dành riêng DIRECT/C10…C70.')
            if r.get('method') not in ['PERCENT','AMOUNT'] or number(r.get('value')) is None or number(r.get('value'))<0:ask(q,path,'Nhập Số tiền (AMOUNT) hoặc Tỷ lệ % (PERCENT) và giá trị không âm.')
            if r.get('nature') not in ['COST','TAX','PROFIT','CONTINGENCY']:ask(q,path+'.nature','Khoản bổ sung là chi phí, thuế, lợi nhuận hay dự phòng?')
            if r.get('nature')=='COST' and r.get('cbs') not in CATEGORIES:ask(q,path+'.cbs','Khoản chi phí bổ sung thuộc CBS nào? Phần này ở cấp dự án.')
            if r.get('method')=='PERCENT' and any(t.strip() not in known for t in str(r.get('basis','')).split('+')):ask(q,path+'.basis','Cơ sở tính % là DIRECT (chi phí trực tiếp), nhóm CBS (C20…) hoặc tổng các khoản trước đó, ví dụ DIRECT+OVERHEAD; không vòng hoặc tự tính trên chính nó.')
            known.add(r.get('id'))
        if not calculate(s)['complete']:ask(q,'adjustments','Chưa có tổng đầy đủ; quay lại bổ sung đầu vào.')
    elif step==7:
        required(q,s['export'],[('prepared_by','Người lập bản số liệu?'),('checked_by','Người kiểm tra trên máy?'),('review_ref','Căn cứ kiểm tra phạm vi, gán mã và dự toán?')],'export')
        if s['export'].get('template_id')!='TPL03_COMPOSITION':ask(q,'export.template_id','Chọn bố cục nguồn CC1 Mễ Sở: 10_WP_BOQ_COMPOSITION, bổ sung các bảng dự toán có truy vết.')
        if s['export'].get('local_draft_ack') is not True:ask(q,'export.local_draft_ack','Xác nhận đây là dự toán kiểm tra trên máy; không phải phê duyệt/phát hành chính thức CC1.')
    return q
def status(s):
    stages=[];unblocked=True
    for i,title in enumerate(STEPS):
        try:qs=questions(s,i)
        except (ValueError,TypeError,KeyError,InvalidOperation,AttributeError) as e:qs=[{'field':KEYS[i],'question':'Cấu trúc đầu vào chưa hợp lệ; kiểm ID/kiểu dữ liệu và trường dữ liệu của bước này: '+str(e)}]
        confirmed=i in s['confirmed'] and not qs and unblocked
        stages.append({'step':i,'title':title,'questions':qs,'confirmed':confirmed,'available':unblocked,'question_count':len(qs)})
        unblocked=confirmed
    return stages
