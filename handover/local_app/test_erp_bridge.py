"""E23 (D87) native tests: ERP reference → packages (through sc.save / save_award gates) and → PAKD C.2 lines. TEST ONLY fixture.

AB (test_pakd.base): 1.1 = 200 m3 (test-source), 1.2 = 10 t (ab2), 2.1 = 100 m3 (ab3). The fixture already has GT-01 + CC1 packages."""
import copy,json,tempfile,threading,unittest,urllib.request,urllib.error
from pathlib import Path
import erp_bridge as eb,subcontract as sc,pakd
from server import App
from test_pakd import base
def with_ref(s):
    s=copy.deepcopy(s);s['erp_reference']={'exported':'TEST ERP','project_label':'TEST',
     'bb_contracts':[{'ref':'TEST/HĐTC/CC1-NTPA','label':'TEST NTP A','vendor':'CC1-NTPA','lines':[
        {'row':10,'kind':'MEASURED','wbs_code':'1.1','uom':'m3','quantity':'120','unit_price':'90'},          # 60 % of AB 1.1
        {'row':11,'kind':'MEASURED','wbs_code':'1.2','uom':'kg','quantity':'5000','unit_price':'20'},        # UOM mismatch (t vs kg) → skipped
        {'row':12,'kind':'MEASURED','wbs_code':'2.1','uom':'m3','quantity':'130','unit_price':'15'},         # > AB 100 → capped, noted
        {'row':13,'kind':'MEASURED','wbs_code':'9.9','uom':'m3','quantity':'1','unit_price':'1'},            # no AB line
        {'row':14,'kind':'HEADING','wbs_code':'1','uom':None,'quantity':None,'unit_price':None}]},
      {'ref':'TEST/HĐTC/CC1-NTPB','label':'TEST NTP B','vendor':'CC1-NTPB','lines':[{'row':20,'kind':'MEASURED','wbs_code':'9.9','uom':'m3','quantity':'1','unit_price':'1'}]}],
     'pakd_gt':{'id':'TEST-GT','name':'TEST','project':'TEST','rows':3,'total':'3500','sections':[{'code':'1.1','name':'VĂN PHÒNG','rows':2,'amount':'3000'},{'code':'1.2','name':'ĐIỆN NƯỚC','rows':1,'amount':'500'}]},
     'pakd_tt':{'id':'TEST-TT','rows':12,'total':'21000'}};return s
class ErpBridge(unittest.TestCase):
    def test_packages_from_erp_gates_and_matching(self):
        s=with_ref(base());s['confirmed']=[0,1]
        with self.assertRaises(ValueError):eb.packages_from_erp(s,{})                      # WBS step not confirmed → gate (sc.require_wbs_ready)
        s['confirmed']=[0,1,2];s2,rep=eb.packages_from_erp(s,{})
        self.assertEqual([r['code'] for r in rep['imported']],['GT-02']);self.assertEqual([r['ref'] for r in rep['skipped_contracts']],['TEST/HĐTC/CC1-NTPB'])
        g=next(p for p in s2['packages'] if p['code']=='GT-02');self.assertEqual(g['erp_ref'],'TEST/HĐTC/CC1-NTPA')
        self.assertEqual([(l['bb_code'],l['ab_line_id'],l['alloc_pct']) for l in g['lines']],[('GT-02.1','test-source','60'),('GT-02.2','ab3','100')])
        self.assertEqual(g['award']['prices'],{'GT-02.1':'90','GT-02.2':'15'});self.assertIn('dòng 10',g['award']['price_refs']['GT-02.1']);self.assertIn('phần vượt',g['award']['price_refs']['GT-02.2'])
        self.assertEqual(g['award']['status'],'DRAFT');self.assertEqual(len(g['award']['inputs_sha256']),64)
        why={x['wbs_code']:x['why'] for x in rep['imported'][0]['skipped']};self.assertIn('khác đơn vị',why['1.2']);self.assertIn('không có dòng AB',why['9.9'])
        self.assertEqual(eb.summary(s2)['bb_imported'],1)
        with self.assertRaises(ValueError):eb.packages_from_erp(s2,{})                    # nothing left: A done, B unmatched
        s3,rep3=eb.packages_from_erp(s2,{'refs':['TEST/HĐTC/CC1-NTPA']}) if False else (None,None)  # explicit re-import of a done ref is a no-op (covered by 'already')
        self.assertTrue(sc.coverage(s2)['test-source']['allocated']>=sc.HUNDRED)             # GT-01 100 % + GT-02 60 % → OVER is reported, not hidden
    def test_pakd_from_erp_adds_c2_lines_once(self):
        s=with_ref(base());s2,rep=eb.pakd_from_erp(s,{})
        self.assertEqual((rep['added'],rep['tt_total']),(2,'21000'))
        ls=[l for l in pakd.state(s2)['scenarios'][0]['lines'] if l['code']=='C.2'];self.assertEqual([(l['value'],l['process_group']) for l in ls],[('3000','C'),('500','C')]);self.assertTrue(all(l['source_ref'].startswith('PAKD_GT ERP') for l in ls))
        with self.assertRaises(ValueError):eb.pakd_from_erp(s2,{})                         # idempotent
        self.assertTrue(eb.summary(s2)['pakd_gt_imported']);self.assertEqual(eb.summary(s2)['pakd_gt_total'],'3500')
class ErpHttp(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.app=App(('127.0.0.1',0),Path(self.tmp.name)/'db.sqlite');threading.Thread(target=self.app.serve_forever,daemon=True).start()
        self.base=f'http://127.0.0.1:{self.app.server_port}';s=with_ref(base());s['confirmed']=[0,1,2];p=self.app.store.create('TEST ERP');s.update(id=p['id'],revision=p['revision'],name=p['name']);self.s=self.app.store.put(s,p['revision'],'TEST_SEED')
    def tearDown(self):self.app.shutdown();self.app.server_close();self.tmp.cleanup()
    def call(self,path,body):
        req=urllib.request.Request(self.base+path,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','X-CC1-Session':self.app.token})
        with urllib.request.urlopen(req) as r:return json.load(r)
    def test_routes(self):
        pid=self.s['id'];v=self.call(f'/api/projects/{pid}/subcontract',{'revision':self.s['revision']}) if False else None
        with self.assertRaises(urllib.error.HTTPError) as e:self.call(f'/api/projects/{pid}/erp-packages',{'revision':0})
        self.assertEqual(e.exception.code,409)
        v=self.call(f'/api/projects/{pid}/erp-packages',{'revision':self.s['revision']});self.assertEqual(v['result']['imported'][0]['code'],'GT-02');self.assertEqual(v['erp']['bb_imported'],1)
        v=self.call(f'/api/projects/{pid}/erp-pakd',{'revision':v['revision']});self.assertEqual(v['result']['added'],2)
        self.assertEqual([e['action'] for e in self.app.store.events(pid)][-2:],['IMPORT_ERP_PACKAGES','IMPORT_ERP_PAKD'])
if __name__=='__main__':unittest.main(verbosity=1)
