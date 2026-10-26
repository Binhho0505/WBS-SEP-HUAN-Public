"""E21 (D85): one UI for the estimate app (8765) and CERP-QTO (8770).

CERP-QTO stays a separate service (D62). This module makes 8765 the single front door:
  * proxy — the browser only talks to 8765; `/v1/*`, `/healthz` and `/qto/ui/*` are forwarded to the CERP-QTO service on
    loopback and the CERP-QTO bearer token is attached here (stored once in runtime/qto_settings.json, like the AI keys; never
    returned to the page). The CERP-QTO review UI is embedded in the 8765 shell (`/qto/ui/?embedded=1`), so the user never
    pastes a token or types a project code twice. Only loopback upstreams are allowed.
  * import — approved take-off items of the linked CERP-QTO project become quantity CANDIDATES of the estimate project
    (same shape as the local PDF/DXF candidates of E14): the BOQ of the consultant (AB) is never changed; the QS confirms each
    candidate against an AB line with a factor and a basis, and the app only reports the deviation. A candidate whose WBS code
    and unit match an AB line gets a SUGGESTION, not an assignment. Re-import is idempotent per take-off item id; a newer
    version of the same item key replaces the value and keeps the confirmed assignment flagged as "updated".
"""
import http.client,json,os,re,uuid
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlsplit
from domain import index,same_uom,number
DEFAULT_URL='http://127.0.0.1:8770'
PROXY_PREFIXES=('/v1/','/healthz','/qto/ui/','/qto/ui')
HOP=('connection','keep-alive','transfer-encoding','te','trailer','upgrade','proxy-authenticate','proxy-authorization','content-length','host')
def now():return datetime.now(timezone.utc).isoformat(timespec='seconds')
class Settings:
    """runtime/qto_settings.json: {'url':..., 'token':...}. The token is write-only from the UI."""
    def __init__(self,path):self.path=Path(path)
    def load(self):
        try:d=json.loads(self.path.read_text(encoding='utf-8'))
        except (FileNotFoundError,json.JSONDecodeError):d={}
        d.setdefault('url',os.environ.get('CC1_QTO_URL',DEFAULT_URL));d.setdefault('token',os.environ.get('CC1_QTO_TOKEN',''));return d
    def save(self,d):
        self.path.parent.mkdir(parents=True,exist_ok=True);tmp=self.path.with_suffix('.tmp');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(tmp,self.path)
    def set(self,url=None,token=None):
        d=self.load()
        if url is not None:
            u=urlsplit(str(url).strip() or DEFAULT_URL)
            if u.scheme!='http' or u.hostname not in ('127.0.0.1','localhost','::1'):raise ValueError('CERP-QTO chỉ được nối qua loopback (http://127.0.0.1:cổng).')
            d['url']=f'{u.scheme}://{u.hostname}:{u.port or 80}'
        if token is not None:d['token']=str(token).strip()
        self.save(d);return d
def _conn(url,timeout):
    u=urlsplit(url);return http.client.HTTPConnection(u.hostname,u.port or 80,timeout=timeout)
def call(settings,method,path,body=None,headers=None,timeout=30):
    """One upstream call; returns (status, headers dict lower-cased, bytes). Raises ConnectionError when the service is down."""
    d=settings.load();h={'Accept':'application/json'}
    if d.get('token'):h['Authorization']='Bearer '+d['token']
    h.update(headers or {})
    try:
        c=_conn(d['url'],timeout);c.request(method,path,body=body,headers=h);r=c.getresponse();data=r.read();hs={k.lower():v for k,v in r.getheaders()};c.close()
    except (OSError,http.client.HTTPException) as e:raise ConnectionError(f'Không nối được CERP-QTO tại {d["url"]} ({type(e).__name__}). Khởi động service bóc khối lượng rồi thử lại.') from None
    return r.status,hs,data
def call_json(settings,method,path,payload=None):
    body=json.dumps(payload).encode() if payload is not None else None
    st,hs,data=call(settings,method,path,body,{'Content-Type':'application/json'} if body else None)
    try:j=json.loads(data) if data else None
    except ValueError:j={'detail':data[:200].decode('utf-8','replace')}
    if st>=400:raise PermissionError(f'CERP-QTO trả {st}: '+str((j or {}).get('detail') or '')) if st in (401,403) else ValueError(f'CERP-QTO trả {st}: '+str((j or {}).get('detail') or ''))
    return j
