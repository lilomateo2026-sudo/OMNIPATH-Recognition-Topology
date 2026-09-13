import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "attestation_ledger" / "v1" / "o22_6_main_ab1235e5"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class LedgerIntegrityTest(unittest.TestCase):
    def test_record_set_hashes(self):
        data = json.loads((ROOT / "promotion_manifest.json").read_text())
        self.assertEqual(data["order"], "O22.8A")
        for name, expected in data["components"].items():
            self.assertEqual(sha(ROOT / name), expected)
        material = dict(data)
        expected = material.pop("record_set_sha256")
        raw = json.dumps(material, sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), expected)


if __name__ == "__main__":
    unittest.main()
