import json
import unittest
from pathlib import Path

from v6.five_generation_differential import run

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "omnipath" / "recognition" / "v6" / "O32_1_v6_genesis.json"


class O32V6GenesisTests(unittest.TestCase):
    def test_five_generation_differential_is_stable(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        config = manifest["five_generation_differential"]
        result = run(seed=config["seed"], trials=config["trials"])
        self.assertEqual(result["mismatch_count"], config["expected_mismatches"])
        self.assertEqual(result["digest_sha256"], config["expected_digest_sha256"])
        self.assertEqual(result["operator_count"], config["operator_count"])
        self.assertEqual(result["mutation_widths"], config["mutation_widths"])
        self.assertEqual(set(result["versions"]), {"gen2", "v3", "v4", "v5", "v6"})

    def test_v6_authority_is_reset(self):
        authority = json.loads(MANIFEST.read_text(encoding="utf-8"))["authority_reset"]
        self.assertFalse(authority["inherits_promotion_authority"])
        self.assertTrue(authority["self_promotion_forbidden"])
        self.assertFalse(authority["main_mutation_authority"])
        self.assertEqual(authority["promotion_state"], "OBSERVED")
        self.assertTrue(authority["fresh_descendant_ci_required"])
        self.assertTrue(authority["fresh_genealogy_ci_required"])
        self.assertTrue(authority["fresh_closure_ci_required"])
        self.assertTrue(authority["new_promotion_tribunal_required"])

    def test_v6_parent_is_exact_o31_8_attested_root(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["parent_main_sha"], "c19551d92c306236b7c80c9422eb44a1afacb1af")
        self.assertEqual(manifest["o31_8_attestation_commit"], "48dc9f87a4f824fabfe07b7644b0aa8e934a4b70")


if __name__ == "__main__":
    unittest.main()
