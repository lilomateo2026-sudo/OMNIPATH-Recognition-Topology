import copy
import json
import unittest
from pathlib import Path

from omnipath.recognition.validate_pathology import validate


FIXTURE = Path(__file__).parent / "fixtures" / "pathology.valid.json"


class RecognitionConformanceTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def assertRejected(self, mutate):
        candidate = copy.deepcopy(self.record)
        mutate(candidate)
        self.assertTrue(validate(candidate))

    def test_valid_record_passes(self):
        self.assertEqual([], validate(self.record))

    def test_root_substitution_fails(self):
        self.assertRejected(lambda r: r["provenance"].update(constitutional_root_sha="forged"))

    def test_false_replay_agreement_fails(self):
        self.assertRejected(lambda r: r["replay"].update(match=True))

    def test_high_severity_cannot_have_no_effect(self):
        self.assertRejected(lambda r: r.update(promotion_effect="NO_EFFECT"))

    def test_blocked_pathology_cannot_be_verified(self):
        self.assertRejected(lambda r: r.update(epistemic_state="VERIFIED_WITHIN_SCOPE"))

    def test_absolute_state_fails(self):
        self.assertRejected(lambda r: r.update(epistemic_state="ABSOLUTE"))

    def test_observer_judgment_is_required(self):
        self.assertRejected(lambda r: r.pop("observer_judgment"))

    def test_scope_boundary_is_required(self):
        self.assertRejected(lambda r: r["scope"].pop("does_not_support"))


if __name__ == "__main__":
    unittest.main()
