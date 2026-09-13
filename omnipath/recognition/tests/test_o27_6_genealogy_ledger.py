import json
import unittest
from pathlib import Path

from promotion_genealogy_registry import audit_genealogy_registry
from promotion_ledger_verifier import verify_durable_ledger

HERE = Path(__file__).resolve().parent
RECOGNITION = HERE.parent
REPOSITORY = RECOGNITION.parent.parent


class O276LedgerTests(unittest.TestCase):
    def test_o22_8a_durable_ledger_verifies(self):
        ref = "omnipath/recognition/attestation_ledger/v1/o22_6_main_ab1235e5"
        result = verify_durable_ledger(REPOSITORY, ref)
        self.assertTrue(result["valid"], result["failures"])
        self.assertEqual(result["record_set_sha256"], "32c2b50c668d04972951788b7d580d259f7ce11534290ec693a30f72cbc62cf2")
        self.assertEqual(result["source_commit"], "ab1235e5cd90a9d327e7dca94464f35b71fdcde1")
        self.assertEqual(result["constitutional_root_sha"], "a730bba4e6a466e15b95c47998ae403c0ffe3a23")
        self.assertEqual(len(result["specimen_sha256"]), 4)

    def test_persisted_registry_requires_genealogy_contract(self):
        registry = json.loads((RECOGNITION / "promotion_registry/registry.json").read_text(encoding="utf-8"))
        result = audit_genealogy_registry(registry)
        self.assertTrue(result["valid"], result["failures"])


if __name__ == "__main__":
    unittest.main()
