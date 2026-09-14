import json
import unittest
from pathlib import Path

from v6.genealogy_mutation_matrix import run

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "omnipath" / "recognition" / "v6" / "O32_4_genealogy_mutation_matrix.json"


class O324GenealogyMutationMatrixTests(unittest.TestCase):
    def test_all_genealogy_mutations_are_detected(self):
        matrix = json.loads(MANIFEST.read_text(encoding="utf-8"))["matrix"]
        result = run(ROOT, seed=matrix["seed"], trials_per_operator=matrix["trials_per_operator"])
        self.assertEqual(result["total_mutations"], matrix["total_mutations"])
        self.assertEqual(result["undetected_mutations"], matrix["expected_undetected_mutations"])
        self.assertEqual(result["matrix_digest_sha256"], matrix["expected_digest_sha256"])

    def test_each_surface_has_independent_detection(self):
        result = run(ROOT, trials_per_operator=1)
        expected = {
            "alias_redirect": ["ALIAS"],
            "ledger_ref_swap": ["LEDGER_LINK"],
            "ordering_swap": ["ORDER"],
            "recovery_ref_rewrite": ["RECOVERY"],
            "evidence_ancestry_rewrite": ["ANCESTRY"],
        }
        observed = {row["operator"]: row["failures"] for row in result["rows"]}
        self.assertEqual(observed, expected)


if __name__ == "__main__":
    unittest.main()
