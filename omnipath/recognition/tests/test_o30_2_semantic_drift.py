import json
import unittest
from pathlib import Path
from v5.semantic_drift_matrix import run

ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / "omnipath" / "recognition" / "v5" / "O30_2_semantic_drift_matrix.json"

class O302SemanticDriftTests(unittest.TestCase):
    def test_semantic_matrix_is_stable(self):
        expected = json.loads(REPORT.read_text(encoding="utf-8"))
        observed = run(expected["seed"], expected["cases"])
        self.assertEqual(observed["checks"], expected["checks"])
        self.assertEqual(observed["semantic_mismatches"], 0)
        self.assertEqual(observed["cross_generation_mismatches"], 0)
        self.assertEqual(observed["digest_sha256"], expected["digest_sha256"])

    def test_o302_is_experimental_only(self):
        expected = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertTrue(expected["experimental_only"])
        self.assertEqual(expected["epistemic_state"], "VERIFIED_WITHIN_SCOPE")

if __name__ == "__main__":
    unittest.main()
