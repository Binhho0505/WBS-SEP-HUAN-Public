"""D81 QA seed for browser_ux.cjs: an ISOLATED QA database with the TEST ONLY single-line fixture of test_app, steps 1–7
confirmed so every step (incl. prices) is open. Never the runtime DB.
Usage: python seed_ux_qa.py <new_qa.sqlite> <out_dir>  → writes out_dir/ids.json
"""
import json,sys
from pathlib import Path
from store import Store
from test_app import fixture
def main(db,out):
    db=Path(db);out=Path(out)
    if db.exists():raise SystemExit('QA DB đã tồn tại; dùng file mới.')
    if 'runtime' in db.parts:raise SystemExit('Không dùng runtime DB.')
    out.mkdir(parents=True,exist_ok=True);st=Store(db);f=fixture();s=st.create('TEST ONLY · UX QA (không phải dự án thật)')
    s.update({k:f[k] for k in ('context','boq','wbs','mapping','applications','norms','resources','prices','adjustments','export','resource_completeness_ref') if k in f},confirmed=list(range(7)))
    s=st.put(s,s['revision'],'TEST_FIXTURE');(out/'ids.json').write_text(json.dumps([s['id']]),encoding='utf-8');print(s['id'])
if __name__=='__main__':main(*sys.argv[1:])
