#!/usr/bin/env python3
"""O24.3 independent reference/evidence rail evolution generator."""

from __future__ import annotations

import hashlib
import json
import random

from adversarial.full_payload_mutation_tournament import OPERATORS


def generate_rail(name: str, seed: int, cases: int = 512) -> dict:
    rng = random.Random(seed)
    rows = []
    for index in range(1, cases + 1):
        width = rng.choice([1, 2, 3])
        operators = tuple(sorted(rng.sample(OPERATORS, width)))
        source_event_id = f"{name}:source:{index:04d}"
        payload = f"{name}|{seed}|{index}|{','.join(operators)}"
        discovery_id = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]
        rows.append(
            {
                "case": index,
                "source_event_id": source_event_id,
                "discovery_id": discovery_id,
                "operators": list(operators),
            }
        )

    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    return {
        "rail": name,
        "seed": seed,
        "cases": cases,
        "digest_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "rows": rows,
    }


def run(cases: int = 512) -> dict:
    reference = generate_rail("reference-transfer", 2403001, cases)
    evidence = generate_rail("evidence-transfer", 2403002, cases)

    reference_discoveries = {row["discovery_id"] for row in reference["rows"]}
    evidence_discoveries = {row["discovery_id"] for row in evidence["rows"]}
    reference_sources = {row["source_event_id"] for row in reference["rows"]}
    evidence_sources = {row["source_event_id"] for row in evidence["rows"]}

    shared_discoveries = sorted(reference_discoveries & evidence_discoveries)
    shared_sources = sorted(reference_sources & evidence_sources)
    independent = not shared_discoveries and not shared_sources

    return {
        "schema": "omnipath.cross-rail-evolution/v1",
        "order": "O24.3",
        "shared_root": "O24.2@397434ebeca79b077cd5e95142ebbfa3a936fde4",
        "reference": reference,
        "evidence": evidence,
        "shared_discovery_ids": shared_discoveries,
        "shared_source_event_ids": shared_sources,
        "shared_root_only": independent,
        "authority_merged": False,
        "independence_pass": independent,
    }
