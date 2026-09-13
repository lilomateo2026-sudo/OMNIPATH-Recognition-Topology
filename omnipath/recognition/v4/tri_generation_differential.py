#!/usr/bin/env python3
"""O28.2 Generation-2/V3/V4 differential fuzzer."""
from __future__ import annotations
import copy, hashlib, json, random
from adversarial.full_payload_mutation_tournament import OPERATORS, apply_operator, baseline_envelope, detect_pathologies, disposition
TRANSFORMS=("reverse_scope_order","reverse_constraint_order","add_nonsemantic_metadata","rename_run_id","reorder_provenance_keys","clone_observer")
VERSIONS={"gen2":("4147562ee866bee2e96978907661a6fba9072779","generation-2"),"v3":("ba8a83d3b2def74ded2bbf9154c6190940ebd888","generation-v3"),"v4":("e031ff386c426b6644c01d94da3009628c0cf1e4","generation-v4")}
def version_baseline(parent,self_id):
    v=baseline_envelope(); v["lineage"]["parent"]=parent; v["lineage"]["self"]=self_id; return v
def mutate(v,ops):
    r=copy.deepcopy(v)
    for op in ops: r=apply_operator(r,op)
    return r
def classify(v,b):
    p=sorted(detect_pathologies(v,b)); return [p,disposition(set(p))]
def transform(v,name,case):
    x=copy.deepcopy(v)
    if name=="reverse_scope_order": x["evidence_scope"]=list(reversed(x["evidence_scope"]))
    elif name=="reverse_constraint_order": x["scope_constraints"]=list(reversed(x["scope_constraints"]))
    elif name=="add_nonsemantic_metadata": x["non_semantic_metadata"]={"case":case,"version":1}
    elif name=="rename_run_id": x["run_id"]=f"semantic-alias-{case}"
    elif name=="reorder_provenance_keys": x["provenance"]={k:x["provenance"][k] for k in reversed(list(x["provenance"].keys()))}
    elif name=="clone_observer": x["observer_boundary"]=dict(x["observer_boundary"])
    else: raise ValueError(name)
    return x
def run(full_seed=2802001,full_trials=4200,semantic_seed=2802002,semantic_cases=300):
    bases={n:version_baseline(*cfg) for n,cfg in VERSIONS.items()}; rng=random.Random(full_seed); rows=[]; mismatches=0
    for trial in range(1,full_trials+1):
        width=rng.choice([1,2,3,4,5,6]); ops=tuple(sorted(rng.sample(OPERATORS,width))); results={n:classify(mutate(b,ops),b) for n,b in bases.items()}; mismatch=len({(tuple(v[0]),v[1]) for v in results.values()})!=1; mismatches+=int(mismatch); rows.append({"trial":trial,"operators":list(ops),**results,"mismatch":mismatch})
    full_digest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(",",":")).encode()).hexdigest(); rng=random.Random(semantic_seed); srows=[]; semantic_mismatches=0; cross_mismatches=0
    for case in range(1,semantic_cases+1):
        width=rng.choice([0,1,2,3,4,5,6]); ops=tuple(sorted(rng.sample(OPERATORS,width))) if width else (); candidates={n:mutate(b,ops) for n,b in bases.items()}; expected={n:classify(candidates[n],bases[n]) for n in bases}
        for tr in TRANSFORMS:
            results={n:classify(transform(candidates[n],tr,case),transform(bases[n],tr,case)) for n in bases}; sm=any(results[n]!=expected[n] for n in bases); cv=len({(tuple(v[0]),v[1]) for v in results.values()})!=1; semantic_mismatches+=int(sm); cross_mismatches+=int(cv); srows.append({"case":case,"transform":tr,"operators":list(ops),**results,"semantic_mismatch":sm,"cross_version_mismatch":cv})
    semantic_digest=hashlib.sha256(json.dumps(srows,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return {"order":"O28.2","full_payload":{"trials":full_trials,"mismatches":mismatches,"digest_sha256":full_digest},"semantic":{"cases":semantic_cases,"checks":len(srows),"semantic_mismatches":semantic_mismatches,"cross_version_mismatches":cross_mismatches,"digest_sha256":semantic_digest}}
