import json,re,sqlite3,unicodedata,uuid
from contextlib import contextmanager
from datetime import datetime,timezone
from pathlib import Path
from domain import new_project,digest,upgrade
class Conflict(Exception):pass
LIBRARY_KINDS={'NORMS':'norms','RESOURCES':'resources','PRICES':'prices','REFERENCE':'reference'}
def fold(s):
    """Accent-insensitive lowercase text for Vietnamese search."""
    s=str(s).replace('đ','d').replace('Đ','D')
    for c in 'ØøΦφ⌀':s=s.replace(c,' phi ')
    s=unicodedata.normalize('NFKD',s)
    return re.sub(r'phi\s+(?=\d)','phi',''.join(c for c in s if not unicodedata.combining(c)).lower())
def matches(terms,text):
    """Numbers and short tokens (≤3 chars, e.g. '2', 'ii') must match a whole word; longer tokens may be substrings."""
    words=set(re.findall(r'[a-z0-9.,/]+',text))
    return all((t in words) if (len(t)<=3 or t.replace('.','').replace(',','').isdigit()) else (t in text) for t in terms)
def now():return datetime.now(timezone.utc).isoformat()
class Store:
    def __init__(self,path):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as db:
            db.executescript('CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY,name TEXT,revision INTEGER NOT NULL,state TEXT NOT NULL); CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY,project_id TEXT,revision INTEGER,event_time TEXT,action TEXT,state_digest TEXT,state TEXT,UNIQUE(project_id,revision),FOREIGN KEY(project_id) REFERENCES projects(id)); CREATE TABLE IF NOT EXISTS uploads(sha256 TEXT PRIMARY KEY,filename TEXT,data BLOB);'
                'CREATE TABLE IF NOT EXISTS library(id TEXT PRIMARY KEY,kind TEXT NOT NULL,name TEXT NOT NULL,version INTEGER NOT NULL,sha256 TEXT NOT NULL,filename TEXT,note TEXT,created TEXT NOT NULL,row_count INTEGER NOT NULL,rows TEXT NOT NULL,status TEXT NOT NULL DEFAULT \'ACTIVE\',UNIQUE(kind,name,version));'
                'CREATE TABLE IF NOT EXISTS qs_choices(id INTEGER PRIMARY KEY,created TEXT NOT NULL,project_id TEXT NOT NULL,project_name TEXT,revision INTEGER NOT NULL,item_id TEXT,key TEXT NOT NULL,uom TEXT,description TEXT,path TEXT,norm_id TEXT NOT NULL,norm_code TEXT,qty_factor TEXT,factor_ref TEXT,conversion_ref TEXT,selection_ref TEXT,source_ref TEXT,UNIQUE(project_id,revision,item_id,norm_id));'
                'CREATE TABLE IF NOT EXISTS qs_choice_revocations(id INTEGER PRIMARY KEY,created TEXT NOT NULL,choice_id INTEGER NOT NULL UNIQUE,reason TEXT NOT NULL,decided_by TEXT,decision_ref TEXT,FOREIGN KEY(choice_id) REFERENCES qs_choices(id));'
                'CREATE TABLE IF NOT EXISTS ai_proposals(id TEXT PRIMARY KEY,project_id TEXT,step INTEGER,provider TEXT,model TEXT,question TEXT,prompt_digest TEXT,response TEXT,created TEXT,status TEXT);')
    @contextmanager
    def connect(self):
        db=sqlite3.connect(self.path,timeout=20);db.execute('PRAGMA foreign_keys=ON')
        try:
            with db:yield db
        finally:db.close()
    def _flags(self,db):
        """D87: side-list flags live in two indexed columns (hidden, deleted_at) so listing 80+ large projects does not parse their JSON."""
        cols={r[1] for r in db.execute('PRAGMA table_info(projects)')}
        if 'hidden' not in cols:
            db.execute('ALTER TABLE projects ADD COLUMN hidden INTEGER NOT NULL DEFAULT 0');db.execute('ALTER TABLE projects ADD COLUMN deleted_at TEXT')
            db.execute("UPDATE projects SET hidden=COALESCE(json_extract(state,'$.meta.hidden'),0),deleted_at=json_extract(state,'$.meta.deleted_at')")
    def list(self):
        """Projects for the side list, newest first, with the D84 flags (hidden / moved to the bin)."""
        with self.connect() as db:
            self._flags(db)
            return [dict(id=r[0],name=r[1],revision=r[2],hidden=bool(r[3]),deleted_at=r[4]) for r in db.execute("SELECT id,name,revision,hidden,deleted_at FROM projects ORDER BY rowid DESC")]
    def purge(self,pid):
        """D84: permanent delete of a project already in the bin — its row, revision history and AI proposals. QS choice memory
        (shared across projects, keeps the project name) is not removed."""
        with self.connect() as db:
            db.execute('DELETE FROM events WHERE project_id=?',(pid,));db.execute('DELETE FROM ai_proposals WHERE project_id=?',(pid,))
            if db.execute('DELETE FROM projects WHERE id=?',(pid,)).rowcount!=1:raise KeyError('Hồ sơ không tồn tại')
    def get(self,pid):
        with self.connect() as db:r=db.execute('SELECT state FROM projects WHERE id=?',(pid,)).fetchone()
        if not r:raise KeyError('Hồ sơ không tồn tại')
        return upgrade(json.loads(r[0]))
    def create(self,name):
        s=new_project(name)
        with self.connect() as db:
            db.execute('INSERT INTO projects(id,name,revision,state) VALUES(?,?,?,?)',(s['id'],name,0,json.dumps(s,ensure_ascii=False)))
        return s
    def put(self,s,expected,action):
        s['revision']=expected+1;encoded=json.dumps(s,ensure_ascii=False)
        with self.connect() as db:
            self._flags(db);meta=s.get('meta') or {}
            changed=db.execute('UPDATE projects SET state=?,revision=?,name=?,hidden=?,deleted_at=? WHERE id=? AND revision=?',(encoded,s['revision'],s['name'],1 if meta.get('hidden') else 0,meta.get('deleted_at'),s['id'],expected)).rowcount
            if changed!=1:raise Conflict('Hồ sơ đã được thay đổi ở cửa sổ khác. Tải lại trước khi lưu.')
            db.execute('INSERT INTO events(project_id,revision,event_time,action,state_digest,state) VALUES(?,?,?,?,?,?)',(s['id'],s['revision'],now(),action,digest(s),encoded))
        return s
    def events(self,pid):
        with self.connect() as db:return [dict(revision=r[0],time=r[1],action=r[2],digest=r[3]) for r in db.execute('SELECT revision,event_time,action,state_digest FROM events WHERE project_id=? ORDER BY revision',(pid,))]
    def upload(self,hash,name,data):
        with self.connect() as db:db.execute('INSERT OR IGNORE INTO uploads VALUES(?,?,?)',(hash,name,data))
    # Data library: immutable dataset versions shared across projects; archive instead of delete.
    def library_add(self,kind,name,sha256,filename,note,rows):
        if kind not in LIBRARY_KINDS:raise ValueError('Loại thư viện phải là NORMS, RESOURCES, PRICES hoặc REFERENCE.')
        with self.connect() as db:
            version=(db.execute('SELECT MAX(version) FROM library WHERE kind=? AND name=?',(kind,name)).fetchone()[0] or 0)+1;did=str(uuid.uuid4())
            db.execute('INSERT INTO library(id,kind,name,version,sha256,filename,note,created,row_count,rows) VALUES(?,?,?,?,?,?,?,?,?,?)',(did,kind,name,version,sha256,filename,note,now(),len(rows),json.dumps(rows,ensure_ascii=False)))
        return self.library_get(did,False)
    def library_list(self):
        with self.connect() as db:return [dict(id=r[0],kind=r[1],name=r[2],version=r[3],sha256=r[4],filename=r[5],note=r[6],created=r[7],row_count=r[8],status=r[9]) for r in db.execute('SELECT id,kind,name,version,sha256,filename,note,created,row_count,status FROM library ORDER BY created DESC')]
    def library_rows(self,did):
        """Rows of one dataset version; versions are immutable, so the parsed rows are cached per id."""
        cache=self.__dict__.setdefault('_rows_cache',{})
        if did not in cache:cache[did]=self.library_get(did)['rows']
        return cache[did]
    def library_get(self,did,rows=True):
        with self.connect() as db:r=db.execute('SELECT id,kind,name,version,sha256,filename,note,created,row_count,status,rows FROM library WHERE id=?',(did,)).fetchone()
        if not r:raise KeyError('Bộ dữ liệu không tồn tại')
        d=dict(id=r[0],kind=r[1],name=r[2],version=r[3],sha256=r[4],filename=r[5],note=r[6],created=r[7],row_count=r[8],status=r[9])
        if rows:d['rows']=json.loads(r[10])
        return d
    def library_search(self,kind,query,limit=50,dataset=None):
        """Token AND search over ACTIVE datasets of one kind (accent-insensitive); returns rows with dataset lineage."""
        terms=fold(query).split();hits=[]
        with self.connect() as db:
            sets=db.execute("SELECT id,name,version,sha256,rows FROM library WHERE kind=? AND status='ACTIVE'"+(' AND id=?' if dataset else '')+' ORDER BY created DESC',(kind,dataset) if dataset else (kind,)).fetchall()
        for did,name,version,sha,rows in sets:
            for r in json.loads(rows):
                text=fold(' '.join(str(v) for v in r.values() if isinstance(v,(str,int,float))))
                if matches(terms,text):
                    head=fold(' '.join(str(r.get(k,'')) for k in ('name','spec','code','resource_code','location')))
                    hits.append((-sum(matches([t],head) for t in terms),len(hits),dict(r,library_dataset=did,library_sha256=sha,library_name=f'{name} · v{version}')))
        hits.sort(key=lambda h:h[:2])
        return {'rows':[h[2] for h in hits[:limit]],'total':len(hits)}
    def library_archive(self,did):
        with self.connect() as db:
            if db.execute("UPDATE library SET status='ARCHIVED' WHERE id=?",(did,)).rowcount!=1:raise KeyError('Bộ dữ liệu không tồn tại')
    def library_activate(self,did):
        """D59/FR-17: re-activate one version; other versions of the same kind+name are archived (never deleted)."""
        d=self.library_get(did,False)
        with self.connect() as db:
            db.execute("UPDATE library SET status='ARCHIVED' WHERE kind=? AND name=? AND id<>?",(d['kind'],d['name'],did))
            db.execute("UPDATE library SET status='ACTIVE' WHERE id=?",(did,))
        return self.library_get(did,False)
    # AI proposals live outside project state: they never change revisions or confirmations.
    def choices_add(self,rows):
        """BL63: append-only memory of QS norm choices that passed the step-3 gate (never updated or deleted)."""
        cols=['created','project_id','project_name','revision','item_id','key','uom','description','path','norm_id','norm_code','qty_factor','factor_ref','conversion_ref','selection_ref','source_ref']
        with self.connect() as db:
            return sum(db.execute('INSERT OR IGNORE INTO qs_choices('+','.join(cols)+') VALUES('+','.join('?'*len(cols))+')',[r.get(c) for c in cols]).rowcount for r in rows)
    def choices_revoke(self,ids,reason,decided_by,decision_ref):
        """BL70: append-only revocation of remembered choices (the choice rows themselves are never changed)."""
        with self.connect() as db:
            return sum(db.execute('INSERT OR IGNORE INTO qs_choice_revocations(created,choice_id,reason,decided_by,decision_ref) VALUES(?,?,?,?,?)',(now(),i,reason,decided_by,decision_ref)).rowcount for i in ids)
    def choices_for(self,keys):
        keys=list({k for k in keys if k})
        if not keys:return []
        with self.connect() as db:
            # BL70 (D45): revoked choices stay as evidence but are never returned for reuse
            cur=db.execute('SELECT * FROM qs_choices WHERE key IN ('+','.join('?'*len(keys))+') AND id NOT IN (SELECT choice_id FROM qs_choice_revocations) ORDER BY id',keys);names=[d[0] for d in cur.description]
            return [dict(zip(names,r)) for r in cur.fetchall()]
    def proposal_add(self,pid,step,provider,model,question,prompt_digest,response):
        p=dict(id=str(uuid.uuid4()),project_id=pid,step=step,provider=provider,model=model,question=question,prompt_digest=prompt_digest,response=response,created=now(),status='AI_PROPOSAL_NOT_APPLIED')
        with self.connect() as db:db.execute('INSERT INTO ai_proposals VALUES(?,?,?,?,?,?,?,?,?,?)',tuple(p.values()))
        return p
    def proposals(self,pid):
        with self.connect() as db:return [dict(id=r[0],step=r[1],provider=r[2],model=r[3],question=r[4],prompt_digest=r[5],response=r[6],created=r[7],status=r[8]) for r in db.execute('SELECT id,step,provider,model,question,prompt_digest,response,created,status FROM ai_proposals WHERE project_id=? ORDER BY created DESC LIMIT 50',(pid,))]
