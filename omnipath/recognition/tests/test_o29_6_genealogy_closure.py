from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from promotion_genealogy_closure import (
    GAP_REGISTRY_REF,
    INDEX_REF,
    audit_genealogy_closure,
)


ROOT = Path(__file__).resolve().parents[3]


def load(ref: str) -> dict:
    return json.loads((ROOT / ref).read_text(encoding="utf-8"))


class O296GenealogyClosureTests(unittest.TestCase):
    def test_live_genealogy_is_closed(self) -> None:
        result = audit_genealogy_closure(ROOT)
        self.assertTrue(result["closed"], result["failures"])
        self.assertEqual(result["ledger_count"], 5)
        self.assertEqual(result["index_entry_count"], 5)
        self.assertEqual(result["alias_count"], 9)
        self.assertEqual(result["promoted_main_with_durable_evidence"], 5)
        self.assertEqual(result["legacy_gap_count"], 1)
        self.assertEqual(result["legacy_gap_ids"], ["O23.9:promotion_manifest"])

    def test_o23_9_missing_manifest_requires_explicit_gap(self) -> None:
        gaps = load(GAP_REGISTRY_REF)
        gaps["gaps"] = []
        result = audit_genealogy_closure(ROOT, gap_registry=gaps)
        self.assertFalse(result["closed"])
        self.assertTrue(any("UNCLASSIFIED_MISSING_SOURCE" in item for item in result["failures"]))

    def test_gap_metadata_drift_is_detected(self) -> None:
        gaps = load(GAP_REGISTRY_REF)
        gaps["gaps"][0]["declared_blob_sha"] = "0" * 40
        result = audit_genealogy_closure(ROOT, gap_registry=gaps)
        self.assertFalse(result["closed"])
        self.assertTrue(any("GAP_BLOB_DRIFT" in item for item in result["failures"]))

    def test_orphan_ledger_is_detected(self) -> None:
        index = load(INDEX_REF)
        index = copy.deepcopy(index)
        removed = index["entries"].pop()
        index["entry_count"] = len(index["entries"])
        for alias in removed["aliases"]:
            index["alias_map"].pop(alias, None)
        result = audit_genealogy_closure(ROOT, committed_index=index)
        self.assertFalse(result["closed"])
        self.assertTrue(any("ORPHAN_LEDGER" in item for item in result["failures"]))

    def test_duplicate_alias_is_detected(self) -> None:
        index = load(INDEX_REF)
        index = copy.deepcopy(index)
        shared = index["entries"][0]["aliases"][0]
        index["entries"][1]["aliases"].append(shared)
        result = audit_genealogy_closure(ROOT, committed_index=index)
        self.assertFalse(result["closed"])
        self.assertTrue(any("AMBIGUOUS_ALIAS" in item for item in result["failures"]))


if __name__ == "__main__":
    unittest.main()
