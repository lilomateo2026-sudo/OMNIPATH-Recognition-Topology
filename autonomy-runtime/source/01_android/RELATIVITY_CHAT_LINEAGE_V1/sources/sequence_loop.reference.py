#!/usr/bin/env python3
import fcntl,hashlib,json,time,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from deep_arbitration import arbitrate
from semantic_recall import recall_packet
from helix_harness import enrich_packet
from helix_contract_v3 import admission_gate
from helix_ledger_v1 import record_ingress_decision
ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'state'; STATE.mkdir(parents=True,exist_ok=True)
LOCK=STATE/'.sequence_loop.lock'
_lock_fd=open(LOCK,'w')
try:
    fcntl.flock(_lock_fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
except BlockingIOError:
    print(json.dumps({'processed_now':0,'status':'LOCKED','state_root':str(STATE)},sort_keys=True)); raise SystemExit(0)
IN=STATE/'inbox'; OUT=STATE/'outbox'; DEC=STATE/'decisions'
for d in (IN,OUT,DEC): d.mkdir(parents=True,exist_ok=True)
count=0
for p in sorted(IN.glob('*.json')):
    try: packet=json.loads(p.read_text())
    except Exception: continue
    raw=json.dumps(packet,sort_keys=True,separators=(',',':')).encode(); ps=hashlib.sha256(raw).hexdigest()
    gate=admission_gate(packet)
    if not gate.get('allowed'):
        decision=gate|{'packet_sha256':ps,'source_file':p.name,'created_ns':time.time_ns(),'semantic_recall_required':False}
        decision['candidate_seed']=packet if packet.get('kind')=='CANDIDATE_SEED' or packet.get('state')=='CANDIDATE_SEED' else None
        decision['decision_sha256']=hashlib.sha256(json.dumps(decision,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        record_ingress_decision(packet,decision)
        (DEC/p.name).write_text(json.dumps(decision,indent=2,sort_keys=True)+'\n')
        (OUT/p.name).write_text(json.dumps({'packet':packet,'decision':decision},indent=2,sort_keys=True)+'\n')
        p.rename(IN/(p.stem+'.processed')); count+=1
        continue
    recall=recall_packet(packet,limit=5)
    decision=arbitrate(packet)|gate|{'semantic_recall':recall,'semantic_recall_required':True,'packet_sha256':ps,'source_file':p.name,'created_ns':time.time_ns()}
    decision['omnipath_helix']=enrich_packet(packet,decision)
    decision['decision_sha256']=hashlib.sha256(json.dumps(decision,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    record_ingress_decision(packet,decision)
    (DEC/p.name).write_text(json.dumps(decision,indent=2,sort_keys=True)+'\n')
    (OUT/p.name).write_text(json.dumps({'packet':packet,'decision':decision},indent=2,sort_keys=True)+'\n')
    p.rename(IN/(p.stem+'.processed')); count+=1
print(json.dumps({'processed_now':count,'outbox_total':len(list(OUT.glob('*.json'))),'state_root':str(STATE),'status':'PASS'},sort_keys=True))
