"""E21 (D85) native tests for the CERP-QTO bridge, against a FAKE upstream on loopback (TEST ONLY): proxy with token
injection and CSP rewrite, same-origin rule, status, project link, take-off import → candidates → confirm → review."""
import json,tempfile,threading,unittest,urllib.request,urllib.error
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from server import App
from test_app import fixture
import qto_bridge,drawings
ITEMS=[{'id':'11111111-1111-1111-1111-111111111111','item_key':'1.1||m3','version':1,'wbs_code':'1.1','norm_code':None,'cbs_code':None,'description':'TEST bê tông','quantity':'190.0000','unit':'m3','basis':['a','b'],'status':'approved'},
       {'id':'22222222-2222-2222-2222-222222222222','item_key':'9.9||kg','version':1,'wbs_code':'9.9','norm_code':'AF.1','cbs_code':None,'description':'TEST thép','quantity':'50.0000','unit':'kg','basis':['c'],'status':'approved'},
       {'id':'33333333-3333-3333-3333-333333333333','item_key':'1.1||m3','version':0,'wbs_code':'1.1','norm_code':None,'cbs_code':None,'description':'old','quantity':'1','unit':'m3','basis':[],'status':'superseded'}]
class Fake(BaseHTTPRequestHandler):
    seen=[];items=ITEMS
    def log_message(self,*a):pass
    def _j(self,code,obj,extra=None):
        b=json.dumps(obj).encode();self.send_response(code)
        for k,v in (extra or {}).items():self.send_header(k,v)
        self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
    def do_GET(self):
        Fake.seen.append((self.command,self.path,self.headers.get('Authorization'),self.headers.get('Cookie')))
        if self.path=='/healthz':return self._j(200,{'status':'ok'})
        if self.headers.get('Authorization')!='Bearer tok-test':return self._j(401,{'detail':'Thiếu token'})
        if self.path=='/v1/me':return self._j(200,{'user':'e2e','roles':['qto.read'],'projects':['DEMO']})
        if self.path=='/v1/projects/DEMO/takeoff-items':return self._j(200,Fake.items)
        if self.path.startswith('/ui/'):
            b=b'<html><body>QTO UI</body></html>';self.send_response(200);self.send_header('Content-Type','text/html');self.send_header('Content-Security-Policy',"default-src 'self'; frame-ancestors 'none'");self.send_header('Set-Cookie','x=1');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b);return
        return self._j(404,{'detail':'no'})
    def do_POST(self):
        n=int(self.headers.get('Content-Length') or 0);body=self.rfile.read(n);Fake.seen.append((self.command,self.path,self.headers.get('Authorization'),self.headers.get('Content-Type')))
        return self._j(201,{'echo':len(body),'ct':self.headers.get('Content-Type')})
    def do_PUT(self):
        n=int(self.headers.get('Content-Length') or 0);self.rfile.read(n);Fake.seen.append((self.command,self.path,self.headers.get('Authorization'),None));return self._j(200,{'put':True})
