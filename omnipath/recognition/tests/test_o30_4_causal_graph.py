import json
import unittest
from pathlib import Path
from v5.causal_counterexample_graph import run

ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / "omnipath" / "recognition" / "v5" / "O30_4_causal_counterexample_graph.json"

class O304CausalGraphTests(unittest.TestCase):
    def test_causal_graph_is_exact(self):
        expected = json.loads(REPORT.read_text(encoding="utf-8"))
        observed = run()
        self.assertEqual(observed["semantic_real_counterexamples"], 0)
        self.assertEqual(observed["cross_generation_real_counterexamples"], 0)
        self.assertEqual(len(observed["operator_causes"]), expected["operator_control_count"])
        self.assertEqual(len(observed["semantic_transform_controls"]), expected["semantic_transform_control_count"])
        self.assertEqual(observed["cause_graph_digest_sha256"], expected["cause_graph_digest_sha256"])

    def test_synthetic_controls_are_not_promoted_as_real_failures(self):
        expected = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertTrue(expected["synthetic_controls_are_not_production_evidence"])
        self.assertTrue(expected["experimental_only"])

if __name__ == "__main__":
    unittest.main()
