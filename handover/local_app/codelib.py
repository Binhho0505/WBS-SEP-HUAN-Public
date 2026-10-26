"""Code library services on top of the data library (D29/D30): norm search and detail with resource-master
mapping, and automatic price proposals keyed by CC1 resource master codes.

Auto-proposed prices are never accepted silently: each row keeps lineage (mapped_from) and an empty price_ref,
so the price gate still asks the estimator for the basis of use; earlier periods also need period_ref.
"""
import re
from domain import needed_price_keys,price_key
MCODE=re.compile(r'^M\d{3}\.\d{4}[a-z]?$')
def active(store,kind):return [d for d in store.library_list() if d['kind']==kind and d['status']=='ACTIVE']
def master_index(store):
    """RESOURCE_MASTER reference rows keyed by master code (several TT38 names may share one M code)."""
    idx={}
    for d in active(store,'REFERENCE'):
        if not d['name'].startswith('Danh mục nguồn lực CC1'):continue
        for r in store.library_rows(d['id']):idx.setdefault(r.get('code'),[]).append(r)
    return idx
def search_norms(store,q,limit=50):
    hits=store.library_search('NORMS',q,limit)
    return {'total':hits['total'],'rows':[{k:r.get(k) for k in ('id','code','edition','uom','denominator','conditions','parse_status','parse_flags','source_ref','library_dataset','library_name')} for r in hits['rows']]}
def norm_detail(store,nid):
    norm=None
    for d in active(store,'NORMS'):
        norm=next((dict(r,library_dataset=d['id'],library_sha256=d['sha256']) for r in store.library_rows(d['id']) if r.get('id')==nid),None)
        if norm:break
    if not norm:raise KeyError('Không có mã định mức '+str(nid)+' trong thư viện đang dùng.')
    lines=[]
    for d in active(store,'RESOURCES'):
        lines+=[dict(r,library_dataset=d['id'],library_sha256=d['sha256']) for r in store.library_rows(d['id']) if r.get('norm_id')==nid]
    masters=master_index(store)
    for l in lines:
        m=next((x for x in masters.get(l.get('master_code'),[]) if x.get('name')==l.get('name')),None) or (masters.get(l.get('master_code')) or [None])[0]
        l['map']={'status':m.get('status'),'target':m.get('value'),'candidates':m.get('candidates',[])} if m else None
    return {'norm':norm,'lines':lines}
def for_project(norm,lines):
    """Norm + lines ready for a project draft: resource_code becomes the CC1 master code when one exists."""
    out=[]
    for l in lines:
        r={k:v for k,v in l.items() if k not in ('map',)}
        if l.get('master_code'):r['resource_code']=l['master_code']
        out.append(r)
    return norm,out
# ---------- BOQ item -> TT38 norm suggestions (candidates only; QS selects and verifies the source table) ----------
import math
from store import fold
STOPW={'va','cac','loai','cho','bang','cua','trong','co','the','theo','tai','khac','mot','so','cong','tac','thi','lap','dat','xay','dung','thuong','hang','muc','phan','kien','ket','trinh','tam','tinh','dia','vi','chi','phi'}
ACTIONS=('pha do','thao do','van chuyen','thay the','kiem tra','sua chua','boc xep','khoan tao lo','xu ly','bom vua','ve sinh','nao vet')
TESTW=('thi nghiem','khao sat','sieu am','nen tinh','pda','kiem dinh','khoan lay mau','do dac')  # PL1 field tests / PL5 lab tests
LUMP=('trongoi','tg','khoan','goi','ls','lumpsum')  # lump-sum BOQ units: no consumption norm to suggest
# BOQ wording -> TT38 wording (folded). Small, explicit list for QS review; the original words are replaced so that
# e.g. 'chậu' in 'gối chậu' (pot bearing) no longer matches 'chậu rửa' (sink).
SYN={'goi chau (song|da|don) huong':'goi cau','goi chau co dinh':'goi cau','goi chau':'goi cau','goi cao su':'goi cau cao su','goi thep':'goi cau thep',
     'thi cong coc khoan nhoi':'khoan vao dat coc khoan nhoi','upvc':'pvc','xa mu':'mu tru',  # BL58: AC.32/33 tables are titled 'Khoan vào đất…'
     # BL75: guardrail is titled 'tôn lượn sóng' (AD.341/343), not 'hộ lan' (AL.271 is the rolling barrier); road
     # projects haul soil by dump truck (AB.41/42) — without it 'cự ly … km' matches drilling-mud haulage first
     'ho lan (ton )?(luon )?song':'ton luon song dai phan cach','tam (ton )?song':'tam ton luon song dai phan cach',
     'van chuyen dat':'van chuyen dat bang o to tu do'}
