"""E14 (D59): technical drawings and quantity take-off CANDIDATES.

A candidate is a number read from a drawing with its source (PDF page + bbox / table, DXF layer + handle). It never becomes
a BOQ quantity: the QS assigns it to an AB line with a conversion factor and basis, confirms or rejects it, and the app only
reports the deviation against the BOQ quantity (the AB source stays immutable).
Libraries: pdfplumber (already in .venv) for PDF text layers; DXF is parsed from its ASCII group codes here. Scanned PDFs
(no text layer), DWG binaries and IFC are not read in v1 (PRD §8 Q2).
"""
import io,math,re,uuid
from decimal import Decimal
from domain import number,index,same_uom
UNIT=r'(m3|m³|m2|m²|md|m|kg|tấn|tan|t|cái|cai|bộ|bo|cọc|coc)'
NUM=r'(\d{1,3}(?:[.\s]\d{3})*(?:,\d+)?|\d+(?:[.,]\d+)?)'
PAIR=re.compile(NUM+r'\s*'+UNIT+r'(?![a-zà-ỹ0-9])',re.I)
UNITS={'m³':'m3','m²':'m2','tan':'tấn','t':'tấn','cai':'cái','bo':'bộ','coc':'cọc','md':'m'}
INSUNITS={1:'in',2:'ft',4:'mm',5:'cm',6:'m'}
def to_num(t):
    t=str(t).strip().replace(' ','')
    if ',' in t and '.' in t:t=t.replace('.','').replace(',','.')
    elif ',' in t:t=t.replace(',','.')
    elif re.fullmatch(r'\d{1,3}(\.\d{3})+',t):t=t.replace('.','')
    return number(t)
def kind_of(filename):
    n=str(filename).lower()
    if n.endswith('.pdf'):return 'PDF'
    if n.endswith('.dxf'):return 'DXF'
    raise ValueError('Bản vẽ v1 nhận PDF (có lớp chữ) hoặc DXF ASCII. DWG/IFC/ảnh quét chưa hỗ trợ (cần thư viện — PRD §8).')
def pdf_candidates(data):
    import pdfplumber
    out=[];text_pages=0
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for pno,page in enumerate(pdf.pages,1):
            words=page.extract_words(keep_blank_chars=False,use_text_flow=True) or []
            if words:text_pages+=1
            lines={}
            for w in words:lines.setdefault(round(w['top']/3),[]).append(w)
            for key in sorted(lines):
                ws=sorted(lines[key],key=lambda w:w['x0']);line=' '.join(w['text'] for w in ws)
                for m in PAIR.finditer(line):
                    v=to_num(m.group(1))
                    if v is None or v==0:continue
                    out.append({'kind':'PDF_TEXT','text':line[:200],'value':format(v,'f'),'uom':UNITS.get(m.group(2).lower(),m.group(2).lower()),
                                'source':{'page':pno,'bbox':[round(ws[0]['x0'],1),round(ws[0]['top'],1),round(ws[-1]['x1'],1),round(ws[-1]['bottom'],1)]}})
            for ti,table in enumerate(page.extract_tables() or []):
                head=[str(c or '').lower() for c in (table[0] if table else [])]
                ucol=next((i for i,h in enumerate(head) if 'đơn vị' in h or 'dvt' in h or 'đvt' in h),None)
                qcol=next((i for i,h in enumerate(head) if 'khối lượng' in h or 'kl' == h.strip() or 'tổng' in h or 'số lượng' in h),None)
                if ucol is None or qcol is None:continue
                for ri,row in enumerate(table[1:],2):
                    v=to_num(row[qcol]) if qcol<len(row) else None;u=str(row[ucol] or '').strip() if ucol<len(row) else ''
                    if v is None or v==0 or not u:continue
                    out.append({'kind':'PDF_TABLE','text':' | '.join(str(c or '') for c in row)[:200],'value':format(v,'f'),'uom':UNITS.get(u.lower(),u),'source':{'page':pno,'table':ti+1,'row':ri}})
    if not text_pages:raise ValueError('PDF không có lớp chữ (bản quét): v1 chưa đọc OCR.')
    return out
