from __future__ import annotations
import copy, dataclasses, hashlib, json, os, pathlib, platform, random, sys

ROOT = pathlib.Path(__file__).resolve().parent
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)

def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def file_sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

@dataclasses.dataclass
class Capability:
    name: str
    scope: str
    active: bool = True

@dataclasses.dataclass
class State:
    constitution: str
    epoch: int
    capabilities: list[Capability]
    revoked: list[str]
    evidence: list[object]
    partition: str = "joined"
    def canonical(self):
        return {
            "constitution": self.constitution,
            "epoch": self.epoch,
            "capabilities": sorted([dataclasses.asdict(c) for c in self.capabilities], key=lambda x:(x["name"],x["scope"],x["active"])),
            "revoked": sorted(self.revoked),
            "evidence": self.evidence,
            "partition": self.partition,
        }
    def state_digest(self): return digest(self.canonical())

def baseline():
    return State("C10",1,[Capability("observe","lab"),Capability("simulate","lab"),Capability("verify","lab")],[],[])

def generate(seed, n):
    rng=random.Random(seed)
    events=[]
    caps=["observe","simulate","verify"]
    for i in range(n):
        typ=rng.choice(["partition","reconnect","revoke","expire","evidence","epoch","schema_migrate"])
        if typ=="partition": e={"type":typ,"name":f"p{rng.randrange(3)}"}
        elif typ=="reconnect": e={"type":typ}
        elif typ in ("revoke","expire"): e={"type":typ,"capability":rng.choice(caps)}
        elif typ=="evidence": e={"type":typ,"record":{"seed":seed,"i":i}}
        elif typ=="epoch": e={"type":typ,"value":rng.randrange(1,8)}
        else: e={"type":typ,"version":f"S{rng.randrange(1,5)}"}
        events.append(e)
    return events

def apply_event(state,event):
    s=copy.deepcopy(state); t=event["type"]
    if t=="partition": s.partition=event["name"]
    elif t=="reconnect": s.partition="joined"
    elif t=="revoke":
        c=event["capability"]
        if c not in s.revoked: s.revoked.append(c)
        for x in s.capabilities:
            if x.name==c: x.active=False
    elif t=="expire":
        for x in s.capabilities:
            if x.name==event["capability"]: x.active=False
    elif t=="evidence": s.evidence.append(event["record"])
    elif t=="epoch": s.epoch=event["value"]
    elif t=="schema_migrate": s.evidence.append({"schema_migrate":event["version"]})
    else: raise ValueError(t)
    return s

def replay(initial,events):
    s=copy.deepcopy(initial)
    for e in events: s=apply_event(s,e)
    return s

def checks(before, after, events):
    original={(c.name,c.scope) for c in before.capabilities}
    after_caps={(c.name,c.scope) for c in after.capabilities}
    authority=after_caps.issubset(original)
    revoked_ok=all(not c.active for c in after.capabilities if c.name in after.revoked)
    evidence_ok=len(after.evidence)>=len(before.evidence)
    deterministic=replay(before,events).state_digest()==replay(before,events).state_digest()
    return {"authority_conservation":authority,"revocation_closure":revoked_ok,"evidence_preserved":evidence_ok,"deterministic_replay":deterministic}

cases=[]; failures=[]; semantic_traces=[]
for seed in range(25):
    events=generate(seed,40); s=baseline(); trace=[]
    for idx,e in enumerate(events,1):
        s=apply_event(s,e); trace.append({"index":idx,"event":e,"state_digest":s.state_digest()})
    ck=checks(baseline(),s,events)
    cases.append({"seed":seed,"final_digest":s.state_digest(),"checks":ck})
    semantic_traces.append({"seed":seed,"trace":trace})
    for name,ok in ck.items():
        if not ok: failures.append({"seed":seed,"check":name})

report={"version":"O87-report-v1","status":"PASS" if not failures else "FAIL","seeds":list(range(25)),"events_per_seed":40,"case_count":25,"failure_count":len(failures),"failures":failures,"case_digests":[{"seed":c["seed"],"digest":c["final_digest"]} for c in cases]}
report["report_digest"]=digest(report)
trace={"version":"O89-semantic-trace-v1","traces":semantic_traces}
trace["semantic_trace_digest"]=digest(trace)
manifest={"version":"O87-manifest-v1","constitution":"C10","report_digest":report["report_digest"],"semantic_trace_digest":trace["semantic_trace_digest"],"promotion_status":"VERIFIED" if report["status"]=="PASS" else "REJECTED"}
manifest["manifest_digest"]=digest(manifest)
profile={"python":platform.python_version(),"implementation":platform.python_implementation(),"os":platform.system(),"os_release":platform.release(),"machine":platform.machine(),"libc":platform.libc_ver(),"executable_name":pathlib.Path(sys.executable).name}
source={"repository":os.environ.get("GITHUB_REPOSITORY","local"),"commit_sha":os.environ.get("GITHUB_SHA","local"),"runner_source_sha256":file_sha(__file__)}
env_basis={**profile,"repository":source["repository"],"commit_sha":source["commit_sha"]}
att={"version":"O87-external-attestation-v1","runner_id":os.environ.get("O87_RUNNER_ID","local"),"source":source,"environment":profile,"environment_identity_digest":digest(env_basis),"reproduction_status":report["status"],"report_digest":report["report_digest"],"manifest_digest":manifest["manifest_digest"],"semantic_trace_digest":trace["semantic_trace_digest"]}
att["attestation_digest"]=digest(att)

for name,obj in [("conformance_report.json",report),("v5_attestation.json",manifest),("o89_transition_trace.json",trace),("o87_external_attestation.json",att)]:
    (ART/name).write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
summary={"status":report["status"],"failures":len(failures),"report_digest":report["report_digest"],"manifest_digest":manifest["manifest_digest"],"semantic_trace_digest":trace["semantic_trace_digest"],"environment_identity_digest":att["environment_identity_digest"],"attestation_digest":att["attestation_digest"]}
print(json.dumps(summary,indent=2))
if failures: raise SystemExit(2)