def status(settings):
    """What the UI needs before showing the drawing workbench: service reachable, token set and valid, user/roles/projects."""
    d=settings.load();out={'url':d['url'],'token_set':bool(d.get('token')),'service':'DOWN','me':None,'error':None}
    try:
        st,_,_=call(settings,'GET','/healthz',timeout=3);out['service']='UP' if st==200 else f'HTTP {st}'
        if d.get('token'):
            try:out['me']=call_json(settings,'GET','/v1/me')
            except PermissionError as e:out['error']='Token CERP-QTO không hợp lệ hoặc hết hạn.'
    except ConnectionError as e:out['error']=str(e)
    return out
# ---------- proxy ----------
def wants_proxy(path):return path.startswith(PROXY_PREFIXES)
def proxy(h,settings,method):
    """Forward the current request of handler `h` upstream. Static UI goes under /qto/ui/ upstream too (CERP-QTO mounts /ui).
    Headers added upstream: Authorization (when the page sent none or an empty bearer). Headers rewritten downstream: the
    CERP-QTO CSP (frame-ancestors 'none') is replaced so the UI may be framed by 8765 itself; everything is no-store."""
    d=settings.load();path=h.path
    if path.startswith('/qto/ui'):path=path[len('/qto'):]
    length=int(h.headers.get('Content-Length') or 0);body=h.rfile.read(length) if length else None
    up={}
    for k,v in h.headers.items():
        if k.lower() in HOP or k.lower() in ('origin','referer','cookie','x-cc1-session'):continue
        up[k]=v
    auth=up.get('Authorization','').strip()
    if (not auth or auth.lower()=='bearer') and d.get('token'):up['Authorization']='Bearer '+d['token']
    try:
        c=_conn(d['url'],120);c.request(method,path,body=body,headers=up);r=c.getresponse();data=r.read();hs=r.getheaders();c.close()
    except (OSError,http.client.HTTPException) as e:
        return h.reply({'detail':f'Không nối được CERP-QTO tại {d["url"]} ({type(e).__name__}). Khởi động service bóc khối lượng (start-api.cmd, start-worker.cmd) rồi thử lại.'},503)
    h.send_response(r.status)
    for k,v in hs:
        kl=k.lower()
        if kl in HOP or kl in ('content-security-policy','set-cookie'):continue
        h.send_header(k,v)
    if path.startswith('/ui'):h.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'self'; base-uri 'none'")
    h.send_header('Content-Length',str(len(data)));h.send_header('Cache-Control','no-store');h.end_headers();h.wfile.write(data)
# ---------- link + import ----------
def link_project(store,s,body):
    code=str(body.get('qto_project') or '').strip()[:100]
    if body.get('revision')!=s['revision']:raise PermissionError('Hồ sơ đã đổi ở cửa sổ khác; tải lại.')
    s['context']['qto_project']=code or None;return store.put(s,s['revision'],'LINK_QTO_PROJECT')
def _latest(items):
    last={}
    for it in items:
        k=it['item_key']
        if k not in last or int(it['version'])>int(last[k]['version']):last[k]=it
    return list(last.values())
