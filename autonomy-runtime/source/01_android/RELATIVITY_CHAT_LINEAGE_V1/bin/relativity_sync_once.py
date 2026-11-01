#!/data/data/com.termux/files/usr/bin/python3
from pathlib import Path
import hashlib,json,shutil,time
H=Path('/data/data/com.termux/files/home')
R=H/'OmniDocuments/OMNI_RELATIVITY_CHAT_LINEAGE_V1'
IN=R/'future_orders/inbox'; ARC=R/'future_orders/archive'; STATE=R/'state'
for d in (IN,ARC,STATE): d.mkdir(parents=True,exist_ok=True)
MIRRORS=[H/'OmniDocuments/TOSH_OMNIPATH_CHAT_V2/relativity',H/'OMNI_AI_WORKSPACE/24_OMNIPATH_AUTONOMY/RELATIVITY_CHAT_LINEAGE_V1',H/'OMNI_NEXTGEN_MEMORY/RELATIVITY_CHAT_LINEAGE_V1']
FACETS=['relativity','provenance','memory','semantic_continuity','causality','uncertainty','topology','scale','information','governance','omnipath','omniteach','recovery']
Q=H/'OMNI_AI_WORKSPACE/08_QUEUES/hv-federation/orders-out'; Q.mkdir(parents=True,exist_ok=True)
processed=0
for p in sorted(IN.glob('*.json')):
    raw=p.read_bytes(); sha=hashlib.sha256(raw).hexdigest()
    try: obj=json.loads(raw)
    except Exception: obj={'raw_file':p.name}
    name=f'{sha[:16]}_{p.name}'
    dst=ARC/name; shutil.copy2(p,dst)
    ref={'time_ns':time.time_ns(),'sha256':sha,'source':str(dst),'order_id':obj.get('order_id') or obj.get('id'),'name':obj.get('name'),'state':obj.get('state','NEW_EXECUTION_ORDER')}
    for f in FACETS:
        d=R/'facets'/f; d.mkdir(parents=True,exist_ok=True)
        with (d/'order_refs.jsonl').open('a') as h: h.write(json.dumps(ref,sort_keys=True)+'\n')
    for m in MIRRORS:
        d=m/'future_orders'; d.mkdir(parents=True,exist_ok=True); shutil.copy2(p,d/name)
    shutil.copy2(p,Q/f'RELATIVITY_{name}')
    p.unlink(); processed+=1
(STATE/'SYNC_HEARTBEAT.json').write_text(json.dumps({'time_ns':time.time_ns(),'processed_now':processed,'status':'PASS'},indent=2)+'\n')
print(json.dumps({'processed_now':processed,'status':'PASS'}))
