import json
import unittest
from pathlib import Path

from adversarial.pathology_mutation_tournament import run as run_mutation


REPO_ROOT = Path(__file__).resolve().parents[3]
LEDGER = REPO_ROOT / "omnipath" / "recognition" / "attestation_ledger" / "v1" / "o23_9_main_b7e1bde3" / "index.json"
EXPECTED_PROMOTED_MERGE = "b7e1bde39d46afc255bc5db46e9f4aed6e1cb399"
EXPECTED_CANDIDATE = "17d4db9907455d29d5ee2aa3e3120bd6bdfea87f"
EXPECTED_TOURNAMENT_DIGEST = "4ab0014ae68bbfaf0d7c968694bd05be71f007c7a66daefd5895d36484e058d8"


class O24PostPromotionGateTests(unittest.TestCase):
    def test_promoted_lineage_is_durable_and_scoped(self):
        ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        self.assertEqual(ledger["schema"], "omnipath.durable-attestation-ledger/v1")
        self.assertEqual(ledger["order"], "O23.9")
        self.assertEqual(ledger["merge"]["commit"], EXPECTED_PROMOTED_MERGE)
        self.assertEqual(ledger["candidate"]["head_sha"], EXPECTED_CANDIDATE)
        self.assertEqual(ledger["postmerge_ci"]["conclusion"], "success")
        self.assertFalse(ledger["candidate_self_promoted"])
        self.assertEqual(
            ledger["future_promotion_rule"],
            "REQUIRE_LEDGER_VERIFICATION_AND_FRESH_DESCENDANT_ATTESTATION",
        )

    def test_next_generation_adversarial_baseline(self):
        result = run_mutation(seed=2401001, trials=2000)
        self.assertTrue(result["all_pathologies_covered"])
        self.assertEqual(result["unique_combinations"], 91)
        self.assertEqual(result["trials"], 2000)
        self.assertEqual(result["tournament_digest_sha256"], EXPECTED_TOURNAMENT_DIGEST)


if __name__ == "__main__":
    unittest.main()
