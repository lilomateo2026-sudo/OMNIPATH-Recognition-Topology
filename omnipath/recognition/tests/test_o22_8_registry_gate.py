import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parents[1]))

from test_o22_7_promotion_manifest import LOCK, valid_attestation, valid_manifest
from promotion_artifact_registry import empty_registry
from promotion_manifest_gate import seal_manifest
from promotion_registry_store import append_promotion


class O228RegistryGateTests(unittest.TestCase):
    def test_o22_7_blocked_candidate_cannot_be_registered(self):
        candidate, parent = "a" * 40, "b" * 40
        evidence = valid_attestation(candidate)
        manifest = valid_manifest(candidate, parent, evidence)
        manifest["unresolved_contradictions"] = 1
        manifest = seal_manifest(manifest)
        with self.assertRaises(ValueError):
            append_promotion(empty_registry(), manifest, evidence, LOCK)


if __name__ == "__main__":
    unittest.main()