def _pairs(text):
    lines=text.splitlines()
    for i in range(0,len(lines)-1,2):yield lines[i].strip(),lines[i+1].strip()
def dxf_candidates(data):
    try:text=data.decode('utf-8')
    except UnicodeDecodeError:text=data.decode('cp1252',errors='replace')
    if 'SECTION' not in text[:2000]:raise ValueError('DXF phải là định dạng ASCII (DXF nhị phân/DWG chưa hỗ trợ).')
    units=None;ents=[];cur=None;in_ent=False;prev=None;in_hdr=False
    for code,val in _pairs(text):
        if code=='2' and prev==('0','SECTION'):in_ent=val=='ENTITIES';in_hdr=val=='HEADER'
        if in_hdr and code=='9' and val=='$INSUNITS':units='?'
        elif in_hdr and units=='?' and code=='70':units=INSUNITS.get(int(val),'chưa rõ')
        if in_ent and code=='0':
            if cur:ents.append(cur)
            cur={'type':val,'pts':[],'layer':'0','handle':None,'flags':0,'text':None,'block':None} if val in ('LINE','LWPOLYLINE','INSERT','TEXT','MTEXT','CIRCLE') else None
        elif in_ent and cur is not None:
            if code=='8':cur['layer']=val
            elif code=='5':cur['handle']=val
            elif code=='70':cur['flags']=int(float(val))
            elif code=='2':cur['block']=val
            elif code in ('1',):cur['text']=val
            elif code=='40':cur['r']=float(val)
            elif code in ('10','11'):cur['pts'].append([float(val),None])
            elif code in ('20','21') and cur['pts'] and cur['pts'][-1][1] is None:cur['pts'][-1][1]=float(val)
        if code=='0' and val=='ENDSEC':
            if cur:ents.append(cur)
            cur=None;in_ent=False;in_hdr=False
        prev=(code,val)
    lengths={};areas={};blocks={};out=[];u=units if units not in (None,'?') else 'chưa rõ'
    for e in ents:
        p=[x for x in e['pts'] if x[1] is not None]
        if e['type'] in ('LINE','LWPOLYLINE') and len(p)>=2:
            seg=sum(math.dist(p[i],p[i+1]) for i in range(len(p)-1))
            closed=e['type']=='LWPOLYLINE' and e['flags']&1
            if closed:seg+=math.dist(p[-1],p[0]);a=abs(sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p))))/2;areas.setdefault(e['layer'],[0,[]]);areas[e['layer']][0]+=a;areas[e['layer']][1].append(e['handle'])
            lengths.setdefault(e['layer'],[0,[]]);lengths[e['layer']][0]+=seg;lengths[e['layer']][1].append(e['handle'])
        elif e['type']=='CIRCLE' and e.get('r'):
            lengths.setdefault(e['layer'],[0,[]]);lengths[e['layer']][0]+=2*math.pi*e['r'];lengths[e['layer']][1].append(e['handle'])
        elif e['type']=='INSERT':
            k=(e['layer'],e['block']);blocks.setdefault(k,[0,[]]);blocks[k][0]+=1;blocks[k][1].append(e['handle'])
        elif e['type'] in ('TEXT','MTEXT') and e['text']:
            for m in PAIR.finditer(e['text']):
                v=to_num(m.group(1))
                if v:out.append({'kind':'DXF_TEXT','text':e['text'][:200],'value':format(v,'f'),'uom':UNITS.get(m.group(2).lower(),m.group(2).lower()),'source':{'layer':e['layer'],'handle':e['handle']}})
    for layer,(v,h) in sorted(lengths.items()):out.append({'kind':'DXF_LENGTH','text':f'Tổng chiều dài lớp {layer}','value':format(Decimal(str(round(v,4))),'f'),'uom':'đơn vị bản vẽ ('+u+')','source':{'layer':layer,'handles':h[:50],'count':len(h),'insunits':u}})
    for layer,(v,h) in sorted(areas.items()):out.append({'kind':'DXF_AREA','text':f'Tổng diện tích đường đa tuyến kín lớp {layer}','value':format(Decimal(str(round(v,4))),'f'),'uom':'đơn vị bản vẽ² ('+u+')','source':{'layer':layer,'handles':h[:50],'count':len(h),'insunits':u}})
    for (layer,b),(n,h) in sorted(blocks.items(),key=lambda x:(x[0][0],str(x[0][1]))):out.append({'kind':'DXF_BLOCK','text':f'Số khối (block) {b} trên lớp {layer}','value':str(n),'uom':'cái','source':{'layer':layer,'block':b,'handles':h[:50]}})
    if not out:raise ValueError('DXF không có đối tượng đo được (LINE/LWPOLYLINE/CIRCLE/INSERT/TEXT) trong ENTITIES.')
    return out
