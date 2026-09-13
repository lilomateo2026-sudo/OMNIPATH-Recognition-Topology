#!/usr/bin/env python3
"""O24.2 deterministic mutation tournament for complete recognition-transfer envelopes."""

from __future__ import annotations

import copy
import hashlib
import json
import random

OPERATORS = [
    "drop_provenance_source",
    "rewrite_provenance_digest",
    "drift_replay_seed",
    "drift_replay_rounds",
    "escalate_observer_authority",
    "collapse_observer_identity",
    "widen_scope",
    "remove_scope_constraint",
    "swap_lineage_parent",
    "self_parent_lineage",
    "erase_contradiction",
    "invert_contradiction",
]

OPERATOR_FIELD = {
    "drop_provenance_source": "provenance",
    "rewrite_provenance_digest": "provenance",
    "drift_replay_seed": "replay_metadata",
    "drift_replay_rounds": "replay_metadata",
    "escalate_observer_authority": "observer_boundary",
    "collapse_observer_identity": "observer_boundary",
    "widen_scope": "evidence_scope",
    "remove_scope_constraint": "evidence_scope",
    "swap_lineage_parent": "lineage",
    "self_parent_lineage": "lineage",
    "erase_contradiction": "contradictory_evidence",
    "invert_contradiction": "contradictory_evidence",
}


def baseline_envelope() -> dict:
    return {
        "run_id": "gen2-baseline",
        "provenance": {
            "source": "fixture://constitutional-transfer",
            "digest": "sha256:root",
            "verified": True,
        },
        "replay_metadata": {"seed": 2402001, "rounds": 1000, "deterministic": True},
        "observer_boundary": {
            "observer_id": "external-c-observer",
            "authority": "adjudicate_only",
            "independent": True,
        },
        "evidence_scope": ["recognition-transfer", "fixture-corpus"],
        "scope_constraints": ["no-absolute-certainty", "no-self-promotion"],
        "lineage": {
            "parent": "dc296965c43e75fd3fab53eea3a96aaccc381a10",
            "self": "candidate-o24",
            "root": "a730bba4e6a466e15b95c47998ae403c0ffe3a23",
        },
        "contradictory_evidence": [
            {"id": "FALSE-CONSENSUS-001", "retained": True, "claim": "observer asymmetry"}
        ],
        "promotion_state": "OBSERVED",
    }


def apply_operator(envelope: dict, operator: str) -> dict:
    result = copy.deepcopy(envelope)
    if operator == "drop_provenance_source":
        result["provenance"]["source"] = ""
    elif operator == "rewrite_provenance_digest":
        result["provenance"]["digest"] = "sha256:forged"
    elif operator == "drift_replay_seed":
        result["replay_metadata"]["seed"] += 1
    elif operator == "drift_replay_rounds":
        result["replay_metadata"]["rounds"] -= 1
    elif operator == "escalate_observer_authority":
        result["observer_boundary"]["authority"] = "promote"
    elif operator == "collapse_observer_identity":
        result["observer_boundary"]["observer_id"] = result["lineage"]["self"]
    elif operator == "widen_scope":
        if "unbounded" not in result["evidence_scope"]:
            result["evidence_scope"].append("unbounded")
    elif operator == "remove_scope_constraint":
        result["scope_constraints"] = [
            value for value in result["scope_constraints"] if value != "no-absolute-certainty"
        ]
    elif operator == "swap_lineage_parent":
        result["lineage"]["parent"] = "unrelated-commit"
    elif operator == "self_parent_lineage":
        result["lineage"]["parent"] = result["lineage"]["self"]
    elif operator == "erase_contradiction":
        result["contradictory_evidence"] = []
    elif operator == "invert_contradiction":
        if result["contradictory_evidence"]:
            result["contradictory_evidence"][0]["retained"] = False
    else:
        raise ValueError(f"unknown mutation operator: {operator}")
    return result


def mutate(envelope: dict, operators: tuple[str, ...] | list[str]) -> dict:
    result = copy.deepcopy(envelope)
    for operator in operators:
        result = apply_operator(result, operator)
    return result


def detect_pathologies(envelope: dict, baseline: dict | None = None) -> set[str]:
    baseline = baseline or baseline_envelope()
    pathologies: set[str] = set()

    if (
        not envelope["provenance"].get("source")
        or envelope["provenance"].get("digest") != baseline["provenance"]["digest"]
    ):
        pathologies.add("PROVENANCE_LOSS")

    if envelope["replay_metadata"] != baseline["replay_metadata"]:
        pathologies.add("REPLAY_DIVERGENCE")

    observer = envelope["observer_boundary"]
    if (
        observer.get("authority") != "adjudicate_only"
        or observer.get("observer_id") == envelope["lineage"].get("self")
    ):
        pathologies.add("OBSERVER_COLLAPSE")

    if (
        "unbounded" in envelope["evidence_scope"]
        or "no-absolute-certainty" not in envelope["scope_constraints"]
    ):
        pathologies.add("SCOPE_INFLATION")

    lineage = envelope["lineage"]
    if (
        lineage.get("parent") != baseline["lineage"]["parent"]
        or lineage.get("parent") == lineage.get("self")
    ):
        pathologies.add("LINEAGE_CORRUPTION")

    contradictions = envelope["contradictory_evidence"]
    if not contradictions or any(not item.get("retained", False) for item in contradictions):
        pathologies.add("CONTRADICTION_ERASURE")

    return pathologies


def disposition(pathologies: set[str]) -> str:
    if not pathologies:
        return "HOLD"
    if "LINEAGE_CORRUPTION" in pathologies or "SCOPE_INFLATION" in pathologies:
        return "REJECT"
    if "REPLAY_DIVERGENCE" in pathologies:
        return "REQUIRE_REPLAY"
    return "REQUIRE_ADJUDICATION"


def run(seed: int = 2402001, trials: int = 3000) -> dict:
    rng = random.Random(seed)
    baseline = baseline_envelope()
    rows = []
    operator_counts = {operator: 0 for operator in OPERATORS}
    field_coverage: set[str] = set()
    escape_count = 0

    for trial in range(1, trials + 1):
        width = rng.choice([1, 2, 3, 4])
        operators = tuple(sorted(rng.sample(OPERATORS, width)))
        for operator in operators:
            operator_counts[operator] += 1
            field_coverage.add(OPERATOR_FIELD[operator])

        candidate = mutate(baseline, operators)
        detected = sorted(detect_pathologies(candidate, baseline))
        decision = disposition(set(detected))
        escaped = decision == "HOLD"
        escape_count += int(escaped)
        rows.append(
            {
                "trial": trial,
                "operators": list(operators),
                "detected_pathologies": detected,
                "decision": decision,
                "escape": escaped,
            }
        )

    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    return {
        "schema": "omnipath.full-payload-mutation-tournament/v1",
        "order": "O24.2",
        "seed": seed,
        "trials": trials,
        "operator_count": len(OPERATORS),
        "operator_coverage": all(count > 0 for count in operator_counts.values()),
        "field_coverage": sorted(field_coverage),
        "escape_count": escape_count,
        "tournament_digest_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "rows": rows,
    }
