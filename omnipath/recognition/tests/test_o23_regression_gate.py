import unittest

from adversarial.pathology_mutation_tournament import run as run_mutation
from replay.dual_rail_replay_harness import run as run_replay
from tribunal.cross_rail_tribunal import adjudicate


REF_ROWS = [
    ("REF-CONTROL-001", [], "ACCEPT_FOR_COMPARISON"),
    ("REF-FALSE-CONSENSUS-001", ["FALSE_CONSENSUS", "SCOPE_INFLATION"], "REQUIRE_ADJUDICATION"),
    ("REF-PROVENANCE-LOSS-001", ["PROVENANCE_LOSS"], "HOLD"),
    ("REF-SCOPE-INFLATION-001", ["SCOPE_INFLATION"], "REJECT"),
    ("REF-OBSERVER-COLLAPSE-001", ["OBSERVER_COLLAPSE"], "HOLD"),
    ("REF-CONTRADICTION-ERASURE-001", ["CONTRADICTION_ERASURE"], "REQUIRE_ADJUDICATION"),
    ("REF-REPLAY-DIVERGENCE-001", ["REPLAY_DIVERGENCE"], "REQUIRE_REPLAY"),
    ("REF-LINEAGE-CORRUPTION-001", ["LINEAGE_CORRUPTION"], "REJECT"),
]

EVD_ROWS = [
    ("EVD-CONTROL-001", [], "ACCEPT_FOR_COMPARISON"),
    ("EVD-FALSE-CONSENSUS-001", ["FALSE_CONSENSUS", "OBSERVER_COLLAPSE", "SCOPE_INFLATION"], "REQUIRE_ADJUDICATION"),
    ("EVD-PROVENANCE-LOSS-001", ["PROVENANCE_LOSS"], "HOLD"),
    ("EVD-SCOPE-INFLATION-001", ["SCOPE_INFLATION"], "REJECT"),
    ("EVD-OBSERVER-COLLAPSE-001", ["OBSERVER_COLLAPSE"], "HOLD"),
    ("EVD-CONTRADICTION-ERASURE-001", ["CONTRADICTION_ERASURE"], "REQUIRE_ADJUDICATION"),
    ("EVD-REPLAY-DIVERGENCE-001", ["REPLAY_DIVERGENCE"], "REQUIRE_REPLAY"),
    ("EVD-LINEAGE-CORRUPTION-001", ["LINEAGE_CORRUPTION"], "REJECT"),
]


def report(rail, rows):
    return {
        "order": "O22.4",
        "rail": rail,
        "all_passed": True,
        "fixture_count": 8,
        "passed_count": 8,
        "failed_count": 0,
        "results": [
            {
                "fixture_id": fixture_id,
                "actual_pathologies": pathologies,
                "actual_disposition": disposition,
                "passed": True,
            }
            for fixture_id, pathologies, disposition in rows
        ],
    }


class O23RegressionGateTests(unittest.TestCase):
    def setUp(self):
        self.reference = report("reference-transfer", REF_ROWS)
        self.evidence = report("evidence-transfer", EVD_ROWS)

    def test_cross_rail_tribunal_preserves_asymmetry(self):
        tribunal = adjudicate(self.reference, self.evidence)
        self.assertEqual(tribunal["pair_count"], 8)
        self.assertEqual(tribunal["pathology_asymmetry_pairs"], 1)
        self.assertEqual(tribunal["disposition_conflict_pairs"], 0)
        self.assertFalse(tribunal["rules"]["authority_merged"])
        self.assertFalse(tribunal["rules"]["agreement_is_proof"])

    def test_mutation_tournament_regression_digest(self):
        result = run_mutation(seed=2301001, trials=1000)
        self.assertTrue(result["all_pathologies_covered"])
        self.assertEqual(result["unique_combinations"], 91)
        self.assertEqual(
            result["tournament_digest_sha256"],
            "d1ff891cb4c55163cb9922db755cb47fe10b0f029bfd2b1e24c3f2cb64592590",
        )

    def test_dual_rail_replay_regression_digest(self):
        tribunal = adjudicate(self.reference, self.evidence)
        result = run_replay(tribunal, rounds=1000)
        self.assertTrue(result["all_rounds_stable"])
        self.assertEqual(result["pathology_divergence_pairs"], 1)
        self.assertEqual(result["disposition_divergence_pairs"], 0)
        self.assertEqual(
            result["canonical_pairs_digest_sha256"],
            "d9bdc1e62777af0cba7803c6c64d9e578a03f17c2a89876902aa3d5cbe3f7d2d",
        )


if __name__ == "__main__":
    unittest.main()
