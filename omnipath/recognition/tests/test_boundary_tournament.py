import unittest

from boundary_tournament import run_tournament
from pathology_validator import DEFAULT_LOCK, DEFAULT_SCHEMA, _load_json, validate_pathology
from tribunal_loader import load_corpus


class BoundaryTournamentTests(unittest.TestCase):
    def test_certified_and_no_final_pass(self):
        report = run_tournament(load_corpus(), _load_json(DEFAULT_SCHEMA), _load_json(DEFAULT_LOCK), validate_pathology)
        self.assertEqual(report["verdict"], "CERTIFIED")
        self.assertEqual(report["variant_count"], 42)
        self.assertEqual(report["final_pass_count"], 0)

    def test_current_base_escapes_are_retained(self):
        report = run_tournament(load_corpus(), _load_json(DEFAULT_SCHEMA), _load_json(DEFAULT_LOCK), validate_pathology)
        self.assertEqual(report["base_pass_count"], 4)


if __name__ == "__main__":
    unittest.main()
