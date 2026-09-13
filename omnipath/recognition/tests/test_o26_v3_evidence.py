import json
import unittest
from pathlib import Path

from v3.semantic_drift_fuzzer import run as run_semantic_drift

ROOT = Path(__file__).resolve().parents[3]
O26_2 = ROOT / "omnipath" / "recognition" / "v3" / "O26_2_semantic_drift_manifest.json"


class O26V3EvidenceTests(unittest.TestCase):
    def test_o262_semantic_drift(self):
        expected = json.loads(O26_2.read_text(encoding="utf-8"))
        result = run_semantic_drift(expected["seed"], expected["source_cases"])
        self.assertEqual(result["checks"], expected["expected_checks"])
        self.assertEqual(result["mismatch_count"], expected["expected_mismatch_count"])
        self.assertEqual(result["digest_sha256"], expected["expected_digest_sha256"])
        self.assertFalse(expected["promotion_authority"])


if __name__ == "__main__":
    unittest.main()
