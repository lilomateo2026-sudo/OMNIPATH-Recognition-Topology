#!/usr/bin/env python3
"""O30.3 deterministic independent V5 genome quintet evidence."""
from __future__ import annotations
import hashlib, itertools, json, random
from adversarial.full_payload_mutation_tournament import OPERATORS
from v5.four_generation_differential import version_baseline, mutate, classify

GENOMES = {
    "A": {"seed": 3003001, "namespace": "v5-genome-A"},
    "B": {"seed": 3003002, "namespace": "v5-genome-B"},
    "C": {"seed": 3003003, "namespace": "v5-genome-C"},
    "D": {"seed": 3003004, "namespace": "v5-genome-D"},
    "E": {"seed": 3003005, "namespace": "v5-genome-E"},
}
PARENT = "9ac6fdf3c4fe21c85631638725cf4d4eedead46c"

def genome_stream(seed: int, namespace: str, events: int = 1000):
    rng = random.Random(seed)
    base = version_baseline("bcb87448524ceaf7ca353277b5445dec9f1b4168", f"{namespace}-candidate")
    rows = []
    for index in range(1, events + 1):
        width = rng.choice([1,2,3,4,5,6,7])
        operators = tuple(sorted(rng.sample(OPERATORS, width)))
        classification = classify(mutate(base, operators), base)
        discovery_id = hashlib.sha256(f"discovery|{namespace}|{seed}|{index}|{','.join(operators)}".encode()).hexdigest()
        source_event_id = hashlib.sha256(f"source|{namespace}|{seed}|{index}|{rng.randrange(1 << 32)}".encode()).hexdigest()
        rows.append({"index": index, "discovery_id": discovery_id, "source_event_id": source_event_id, "operators": list(operators), "classification": classification})
    digest = hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return rows, digest

def run(events: int = 1000) -> dict:
    streams = {g: genome_stream(cfg["seed"], cfg["namespace"], events) for g, cfg in GENOMES.items()}
    discovery = {g: {row["discovery_id"] for row in streams[g][0]} for g in GENOMES}
    source = {g: {row["source_event_id"] for row in streams[g][0]} for g in GENOMES}
    shared_discovery = sum(len(discovery[a] & discovery[b]) for a, b in itertools.combinations(GENOMES, 2))
    shared_source = sum(len(source[a] & source[b]) for a, b in itertools.combinations(GENOMES, 2))
    genomes = {g: {**GENOMES[g], "events": events, "stream_digest_sha256": streams[g][1]} for g in GENOMES}
    payload = {"genomes": genomes, "shared_discovery_ids": shared_discovery, "shared_source_event_ids": shared_source}
    return {**payload, "digest_sha256": hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()}
