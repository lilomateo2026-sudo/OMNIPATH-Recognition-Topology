#!/usr/bin/env python3
import hashlib,json,os,re,sqlite3,time
from pathlib import Path
BASE=Path("/var/lib/omni-sfc/omnipath-auto")
DB=BASE/"state.sqlite3"
CHAT=Path("/var/lib/omni-sfc/odyssey-v2/chat_lineage.sqlite3")
ORD=Path("/var/lib/omni-sfc/amni/omnipath")
AUTO=Path("/var/lib/omni-sfc/autonomy/orders.sqlite3")
def C(x):return json.dumps(x,sort_keys=True,separators=(",",":"),default=str)
def H(x):return hashlib.sha256(C(x).encode()).hexdigest()
def J(p):
 try:return json.loads(Path(p).read_text())
 except:return {}
ROOTS=["/var/lib/omni-sfc/semantic-mapping-data","/var/lib/omni-sfc/recollection","/var/lib/omni-sfc/crossrag","/var/lib/omni-sfc/morphogenesis","/var/lib/omni-sfc/agent-fabric","/var/lib/omni-sfc/happy-accident","/opt/omni-sfc/omniverse/v25","/opt/omni-sfc/repos/OMNIPATH","/var/lib/omni-sfc/omnipath"]
def db():
 BASE.mkdir(parents=True,exist_ok=True); c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; c.execute("pragma journal_mode=wal")
 c.executescript("create table if not exists cycles(id integer primary key,ts integer,state_sha text,plan_sha text,receipt_sha text); create table if not exists orders(id text primary key,cycle integer,slot integer,a text,b text,task text,pathology text,state text,exec_id text); create table if not exists events(seq integer primary key,ts integer,kind text,body text,sha text);")
 c.commit(); return c
def inv(p):
 h=hashlib.sha256(); n=b=0
 if not Path(p).exists():return {"path":p,"files":0,"bytes":0,"sha":None}
 for r,ds,fs in os.walk(p):
  ds.sort(); fs.sort()
  for f in fs:
   q=Path(r)/f
   try:s=q.stat()
   except:continue
   h.update(f"{q.relative_to(p)}|{s.st_size}|{s.st_mtime_ns}\n".encode()); n+=1; b+=s.st_size
 return {"path":p,"files":n,"bytes":b,"sha":h.hexdigest()}
def history():
 x=[]
 for p in ORD.glob("*.json"):
  d=J(p); t=d.get("created_ns",0)
  for k,v in d.get("orders",{}).items():
   x.append({"id":k,"ts":v.get("created_ns",t) if isinstance(v,dict) else t,"state":(v.get("status") or v.get("state") or v.get("outcome") or v.get("decision") or "UNKNOWN") if isinstance(v,dict) else "UNKNOWN"})
 x.sort(key=lambda z:(z["ts"],z["id"])); return x[-5:]
def states(path,table):
 try:
  c=sqlite3.connect(path); z={str(s):n for s,n in c.execute(f"select state,count(*) from {table} group by state")}; c.close(); return z
 except:return {}
ROOTS += ["/opt/omni-sfc/omniverse","/opt/omni-sfc/chat-master-v2","/opt/omni-sfc/tosh-omnipath-chat-v2","/var/lib/omni-sfc/memory-fabric","/var/lib/omni-sfc/semantic"]
def chats():
 c=sqlite3.connect(CHAT); h=hashlib.sha256()
 for r in c.execute("select message_sha256 from messages order by message_id"):
  if r[0]:h.update(r[0].encode())
 titles=[r[0] for r in c.execute("select title from conversations where title is not null and trim(title)!=\"\" order by conversation_id")]
 o={"conversations":c.execute("select count(*) from conversations").fetchone()[0],"messages":c.execute("select count(*) from messages").fetchone()[0],"root":h.hexdigest(),"titles":titles}; c.close(); return o