# BL58: concrete placing method chosen by the estimator (TT38 chapter VI: AF.1 thủ công, AF.2 cần cẩu, AF.3 máy bơm)
# BL58: a table about one component (title) does not price a BOQ line that never names that component
COMPONENTS=('ong vach','van khuon','cot thep','be tong','cap thep')
METHODS={'THU_CONG':'1','CAN_CAU':'2','BOM':'3'}
GROUP_RE=re.compile(r'nhóm ([A-Z]{2}\.[0-9]{5})')
def synonyms(s):
    f=fold(s)
    for a,b in SYN.items():f=re.sub(r'\b'+a+r'\b',b,f)
    return f
def lump_sum(uom):return fold(uom).replace(' ','').replace('.','') in LUMP
UOMS={'m3':'m3','m³':'m3','tan':'t','tấn':'t','t':'t','m2':'m2','m²':'m2','m':'m','md':'m'}
def _toks(s):return [w for w in re.findall(r'[a-z]+',fold(s)) if len(w)>1 and w not in STOPW]
def _bigrams(s):
    w=[x for x in re.findall(r'[a-z]+',fold(s)) if len(x)>1]
    return {a+' '+b for a,b in zip(w,w[1:]) if not (a in STOPW and b in STOPW)}
# BL75: count units (bộ, cái, cột…) never measure the same work as a volume/area/length/mass table
COUNTS=('cai','bo','vien','con','chiec')  # cọc/cột/trụ are often priced per metre: not strict
def _uclass(u):
    f=re.sub(r'^\d+(\.\d+)?','',fold(u).strip()).strip()
    if not f:return ''
    if f in COUNTS:return 'COUNT'
    v=_uom(u);return {'m3':'VOL','m2':'AREA','m':'LEN'}.get(v,'MASS' if f in ('t','tan','kg') else '')
def _uom(u):
    u=fold(u).replace(' ','');u=re.sub(r'^\d+(\.\d+)?','',u)
    for k,v in UOMS.items():
        if u.startswith(fold(k)):return v
    return u
_NIDX={}
def norm_index(store):
    sets=tuple(sorted(d['id'] for d in active(store,'NORMS')))
    if sets in _NIDX:return _NIDX[sets]
    docs=[];df={}
    for did in sets:
        for n in store.library_rows(did):
            t=set(_toks(n.get('conditions','')))
            docs.append((n,t,_bigrams(n.get('conditions',''))));[df.__setitem__(w,df.get(w,0)+1) for w in t]
    N=max(1,len(docs));idf={w:math.log(N/c) for w,c in df.items()};inv={}
    for i,(n,t,_) in enumerate(docs):
        for w in t:inv.setdefault(w,[]).append(i)
    _NIDX.clear();_NIDX[sets]=(docs,idf,inv);return _NIDX[sets]
_RULES={}
def boq_rules(store):
    """BL60: BOQ→TT38 dictionary rows from the ACTIVE reference dataset 'Từ điển BOQ→TT38…' (versioned, QS-editable)."""
    ds=tuple(sorted(d['id'] for d in active(store,'REFERENCE') if d['name'].startswith('Từ điển BOQ→TT38')))
    if ds not in _RULES:
        rows=[]
        for did in ds:
            for r in store.library_rows(did):
                if r.get('series')!='BOQ_TT38_RULE':continue
                try:rows.append(dict(r,_m=re.compile(r.get('match') or '$^'),_c=re.compile(r['ctx']) if r.get('ctx') else None))
                except re.error:continue  # an invalid pattern is skipped, never guessed
        _RULES.clear();_RULES[ds]=rows
    return _RULES[ds]
def matched_rules(store,text,context=''):
    """Rules whose pattern matches the BOQ description (brackets removed) and, if given, the heading path."""
    fd=fold(re.sub(r'\([^)]*\)',' ',str(text)));fc=fold(context)
    return [r for r in boq_rules(store) if r['_m'].search(fd) and (not r['_c'] or r['_c'].search(fc+' '+fd))]
