import unittest

from cross_product_runner import run_cross_product
from pathology_validator import DEFAULT_LOCK, DEFAULT_SCHEMA, _load_json, validate_pathology
from specimen_registry import load_specimens
from tribunal_loader import load_corpus


class CrossProductTests(unittest.TestCase):
    def report(self):
        return run_cross_product(load_corpus(), load_specimens(), _load_json(DEFAULT_SCHEMA), _load_json(DEFAULT_LOCK), validate_pathology)

    def test_certified_counts(self):
        report = self.report()
        self.assertEqual(report["verdict"], "CERTIFIED")
        self.assertEqual(report["variant_count"], 378)
        self.assertEqual(report["cross_product_variant_count"], 342)
        self.assertEqual(report["base_pass_count"], 40)
        self.assertEqual(report["final_pass_count"], 0)
        self.assertEqual(len(report["minimal_counterexamples"]), 4)

    def test_minimal_counterexamples(self):
        report = self.report()
        found = {item["case_id"]: tuple(item["dimensions"]) for item in report["minimal_counterexamples"]}
        self.assertEqual(found, {
            "false-consensus-cross-rail": ("severity", "promotion_effect", "contradictions"),
            "observer-collapse": ("severity", "promotion_effect"),
            "contradiction-erasure": ("severity", "promotion_effect", "contradictions"),
            "replay-divergence": ("severity", "promotion_effect", "replay"),
        })


if __name__ == "__main__":
    unittest.main()
