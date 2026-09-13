from __future__ import annotations

import copy

from boundary_contract import DIMENSIONS


def _severity(record):
    record["severity"] = "INFO"


def _promotion(record):
    record["promotion_effect"] = "NO_EFFECT"


def _provenance(record):
    p = record.setdefault("provenance", {})
    p["parent_refs"] = []
    p["transform_refs"] = []


def _replay(record):
    replay = record.get("replay")
    if isinstance(replay, dict):
        replay["claimed_deterministic"] = False


def _contradictions(record):
    for item in record.get("contradictions", []):
        item["status"] = "RESOLVED"
        item["resolution_ref"] = "o22.4:mutation"


def _epistemic(record):
    record["epistemic_state"] = "OBSERVED"


_MUTATORS = {
    "severity": _severity,
    "promotion_effect": _promotion,
    "provenance": _provenance,
    "replay": _replay,
    "contradictions": _contradictions,
    "epistemic_state": _epistemic,
}


def mutate_case(case):
    variants = []
    for dimension in DIMENSIONS:
        candidate = copy.deepcopy(case["record"])
        _MUTATORS[dimension](candidate)
        variants.append({
            "variant_id": case["case_id"] + "::" + dimension,
            "case_id": case["case_id"],
            "dimension": dimension,
            "compound": False,
            "record": candidate,
        })
    combined = copy.deepcopy(case["record"])
    for dimension in DIMENSIONS:
        _MUTATORS[dimension](combined)
    variants.append({
        "variant_id": case["case_id"] + "::combined",
        "case_id": case["case_id"],
        "dimension": "combined",
        "compound": True,
        "record": combined,
    })
    return variants


def generate_variants(corpus):
    variants = []
    for case in corpus.get("cases", []):
        variants.extend(mutate_case(case))
    return sorted(variants, key=lambda item: item["variant_id"])