class Bridge(unittest.TestCase):
    def setUp(self):
        self.up=ThreadingHTTPServer(('127.0.0.1',0),Fake);threading.Thread(target=self.up.serve_forever,daemon=True).start();Fake.seen=[];Fake.items=ITEMS
        self.tmp=tempfile.TemporaryDirectory();self.app=App(('127.0.0.1',0),Path(self.tmp.name)/'db.sqlite');threading.Thread(target=self.app.serve_forever,daemon=True).start()
        self.base=f'http://127.0.0.1:{self.app.server_port}';self.app.qto.set(url=f'http://127.0.0.1:{self.up.server_port}',token='')
        s=fixture();p=self.app.store.create('TEST QTO');s.update(id=p['id'],revision=p['revision'],name=p['name']);self.s=self.app.store.put(s,p['revision'],'TEST_SEED');self.pid=self.s['id']
    def tearDown(self):
        self.app.shutdown();self.app.server_close();self.up.shutdown();self.up.server_close();self.tmp.cleanup()
    def req(self,method,path,body=None,headers=None,raw=False,session=True):
        h={'Content-Type':'application/json'} if body is not None and not isinstance(body,bytes) else {}
        if session:h['X-CC1-Session']=self.app.token
        h.update(headers or {});data=None if body is None else (body if isinstance(body,bytes) else json.dumps(body).encode())
        req=urllib.request.Request(self.base+path,data=data,headers=h,method=method)
        with urllib.request.urlopen(req) as r:return (r.status,dict(r.headers),r.read()) if raw else json.load(r)
    def test_status_settings_and_proxy(self):
        st=self.req('GET','/api/qto/status');self.assertEqual((st['service'],st['token_set'],st['me']),('UP',False,None))
        with self.assertRaises(ValueError):self.app.qto.set(url='http://example.com:80')              # loopback only
        st=self.req('POST','/api/qto/settings',{'token':'tok-test'});self.assertEqual(st['me']['user'],'e2e');self.assertNotIn('tok-test',json.dumps(st))
        self.assertEqual(json.loads((Path(self.tmp.name)/'qto_settings.json').read_text(encoding='utf-8'))['token'],'tok-test')
        # GET through the proxy: token attached when the page sent none / an empty bearer; CSP rewritten for framing; cookies dropped
        me=self.req('GET','/v1/me',session=False);self.assertEqual(me['user'],'e2e')
        me=self.req('GET','/v1/me',headers={'Authorization':'Bearer '},session=False);self.assertEqual(me['user'],'e2e')
        code,hs,body=self.req('GET','/qto/ui/',raw=True,session=False);self.assertEqual(code,200);self.assertIn(b'QTO UI',body)
        self.assertIn("frame-ancestors 'self'",hs['Content-Security-Policy']);self.assertNotIn('Set-Cookie',hs);self.assertEqual(hs['Cache-Control'],'no-store')
        self.assertTrue(all(c is None for m,p,a,c in Fake.seen if m=='GET'),'cookies never forwarded')
        # mutations through the proxy need a same-origin Origin/Referer (no 8765 session header required); multipart passes through
        with self.assertRaises(urllib.error.HTTPError) as e:self.req('POST','/v1/drawings',b'x',session=False)
        self.assertEqual(e.exception.code,403)
        r=self.req('POST','/v1/drawings',b'--b\r\nContent-Disposition: form-data; name="f"\r\n\r\nhello\r\n--b--',headers={'Origin':self.base,'Content-Type':'multipart/form-data; boundary=b'},session=False)
        self.assertEqual(r['echo'],61);self.assertTrue(r['ct'].startswith('multipart/form-data'))
        r=self.req('PUT','/v1/sheets/1/calibration',{'a':1},headers={'Referer':self.base+'/qto/ui/'},session=False);self.assertTrue(r['put'])
        self.assertTrue(all(a=='Bearer tok-test' for m,p,a,c in Fake.seen if p!='/healthz'),Fake.seen)
        self.up.shutdown();self.up.server_close()                                                        # service down → 503 with a clear message, status says DOWN
        with self.assertRaises(urllib.error.HTTPError) as e:self.req('GET','/v1/me',session=False)
        self.assertEqual(e.exception.code,503);st=self.req('GET','/api/qto/status');self.assertEqual(st['service'],'DOWN');self.assertIn('Khởi động',st['error'])
    def test_link_import_confirm_review(self):
        self.app.qto.set(token='tok-test');rev=lambda:self.app.store.get(self.pid)['revision']
        with self.assertRaises(urllib.error.HTTPError) as e:self.req('POST',f'/api/projects/{self.pid}/qto-import',{'revision':rev()})
        self.assertEqual(e.exception.code,400)                                                           # no linked QTO project yet
        with self.assertRaises(urllib.error.HTTPError) as e:self.req('POST',f'/api/projects/{self.pid}/qto-project',{'revision':0,'qto_project':'DEMO'})
        self.assertEqual(e.exception.code,409)
        r=self.req('POST',f'/api/projects/{self.pid}/qto-project',{'revision':rev(),'qto_project':'DEMO'});self.assertEqual(r['project']['context']['qto_project'],'DEMO')
        r=self.req('POST',f'/api/projects/{self.pid}/qto-import',{'revision':rev(),'threshold_pct':'1'})
        self.assertEqual(r['result'],{'items':2,'added':2,'updated':0,'unchanged':0,'suggested':1})   # superseded v0 ignored; 1.1/m3 matches the AB line
        c={t['id']:t for t in r['review']['candidates']};t1=c['qto:11111111-1111-1111-1111-111111111111']
        self.assertEqual((t1['value'],t1['uom'],t1['source']['measurements'],t1['suggestion']['ab_line_id']),('190.0000','m3',2,'test-source'))
        self.assertIsNone(c['qto:22222222-2222-2222-2222-222222222222']['suggestion'])                   # no AB line 9.9
        self.assertEqual((r['review']['counts']['open'],r['review']['compare'],len(r['review']['no_takeoff'])),(2,[],1))
        s=self.app.store.get(self.pid);self.assertEqual(s['boq'][0]['quantity'],'200')                  # consultant BOQ untouched
        # the QS confirms the suggestion (factor 1, basis) through the existing E14 assign → deviation −5 % flagged at 1 %
        s=drawings.assign(s,{'takeoff_id':t1['id'],'status':'CONFIRMED','ab_line_id':'test-source','factor':'1','factor_ref':'TEST cùng mã WBS và đơn vị','by':'TEST QS'});s=self.app.store.put(s,s['revision'],'ASSIGN_TAKEOFF')
        rv=self.req('POST',f'/api/projects/{self.pid}/qto-review',{'threshold_pct':'1'})['review']
        self.assertEqual((rv['compare'][0]['drawing_quantity'],rv['compare'][0]['deviation_pct'],rv['compare'][0]['flag'],rv['counts']['flagged'],rv['no_takeoff']),('190.0000','-5.0','FLAG',1,[]))
        self.assertIsNone(self.req('POST',f'/api/projects/{self.pid}/qto-review',{})['review']['compare'][0]['flag'])   # no threshold → no flag, number unchanged
        # re-import: same item unchanged keeps the decision; a newer version of 1.1 replaces the value and flags the confirmed assignment
        r=self.req('POST',f'/api/projects/{self.pid}/qto-import',{'revision':rev()});self.assertEqual((r['result']['unchanged'],r['result']['added']),(2,0))
        Fake.items=ITEMS+[{'id':'44444444-4444-4444-4444-444444444444','item_key':'1.1||m3','version':2,'wbs_code':'1.1','norm_code':None,'cbs_code':None,'description':'TEST bê tông v2','quantity':'205.0000','unit':'m3','basis':['a','b','d'],'status':'approved'}]
        r=self.req('POST',f'/api/projects/{self.pid}/qto-import',{'revision':rev(),'threshold_pct':'1'});self.assertEqual((r['result']['updated'],r['result']['unchanged']),(1,1))
        c={t['id']:t for t in r['review']['candidates']};self.assertNotIn('qto:11111111-1111-1111-1111-111111111111',c);t2=c['qto:44444444-4444-4444-4444-444444444444']
        self.assertEqual((t2['assign']['status'],t2['assign']['updated_from'],r['review']['compare'][0]['deviation_pct']),('CONFIRMED',1,'2.5'))
        self.assertIn('IMPORT_QTO_TAKEOFF',[e['action'] for e in self.app.store.events(self.pid)])
class MixedWbsCodes(unittest.TestCase):
    def test_rollup_sorts_numeric_and_alphabetic_codes(self):  # D85: found by the integrated E2E (consultant BOQ with "1.1" and "KT-SAN")
        import subcontract as sc,pmmodels
        s=fixture();s['boq'].append({'id':'test-san','source_code':'KT-SAN','description':'TEST sàn','quantity':'24','uom':'m2','kind':'MEASURED','source_ref':'T:9','source_hash':'e'*64})
        self.assertEqual([g['wbs'] for g in sc.rollup(s)['wbs']],['1.1','KT-SAN']);sc.summary(s,pmmodels.models())
if __name__=='__main__':unittest.main(verbosity=1)
