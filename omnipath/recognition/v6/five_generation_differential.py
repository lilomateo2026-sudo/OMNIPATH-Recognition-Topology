#!/usr/bin/env python3
"""O32.1 deterministic Gen2/V3/V4/V5/V6 differential baseline."""
from __future__ import annotations

import copy
import hashlib
import json
import random

from adversarial.full_payload_mutation_tournament import (
    OPERATORS,
    apply_operator,
    baseline_envelope,
    detect_pathologies,
    disposition,
)

VERSIONS = {
    "gen2": ("4147562ee866bee2e96978907661a6fba9072779", "generation-2"),
    "v3": ("ba8a83d3b2def74ded2bbf9154c6190940ebd888", "generation-v3"),
    "v4": ("18068b6ac6438020ddef335c7e88f8c4a70961a4", "generation-v4"),
    "v5": ("a52f4de61adb9fd2101dafa34daa92c951fca6c2", "generation-v5"),
    "v6": ("c19551d92c306236b7c80c9422eb44a1afacb1af", "generation-v6"),
}


def version_baseline(parent: str, self_id: str) -> dict:
    value = baseline_envelope()
    value["lineage"]["parent"] = parent
    value["lineage"]["self"] = self_id
    return value


def mutate(value: dict, operators: tuple[str, ...]) -> dict:
    result = copy.deepcopy(value)
    for operator in operators:
        result = apply_operator(result, operator)
    return result


def classify(value: dict, baseline: dict) -> list:
    pathologies = sorted(detect_pathologies(value, baseline))
    return [pathologies, disposition(set(pathologies))]


def run(seed: int = 3201001, trials: int = 6000) -> dict:
    bases = {name: version_baseline(*config) for name, config in VERSIONS.items()}
    rng = random.Random(seed)
    rows = []
    mismatch_count = 0
    for trial in range(1, trials + 1):
        width = rng.choice([1, 2, 3, 4, 5, 6, 7, 8])
        operators = tuple(sorted(rng.sample(OPERATORS, width)))
        results = {name: classify(mutate(baseline, operators), baseline) for name, baseline in bases.items()}
        mismatch = len({(tuple(value[0]), value[1]) for value in results.values()}) != 1
        mismatch_count += int(mismatch)
        rows.append({"trial": trial, "operators": list(operators), **results, "mismatch": mismatch})
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    return {
        "schema": "omnipath.five-generation-differential/v1",
        "order": "O32.1",
        "seed": seed,
        "trials": trials,
        "mutation_widths": [1, 2, 3, 4, 5, 6, 7, 8],
        "operator_count": len(OPERATORS),
        "versions": VERSIONS,
        "mismatch_count": mismatch_count,
        "digest_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    }
