#!/usr/bin/env python3
"""O32.4 deterministic genealogy mutation matrix."""
from __future__ import annotations

import copy
import hashlib
import json
import random
from pathlib import Path

from v6.cross_ledger_replay_audit import _candidate, _promoted

INDEX_REF = "omnipath/recognition/promotion_genealogy/index.json"
GAPS_REF = "omnipath/recognition/promotion_genealogy/legacy_evidence_gaps.json"
RECOVERY_REF = "omnipath/recognition/promotion_genealogy/historical_recovery_proofs.json"
OPERATORS = [
    "alias_redirect",
    "ledger_ref_swap",
    "ordering_swap",
    "recovery_ref_rewrite",
    "evidence_ancestry_rewrite",
]


def _read(root: Path, ref: str) -> dict:
    return json.loads((root / ref).read_text(encoding="utf-8"))


def baseline_state(root: Path) -> dict:
    index = _read(root, INDEX_REF)
    ledgers = {entry["ledger_ref"]: _read(root, entry["ledger_ref"]) for entry in index["entries"]}
    return {"index": index, "ledgers": ledgers, "gaps": _read(root, GAPS_REF), "recovery": _read(root, RECOVERY_REF)}


def failures(state: dict) -> list[str]:
    found = set()
    index = state["index"]
    expected_alias = {}
    for entry in index["entries"]:
        for alias in entry["aliases"]:
            expected_alias[alias] = entry["entry_id"]
    if index["alias_map"] != dict(sorted(expected_alias.items())):
        found.add("ALIAS")
    canonical = sorted(index["entries"], key=lambda entry: (entry["generation_order"], entry["promoted_main_sha"], entry["ledger_ref"]))
    if [e["entry_id"] for e in index["entries"]] != [e["entry_id"] for e in canonical]:
        found.add("ORDER")
    for entry in index["entries"]:
        ledger = state["ledgers"].get(entry["ledger_ref"])
        if ledger is None or _candidate(ledger) != entry["candidate_commit_sha"] or _promoted(ledger) != entry["promoted_main_sha"]:
            found.add("LEDGER_LINK")
    for ledger in state["ledgers"].values():
        merge = ledger.get("merge") if isinstance(ledger.get("merge"), dict) else None
        candidate = _candidate(ledger)
        if merge and candidate and merge.get("candidate_parent") != candidate:
            found.add("ANCESTRY")
    gaps = {gap["gap_id"]: gap for gap in state["gaps"].get("gaps", [])}
    for proof in state["recovery"].get("proofs", []):
        gap = gaps.get(proof.get("gap_id"))
        if not gap or any(proof.get(key) != gap.get(key) for key in ("declared_commit", "declared_ref")) or proof.get("expected_blob_sha") != gap.get("declared_blob_sha"):
            found.add("RECOVERY")
    return sorted(found)


def mutate(state: dict, operator: str, rng: random.Random) -> dict:
    value = copy.deepcopy(state)
    entries = value["index"]["entries"]
    if operator == "alias_redirect":
        alias = rng.choice(sorted(value["index"]["alias_map"]))
        current = value["index"]["alias_map"][alias]
        choices = [entry["entry_id"] for entry in entries if entry["entry_id"] != current]
        value["index"]["alias_map"][alias] = rng.choice(choices)
    elif operator == "ledger_ref_swap":
        i = rng.randrange(len(entries)); j = (i + 1) % len(entries)
        entries[i]["ledger_ref"] = entries[j]["ledger_ref"]
    elif operator == "ordering_swap":
        entries[0], entries[-1] = entries[-1], entries[0]
    elif operator == "recovery_ref_rewrite":
        value["recovery"]["proofs"][0]["declared_ref"] = "tampered/" + value["recovery"]["proofs"][0]["declared_ref"]
    elif operator == "evidence_ancestry_rewrite":
        refs = [ref for ref, ledger in value["ledgers"].items() if isinstance(ledger.get("merge"), dict)]
        ref = rng.choice(sorted(refs))
        value["ledgers"][ref]["merge"]["candidate_parent"] = "0" * 40
    else:
        raise ValueError(operator)
    return value


def run(repository_root: str | Path = ".", seed: int = 3204001, trials_per_operator: int = 100) -> dict:
    root = Path(repository_root).resolve()
    base = baseline_state(root)
    if failures(base):
        raise ValueError("baseline genealogy is not clean")
    rng = random.Random(seed)
    rows = []
    for operator in OPERATORS:
        for trial in range(1, trials_per_operator + 1):
            detected_failures = failures(mutate(base, operator, rng))
            rows.append({"operator": operator, "trial": trial, "detected": bool(detected_failures), "failures": detected_failures})
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    return {
        "schema": "omnipath.adversarial-genealogy-mutation-matrix/v1",
        "order": "O32.4",
        "seed": seed,
        "operators": OPERATORS,
        "trials_per_operator": trials_per_operator,
        "total_mutations": len(rows),
        "undetected_mutations": sum(not row["detected"] for row in rows),
        "matrix_digest_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "rows": rows,
    }
