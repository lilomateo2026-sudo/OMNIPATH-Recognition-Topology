import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pathology_validator import DEFAULT_LOCK, DEFAULT_SCHEMA, _load_json, validate_pathology
from tribunal_core import run_cases
from tribunal_loader import load_corpus


class TribunalTests(unittest.TestCase):
    def test_certified(self):
        corpus = load_corpus()
        report = run_cases(corpus, _load_json(DEFAULT_SCHEMA), _load_json(DEFAULT_LOCK), validate_pathology)
        self.assertEqual(report["verdict"], "CERTIFIED")
        self.assertEqual(report["counts"]["PASS"], 0)

    def test_deterministic(self):
        corpus = load_corpus()
        schema = _load_json(DEFAULT_SCHEMA)
        lock = _load_json(DEFAULT_LOCK)
        first = run_cases(copy.deepcopy(corpus), schema, lock, validate_pathology)
        second = run_cases(copy.deepcopy(corpus), schema, lock, validate_pathology)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
