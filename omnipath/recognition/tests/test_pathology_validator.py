import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve()
RECOGNITION_DIR = HERE.parents[1]
sys.path.insert(0, str(RECOGNITION_DIR))

from pathology_validator import validate_pathology  # noqa: E402


def load(name):
    with (RECOGNITION_DIR / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


SCHEMA = load("RECOGNITION_PATHOLOGY.schema.json")
LOCK = load("CONSTITUTIONAL_ROOT.lock.json")
ROOT_SHA = LOCK["constitutional_root"]["commit_sha"]


def base_record():
    return {
        "schema_version": "omnipath.recognition-pathology/v1",
        "pathology_id": "p-test-001",
        "run_id": "run-test-001",
        "rail": "evidence-transfer",
        "pathology_type": "FALSE_CONSENSUS",
        "severity": "LOW",
        "observed_evidence": [
            {
                "evidence_id": "e-1",
                "kind": "comparison",
                "value": {"agreement": 0.51},
                "source_ref": "run:test:a",
                "hash": None,
            }
        ],
        "observer_judgment": {
            "observer_id": "c-observer:test",
            "judgment": "informational anomaly; no promotion effect",
            "confidence": 0.6,
            "assumptions": [],
        },
        "contradictions": [],
        "provenance": {
            "constitutional_root_sha": ROOT_SHA,
            "root_freeze_sha": "07f11ddf005f054d7172c7e1232c2b89a5a8ec65",
            "parent_refs": ["run:test:a"],
            "transform_refs": ["normalize:v1"],
            "model_identity": "test-model@immutable-rev",
            "prompt_hash": "sha256:test",
        },
        "scope": {
            "supports": ["validator fixture only"],
            "does_not_support": ["absolute certainty"],
        },
        "promotion_effect": "NO_EFFECT",
        "epistemic_state": "OBSERVED",
        "notes": ["fixture"],
    }


class ValidatorTests(unittest.TestCase):
    def test_pass_is_deterministic_and_input_is_immutable(self):
        record = base_record()
        before = copy.deepcopy(record)
        first = validate_pathology(record, SCHEMA, LOCK)
        second = validate_pathology(record, SCHEMA, LOCK)
        self.assertEqual("PASS", first["decision"])
        self.assertEqual(first, second)
        self.assertEqual(before, record)

    def test_replay_divergence_quarantines(self):
        record = base_record()
        record.update(
            pathology_type="REPLAY_DIVERGENCE",
            severity="HIGH",
            promotion_effect="REQUIRE_REPLAY",
            replay={
                "claimed_deterministic": True,
                "replay_id": "replay-1",
                "expected_hash": "aaa",
                "actual_hash": "bbb",
                "match": False,
            },
        )
        result = validate_pathology(record, SCHEMA, LOCK)
        self.assertEqual("QUARANTINE", result["decision"])
        self.assertIn(
            "DETERMINISTIC_REPLAY_MISMATCH",
            [item["code"] for item in result["reasons"]],
        )

    def test_open_contradiction_is_preserved_and_quarantined(self):
        record = base_record()
        contradiction = {
            "left_ref": "e-1",
            "right_ref": "e-2",
            "status": "OPEN",
            "resolution_ref": None,
        }
        record.update(
            pathology_type="CONTRADICTION_ERASURE",
            severity="MEDIUM",
            promotion_effect="REQUIRE_ADJUDICATION",
            contradictions=[contradiction],
        )
        result = validate_pathology(record, SCHEMA, LOCK)
        self.assertEqual("QUARANTINE", result["decision"])
        self.assertEqual([contradiction], result["preserved_contradictions"])

    def test_wrong_root_sha_rejects(self):
        record = base_record()
        record["provenance"]["constitutional_root_sha"] = "0" * 40
        result = validate_pathology(record, SCHEMA, LOCK)
        self.assertEqual("REJECT", result["decision"])
        self.assertIn(
            "SCHEMA_VIOLATION",
            [item["code"] for item in result["reasons"]],
        )

    def test_lineage_corruption_rejects(self):
        record = base_record()
        record.update(
            pathology_type="LINEAGE_CORRUPTION",
            severity="HIGH",
            promotion_effect="HOLD",
        )
        result = validate_pathology(record, SCHEMA, LOCK)
        self.assertEqual("REJECT", result["decision"])
        self.assertIn(
            "LINEAGE_CORRUPTION",
            [item["code"] for item in result["reasons"]],
        )

    def test_schema_rule_weakening_rejects_configuration(self):
        record = base_record()
        weakened = copy.deepcopy(SCHEMA)
        weakened["x-omnipath-constitutional-rules"][
            "contradictions_must_be_retained"
        ] = False
        result = validate_pathology(record, weakened, LOCK)
        self.assertEqual("REJECT", result["decision"])
        self.assertIn(
            "SCHEMA_RULE_DISABLED:contradictions_must_be_retained",
            [item["code"] for item in result["reasons"]],
        )


if __name__ == "__main__":
    unittest.main()
