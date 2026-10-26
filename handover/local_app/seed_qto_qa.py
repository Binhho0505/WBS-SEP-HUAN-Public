"""E21 QA seed for browser_qto.cjs: ISOLATED QA database with the TEST ONLY fixture plus one BOQ AB line in m2 (KT-SAN, 24 m2)
that the golden drawing GC-QTO-01 of CERP-QTO (hatch 23 m2) is checked against. Never the runtime DB.
Usage: python seed_qto_qa.py <new_qa.sqlite> <out_dir>  → writes out_dir/ids.json
"""
import json,sys
from pathlib import Path
from store import Store
from test_app import fixture
def main(db,out):
    db=Path(db);out=Path(out)
    if db.exists():raise SystemExit('QA DB đã tồn tại; dùng file mới.')
    if 'runtime' in db.parts:raise SystemExit('Không dùng runtime DB.')
    out.mkdir(parents=True,exist_ok=True);st=Store(db);f=fixture();s=st.create('TEST ONLY · QTO QA (không phải dự án thật)')
    s.update({k:f[k] for k in ('context','boq','wbs','mapping','applications','norms','resources','prices','adjustments','export','resource_completeness_ref') if k in f},confirmed=[0,1])
    s['boq'].append({'id':'test-san','source_code':'KT-SAN','description':'TEST ONLY sàn BTCT (Tư vấn bóc 24 m2)','quantity':'24','uom':'m2','unit_price':'500000','kind':'MEASURED','source_ref':'T:9','source_hash':'e'*64})
    s=st.put(s,s['revision'],'TEST_FIXTURE');(out/'ids.json').write_text(json.dumps([s['id']]),encoding='utf-8');print(s['id'])
if __name__=='__main__':main(*sys.argv[1:])
