import unittest
from pathlib import Path

from promotion_candidate_resolver import DEFAULT_INDEX_REF, resolve_candidate
from promotion_genealogy_common import read_json
from promotion_genealogy_index import generate_genealogy_index, verify_genealogy_index

ROOT = Path(__file__).resolve().parents[3]
REQUIRED_HISTORICAL_GENERATIONS = {"O22.6", "O23.9", "O25.5", "O27.5"}


class GenealogyIndexTests(unittest.TestCase):
    def test_committed_index_is_exact_regeneration(self):
        committed = read_json(ROOT / DEFAULT_INDEX_REF)
        generated = generate_genealogy_index(ROOT)
        self.assertEqual(committed, generated)
        audit = verify_genealogy_index(ROOT, committed)
        self.assertTrue(audit["valid"], audit)

        entries = committed["entries"]
        generations = {entry["generation_order"] for entry in entries}
        all_aliases = {alias for entry in entries for alias in entry["aliases"]}

        self.assertEqual(committed["entry_count"], len(entries))
        self.assertTrue(REQUIRED_HISTORICAL_GENERATIONS.issubset(generations))
        self.assertEqual(len(committed["alias_map"]), len(all_aliases))
        self.assertEqual(set(committed["alias_map"]), all_aliases)

    def test_every_alias_resolves_without_external_refs(self):
        committed = read_json(ROOT / DEFAULT_INDEX_REF)
        by_id = {entry["entry_id"]: entry for entry in committed["entries"]}
        for alias, entry_id in committed["alias_map"].items():
            result = resolve_candidate(ROOT, alias)
            expected = by_id[entry_id]
            self.assertEqual(result["matched_entry_id"], entry_id)
            self.assertEqual(result["canonical_candidate_sha"], expected["candidate_commit_sha"])
            self.assertEqual(result["promoted_main_sha"], expected["promoted_main_sha"])
            self.assertEqual(result["ledger_ref"], expected["ledger_ref"])
            self.assertEqual(result["epistemic_state"], "VERIFIED_WITHIN_SCOPE")
            self.assertEqual(result["constitutional_root_sha"], "a730bba4e6a466e15b95c47998ae403c0ffe3a23")
            self.assertTrue(result["resolution_sha256"])

    def test_unknown_candidate_is_not_guessed(self):
        with self.assertRaises(KeyError):
            resolve_candidate(ROOT, "0" * 40)


if __name__ == "__main__":
    unittest.main()
