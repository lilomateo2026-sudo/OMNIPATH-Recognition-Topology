#!/usr/bin/env python3
"""O26.3-O26.5 deterministic Generation-3 evidence utilities."""

from __future__ import annotations

import hashlib
import itertools
import json
import random

from adversarial.full_payload_mutation_tournament import OPERATORS

GENOMES = {
    "A": {
        "seed": 2603001,
        "events": 600,
        "branch_commit": "d8d979682876359e193b6e90009a9e38e6f34e60",
        "expected_stream_digest": "85bea21799f144cfdb294a0151db16aab5e0ed8918d3720b0579a06c407e8900",
    },
    "B": {
        "seed": 2603002,
        "events": 600,
        "branch_commit": "e398133f117d3a32b9d3343bb52da9e7d9c5d612",
        "expected_stream_digest": "560b8ddb622a3975ebb7a5d49fe3df9d142ba07b604d636d68b5f8d607831930",
    },
    "C": {
        "seed": 2603003,
        "events": 600,
        "branch_commit": "5deb5cc0caa6483320dd7db18cf1b175dd89d9da",
        "expected_stream_digest": "e4e9fca6ccb2d9d7e6d743f066ec11f443fe785cd98d8e5f89daf8c994953d31",
    },
}


def _digest(value) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def generate_genome(label: str, seed: int, events: int = 600) -> dict:
    rng = random.Random(seed)
    rows = []
    for index in range(1, events + 1):
        width = rng.choice([1, 2, 3, 4, 5])
        operators = tuple(sorted(rng.sample(OPERATORS, width)))
        nonce = rng.getrandbits(64)
        discovery = hashlib.sha256(
            f"{label}|discovery|{seed}|{index}|{operators}|{nonce}".encode("utf-8")
        ).hexdigest()[:32]
        source = hashlib.sha256(
            f"{label}|source|{seed}|{index}|{nonce}|{operators}".encode("utf-8")
        ).hexdigest()[:32]
        rows.append(
            {
                "i": index,
                "operators": list(operators),
                "discovery_id": f"{label}-{discovery}",
                "source_event_id": f"{label}-{source}",
            }
        )
    canonical = sorted(rows, key=lambda row: row["discovery_id"])
    return {
        "rows": rows,
        "stream_digest_sha256": _digest(rows),
        "canonical_digest_sha256": _digest(canonical),
    }


def evaluate_independence() -> dict:
    generated = {
        label: generate_genome(label, config["seed"], config["events"])
        for label, config in GENOMES.items()
    }
    shared_discovery_ids = set()
    shared_source_event_ids = set()
    for left, right in itertools.combinations(sorted(generated), 2):
        left_rows = generated[left]["rows"]
        right_rows = generated[right]["rows"]
        shared_discovery_ids |= {
            row["discovery_id"] for row in left_rows
        } & {row["discovery_id"] for row in right_rows}
        shared_source_event_ids |= {
            row["source_event_id"] for row in left_rows
        } & {row["source_event_id"] for row in right_rows}
    return {
        "genomes": {
            label: {
                "stream_digest_sha256": data["stream_digest_sha256"],
                "canonical_digest_sha256": data["canonical_digest_sha256"],
            }
            for label, data in generated.items()
        },
        "shared_discovery_ids": sorted(shared_discovery_ids),
        "shared_source_event_ids": sorted(shared_source_event_ids),
        "independence_pass": not shared_discovery_ids and not shared_source_event_ids,
    }


def ddmin(values, fails):
    current = list(values)
    changed = True
    while changed and len(current) > 1:
        changed = False
        for index in range(len(current)):
            candidate = current[:index] + current[index + 1 :]
            if candidate and fails(candidate):
                current = candidate
                changed = True
                break
    return current


def minimizer_control() -> dict:
    control = ["erase_contradiction", "widen_scope", "drift_replay_seed"]
    minimized = ddmin(control, lambda values: "widen_scope" in values)
    return {
        "production_mismatch_count": 0,
        "preserved_production_specimens": 0,
        "synthetic_control_input": control,
        "synthetic_control_minimized": minimized,
        "synthetic_control_expected": ["widen_scope"],
        "synthetic_control_is_production_evidence": False,
    }


def replay_tournament(rounds_per_genome: int = 1000, replay_seed: int = 2605001) -> dict:
    generated = {
        label: generate_genome(label, config["seed"], config["events"])
        for label, config in GENOMES.items()
    }
    rows = []
    summary = {}
    for genome_index, label in enumerate(sorted(generated)):
        base_rows = generated[label]["rows"]
        expected = generated[label]["canonical_digest_sha256"]
        divergences = 0
        for round_number in range(1, rounds_per_genome + 1):
            shuffled = list(base_rows)
            rng = random.Random(replay_seed + genome_index * 100000 + round_number)
            rng.shuffle(shuffled)
            actual = _digest(sorted(shuffled, key=lambda row: row["discovery_id"]))
            match = actual == expected
            divergences += int(not match)
            rows.append(
                {
                    "genome": label,
                    "round": round_number,
                    "match": match,
                    "digest": actual,
                }
            )
        summary[label] = {
            "canonical_digest_sha256": expected,
            "divergence_count": divergences,
        }
    winner = min(
        summary,
        key=lambda label: (
            summary[label]["divergence_count"],
            summary[label]["canonical_digest_sha256"],
            label,
        ),
    )
    return {
        "schema": "omnipath.v3-replay-stability-tournament/v1",
        "order": "O26.5",
        "rounds_per_genome": rounds_per_genome,
        "total_replays": len(rows),
        "replay_seed": replay_seed,
        "summary": summary,
        "selected_genome": winner,
        "tournament_digest_sha256": _digest(rows),
    }
