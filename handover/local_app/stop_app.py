"""Ask only the matching local app to stop; never terminate arbitrary processes."""
import json,urllib.request
base='http://127.0.0.1:8765'
try:
    with urllib.request.urlopen(base+'/api/bootstrap',timeout=3) as r:boot=json.load(r)
    if boot.get('version') not in ['0.1.0-local','0.2.0-local'] or not boot.get('token'):raise ValueError('Service is not the expected CC1 local app.')
    req=urllib.request.Request(base+'/api/shutdown',data=b'{}',headers={'Content-Type':'application/json','X-CC1-Session':boot['token']})
    with urllib.request.urlopen(req,timeout=3) as r:print(json.load(r)['status'])
except Exception as e:
    print('No service stopped:',e);raise SystemExit(1)
