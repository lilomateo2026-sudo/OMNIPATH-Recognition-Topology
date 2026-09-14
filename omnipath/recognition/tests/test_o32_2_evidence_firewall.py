import json
import unittest
from pathlib import Path

from v6.evidence_firewall import admit, run_injection_matrix

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "omnipath" / "recognition" / "v6" / "O32_2_evidence_firewall.json"


class O322EvidenceFirewallTests(unittest.TestCase):
    def test_read_only_classes_are_admitted_without_repository_capability(self):
        for evidence_class in ("consciousness_space", "HITM"):
            packet = admit({
                "evidence_class": evidence_class,
                "source_id": "fixture",
                "content_digest": "sha256:fixture",
                "payload": {"observation": "bounded evidence"},
            })
            self.assertTrue(packet["read_only"])
            self.assertTrue(all(value is False for value in packet["repository_capabilities"].values()))

    def test_recursive_authority_injection_matrix_has_zero_escapes(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        expected = manifest["injection_matrix"]
        result = run_injection_matrix()
        self.assertEqual(result["attempts"], expected["attempts"])
        self.assertEqual(result["escape_count"], expected["expected_escape_count"])
        self.assertEqual(result["digest_sha256"], expected["expected_digest_sha256"])

    def test_nested_authority_is_rejected(self):
        with self.assertRaises(ValueError):
            admit({
                "evidence_class": "HITM",
                "source_id": "fixture",
                "content_digest": "sha256:fixture",
                "payload": {"deep": {"promotion_authority": True}},
            })


if __name__ == "__main__":
    unittest.main()
