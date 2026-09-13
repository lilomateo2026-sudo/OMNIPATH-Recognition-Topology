#!/usr/bin/env python3
"""O22.5 external cross-rail recognition tribunal.

Consumes the O22.4 reference/evidence validation attestations as read-only
inputs. It never merges rail authority and never treats agreement as proof.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

EXPECTED_REFERENCE_COMMIT = "5899435141cff4acfdc6b304dd4358ecd9bc3bf8"
EXPECTED_EVIDENCE_COMMIT = "a6eeff44c7ba0bfc4afd5d5d90201b5df99a2f1d"
GENESIS_PARENT_SHA = "df7552079f7aea41b6c6732a2f6758f401d9a987"


def _key(fixture_id: str) -> str:
    if fixture_id.startswith("REF-"):
        return fixture_id[4:]
    if fixture_id.startswith("EVD-"):
        return fixture_id[4:]
    return fixture_id


def _index(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {_key(str(row["fixture_id"])): row for row in report.get("results", [])}


def adjudicate(reference: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    if reference.get("order") != "O22.4" or evidence.get("order") != "O22.4":
        raise ValueError("tribunal only accepts O22.4 attestations")
    if reference.get("all_passed") is not True or evidence.get("all_passed") is not True:
        raise ValueError("both source attestations must be fully passing")

    ref = _index(reference)
    evd = _index(evidence)
    keys = sorted(set(ref) | set(evd))
    pairs: list[dict[str, Any]] = []

    for key in keys:
        left = ref.get(key)
        right = evd.get(key)
        if left is None or right is None:
            pairs.append({
                "pair_id": key,
                "status": "MISSING_PEER",
                "tribunal_disposition": "REQUIRE_ADJUDICATION",
            })
            continue

        ref_pathologies = sorted(left.get("actual_pathologies", []))
        evd_pathologies = sorted(right.get("actual_pathologies", []))
        ref_disposition = left.get("actual_disposition")
        evd_disposition = right.get("actual_disposition")
        pathology_match = ref_pathologies == evd_pathologies
        disposition_match = ref_disposition == evd_disposition

        if not disposition_match:
            status = "DISPOSITION_CONFLICT"
            tribunal_disposition = "REQUIRE_ADJUDICATION"
        elif not pathology_match:
            status = "ASYMMETRIC_PATHOLOGY"
            tribunal_disposition = ref_disposition
        else:
            status = "CONSISTENT"
            tribunal_disposition = ref_disposition

        pairs.append({
            "pair_id": key,
            "reference_pathologies": ref_pathologies,
            "evidence_pathologies": evd_pathologies,
            "pathology_match": pathology_match,
            "reference_disposition": ref_disposition,
            "evidence_disposition": evd_disposition,
            "disposition_match": disposition_match,
            "tribunal_disposition": tribunal_disposition,
            "status": status,
        })

    return {
        "schema": "omnipath.cross-rail-tribunal/v1",
        "order": "O22.5",
        "authority": "external-tribunal",
        "genesis_parent_sha": GENESIS_PARENT_SHA,
        "rules": {
            "authority_merged": False,
            "agreement_is_proof": False,
            "asymmetry_must_be_preserved": True,
            "epistemic_ceiling": "VERIFIED_WITHIN_SCOPE",
        },
        "pair_count": len(pairs),
        "pathology_match_pairs": sum(1 for p in pairs if p.get("pathology_match") is True),
        "pathology_asymmetry_pairs": sum(1 for p in pairs if p.get("status") == "ASYMMETRIC_PATHOLOGY"),
        "disposition_match_pairs": sum(1 for p in pairs if p.get("disposition_match") is True),
        "disposition_conflict_pairs": sum(1 for p in pairs if p.get("status") == "DISPOSITION_CONFLICT"),
        "pairs": pairs,
        "decision": "READY_FOR_O23_ADVERSARIAL_EVOLUTION_WITH_ASYMMETRIES_RETAINED",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("reference_report", type=Path)
    parser.add_argument("evidence_report", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    reference = json.loads(args.reference_report.read_text(encoding="utf-8"))
    evidence = json.loads(args.evidence_report.read_text(encoding="utf-8"))
    result = adjudicate(reference, evidence)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if result["disposition_conflict_pairs"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
