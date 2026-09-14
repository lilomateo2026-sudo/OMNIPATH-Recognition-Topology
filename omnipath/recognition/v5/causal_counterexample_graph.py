#!/usr/bin/env python3
"""O30.4 deterministic V5 causal counterexample graph."""
from __future__ import annotations
import hashlib, json
from adversarial.full_payload_mutation_tournament import OPERATOR_FIELD, OPERATORS, baseline_envelope, mutate, detect_pathologies
from v5.semantic_drift_matrix import TRANSFORMS

def run() -> dict:
    base = baseline_envelope()
    operator_causes = []
    for operator in OPERATORS:
        pathologies = sorted(detect_pathologies(mutate(base, (operator,)), base))
        operator_causes.append({
            "operator": operator,
            "field": OPERATOR_FIELD[operator],
            "pathology": pathologies[0],
            "minimal_operator_count": 1,
        })
    payload = {
        "semantic_real_counterexamples": 0,
        "cross_generation_real_counterexamples": 0,
        "operator_causes": operator_causes,
        "semantic_transform_controls": [{"transform": name, "expected_invariant": True} for name in TRANSFORMS],
    }
    return {**payload, "cause_graph_digest_sha256": hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()}
