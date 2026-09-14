import json
import unittest
from pathlib import Path

from v6.cross_ledger_replay_audit import audit

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "omnipath" / "recognition" / "v6" / "O32_3_cross_ledger_replay_audit.json"


class O323CrossLedgerReplayAuditTests(unittest.TestCase):
    def test_every_durable_generation_reconstructs(self):
        expected = json.loads(MANIFEST.read_text(encoding="utf-8"))["expected"]
        result = audit(ROOT)
        for key, value in expected.items():
            self.assertEqual(result[key], value, key)

    def test_all_rows_are_lineage_and_alias_consistent(self):
        result = audit(ROOT)
        self.assertTrue(all(row["lineage_ok"] for row in result["rows"]))
        self.assertTrue(all(row["alias_ok"] for row in result["rows"]))
        self.assertTrue(all(row["replay_identity_ok"] for row in result["rows"]))

    def test_only_historical_backfill_uses_workflow_only_identity(self):
        rows = audit(ROOT)["rows"]
        workflow_only = [row for row in rows if row["identity_level"] == "workflow_only_historical_backfill"]
        self.assertEqual(len(workflow_only), 1)
        self.assertTrue(workflow_only[0]["entry_id"].startswith("O22.6:"))


if __name__ == "__main__":
    unittest.main()