def suggest(store,text,context='',uom='',limit=5,method=''):
    """Rank TT38 atomic norms for a BOQ line: rare words of the description weigh double, the heading path
    adds context; incompatible units and survey/test/repair appendices are down-weighted unless asked for."""
    context=re.sub(r'k[ếe]t c[ấa]u ph[ầa]n (tr[êe]n|d[ưu][ớo]i)','',str(context),flags=re.I)  # 'phần dưới' ≠ 'dưới nước'
    # BL58: text in brackets is usually a spec (cvdc ±160mm, phạm vi ống vách…): weigh it as context, not as the work name
    rules=matched_rules(store,text,context);pref=tuple(p for r in rules for p in r.get('prefer') or [])
    raw=fold(re.sub(r'\([^)]*\)',' ',str(text)))  # BL75: the BOQ's own words, before dictionary rewrites
    if not method and 'be tong' in raw:  # BL75: placing method written in the description itself
        method='THU_CONG' if 'thu cong' in raw else 'BOM' if re.search(r'\bbom\b',raw) else 'CAN_CAU' if 'can cau' in raw else ''
    text=str(text);context=context+' '+' '.join(re.findall(r'\(([^)]*)\)',text));text=re.sub(r'\([^)]*\)',' ',text)
    text=' '.join([text]+[r['rewrite'] for r in rules if r.get('rewrite')])
    text=synonyms(text);context=synonyms(context);docs,idf,inv=norm_index(store);dt=set(_toks(text));near=' '.join(str(context).split(' > ')[-2:]);ct=set(_toks(context))-dt
    fq=fold(text+' '+context);land='tren can' in fq;water='duoi nuoc' in fq
    fdesc=fold(text)
    qn=set(re.findall(r'\d+',fold(text)))-{'0','1'}
    head=(re.findall(r'[a-z]+',fold(str(context).split(' > ')[-1])) or [''])[0];md=METHODS.get(str(method or '').upper(),'')
    qb=_bigrams(text)|_bigrams(near)
    if not dt and not ct or lump_sum(uom):return []
    cand={}
    for w in dt|ct:
        for i in inv.get(w,()):cand[i]=1
    if pref:
        for i,(n,_,_) in enumerate(docs):
            if str(n.get('code','')).startswith(pref):cand[i]=1
    total=sum(2*idf.get(w,0) for w in dt)+sum(idf.get(w,0) for w in ct) or 1;u=_uom(uom);uc=_uclass(uom);ft=fold(text+' '+context);out=[]
    survey='khao sat' in ft;named=[k for k in ('be tong','cot thep','van khuon') if k in raw]
    for i in cand:
        n,t,b=docs[i];s=(sum(2*idf.get(w,0) for w in dt&t)+sum(idf.get(w,0) for w in ct&t))/total+min(0.45,0.15*len(qb&b))
        fd=fold(n.get('conditions',''))
        if (land and 'duoi nuoc' in fd and 'tren can' not in fd) or (water and 'tren can' in fd and 'duoi nuoc' not in fd):s*=0.6
        if any(a in fd and a not in fq for a in ACTIONS):s*=0.6
        nu=_uom(n.get('uom',''))
        if u and nu and u!=nu:
            nc=_uclass(n.get('uom',''));s*=0.45 if uc and nc and 'COUNT' in (uc,nc) and uc!=nc else 0.6
        ed=str(n.get('edition',''))
        test=any(k in ft for k in TESTW)
        if (' PL1' in ed and not test) or (' PL5' in ed and not test) or (' PL6' in ed and not any(k in ft for k in ('sua chua','bao duong','thay the'))):s*=0.7
        if test and (' PL1' in ed or ' PL5' in ed) and 'thi nghiem' in fd:s*=1.25  # a test line is priced by a test norm
        elif survey and ' PL1' in ed:s*=1.25  # BL75: a line under a survey heading is priced by a PL1 survey norm
        if qn:s+=min(0.1,0.05*len(qn&set(re.findall(r'\d+',fd))))  # BL58: C16 ~ BTNC16, D160, 9000kN columns
        tt=';'.join(fd.split(';')[:2])
        if any(k in tt and k not in fdesc for k in COMPONENTS):s*=0.7
        if named and not any(k in tt for k in named):s*=0.7  # BL75: BOQ names the component, the table title does not
        if head=='mong':s*=1.15 if 'mong' in fd else 0.6  # BL58: line under a 'Móng …' heading is a foundation element
        c=str(n.get('code',''))
        if md and c[:3]=='AF.' and c[3:4] in '123':s*=1.15 if c[3]==md else 0.85
        if c.startswith('AN.') and 'tro xi' not in ft:s*=0.6  # BL75: chapter AN is fly-ash/slag work only
        if pref and c.startswith(pref):s=s*1.5+0.3  # BL60 dictionary preference
        out.append((round(s,3),n))
    out.sort(key=lambda x:(-x[0],x[1].get('code','')))
    # one suggestion per source table (group heading from source_ref, else code prefix): best column first, sibling columns listed
    groups={}
    for s,n in out:
        m=GROUP_RE.search(str(n.get('source_ref','')));k=m.group(1) if m else str(n.get('code',''))[:6]
        if k not in groups:
            if len(groups)>=limit:continue  # keep scanning: sibling columns of the top tables may rank lower
            groups[k]={'score':s,'id':n.get('id'),'code':n.get('code'),'uom':n.get('uom'),'denominator':n.get('denominator'),'conditions':str(n.get('conditions',''))[:220],'parse_status':n.get('parse_status'),'unit_match':(not u or _uom(n.get('uom',''))==u),'columns':[]}
        g=groups[k]
        if len(g['columns'])<12:g['columns'].append({'id':n.get('id'),'code':n.get('code'),'column':str(n.get('conditions','')).split('; ')[-1][:60]})
    return list(groups.values())