def add(s,body,sha,data):
    k=kind_of(body.get('filename'));cands=pdf_candidates(data) if k=='PDF' else dxf_candidates(data)
    did=str(uuid.uuid4())
    s.setdefault('drawings',[]).append({'id':did,'sha256':sha,'filename':str(body.get('filename'))[:200],'type':k,'label':str(body.get('label') or '')[:200],'revision_label':str(body.get('revision_label') or '')[:50],'wbs_hint':str(body.get('wbs_hint') or '')[:100],'candidates':len(cands)})
    s.setdefault('takeoffs',[]).extend({'id':str(uuid.uuid4()),'drawing_id':did,**c,'assign':None} for c in cands[:5000])
    return s,{'drawing_id':did,'candidates':len(cands),'kept':min(len(cands),5000)}
def assign(s,body):
    t=next((x for x in s.get('takeoffs') or [] if x['id']==body.get('takeoff_id')),None)
    if not t:raise ValueError('Không có ứng viên khối lượng này.')
    st=body.get('status')
    if st=='CLEAR':t['assign']=None;return s
    if st=='REJECTED':t['assign']={'status':'REJECTED','reason':str(body.get('reason') or '')[:500]};return s
    if st!='CONFIRMED':raise ValueError('Trạng thái phải là xác nhận (CONFIRMED), loại (REJECTED) hoặc bỏ chọn (CLEAR).')
    ab=index(s['boq']).get(body.get('ab_line_id'))
    if not ab or ab.get('kind')!='MEASURED':raise ValueError('Chọn dòng BOQ AB đo được để gán.')
    f=number(body.get('factor'))
    if f is None or f<=0:raise ValueError('Hệ số quy đổi phải > 0 (1 nếu cùng đơn vị).')
    if not str(body.get('factor_ref') or '').strip():raise ValueError('Nhập căn cứ hệ số quy đổi/đơn vị (vd bản vẽ đơn vị mm → m: 0,001).')
    t['assign']={'status':'CONFIRMED','ab_line_id':ab['id'],'factor':format(f,'f'),'factor_ref':str(body['factor_ref'])[:500],'by':str(body.get('by') or '')[:200]}
    return s
def compare(s):
    """Σ confirmed candidates × factor per AB line vs the BOQ quantity; the BOQ itself is never changed."""
    ab=index(s['boq']);tot={}
    for t in s.get('takeoffs') or []:
        a=t.get('assign') or {}
        if a.get('status')!='CONFIRMED':continue
        v=number(t['value']);f=number(a['factor'])
        if v is None or f is None:continue
        d=tot.setdefault(a['ab_line_id'],{'value':Decimal(0),'n':0});d['value']+=v*f;d['n']+=1
    out=[]
    for i,d in tot.items():
        r=ab.get(i) or {};q=number(r.get('quantity'))
        out.append({'ab_line_id':i,'wbs_code':r.get('source_code'),'description':r.get('description'),'uom':r.get('uom'),'boq_quantity':r.get('quantity'),'drawing_quantity':format(d['value'].quantize(Decimal('0.0001')),'f'),'candidates':d['n'],
                    'deviation_pct':format(((d['value']-q)/q*100).quantize(Decimal('0.1')),'f') if q else None})
    return out
