import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parents[1]))

from test_o22_7_promotion_manifest import LOCK, valid_attestation, valid_manifest
from promotion_artifact_registry import empty_registry, seal_entry, seal_registry
from promotion_registry_audit import audit_registry
from promotion_registry_store import append_promotion, reconstruct_promotion


class O228RegistryIntegrityTests(unittest.TestCase):
    def add(self, registry, candidate, parent):
        evidence = valid_attestation(candidate)
        manifest = valid_manifest(candidate, parent, evidence)
        return append_promotion(registry, manifest, evidence, LOCK)

    def test_second_entry_links_to_first_and_versions_advance(self):
        registry = self.add(empty_registry(), "a" * 40, "b" * 40)
        registry = self.add(registry, "c" * 40, "a" * 40)
        first, second = registry["entries"]
        self.assertEqual(2, second["lineage_version"])
        self.assertEqual(first["entry_sha256"], second["previous_entry_sha256"])
        self.assertTrue(audit_registry(registry)["valid"])

    def test_rehashed_incomplete_entry_is_still_rejected(self):
        registry = self.add(empty_registry(), "a" * 40, "b" * 40)
        entry = dict(registry["entries"][0])
        entry.pop("o22_6_workflow_run_id")
        entry = seal_entry(entry)
        registry["entries"][0] = entry
        registry["head_entry_sha256"] = entry["entry_sha256"]
        registry = seal_registry(registry)
        result = audit_registry(registry)
        self.assertFalse(result["valid"])
        self.assertIn("ENTRY_1:MISSING_FIELD", result["failures"])

    def test_reconstruction_returns_hash_chain_to_genesis(self):
        registry = self.add(empty_registry(), "a" * 40, "b" * 40)
        registry = self.add(registry, "c" * 40, "a" * 40)
        rebuilt = reconstruct_promotion(registry, "c" * 40)
        self.assertEqual([2, 1], [e["lineage_version"] for e in rebuilt["ancestry_to_genesis"]])
        self.assertEqual(registry["registry_sha256"], rebuilt["registry_sha256"])


if __name__ == "__main__":
    unittest.main()
