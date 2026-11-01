#!/usr/bin/env python3
import json, math, sqlite3, urllib.request
from pathlib import Path
BASE=Path('/opt/omni-sfc/omni-platform'); DB=BASE/'state/omni_matrix.sqlite3'; OUT=BASE/'state/matrix_lineage'
TOPICS=['relativity','provenance','memory','contradiction','semantic continuity','resilience','creativity','efficiency','quantum formalism','metaphysics','metadata','language','information','topology','scale','causality','uncertainty']
DESC={
'relativity':'relationships that change with frame, context, scale or observer','provenance':'lineage, source identity, receipts and evidence genealogy','memory':'continuity, retrieval and historical state','contradiction':'conflict detection, falsification and opposing claims','semantic continuity':'preserving meaning across changing representations','resilience':'recovery, robustness and fault tolerance','creativity':'novel counterfactual synthesis and architectural imagination','efficiency':'latency, memory, cost and throughput','quantum formalism':'density matrices, operators and quantum information mathematics','metaphysics':'philosophical possibility, observer and ontology hypotheses','metadata':'typed descriptive records about artifacts and transformations','language':'natural, symbolic and programming language translation','information':'entropy, compression and causal organization','topology':'graph structure, connectivity and arrangement','scale':'micro to macro normalization and dimensionless comparison','causality':'intervention, dependency and directional explanation','uncertainty':'calibration, confidence and unknown-state representation'}
def emb(text):
    req=urllib.request.Request('http://127.0.0.1:11434/api/embeddings',data=json.dumps({'model':'nomic-embed-text:latest','prompt':text}).encode(),headers={'Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(req,timeout=20) as r:return json.load(r)['embedding']
def cos(a,b):
    d=sum(x*y for x,y in zip(a,b)); na=math.sqrt(sum(x*x for x in a)); nb=math.sqrt(sum(y*y for y in b)); return d/(na*nb) if na and nb else 0.0
c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
r=c.execute("select genome_json from sim_candidates where cycle_id=(select cycle_id from sim_cycles where status='COMPLETE' order by ordinal desc limit 1) order by aggregate_score desc limit 1").fetchone(); genome=json.loads(r['genome_json']) if r else {}
context='OMNI Matrix orchestration candidate: '+json.dumps(genome,sort_keys=True)
cv=emb(context); vec={t:emb(t+': '+DESC[t]) for t in TOPICS}
best=None
for i,a in enumerate(TOPICS):
  for b in TOPICS[i+1:]:
    ra=max(0,cos(cv,vec[a])); rb=max(0,cos(cv,vec[b])); dist=max(0,1-cos(vec[a],vec[b])); bridge=0.55*((ra+rb)/2)+0.45*dist
    row=(bridge,a,b,ra,rb,dist)
    if best is None or row>best:best=row
out={'status':'PASS','topics':[best[1],best[2]],'bridge_score':round(best[0],6),'context_relevance':[round(best[3],6),round(best[4],6)],'semantic_distance':round(best[5],6),'model':'nomic-embed-text:latest','method':'0.55*context_relevance + 0.45*semantic_distance'}
OUT.mkdir(parents=True,exist_ok=True); (OUT/'semantic_bridge_latest.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
