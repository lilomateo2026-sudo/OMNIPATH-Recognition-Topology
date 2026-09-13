from __future__ import annotations

import json
from pathlib import Path

from tribunal_contract import PARENT_SHA

HERE = Path(__file__).resolve().parent
CORPUS_DIR = HERE / "corpus" / "o22_3"
ROOT = "a730bba4e6a466e15b95c47998ae403c0ffe3a23"
FREEZE = "07f11ddf005f054d7172c7e1232c2b89a5a8ec65"


def lineage_case():
    return {
        "case_id": "lineage-integrity",
        "corruption_expected": True,
        "expected_decision": "REJECT",
        "expected_reason_codes": ["LINEAGE_CORRUPTION"],
        "record": {
            "schema_version": "omnipath.recognition-pathology/v1",
            "pathology_id": "O223-LC-001",
            "run_id": "o22.3-lineage-integrity",
            "rail": "cross-rail",
            "pathology_type": "LINEAGE_CORRUPTION",
            "severity": "LOW",
            "observed_evidence": [{"evidence_id": "lc-e1", "kind": "challenge_fixture", "value": "lineage test", "source_ref": "corpus:lineage", "hash": None}],
            "observer_judgment": {"observer_id": "o22.3-tribunal", "judgment": "Lineage check required.", "confidence": 0.99},
            "provenance": {"constitutional_root_sha": ROOT, "root_freeze_sha": FREEZE, "parent_refs": [PARENT_SHA], "transform_refs": ["o22.3:lineage"], "model_identity": None, "prompt_hash": None},
            "scope": {"supports": ["lineage handling test"], "does_not_support": ["automatic promotion"]},
            "promotion_effect": "NO_EFFECT",
            "epistemic_state": "OBSERVED"
        }
    }


def load_corpus():
    cases = []
    for path in sorted(CORPUS_DIR.glob("*.json")):
        with path.open("r", encoding="utf-8") as handle:
            cases.append(json.load(handle))
    cases.append(lineage_case())
    return {
        "corpus_version": "omnipath.adversarial-pathology-corpus/v1",
        "order": "O22.3",
        "parent_order": "O22.2",
        "parent_commit_sha": PARENT_SHA,
        "corrupted_case_must_never_pass": True,
        "cases": cases,
    }
