import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parents[1]))

from test_o22_7_promotion_manifest import LOCK, valid_attestation, valid_manifest
from promotion_artifact_registry import empty_registry
from promotion_registry_audit import audit_registry
from promotion_registry_store import append_promotion


class O228RegistryCoreTests(unittest.TestCase):
    def setUp(self):
        self.candidate = "a" * 40
        self.parent = "b" * 40
        self.attestation = valid_attestation(self.candidate)
        self.manifest = valid_manifest(self.candidate, self.parent, self.attestation)

    def test_genesis_registry_is_canonical_and_valid(self):
        path = HERE.parents[1] / "promotion_registry" / "registry.json"
        stored = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(empty_registry(), stored)
        self.assertTrue(audit_registry(stored)["valid"])

    def test_append_is_deterministic_and_does_not_mutate_inputs(self):
        registry = empty_registry()
        before = copy.deepcopy(registry)
        first = append_promotion(registry, self.manifest, self.attestation, LOCK)
        second = append_promotion(registry, self.manifest, self.attestation, LOCK)
        self.assertEqual(first, second)
        self.assertEqual(before, registry)
        self.assertEqual(1, first["entries"][0]["lineage_version"])
        self.assertEqual(first["head_entry_sha256"], first["entries"][0]["entry_sha256"])
        self.assertEqual("12345", first["entries"][0]["o22_6_workflow_run_id"])
        self.assertEqual("67890", first["entries"][0]["o22_6_replay_artifact_id"])

    def test_duplicate_candidate_is_rejected(self):
        registry = append_promotion(empty_registry(), self.manifest, self.attestation, LOCK)
        with self.assertRaises(ValueError):
            append_promotion(registry, self.manifest, self.attestation, LOCK)


if __name__ == "__main__":
    unittest.main()