def snap():
 ch=chats(); last=history(); invs=[inv(p) for p in ROOTS]; load=os.getloadavg(); cpu=os.cpu_count() or 1
 o={"last5":last,"chat":{"conversations":ch["conversations"],"messages":ch["messages"],"root":ch["root"]},"titles":ch["titles"],"inventory":invs}
 o["priority"]=J("/var/lib/omni-sfc/semantic-mapping-data/priority_staging_latest.json")
 o["node04"]=J("/var/lib/omni-sfc/worlds/world-04-iphone/promotion_gate.json")
 o["temple"]=J("/var/lib/omni-sfc/omni-temple/training/dataset_tribunal_latest.json")
 o["gpu"]=J("/var/lib/omni-sfc/semantic-mapping-data/gpu_admission_latest.json")
 o["queues"]={"omnipath":states("/var/lib/omni-sfc/omnipath/queue.sqlite3","jobs"),"autonomy":states("/var/lib/omni-sfc/autonomy/orders.sqlite3","orders"),"agents":states("/var/lib/omni-sfc/agent-fabric/fabric.sqlite3","jobs")}
 o["load"]={"one":round(load[0],3),"five":round(load[1],3),"fifteen":round(load[2],3),"cpus":cpu,"ratio":round(load[0]/cpu,3)}
 stable={k:v for k,v in o.items() if k not in ("titles","load")}; o["state_sha"]=H(stable); o["source_sha"]=H(invs); return o
def specs(s):
 n=s["node04"].get("criteria",{}); miss=sum(1 for v in n.values() if not v); gb=len(s["gpu"].get("blockers",[])); lr=s["load"]["ratio"]; ts=s["temple"].get("samples",0)
 return [
  ("node04","NODE-04 Native Continuity",1000 if miss else 300,"OBSERVE",f"Preserve and re-evaluate {miss} missing native NODE-04 gates using native evidence only.",["node04","iphone"]),
  ("sequence","Sequence-Loop Determinism",980,"TRANSFORM","Verify last-five to next-five deterministic replay, idempotency and append-only receipts.",["omnipath","sequence"]),
  ("resource","Flagship Resource Relativity",970 if lr>.75 else 420,"OBSERVE",f"Evaluate load ratio {lr:.3f} and protect Hivelocity foreground work with reversible controls.",["load","hivelocity"]),
  ("gpu","GPU Admission Relativity",900 if gb else 350,"TRACE",f"Re-evaluate {gb} GPU blockers while keeping training default-deny until admission evidence passes.",["gpu","training"]),
  ("temple","Temple Evolution",820,"TRACE",f"Compare Temple corpus state ({ts} samples) against sealed baselines and regression gates.",["temple","dataset"]),
  ("chat","Chat-Lineage Recollection",790,"RAG",f"Use {s[\"chat\"][\"conversations\"]} exported chats and {s[\"chat\"][\"messages\"]} messages as evidence-addressed continuation history.",["chat","lineage"]),
  ("crossrag","CrossRAG Evidence",760,"RAG","Ground next-step proposals in CrossRAG provenance before promotion.",["crossrag","evidence"]),
  ("recollection","Recollection Recovery",740,"TRANSFORM","Bind receipts, chat lineage and contradictions into recoverable continuation state.",["recollection","memory"]),
  ("morphogenesis","Morphogenesis Runtime",730,"EVOLVE","Generate a bounded causal upgrade candidate with rollback and tribunal requirements.",["morphogenesis","causal"]),
  ("agent","Agent Fabric Backpressure",710,"ROUTE","Audit agent-fabric pressure and route only resource-bounded jobs.",["agent","fabric"]),
  ("omniverse","OMNIVERSE V25 Continuity",700,"TRACE","Compare current lineage against OMNIVERSE V25/V26/V27 artifacts and surface compatible upgrades.",["omniverse","v25"]),
  ("tosh","TOSH Language Queue",690,"TRACE","Verify TOSH queue payload and receipt lineage without treating model prose as authority.",["tosh","queue"]),
  ("orchard","Happy Orchard Novelty",680,"EVOLVE","Harvest novelty as candidate structure without allowing novelty to override evidence.",["orchard","novelty"]) ]
