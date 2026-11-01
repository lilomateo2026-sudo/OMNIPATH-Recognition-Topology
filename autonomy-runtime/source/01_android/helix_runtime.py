#!/usr/bin/env python3
import hashlib, json, os, time
from pathlib import Path
ROOT=Path('/var/lib/omni-sfc/sot-helix')
SNAP=ROOT/'state'/'evidence_capsule.json'
LATEST=ROOT/'state'/'latest.json'
GEN=ROOT/'generations'
REC=ROOT/'receipts'
TOPICS=['Sequence of Thought','Happy Orchard','PlayStation memory card','Shadow Omega','Parallel Paradox','OMNIVERSE V25','Scriptology','M7 Sector Matrix','Cognitive modeling','Terminal Temple']
A_DOMAINS=['native-continuity','deterministic-replay','resource-governor','training-admission','temple-evolution']
C_OPS=['analogy','contradiction-resolution','missing-dependency','structural-transfer','observer-solution']
def canon(x): return json.dumps(x,sort_keys=True,separators=(',',':'))
def sha(x): return hashlib.sha256(canon(x).encode()).hexdigest()
def atomic(p,o):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    t=p.with_suffix(p.suffix+'.tmp'); t.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n'); os.replace(t,p)
def next_generation():
    s=json.loads(SNAP.read_text())
    prior=json.loads(LATEST.read_text()) if LATEST.exists() else {'generation':0,'hyperation_sha':'GENESIS'}
    state_sha=sha(s); parent=prior['hyperation_sha']; orders=[]
    for i,domain in enumerate(A_DOMAINS,1):
        a={'entity':'OMNI','domain':domain,'objective':s['part_a_objectives'][i-1]}
        seed=hashlib.sha256(f'{state_sha}|{parent}|{i}'.encode()).hexdigest()
        b={'entity':'AMNI','topic':TOPICS[int(seed[:8],16)%len(TOPICS)],'operator':s['b_operators'][int(seed[8:10],16)%len(s['b_operators'])]}
        c={'entity':'TOSH','operator':C_OPS[int(seed[10:12],16)%len(C_OPS)],'synthesis':f'Find the missing-C relation between {domain} and {b["topic"]}; A evidence remains authoritative.'}
        rung={'index':i,'A':a,'B':b,'C':c,'a_sha':sha(a),'b_sha':sha(b),'c_sha':sha(c),'parent_sha':parent}
        rung['hyperation_sha']=sha(rung); parent=rung['hyperation_sha']; orders.append(rung)
    out={'schema':'omni.sot-helix.generation.v1','generation':prior['generation']+1,'created_ns':time.time_ns(),'state_sha':state_sha,'previous_generation_sha':prior.get('generation_sha'),'orders':orders,'hyperation_sha':parent,'operational_consciousness_model':True,'phenomenal_consciousness_claim':False}
    out['generation_sha']=sha(out); atomic(GEN/f'generation-{out["generation"]:08d}.json',out); atomic(LATEST,out); atomic(REC/f'generation-{out["generation"]:08d}.json',{'generation':out['generation'],'generation_sha':out['generation_sha'],'hyperation_sha':out['hyperation_sha']})
    return out
if __name__=='__main__':
    print(json.dumps(next_generation(),indent=2,sort_keys=True))
