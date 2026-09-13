import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve()
RECOGNITION_DIR = HERE.parents[1]
sys.path.insert(0, str(RECOGNITION_DIR))

from promotion_manifest_gate import (  # noqa: E402
    CANONICAL_CHECKPOINTS,
    canonical_sha256,
    evaluate_promotion,
    seal_manifest,
)


def load(name):
    with (RECOGNITION_DIR / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


LOCK = load("CONSTITUTIONAL_ROOT.lock.json")
ROOT_SHA = LOCK["constitutional_root"]["commit_sha"]


def valid_attestation(candidate):
    return {
        "schema": "omnipath.o22-6-ci-attestation/v1",
        "order": "O22.6",
        "source_commit": candidate,
        "workflow_run_id": "12345",
        "replay_job_result": "success",
        "replay_artifact_id": "67890",
        "replay_artifact_digest": "sha256:" + "b" * 64,
        "external_ci_status": "SUCCESS",
        "promotion_eligible": True,
        "replay_manifest_sha256": "c" * 64,
        "o22_5_report_sha256": "d" * 64,
        "specimen_sha256": {
            "contradiction_erasure.json": "1" * 64,
            "false_consensus.json": "2" * 64,
            "observer_collapse.json": "3" * 64,
            "replay_divergence.json": "4" * 64,
        },
        "variant_count": 378,
        "cross_product_variant_count": 342,
        "final_pass_count": 0,
    }


def valid_manifest(candidate, parent, attestation):
    return seal_manifest(
        {
            "schema": "omnipath.o22-7-promotion-manifest/v1",
            "order": "O22.7",
            "candidate_id": "recognition-topology:test-candidate",
            "candidate_commit_sha": candidate,
            "parent_commit_sha": parent,
            "rollback_commit_sha": parent,
            "constitutional_root_sha": ROOT_SHA,
            "checkpoint_commits": copy.deepcopy(CANONICAL_CHECKPOINTS),
            "o22_6_attestation_sha256": canonical_sha256(attestation),
            "unresolved_contradictions": 0,
            "unresolved_escape_specimens": 0,
            "independent_attestation_required": True,
            "candidate_self_promoted": False,
            "epistemic_ceiling": "VERIFIED_WITHIN_SCOPE",
        }
    )


class O227PromotionManifestTests(unittest.TestCase):
    def setUp(self):
        self.candidate = "a" * 40
        self.parent = "b" * 40
        self.attestation = valid_attestation(self.candidate)
        self.manifest = valid_manifest(self.candidate, self.parent, self.attestation)

    def test_promotable_manifest_is_deterministic_and_immutable(self):
        before_manifest = copy.deepcopy(self.manifest)
        before_attestation = copy.deepcopy(self.attestation)
        first = evaluate_promotion(self.manifest, self.attestation, LOCK)
        second = evaluate_promotion(self.manifest, self.attestation, LOCK)
        self.assertTrue(first["promotion_allowed"])
        self.assertEqual("PROMOTABLE", first["promotion_status"])
        self.assertEqual(first, second)
        self.assertEqual(before_manifest, self.manifest)
        self.assertEqual(before_attestation, self.attestation)

    def test_candidate_commit_must_match_o22_6_attestation(self):
        self.attestation["source_commit"] = "c" * 40
        self.manifest["o22_6_attestation_sha256"] = canonical_sha256(self.attestation)
        self.manifest = seal_manifest(self.manifest)
        result = evaluate_promotion(self.manifest, self.attestation, LOCK)
        self.assertFalse(result["promotion_allowed"])
        self.assertIn("O22_6:source_commit", result["failures"])

    def test_unresolved_contradiction_blocks_promotion(self):
        self.manifest["unresolved_contradictions"] = 1
        self.manifest = seal_manifest(self.manifest)
        result = evaluate_promotion(self.manifest, self.attestation, LOCK)
        self.assertEqual("BLOCKED", result["promotion_status"])
        self.assertIn("UNRESOLVED_CONTRADICTIONS", result["failures"])

    def test_unresolved_escape_specimen_blocks_promotion(self):
        self.manifest["unresolved_escape_specimens"] = 1
        self.manifest = seal_manifest(self.manifest)
        result = evaluate_promotion(self.manifest, self.attestation, LOCK)
        self.assertIn("UNRESOLVED_ESCAPE_SPECIMENS", result["failures"])

    def test_checkpoint_drift_blocks_promotion(self):
        self.manifest["checkpoint_commits"]["O22.2"] = "f" * 40
        self.manifest = seal_manifest(self.manifest)
        result = evaluate_promotion(self.manifest, self.attestation, LOCK)
        self.assertIn("CHECKPOINT_LINEAGE", result["failures"])

    def test_candidate_cannot_assert_its_own_promotion_status(self):
        self.manifest["promotion_status"] = "PROMOTABLE"
        result = evaluate_promotion(self.manifest, self.attestation, LOCK)
        self.assertIn("SELF_ASSERTED_PROMOTION_STATUS", result["failures"])

    def test_tampered_manifest_hash_blocks_promotion(self):
        self.manifest["candidate_id"] = "tampered-after-seal"
        result = evaluate_promotion(self.manifest, self.attestation, LOCK)
        self.assertIn("MANIFEST_HASH_MISMATCH", result["failures"])

    def test_rollback_must_be_immediate_parent(self):
        self.manifest["rollback_commit_sha"] = "c" * 40
        self.manifest = seal_manifest(self.manifest)
        result = evaluate_promotion(self.manifest, self.attestation, LOCK)
        self.assertIn("ROLLBACK_NOT_PARENT", result["failures"])


if __name__ == "__main__":
    unittest.main()