def boq_path(boq,row):
    """Heading path of a BOQ line from parent WBS codes (1.2.2.1 -> descriptions of 1, 1.2, 1.2.2 …)."""
    by={str(r.get('source_code')):r for r in boq if r.get('source_code')};code=str(row.get('source_code') or '');parts=code.split('.');path=[]
    for k in range(1,len(parts)):
        p=by.get('.'.join(parts[:k]))
        if p and p is not row:path.append(str(p.get('description','')))
    return ' > '.join(path)
def suggest_items(store,s,item_ids=None,limit=5,method=''):
    boq={r.get('id'):r for r in s['boq']};out=[]
    for m in s['mapping']:
        if item_ids and m.get('id') not in item_ids:continue
        b=boq.get(m.get('source_line_id'),{});path=boq_path(s['boq'],b)
        u=m.get('uom') or b.get('uom') or ''
        rl=[{k:r.get(k) for k in ('id','flag','note','status')} for r in matched_rules(store,str(b.get('description','')),path)]
        out.append({'item_id':m.get('id'),'source_code':b.get('source_code'),'description':b.get('description'),'uom':u,'path':path,'note':'LUMP_SUM' if lump_sum(u) else '','rules':rl,'candidates':suggest(store,str(b.get('description','')),path,u,limit,method)})
    return out
def period_choice(rows,period):
    """Same period first; otherwise the latest earlier period (needs period_ref); later periods are never used."""
    same=[r for r in rows if r.get('period')==period]
    if same:return same,False
    earlier=sorted({r.get('period') for r in rows if r.get('period') and r.get('period')<period})
    return ([r for r in rows if r.get('period')==earlier[-1]],True) if earlier else ([],False)
def place_ok(price_loc,zone):
    """Exact zone, or a province-wide price for a zone inside that province ('Hưng Yên' for 'Hưng Yên - Vùng II')."""
    a=str(price_loc or '').strip();b=str(zone or '').strip()
    return bool(a) and bool(b) and (a==b or b.startswith(a+' ') or b.startswith(a+'-') or a.startswith(b+' –') or a.startswith(b+' -'))