def import_takeoff(store,settings,s,body):
    """Pull approved take-off items of the linked CERP-QTO project into the estimate project as candidates (source QTO)."""
    if body.get('revision')!=s['revision']:raise PermissionError('Hồ sơ đã đổi ở cửa sổ khác; tải lại.')
    code=s['context'].get('qto_project')
    if not code:raise ValueError('Chưa chọn dự án CERP-QTO cho hồ sơ này.')
    items=_latest([x for x in call_json(settings,'GET',f'/v1/projects/{code}/takeoff-items') or [] if x.get('status') in ('approved','pushed')])
    ab=[r for r in s['boq'] if r.get('kind')=='MEASURED'];by_code={}
    for r in ab:by_code.setdefault(str(r.get('source_code') or '').strip(),[]).append(r)
    dr=next((x for x in s.get('drawings') or [] if x.get('type')=='QTO' and (x.get('qto') or {}).get('project')==code),None)
    if not dr:
        dr={'id':str(uuid.uuid4()),'sha256':None,'filename':f'CERP-QTO · dự án {code}','type':'QTO','label':'Takeoff đã duyệt (CERP-QTO)','revision_label':'','wbs_hint':'','candidates':0,'qto':{'project':code,'url':settings.load()['url']}}
        s.setdefault('drawings',[]).append(dr)
    existing={t['id']:t for t in s.get('takeoffs') or [] if str(t['id']).startswith('qto:')}
    by_key={(t.get('qto') or {}).get('item_key'):t for t in existing.values() if (t.get('qto') or {}).get('project')==code}
    added=updated=unchanged=0;seen=set()
    for it in items:
        tid='qto:'+str(it['id']);seen.add(tid);key=it['item_key'];unit=it.get('unit')
        cands=[r for r in by_code.get(str(it.get('wbs_code') or '').strip(),[]) if same_uom(r.get('uom'),unit)]
        sug={'ab_line_id':cands[0]['id'],'reason':'Cùng mã WBS và đơn vị với BOQ AB'} if len(cands)==1 else ({'ab_line_id':None,'reason':f'{len(cands)} dòng AB cùng mã WBS — chọn tay'} if cands else None)
        rec={'id':tid,'drawing_id':dr['id'],'kind':'QTO_ITEM','text':str(it.get('description') or key)[:200],'value':str(it['quantity']),'uom':unit,
             'source':{'qto_project':code,'item_key':key,'version':int(it['version']),'measurements':len(it.get('basis') or []),'wbs_code':it.get('wbs_code'),'norm_code':it.get('norm_code'),'cbs_code':it.get('cbs_code')},
             'qto':{'project':code,'item_id':str(it['id']),'item_key':key,'version':int(it['version']),'status':it.get('status'),'imported_at':now()},'suggestion':sug,'assign':None}
        if tid in existing:
            old=existing[tid];rec['assign']=old.get('assign');rec['qto']['imported_at']=old['qto'].get('imported_at');old.clear();old.update(rec);unchanged+=1;continue
        prev=by_key.get(key)
        if prev:  # newer version of the same item key: keep the QS decision, flag it
            a=prev.get('assign')
            if a and a.get('status')=='CONFIRMED':a=dict(a,updated_from=prev['qto']['version'],updated_at=now())
            rec['assign']=a;s['takeoffs']=[t for t in s['takeoffs'] if t['id']!=prev['id']];updated+=1
        else:added+=1
        s.setdefault('takeoffs',[]).append(rec)
    dr['candidates']=sum(1 for t in s.get('takeoffs') or [] if t.get('drawing_id')==dr['id']);dr['qto']['imported_at']=now();dr['qto']['items']=len(items)
    s=store.put(s,s['revision'],'IMPORT_QTO_TAKEOFF')
    return s,{'items':len(items),'added':added,'updated':updated,'unchanged':unchanged,'suggested':sum(1 for t in s['takeoffs'] if t['id'] in seen and (t.get('suggestion') or {}).get('ab_line_id'))}
def review(s,threshold_pct=None):
    """Thẩm định: every QTO candidate with its suggestion / decision, and per AB line the confirmed drawing quantity vs the
    consultant's BOQ quantity. `threshold_pct` only flags; it never changes a number."""
    import drawings
    ab=index(s['boq']);th=number(threshold_pct) if threshold_pct not in (None,'') else None
    cands=[t for t in s.get('takeoffs') or [] if str(t['id']).startswith('qto:')]
    rows=drawings.compare(s)
    for r in rows:
        d=number(r.get('deviation_pct'));r['flag']=None if d is None or th is None else ('FLAG' if abs(d)>th else 'OK')
    covered={r['ab_line_id'] for r in rows}
    missing=[{'ab_line_id':r['id'],'wbs_code':r.get('source_code'),'description':r.get('description'),'uom':r.get('uom'),'boq_quantity':r.get('quantity')} for r in s['boq'] if r.get('kind')=='MEASURED' and r['id'] not in covered]
    return {'candidates':cands,'compare':rows,'no_takeoff':missing,'counts':{'candidates':len(cands),'confirmed':sum(1 for t in cands if (t.get('assign') or {}).get('status')=='CONFIRMED'),
            'rejected':sum(1 for t in cands if (t.get('assign') or {}).get('status')=='REJECTED'),'open':sum(1 for t in cands if not t.get('assign')),'flagged':sum(1 for r in rows if r.get('flag')=='FLAG'),'no_takeoff':len(missing)},
            'threshold_pct':str(th) if th is not None else None}
