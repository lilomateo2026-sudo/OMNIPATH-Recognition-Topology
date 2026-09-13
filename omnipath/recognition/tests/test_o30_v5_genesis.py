import json
import unittest
from pathlib import Path

from v5.four_generation_differential import run

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "omnipath" / "recognition" / "v5" / "O30_1_v5_genesis.json"


class O30V5GenesisTests(unittest.TestCase):
    def test_four_generation_differential_is_stable(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        config = manifest["four_generation_differential"]
        result = run(seed=config["seed"], trials=config["trials"])
        self.assertEqual(result["mismatch_count"], config["expected_mismatches"])
        self.assertEqual(result["digest_sha256"], config["expected_digest_sha256"])
        self.assertEqual(result["operator_count"], config["operator_count"])
        self.assertEqual(result["mutation_widths"], config["mutation_widths"])

    def test_v5_authority_is_reset(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        authority = manifest["authority_reset"]
        self.assertFalse(authority["inherits_promotion_authority"])
        self.assertTrue(authority["self_promotion_forbidden"])
        self.assertFalse(authority["main_mutation_authority"])
        self.assertEqual(authority["promotion_state"], "OBSERVED")
        self.assertTrue(authority["fresh_descendant_ci_required"])
        self.assertTrue(authority["fresh_genealogy_ci_required"])
        self.assertTrue(authority["new_promotion_tribunal_required"])

    def test_v5_parent_is_exact_dual_verified_o29_5_state(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(
            manifest["parent_main_sha"],
            "bcb87448524ceaf7ca353277b5445dec9f1b4168",
        )
        self.assertEqual(manifest["parent_verification"]["recognition_result"], "success")
        self.assertEqual(manifest["parent_verification"]["genealogy_result"], "success")


if __name__ == "__main__":
    unittest.main()