def ranked(s):
 b=C(s["last5"]).lower(); out=[]
 for dom,title,need,path,task,keys in specs(s):
  cont=100 if any(k in b for k in keys) else 40; novel=25 if cont==100 else 100
  hist=min(100,8*sum(1 for t in s["titles"] if any(k in t.lower() for k in keys)))
  penalty=80 if cont==100 and need>=950 else (240 if cont==100 else 0)
  score=4*need+2*cont+hist+novel-penalty; out.append({"domain":dom,"title":title,"need":need,"pathology":path,"task":task,"keys":keys,"score":score,"continuity":cont,"history":hist,"novelty":novel,"penalty":penalty})
 return sorted(out,key=lambda x:(-x["score"],H(x["domain"])))
BOPS=["constraint-transfer","failure-mode-analogy","memory-structure","routing-pattern","evaluation-pattern","counterfactual-bridge"]
def pick_b(s,a,slot,seed,used):
 titles=s["titles"] or ["Sequence of Thought"]
 q=hashlib.sha256(f"{seed}|{slot}|{a[\"domain\"]}".encode()).digest()
 start=int.from_bytes(q[:8],"big")%len(titles); title=titles[start]
 for j in range(len(titles)):
  t=titles[(start+j)%len(titles)]
  if t not in used and not any(k in t.lower() for k in a["keys"]): title=t; break
 used.add(title)
 return {"topic":title,"operator":BOPS[q[8]%len(BOPS)],"authority":"candidate_only"}
def make_plan(c,s,cid):
 r=c.execute("select plan_sha from cycles where id<? order by id desc limit 1",(cid,)).fetchone()
 prior=r[0] if r and r[0] else "GENESIS"
 seed=H({"state":s["state_sha"],"last5":s["last5"],"prior":prior})
 used=set(); orders=[]
 for slot,a in enumerate(ranked(s)[:5],1):
  b=pick_b(s,a,slot,seed,used); oid=f"O-AUTO-NEXT5-{cid:06d}-{slot:02d}"
  task=a["task"]+f" Part B helix: use {b[\"topic\"]!r} through {b[\"operator\"]} to test one cross-domain bridge; Part A remains authoritative."
  orders.append({"id":oid,"slot":slot,"a":a,"b":b,"task":task,"pathology":a["pathology"],"sot":["experience","observation","perspective_shift","meaning","regulation","creation"]})
 p={"schema":"omni.next5.autonomous-plan.v1","cycle":cid,"state_sha":s["state_sha"],"source_sha":s["source_sha"],"chat_sha":s["chat"]["root"],"last5":s["last5"],"orders":orders}
 p["path_count"]=5; p["subpath_count"]=10; p["previous_plan_sha"]=prior; p["plan_sha"]=H(p); return p
SEQ=Path("/opt/omni-sfc/repos/OMNIPATH/src/sequence_loop.py")
SEQIN=Path("/opt/omni-sfc/repos/OMNIPATH/state/inbox")
def sequence_stage(p):
 SEQIN.mkdir(parents=True,exist_ok=True)
 for o in p["orders"]:
  q={"order_id":o["id"],"title":o["a"]["title"],"task":o["task"],"requires":o["a"].get("keys",[]),"estimated_cost":0.2,"mode":"shadow" if o["pathology"]=="EVOLVE" else "observation","provenance_required":True,"part_a":o["a"],"part_b":o["b"]}
  f=SEQIN/(o["id"]+".json")
  if not f.exists() and not (SEQIN/(o["id"]+".processed")).exists(): f.write_text(json.dumps(q,indent=2,sort_keys=True)+"\n")
def sequence_process(ratio):
 if ratio>.75:return {"status":"DEFERRED_HIGH_LOAD"}
 try:
  r=subprocess.run(["/usr/bin/python3",str(SEQ)],capture_output=True,text=True,timeout=300); return {"status":"PASS" if r.returncode==0 else "ERROR","stdout":r.stdout[-500:],"stderr":r.stderr[-500:]}
 except Exception as e:return {"status":"ERROR","error":type(e).__name__}
ALLOW={"OBSERVE","TRACE","RAG","TRANSFORM","RECOVER","ROUTE","EVOLVE"}
def submit(c,cid,p):
 ac=sqlite3.connect(AUTO); now=time.time()
