"""D59 routes for E10–E16 (packages, quotes, award, progress, drawings, library tools, dictionaries, PM models, packs) and E17 PAKD (D76).

server.py calls get()/post() first; they return True when they answered. Mutations need the local session token (checked
by server.guard) and the project revision (optimistic lock → 409), exactly like the 8-step API.
"""
import base64,hashlib,os,re,tempfile,json
from pathlib import Path
import copy
import subcontract as sc,libtools,pmmodels,drawings,packs,pakd,contracts,erp_bridge
from domain import status
XLSX='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';ZIP='application/zip'
def _proj(h,pid):return h.server.store.get(pid)
def _rev(h,s,body):
    if body.get('revision')!=s['revision']:
        h.reply({'error':'Hồ sơ đã đổi; tải lại để tránh ghi đè.'},409);return False
    return True
def _file(body):
    data=base64.b64decode(body.get('data') or '',validate=True)
    if not data:raise ValueError('File rỗng.')
    return data,hashlib.sha256(data).hexdigest()
def view(h,s):
    models=pmmodels.models(h.server.store);sub=sc.summary(s,models);st=status(s);m=models.get(s['context'].get('pm_model'))
    return {'project':s,'revision':s['revision'],'packages':s.get('packages') or [],'quotes':[{k:v for k,v in q.items() if k!='rows'}|{'rows':len(q['rows'])} for q in s.get('quotes') or []],
            'progress_entries':s.get('progress') or [],'drawings':s.get('drawings') or [],'takeoffs':s.get('takeoffs') or [],'takeoff_compare':drawings.compare(s),
            'summary':sub,'pm_model':s['context'].get('pm_model'),'models':{k:{'name':v['name'],'status':v['status'],'procurement_methods':v.get('procurement_methods',{})} for k,v in models.items()},
            'checklist':pmmodels.checklist(s,m,st,sub) if m else [],'wbs_ready':st[2]['confirmed'],'pakd':pakd.view(s,sub),'contracts':contracts.view(s),'package_usage':sc.package_usage(s),'erp':erp_bridge.summary(s)}
def get(h,path,params):
    store=h.server.store
    if path=='/api/pm-models':return h.reply({'models':pmmodels.models(store),'status':pmmodels.STATUS}) or True
    if path=='/api/dictionaries.xlsx':
        pid=params.get('project',[None])[0];s=store.get(pid) if pid else None
        return h.send(libtools.dictionaries_workbook(store,s),XLSX,filename='TU_DIEN_MA_CC1_DU_THAO.xlsx') or True
    m=re.fullmatch(r'/api/projects/([0-9a-f-]+)/contracts/([0-9a-f-]+)\.xlsx',path)
    if m:
        s=_proj(h,m.group(1));c=contracts._get(s,m.group(2))
        return h.send(contracts.workbook(s,c['id']),XLSX,filename=f'HO_SO_HD_NTP_{c["package_code"]}_{c["status"]}_r{s["revision"]}.xlsx') or True
    m=re.fullmatch(r'/api/projects/([0-9a-f-]+)/(subcontract|pakd\.xlsx|tender-pack\.zip|procurement-pack\.zip|bb/(GT-\d{2,3})\.xlsx)',path)
    if not m:return False
    s=_proj(h,m.group(1));what=m.group(2)
    if what=='pakd.xlsx':
        ver=params.get('version',[None])[0];sid=params.get('scenario',[None])[0]
        return h.send(pakd.workbook(s,sid,ver),XLSX,filename=f'PAKD_BM01_{s["context"].get("project_code") or s["id"][:8]}_r{s["revision"]}{"_CHOT" if ver else ""}.xlsx') or True
    if what=='subcontract':return h.reply(view(h,s)) or True
    if what=='tender-pack.zip':
        est=None
        if all(x['confirmed'] for x in status(s)):
            from exporter import workbook
            fd,tmp=tempfile.mkstemp(suffix='.xlsx',dir=str(h.server.export_dir));os.close(fd)
            try:workbook(s,store.events(s['id']),Path(tmp));est=Path(tmp).read_bytes()
            finally:Path(tmp).unlink(missing_ok=True)
        return h.send(packs.tender_pack(s,store,store.events(s['id']),est),ZIP,filename=f'HO_SO_DAU_THAU_{s["context"].get("project_code") or s["id"][:8]}_r{s["revision"]}.zip') or True
    if what=='procurement-pack.zip':return h.send(packs.procurement_pack(s,store),ZIP,filename=f'HO_SO_CHAO_THAU_GIAO_THAU_{s["context"].get("project_code") or s["id"][:8]}_r{s["revision"]}.zip') or True
    code=m.group(3);internal=params.get('internal',['0'])[0]=='1'
    sub=next((x for x in sc.summary(s,pmmodels.models(store))['packages'] if x['code']==code),None) if internal else None
    return h.send(packs.bb_workbook(s,code,internal,sub),XLSX,filename=f'BOQ_BB_{code}{"_NOI_BO" if internal else ""}_r{s["revision"]}.xlsx') or True
