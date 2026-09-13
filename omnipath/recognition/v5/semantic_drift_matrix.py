#!/usr/bin/env python3
"""O30.2 deterministic four-generation semantic drift matrix."""
from __future__ import annotations
import copy, hashlib, json, random
from adversarial.full_payload_mutation_tournament import OPERATORS
from v5.four_generation_differential import VERSIONS, version_baseline, mutate, classify

TRANSFORMS = (
    "reverse_scope_order",
    "reverse_constraint_order",
    "add_nonsemantic_metadata",
    "rename_run_id",
    "reorder_provenance_keys",
    "clone_observer",
    "reorder_contradiction_keys",
)

def transform(value: dict, name: str, case: int) -> dict:
    result = copy.deepcopy(value)
    if name == "reverse_scope_order":
        result["evidence_scope"] = list(reversed(result["evidence_scope"]))
    elif name == "reverse_constraint_order":
        result["scope_constraints"] = list(reversed(result["scope_constraints"]))
    elif name == "add_nonsemantic_metadata":
        result["non_semantic_metadata"] = {"case": case, "version": 1, "tag": "v5-semantic"}
    elif name == "rename_run_id":
        result["run_id"] = f"semantic-alias-{case}"
    elif name == "reorder_provenance_keys":
        result["provenance"] = {k: result["provenance"][k] for k in reversed(list(result["provenance"].keys()))}
    elif name == "clone_observer":
        result["observer_boundary"] = dict(result["observer_boundary"])
    elif name == "reorder_contradiction_keys":
        if result["contradictory_evidence"]:
            item = result["contradictory_evidence"][0]
            result["contradictory_evidence"][0] = {k: item[k] for k in reversed(list(item.keys()))}
    else:
        raise ValueError(name)
    return result

def run(seed: int = 3002001, cases: int = 800) -> dict:
    bases = {name: version_baseline(*config) for name, config in VERSIONS.items()}
    rng = random.Random(seed)
    rows = []
    semantic_mismatches = 0
    cross_generation_mismatches = 0
    for case in range(1, cases + 1):
        width = rng.choice([0,1,2,3,4,5,6,7])
        operators = tuple(sorted(rng.sample(OPERATORS, width))) if width else ()
        candidates = {name: mutate(base, operators) for name, base in bases.items()}
        expected = {name: classify(candidates[name], bases[name]) for name in bases}
        for semantic_transform in TRANSFORMS:
            results = {
                name: classify(
                    transform(candidates[name], semantic_transform, case),
                    transform(bases[name], semantic_transform, case),
                )
                for name in bases
            }
            semantic_mismatch = any(results[name] != expected[name] for name in bases)
            cross_generation_mismatch = len({(tuple(value[0]), value[1]) for value in results.values()}) != 1
            semantic_mismatches += int(semantic_mismatch)
            cross_generation_mismatches += int(cross_generation_mismatch)
            rows.append({
                "case": case,
                "transform": semantic_transform,
                "operators": list(operators),
                **results,
                "semantic_mismatch": semantic_mismatch,
                "cross_generation_mismatch": cross_generation_mismatch,
            })
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    return {
        "schema": "omnipath.v5-semantic-drift-matrix/v1",
        "order": "O30.2",
        "seed": seed,
        "cases": cases,
        "checks": len(rows),
        "transforms": list(TRANSFORMS),
        "semantic_mismatches": semantic_mismatches,
        "cross_generation_mismatches": cross_generation_mismatches,
        "digest_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    }