def auto_prices(store,s):
    ctx=s['context'];have={(p.get('resource_code'),p.get('spec'),p.get('uom'),p.get('location')) for p in s['prices']}
    need=sorted(needed_price_keys(s)-have,key=lambda k:tuple(str(x) for x in k))
    by_code={};by_id={}
    for d in active(store,'PRICES'):
        for r in store.library_rows(d['id']):
            r=dict(r,library_dataset=d['id'],library_sha256=d['sha256'],library_name=f"{d['name']} · v{d['version']}")
            by_code.setdefault(r.get('resource_code'),[]).append(r);by_id[r.get('id')]=r
    masters=master_index(store);rows=[];unresolved=[]
    for code,spec,uom,zone in need:
        cands=[];how=''
        if code and (code.startswith('NC.') or MCODE.match(code)):
            cands=[r for r in by_code.get(code,[]) if r.get('currency')==ctx.get('currency') and str(r.get('uom')).lower()==str(uom).lower() and place_ok(r.get('location'),zone)];how='CODE'
        elif code and code.startswith('VL.'):
            ms=masters.get(code,[]);good=[m for m in ms if m.get('status') in ('STRONG','PROPOSED')];elsewhere=[]
            for m in good:
                for c in m.get('candidates',[]):
                    r=by_id.get(c.get('price_id'))
                    if not r or str(r.get('uom')).lower()!=str(uom).lower() or r.get('currency')!=ctx.get('currency'):continue
                    if place_ok(r.get('location'),zone):cands.append(r);how='MASTER_'+m['status']
                    else:elsewhere.append(r.get('location'))
            if not cands:how='VL_WEAK' if ms and not good else 'VL_ELSEWHERE' if elsewhere else 'VL_NOPRICE' if good else ''
        if not cands:
            reason={'CODE':'Không có giá cùng mã/đơn vị/vùng/tiền tệ trong thư viện','VL_WEAK':'Ghép vật tư chỉ ở mức yếu/không có (WEAK/NONE); gán thủ công bằng "Tìm & gán giá"','VL_NOPRICE':'Ứng viên ghép không còn trong bảng giá đang dùng','':'Mã chưa ghép (MTC.* hoặc mã tạm): gán thủ công bằng "Tìm & gán giá"'}.get(how) or ('Ứng viên giá ở địa bàn khác ('+', '.join(sorted({str(x)[:40] for x in elsewhere}))[:120]+'); cần giá vùng '+str(zone))
            unresolved.append({'resource_code':code,'spec':spec,'uom':uom,'zone':zone,'reason':reason});continue
        pick,earlier=period_choice(cands,ctx.get('period'))
        if not pick:unresolved.append({'resource_code':code,'spec':spec,'uom':uom,'zone':zone,'reason':'Chỉ có giá kỳ sau kỳ hồ sơ'});continue
        if len({r.get('unit_price') for r in pick})>1:unresolved.append({'resource_code':code,'spec':spec,'uom':uom,'zone':zone,'reason':f'{len(pick)} giá khác nhau cùng kỳ {pick[0].get("period")}; chọn thủ công'});continue
        r=pick[0]
        rows.append({'id':'auto-'+str(r.get('id')),'resource_code':code,'spec':spec,'uom':uom,'location':zone,'unit_price':r.get('unit_price'),'period':r.get('period'),'currency':r.get('currency'),'tax_basis':r.get('tax_basis'),'delivery':r.get('delivery'),'included':r.get('included',''),'source_ref':(r.get('source_ref') or '')+' · '+r['library_name'],'price_ref':'','period_ref':'','label':r.get('label',''),'mapped_from':{'match':how,'library_dataset':r['library_dataset'],'library_sha256':r['library_sha256'],'id':r.get('id'),'name':r.get('name'),'location':r.get('location'),'earlier_period':earlier}})
    return {'rows':rows,'unresolved':unresolved,'needed':len(need)}
# ---------- BL63: memory of QS choices, applied automatically to identical BOQ lines (user decision D37) ----------
UNCONFIRMED=re.compile(r'cần qs xác nhận|chưa qs|qs chưa xác nhận',re.I)
def memory_key(desc,uom):
    """Identical line = same description (accent/space/case folded, brackets kept) and same output unit."""
    return ' '.join(fold(desc).split())+'|'+_uom(uom or '')
def _items(s):
    boq={r.get('id'):r for r in s['boq']}
    for m in s['mapping']:
        b=boq.get(m.get('source_line_id'),{});u=m.get('uom') or b.get('uom') or ''
        yield m,b,u,memory_key(b.get('description',''),u)
