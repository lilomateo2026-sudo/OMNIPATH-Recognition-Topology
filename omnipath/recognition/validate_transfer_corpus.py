#!/usr/bin/env python3
"""O22.4 deterministic constitutional transfer validator.

Validates O22.3 fixture corpora against the O21.3 constitutional root,
O21.4 root freeze, O22.1 pathology vocabulary, and O22.2 rail contracts.
Uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT_SHA = "a730bba4e6a466e15b95c47998ae403c0ffe3a23"
FREEZE_SHA = "07f11ddf005f054d7172c7e1232c2b89a5a8ec65"
PATHOLOGIES = {
    "FALSE_CONSENSUS",
    "PROVENANCE_LOSS",
    "SCOPE_INFLATION",
    "OBSERVER_COLLAPSE",
    "CONTRADICTION_ERASURE",
    "REPLAY_DIVERGENCE",
    "LINEAGE_CORRUPTION",
}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def classify_fixture(fixture: dict[str, Any]) -> list[str]:
    candidate = _dict(fixture.get("candidate_transfer"))
    provenance = _dict(candidate.get("provenance"))
    transforms = {str(x) for x in _list(provenance.get("transform_refs"))}
    parents = [str(x) for x in _list(provenance.get("parent_refs"))]
    recognition = _dict(candidate.get("recognition_vector"))
    observer = _dict(candidate.get("c_observer_judgment"))
    replay = _dict(candidate.get("replay_metadata"))
    scope = _dict(candidate.get("evidence_scope"))
    supports = [str(x).lower() for x in _list(scope.get("supports"))]
    does_not_support = [str(x).lower() for x in _list(scope.get("does_not_support"))]
    observed = _list(candidate.get("observed_evidence"))
    contradictions = _list(candidate.get("contradictions"))
    judgment = str(observer.get("judgment", "")).lower()

    found: set[str] = set()

    root = provenance.get("constitutional_root_sha")
    freeze = provenance.get("root_freeze_sha")
    lineage_present = root is not None or freeze is not None
    if (
        candidate.get("prompt_hash") in (None, "")
        or root is None
        or freeze is None
        or not parents
    ):
        found.add("PROVENANCE_LOSS")

    if (
        (root is not None and root != ROOT_SHA)
        or (freeze is not None and freeze != FREEZE_SHA)
        or (lineage_present and any("unknown-parent" in p for p in parents))
    ):
        found.add("LINEAGE_CORRUPTION")
        if candidate.get("prompt_hash") not in (None, "") and root is not None and freeze is not None and parents:
            found.discard("PROVENANCE_LOSS")

    if (
        "cross-rail-agreement-to-proof" in transforms
        or "agreement-proves-correctness" in judgment
    ):
        found.add("FALSE_CONSENSUS")

    universal_scope = any(
        "all models" in text or "future runs" in text or "universal" in text
        for text in supports
    )
    if (
        universal_scope
        or "universally true" in judgment
        or ("FALSE_CONSENSUS" in found and not does_not_support)
    ):
        found.add("SCOPE_INFLATION")

    observed_sources = [
        str(_dict(item).get("source_ref", "")).lower() for item in observed
    ]
    if (
        "judgment-to-evidence" in transforms
        or "copy-reference-judgment-as-independent-evidence" in transforms
        or str(recognition.get("source", "")).lower() == "c_observer_judgment"
        or any("c_observer_judgment" in source for source in observed_sources)
    ):
        found.add("OBSERVER_COLLAPSE")

    if (
        {"drop-minority-observation", "drop-conflicting-evidence"} & transforms
        and not contradictions
    ):
        found.add("CONTRADICTION_ERASURE")

    if replay.get("claimed_deterministic") is True:
        expected_hash = replay.get("expected_hash")
        actual_hash = replay.get("actual_hash")
        if expected_hash is not None and actual_hash is not None and expected_hash != actual_hash:
            found.add("REPLAY_DIVERGENCE")

    unknown = found - PATHOLOGIES
    if unknown:
        raise ValueError(f"validator emitted unknown pathology classes: {sorted(unknown)}")
    return sorted(found)


def disposition(pathologies: list[str]) -> str:
    found = set(pathologies)
    if not found:
        return "ACCEPT_FOR_COMPARISON"
    if "LINEAGE_CORRUPTION" in found:
        return "REJECT"
    if "REPLAY_DIVERGENCE" in found:
        return "REQUIRE_REPLAY"
    if "FALSE_CONSENSUS" in found or "CONTRADICTION_ERASURE" in found:
        return "REQUIRE_ADJUDICATION"
    if "SCOPE_INFLATION" in found:
        return "REJECT"
    if "PROVENANCE_LOSS" in found or "OBSERVER_COLLAPSE" in found:
        return "HOLD"
    return "HOLD"


def validate_corpus(corpus: dict[str, Any]) -> dict[str, Any]:
    contract = _dict(corpus.get("fixture_contract"))
    fixtures = _list(corpus.get("fixtures"))
    header_errors: list[str] = []

    if corpus.get("schema") != "omnipath.transfer-fixture-corpus/v1":
        header_errors.append("unexpected corpus schema")
    if corpus.get("order") != "O22.3":
        header_errors.append("unexpected corpus order")
    if corpus.get("constitutional_root_sha") != ROOT_SHA:
        header_errors.append("corpus constitutional root mismatch")
    if corpus.get("root_freeze_sha") != FREEZE_SHA:
        header_errors.append("corpus root freeze mismatch")
    if contract.get("deterministic") is not True:
        header_errors.append("fixture corpus is not marked deterministic")
    if contract.get("controls") != 1 or contract.get("pathology_cases") != 7:
        header_errors.append("expected exactly 1 control and 7 pathology fixtures")
    if len(fixtures) != 8:
        header_errors.append(f"expected 8 fixtures, found {len(fixtures)}")

    results: list[dict[str, Any]] = []
    for fixture in fixtures:
        if not isinstance(fixture, dict):
            results.append({"fixture_id": None, "passed": False, "error": "fixture is not an object"})
            continue
        actual_pathologies = classify_fixture(fixture)
        expected_pathologies = sorted(str(x) for x in _list(fixture.get("expected_pathologies")))
        actual_disposition = disposition(actual_pathologies)
        expected_disposition = fixture.get("expected_disposition")
        pathology_match = actual_pathologies == expected_pathologies
        disposition_match = actual_disposition == expected_disposition
        results.append(
            {
                "fixture_id": fixture.get("fixture_id"),
                "class": fixture.get("class"),
                "expected_pathologies": expected_pathologies,
                "actual_pathologies": actual_pathologies,
                "expected_disposition": expected_disposition,
                "actual_disposition": actual_disposition,
                "pathology_match": pathology_match,
                "disposition_match": disposition_match,
                "passed": pathology_match and disposition_match,
            }
        )

    passed = not header_errors and all(item.get("passed") is True for item in results)
    return {
        "schema": "omnipath.transfer-validation-report/v1",
        "order": "O22.4",
        "rail": corpus.get("rail"),
        "corpus_order": corpus.get("order"),
        "constitutional_root_sha": ROOT_SHA,
        "root_freeze_sha": FREEZE_SHA,
        "header_errors": header_errors,
        "fixture_count": len(fixtures),
        "passed_count": sum(1 for item in results if item.get("passed") is True),
        "failed_count": sum(1 for item in results if item.get("passed") is not True),
        "all_passed": passed,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an OMNIPATH O22.3 transfer fixture corpus")
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    corpus = json.loads(args.corpus.read_text(encoding="utf-8"))
    report = validate_corpus(corpus)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
