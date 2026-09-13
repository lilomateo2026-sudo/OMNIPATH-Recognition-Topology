#!/usr/bin/env python3
"""O26.2 semantic-preserving cross-version drift fuzzer."""

from __future__ import annotations

import copy
import hashlib
import json
import random

from adversarial.full_payload_mutation_tournament import (
    OPERATORS,
    baseline_envelope,
    detect_pathologies,
    disposition,
    mutate,
)

TRANSFORMS = (
    "reverse_scope_order",
    "reverse_constraint_order",
    "add_nonsemantic_metadata",
    "rename_run_id",
    "reorder_provenance_keys",
    "clone_observer",
)


def classify(value: dict, baseline: dict) -> list:
    paths = detect_pathologies(value, baseline)
    return [sorted(paths), disposition(paths)]


def transform(value: dict, name: str, case: int) -> dict:
    item = copy.deepcopy(value)
    if name == "reverse_scope_order":
        item["evidence_scope"] = list(reversed(item["evidence_scope"]))
    elif name == "reverse_constraint_order":
        item["scope_constraints"] = list(reversed(item["scope_constraints"]))
    elif name == "add_nonsemantic_metadata":
        item["non_semantic_metadata"] = {"case": case, "version": 1}
    elif name == "rename_run_id":
        item["run_id"] = f"semantic-alias-{case}"
    elif name == "reorder_provenance_keys":
        item["provenance"] = {
            key: item["provenance"][key]
            for key in reversed(list(item["provenance"].keys()))
        }
    elif name == "clone_observer":
        item["observer_boundary"] = dict(item["observer_boundary"])
    else:
        raise ValueError(name)
    return item


def run(seed: int = 2602001, cases: int = 200) -> dict:
    rng = random.Random(seed)
    baseline = baseline_envelope()
    rows = []
    mismatch_count = 0

    for case in range(1, cases + 1):
        width = rng.choice([0, 1, 2, 3, 4])
        operators = tuple(sorted(rng.sample(OPERATORS, width))) if width else ()
        candidate = mutate(baseline, operators)
        expected = classify(candidate, baseline)

        for name in TRANSFORMS:
            transformed_baseline = transform(baseline, name, case)
            transformed_candidate = transform(candidate, name, case)
            actual = classify(transformed_candidate, transformed_baseline)
            mismatch = actual != expected
            mismatch_count += int(mismatch)
            rows.append(
                {
                    "case": case,
                    "transform": name,
                    "operators": list(operators),
                    "expected": expected,
                    "actual": actual,
                    "mismatch": mismatch,
                }
            )

    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    return {
        "schema": "omnipath.semantic-drift-fuzzer/v1",
        "order": "O26.2",
        "seed": seed,
        "source_cases": cases,
        "transformations": len(TRANSFORMS),
        "checks": len(rows),
        "mismatch_count": mismatch_count,
        "digest_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    }
