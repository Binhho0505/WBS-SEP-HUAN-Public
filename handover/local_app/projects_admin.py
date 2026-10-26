"""D84: quản lý bộ hồ sơ từ menu ⋮ ở thanh bên — đổi tên, nhân bản, ẩn / hiện, chuyển vào thùng rác, khôi phục, xóa vĩnh viễn.

Every change except the permanent delete is a normal revision (optimistic lock + event log). Flags live in state.meta.
Duplicate = a new working copy of the estimate: inputs, packages, quotes, award drafts and PAKD scenarios are copied;
confirmations are reset (each step is checked again) and execution evidence of the original is NOT copied — contract dossiers,
change requests, progress / acceptance / payment facts and frozen PAKD versions stay with the original project.
"""
import copy
from datetime import datetime,timezone
NOT_COPIED=('contracts','changes','facts','progress')
def now():return datetime.now(timezone.utc).isoformat(timespec='seconds')
def manage(store,pid,body):
    a=body.get('action');s=store.get(pid);meta=dict(s.get('meta') or {})
    if a!='purge' and body.get('revision')!=s['revision']:raise PermissionError('Hồ sơ đã đổi ở cửa sổ khác; tải lại trước khi thao tác.')
    def save(action):s['meta']=meta;return store.put(s,s['revision'],action)
    if a=='rename':
        n=str(body.get('name') or '').strip()
        if not n or len(n)>200:raise ValueError('Tên hồ sơ từ 1 đến 200 ký tự.')
        if n==s['name']:return {'project':s}
        meta.setdefault('names',[]).append({'from':s['name'],'to':n,'at':now()});s['name']=n;return {'project':save('RENAME_PROJECT')}
    if a in ('hide','unhide'):
        meta['hidden']=a=='hide';return {'project':save('HIDE_PROJECT' if a=='hide' else 'UNHIDE_PROJECT')}
    if a=='delete':
        if meta.get('deleted_at'):raise ValueError('Hồ sơ đã ở thùng rác.')
        meta['deleted_at']=now();return {'project':save('MOVE_PROJECT_TO_BIN')}
    if a=='restore':
        if not meta.get('deleted_at'):raise ValueError('Hồ sơ không ở thùng rác.')
        meta.pop('deleted_at',None);return {'project':save('RESTORE_PROJECT_FROM_BIN')}
    if a=='purge':
        if not meta.get('deleted_at'):raise ValueError('Chỉ xóa vĩnh viễn hồ sơ đã ở thùng rác.')
        if str(body.get('confirm_name') or '').strip()!=s['name']:raise ValueError('Gõ đúng tên hồ sơ để xác nhận xóa vĩnh viễn.')
        store.purge(pid);return {'purged':pid}
    if a=='duplicate':
        n=str(body.get('name') or (s['name']+' (bản sao)')).strip()[:200]
        if not n:raise ValueError('Nhập tên hồ sơ bản sao.')
        new=store.create(n);keep={'id':new['id'],'name':n,'revision':new['revision']}
        c=copy.deepcopy(s)
        for k in NOT_COPIED:c.pop(k,None)
        if isinstance(c.get('pakd'),dict):c['pakd']=dict(c['pakd'],versions=[])
        c.update(keep,confirmed=[],meta={'copied_from':{'project_id':pid,'name':s['name'],'revision':s['revision'],'at':now(),
                 'note':'Bản sao làm việc: các bước phải xác nhận lại; hồ sơ hợp đồng, thay đổi, khối lượng / nghiệm thu / thanh toán và phiên bản PAKD đã chốt không chép.'}})
        for k in ('restored_from',):c.pop(k,None)
        return {'project':store.put(c,new['revision'],'DUPLICATED_FROM:'+pid)}
    raise ValueError('Thao tác không hợp lệ.')
