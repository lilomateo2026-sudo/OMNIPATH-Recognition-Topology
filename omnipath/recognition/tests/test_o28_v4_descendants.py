import copy, hashlib, json, random, unittest
from pathlib import Path
from adversarial.full_payload_mutation_tournament import OPERATORS, apply_operator, baseline_envelope, detect_pathologies, disposition
ROOT=Path(__file__).resolve().parents[3]
Q=ROOT/"omnipath"/"recognition"/"v4"/"O28_3_genome_quartet.json"
C=ROOT/"omnipath"/"recognition"/"v4"/"O28_4_differential_cause_graph.json"
T=ROOT/"omnipath"/"recognition"/"v4"/"O28_5_replay_counterexample_tournament.json"

def stream(letter,cfg,n):
    rng=random.Random(cfg["seed"]); rows=[]
    for i in range(1,n+1):
        nonce=rng.getrandbits(64); ns=cfg["namespace"]
        did=hashlib.sha256(f"{ns}|discovery|{i}|{nonce}".encode()).hexdigest()[:24]
        sid=hashlib.sha256(f"{ns}|source|{i}|{nonce^cfg['seed']}".encode()).hexdigest()[:24]
        rows.append({"index":i,"discovery_id":did,"source_event_id":sid})
    digest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return rows,digest

def mutate(value,ops):
    result=copy.deepcopy(value)
    for op in ops: result=apply_operator(result,op)
    return result

def classify(value,base):
    p=sorted(detect_pathologies(value,base)); return p,disposition(set(p))

class O28V4DescendantTests(unittest.TestCase):
    def test_o283_quartet_independence(self):
        m=json.loads(Q.read_text()); disc={}; src={}
        for letter,cfg in m["genomes"].items():
            rows,digest=stream(letter,cfg,m["events_per_genome"]); self.assertEqual(digest,cfg["stream_digest_sha256"])
            disc[letter]={r["discovery_id"] for r in rows}; src[letter]={r["source_event_id"] for r in rows}
        letters=sorted(disc)
        for i,a in enumerate(letters):
            for b in letters[i+1:]:
                self.assertEqual(len(disc[a]&disc[b]),m["expected_shared_discovery_ids"])
                self.assertEqual(len(src[a]&src[b]),m["expected_shared_source_event_ids"])
        self.assertFalse(m["promotion_authority"])

    def test_o284_cause_graph_and_minimal_controls(self):
        m=json.loads(C.read_text()); base=baseline_envelope()
        canonical=json.dumps(m["operator_causes"],sort_keys=True,separators=(",",":")); self.assertEqual(hashlib.sha256(canonical.encode()).hexdigest(),m["cause_graph_digest_sha256"])
        for node in m["operator_causes"]:
            detected=detect_pathologies(apply_operator(base,node["operator"]),base)
            self.assertIn(node["pathology"],detected); self.assertEqual(node["minimal_operator_count"],1)
        self.assertEqual(m["real_cross_generation_mismatches"],0); self.assertEqual(m["real_counterexample_nodes"],0)
        self.assertFalse(m["promotion_authority"])

    def test_o285_replay_counterexample_tournament(self):
        q=json.loads(Q.read_text()); m=json.loads(T.read_text()); base=baseline_envelope(); base["lineage"]["parent"]="e031ff386c426b6644c01d94da3009628c0cf1e4"; base["lineage"]["self"]="v4-replay"
        summaries={}
        for letter,cfg in q["genomes"].items():
            rows=[]; div=0
            for offset in m["schedule_offsets"]:
                rng=random.Random(cfg["seed"]+offset)
                for rnd in range(1,m["rounds_per_schedule"]+1):
                    width=rng.choice([1,2,3,4,5,6]); ops=tuple(sorted(rng.sample(OPERATORS,width)))
                    forward=classify(mutate(base,ops),base); reverse=classify(mutate(base,tuple(reversed(ops))),base); mismatch=forward!=reverse; div+=int(mismatch)
                    rows.append({"genome":letter,"schedule_seed":cfg["seed"]+offset,"round":rnd,"operators":list(ops),"forward":[forward[0],forward[1]],"reverse":[reverse[0],reverse[1]],"divergence":mismatch})
            digest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(",",":")).encode()).hexdigest(); expected=m["genomes"][letter]
            self.assertEqual(div,expected["divergences"]); self.assertEqual(digest,expected["replay_digest_sha256"])
            summaries[letter]={"rounds":len(rows),"divergences":div,"replay_digest_sha256":digest,"stream_digest_sha256":cfg["stream_digest_sha256"]}
        winner=min(summaries,key=lambda x:(summaries[x]["divergences"],summaries[x]["stream_digest_sha256"],x)); overall=hashlib.sha256(json.dumps({"summaries":summaries,"winner":winner},sort_keys=True,separators=(",",":")).encode()).hexdigest()
        self.assertEqual(winner,m["selected_genome"]); self.assertEqual(overall,m["tournament_digest_sha256"]); self.assertEqual(m["real_counterexample_count"],0); self.assertEqual(m["unminimized_real_counterexamples"],0); self.assertFalse(m["promotion_authority"])

if __name__=="__main__": unittest.main()