def post(h,path,body):
    store=h.server.store
    if path=='/api/dictionaries/import':return h.reply(libtools.import_dictionary(store,body),201 if not body.get('dry_run',True) else 200) or True
    m=re.fullmatch(r'/api/projects/([0-9a-f-]+)/manage',path)  # D84: menu ⋮ of the project list
    if m:
        import projects_admin
        try:r=projects_admin.manage(store,m.group(1),body)
        except PermissionError as e:return h.reply({'error':str(e)},409) or True
        return h.reply(dict(r,projects=store.list())) or True
    m=re.fullmatch(r'/api/library/([0-9a-f-]+)/(derive|activate)',path)
    if m:
        if m.group(2)=='derive':return h.reply(libtools.derive(store,m.group(1),body),201) or True
        return h.reply({'dataset':store.library_activate(m.group(1)),'datasets':store.library_list()}) or True
    m=re.fullmatch(r'/api/projects/([0-9a-f-]+)/(packages|packages/add-lines|packages/delete|quotes|award|progress|drawings|takeoff-assign|pakd|contracts|erp-packages|erp-pakd)',path)
    if not m:return False
    s=_proj(h,m.group(1));what=m.group(2)
    if not _rev(h,s,body):return True
    extra={};old=copy.deepcopy(s)
    if what=='packages':
        pm=body.get('pm_model')
        if pm not in (None,'') and pm not in pmmodels.models(store):raise ValueError('Mô hình QLDA không hợp lệ.')
        s=sc.save(s,body);action='SAVE_PACKAGES'
    elif what=='packages/add-lines':s,extra=sc.add_lines(s,body);action='SAVE_PACKAGES_ADD_LINES'
    elif what=='packages/delete':s,rep=sc.delete_packages(s,body);extra={'deleted':rep};action='DELETE_DRAFT_PACKAGES'
    elif what=='erp-packages':s,extra=erp_bridge.packages_from_erp(s,body);action='IMPORT_ERP_PACKAGES'  # D87
    elif what=='erp-pakd':s,extra=erp_bridge.pakd_from_erp(s,body);action='IMPORT_ERP_PAKD'
    elif what=='quotes':
        data,sha=_file(body);rows=sc.parse_quote(body.get('filename'),data);store.upload(sha,str(body.get('filename'))[:200],data)
        s=sc.add_quote(s,body,sha,rows);action='ADD_SUBCONTRACT_QUOTE';extra={'rows':len(rows)}
    elif what=='award':s=sc.save_award(s,body);action='SAVE_AWARD_DRAFT'
    elif what=='progress':s=sc.add_progress(s,body);action='ADD_SUBCONTRACT_PROGRESS'
    elif what=='pakd':s=pakd.act(s,body);action='PAKD_'+str(body.get('action')).upper()
    elif what=='contracts':
        f=None
        if body.get('data'):data,sha=_file(body);name=str(body.get('filename') or 'file')[:200];store.upload(sha,name,data);f=(name,data,sha)
        s=contracts.act(s,body,f);action='CONTRACT_'+str(body.get('action')).upper()
    elif what=='drawings':
        data,sha=_file(body);store.upload(sha,str(body.get('filename'))[:200],data);s,extra=drawings.add(s,body,sha,data);action='ADD_DRAWING_TAKEOFF'
    else:s=drawings.assign(s,body);action='ASSIGN_TAKEOFF'
    if what in ('packages','packages/add-lines','award'):contracts.guard(old,s)  # E18: signed packages change only through an amendment
    s=store.put(s,body['revision'],action)
    return h.reply(dict(view(h,s),result=extra)) or True
