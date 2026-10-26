"""D84 native tests: project menu ⋮ (rename, duplicate, hide, bin, restore, purge). TEST ONLY fixtures."""
import json,tempfile,threading,unittest,urllib.request,urllib.error
from pathlib import Path
from server import App
from test_pakd import base
import contracts as ct,pakd
class ProjectsAdmin(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.app=App(('127.0.0.1',0),Path(self.tmp.name)/'db.sqlite');threading.Thread(target=self.app.serve_forever,daemon=True).start()
        self.base=f'http://127.0.0.1:{self.app.server_port}';s=base();p=self.app.store.create('TEST gốc');s.update(id=p['id'],revision=p['revision'],name=p['name'])
        s=ct.act(s,{'action':'create','package_id':'id-GT-01','by':'TEST'});s['facts']=[{'id':'f1'}];s['progress']=[]
        sid=pakd.state(s)['current'];s=pakd.act(s,{'action':'save','scenario_id':sid,'basis':{'id-GT-01':'AWARD'}});s['pakd']['versions']=[{'id':'v1'}];s['confirmed']=[0,1,2]
        self.s=self.app.store.put(s,p['revision'],'TEST_SEED');self.pid=self.s['id']
    def tearDown(self):self.app.shutdown();self.app.server_close();self.tmp.cleanup()
    def call(self,body,pid=None):
        req=urllib.request.Request(f'{self.base}/api/projects/{pid or self.pid}/manage',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-CC1-Session':self.app.token})
        with urllib.request.urlopen(req) as r:return json.load(r)
    def rev(self,pid=None):return self.app.store.get(pid or self.pid)['revision']
    def flags(self):return {p['id']:p for p in self.app.store.list()}[self.pid]
    def test_rename_hide_bin_restore_purge(self):
        r=self.call({'action':'rename','revision':self.rev(),'name':'TEST đổi tên'});self.assertEqual(r['project']['name'],'TEST đổi tên')
        self.assertEqual(self.flags()['name'],'TEST đổi tên');self.assertEqual(r['project']['meta']['names'][0]['from'],'TEST gốc')
        with self.assertRaises(urllib.error.HTTPError) as e:self.call({'action':'rename','revision':0,'name':'x'})
        self.assertEqual(e.exception.code,409)                                                   # optimistic lock
        with self.assertRaises(urllib.error.HTTPError) as e:self.call({'action':'rename','revision':self.rev(),'name':' '})
        self.assertEqual(e.exception.code,400)
        self.call({'action':'hide','revision':self.rev()});self.assertTrue(self.flags()['hidden'])
        self.call({'action':'unhide','revision':self.rev()});self.assertFalse(self.flags()['hidden'])
        with self.assertRaises(urllib.error.HTTPError):self.call({'action':'purge','confirm_name':'TEST đổi tên'})   # only from the bin
        self.call({'action':'delete','revision':self.rev()});self.assertTrue(self.flags()['deleted_at'])
        self.call({'action':'restore','revision':self.rev()});self.assertIsNone(self.flags()['deleted_at'])
        self.call({'action':'delete','revision':self.rev()})
        with self.assertRaises(urllib.error.HTTPError):self.call({'action':'purge','confirm_name':'sai tên'})
        acts=[e['action'] for e in self.app.store.events(self.pid)]
        for a in ('RENAME_PROJECT','HIDE_PROJECT','UNHIDE_PROJECT','MOVE_PROJECT_TO_BIN','RESTORE_PROJECT_FROM_BIN'):self.assertIn(a,acts)
        r=self.call({'action':'purge','confirm_name':'TEST đổi tên'});self.assertEqual(r['purged'],self.pid)
        self.assertNotIn(self.pid,{p['id'] for p in r['projects']});self.assertEqual(self.app.store.events(self.pid),[])
    def test_duplicate_copies_estimate_not_evidence(self):
        r=self.call({'action':'duplicate','revision':self.rev()});d=r['project']
        self.assertEqual(d['name'],'TEST gốc (bản sao)');self.assertNotEqual(d['id'],self.pid);self.assertEqual(d['confirmed'],[])
        self.assertEqual([p['code'] for p in d['packages']],[p['code'] for p in self.s['packages']]);self.assertEqual(d['boq'],self.s['boq'])
        self.assertEqual(d['pakd']['scenarios'][0]['basis'],{'id-GT-01':'AWARD'});self.assertEqual(d['pakd']['versions'],[])
        for k in ('contracts','facts','progress','changes'):self.assertNotIn(k,d)
        self.assertEqual(d['meta']['copied_from']['project_id'],self.pid)
        o=self.app.store.get(self.pid);self.assertEqual(len(o['contracts']),1);self.assertEqual(o['pakd']['versions'],[{'id':'v1'}])  # original untouched
        self.assertIn('DUPLICATED_FROM:'+self.pid,[e['action'] for e in self.app.store.events(d['id'])])
if __name__=='__main__':unittest.main(verbosity=1)