def remember(store,s):
    """Record the step-3 choices of a gate-confirmed project: only library TT38 norms that the QS verified and justified."""
    if 3 not in s.get('confirmed',[]):return 0
    norms={n.get('id'):n for n in s['norms']};apps={}
    for a in s['applications']:apps.setdefault(a.get('item_id'),[]).append(a)
    lib={n.get('id') for d in active(store,'NORMS') for n in store.library_rows(d['id'])};rows=[]
    for m,b,u,key in _items(s):
        for a in apps.get(m.get('id'),[]):
            n=norms.get(a.get('norm_id'),{})
            # D47: a per-application QS basis (pilot import) wins over the norm-level one shared by other items
            sel=str(a.get('selection_ref') or n.get('selection_ref') or '').strip();verified=a.get('table_verified',n.get('table_verified'))
            if a.get('norm_id') not in lib or verified is not True or n.get('table_verified') is not True or not sel:continue
            if UNCONFIRMED.search(sel):continue  # BL70: a basis that says it still needs QS confirmation is not a QS choice
            if any(UNCONFIRMED.search(str(m.get(k) or '')) for k in ('norm_match_ref','method','technical_spec')):continue  # D47: item facts not confirmed by QS
            rows.append({'created':__import__('store').now(),'project_id':s['id'],'project_name':s.get('name'),'revision':s['revision'],'item_id':m.get('id'),'key':key,'uom':u,'description':b.get('description'),'path':boq_path(s['boq'],b),'norm_id':a.get('norm_id'),'norm_code':n.get('code'),'qty_factor':str(a.get('qty_factor') or '1'),'factor_ref':a.get('factor_ref'),'conversion_ref':a.get('conversion_ref'),'selection_ref':sel,'source_ref':b.get('source_ref')})
    return store.choices_add(rows)
def _choice_sets(hits):
    """Group remembered rows by (project, revision, item): one QS decision = the set of (norm, factor) it composed."""
    g={}
    for h in hits:g.setdefault((h['project_id'],h['revision'],h['item_id']),[]).append(h)
    return {k:tuple(sorted((h['norm_id'],h['qty_factor']) for h in v)) for k,v in g.items()},g
def memory_for(store,s,item_ids=None):
    want=[(m,key) for m,b,u,key in _items(s) if not item_ids or m.get('id') in item_ids];by={}
    for h in store.choices_for([k for _,k in want]):by.setdefault(h['key'],[]).append(h)
    out={}
    for m,key in want:
        hits=by.get(key,[])
        if not hits:continue
        sets,groups=_choice_sets(hits);distinct=set(sets.values());last=groups[max(groups,key=lambda k:groups[k][-1]['id'])]
        out[m['id']]={'status':'CONFLICT' if len(distinct)>1 else 'UNIQUE','decisions':len(sets),'choices':[{'norm_id':h['norm_id'],'code':h['norm_code'],'qty_factor':h['qty_factor'],'project':h['project_name'],'revision':h['revision'],'created':h['created'],'selection_ref':h['selection_ref'],'factor_ref':h['factor_ref'],'conversion_ref':h['conversion_ref']} for h in last]}
    return out
def apply_memory(store,s):
    """Compose remembered choices for items that have no recipe yet. Applies only when every remembered decision for the
    identical line agrees (else CONFLICT, nothing guessed). Item facts (technical_spec, method, norm_match_ref) are not copied."""
    have={a.get('item_id') for a in s['applications']};mem=memory_for(store,s);norms={n.get('id') for n in s['norms']}
    out={'norms':[],'resources':[],'applications':[],'applied':[],'conflicts':[],'skipped_has_recipe':[]}
    for iid,mm in mem.items():
        if iid in have:out['skipped_has_recipe'].append(iid);continue
        if mm['status']=='CONFLICT':out['conflicts'].append({'item_id':iid,'decisions':mm['decisions']});continue
        for c in mm['choices']:
            prov=f"Theo lựa chọn QS đã nhớ: hồ sơ «{c['project']}» PB {c['revision']} ({str(c['created'])[:10]}); căn cứ gốc: {c['selection_ref']}"
            if c['norm_id'] not in norms:
                d=norm_detail(store,c['norm_id']);n,lines=for_project(d['norm'],d['lines'])
                n=dict(n,selection_ref=prov,table_verified=True,table_verified_ref='QS đã kiểm bảng ở hồ sơ «'+str(c['project'])+'» PB '+str(c['revision']),qs_memory=True)
                out['norms'].append(n);out['resources']+=lines;norms.add(c['norm_id'])
            a={'id':str(__import__('uuid').uuid4()),'item_id':iid,'norm_id':c['norm_id'],'qty_factor':c['qty_factor'],'qs_memory':prov}
            if c.get('factor_ref'):a['factor_ref']=c['factor_ref']+' (theo lựa chọn QS đã nhớ)'
            if c.get('conversion_ref'):a['conversion_ref']=c['conversion_ref']+' (theo lựa chọn QS đã nhớ)'
            out['applications'].append(a)
        out['applied'].append(iid)
    return out
