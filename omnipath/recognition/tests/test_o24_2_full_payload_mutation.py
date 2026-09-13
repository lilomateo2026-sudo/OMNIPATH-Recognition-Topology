import unittest

from adversarial.full_payload_mutation_tournament import run


EXPECTED_DIGEST = "65449a768f02abb149dcb1fe055949c2232bedc2bc09630d36f7e1b8e50dd956"
EXPECTED_FIELDS = [
    "contradictory_evidence",
    "evidence_scope",
    "lineage",
    "observer_boundary",
    "provenance",
    "replay_metadata",
]


class O242FullPayloadMutationTests(unittest.TestCase):
    def test_complete_payload_tournament_has_no_undetected_escape(self):
        result = run(seed=2402001, trials=3000)
        self.assertEqual(result["schema"], "omnipath.full-payload-mutation-tournament/v1")
        self.assertEqual(result["order"], "O24.2")
        self.assertEqual(result["trials"], 3000)
        self.assertEqual(result["operator_count"], 12)
        self.assertTrue(result["operator_coverage"])
        self.assertEqual(result["field_coverage"], EXPECTED_FIELDS)
        self.assertEqual(result["escape_count"], 0)
        self.assertEqual(result["tournament_digest_sha256"], EXPECTED_DIGEST)

    def test_tournament_is_deterministic(self):
        first = run(seed=2402001, trials=3000)
        second = run(seed=2402001, trials=3000)
        self.assertEqual(first["tournament_digest_sha256"], second["tournament_digest_sha256"])
        self.assertEqual(first["rows"], second["rows"])


if __name__ == "__main__":
    unittest.main()
