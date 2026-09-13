#!/usr/bin/env python3
"""O22.2 executable conformance gate for recognition-pathology records."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT_SHA = "a730bba4e6a466e15b95c47998ae403c0ffe3a23"
FREEZE_SHA = "07f11ddf005f054d7172c7e1232c2b89a5a8ec65"
SCHEMA_VERSION = "omnipath.recognition-pathology/v1"
PATHOLOGY_TYPES = {
    "FALSE_CONSENSUS", "PROVENANCE_LOSS", "SCOPE_INFLATION",
    "OBSERVER_COLLAPSE", "CONTRADICTION_ERASURE", "REPLAY_DIVERGENCE",
    "LINEAGE_CORRUPTION",
}
STATES = {
    "OBSERVED", "COMPARED", "REPLAYED", "CONTRADICTED",
    "VERIFIED_WITHIN_SCOPE", "REJECTED", "ROLLED_BACK",
}
EFFECTS = {
    "NO_EFFECT", "HOLD", "REQUIRE_REPLAY", "REQUIRE_ADJUDICATION",
    "REJECT", "ROLLBACK",
}
BLOCKING_EFFECTS = EFFECTS - {"NO_EFFECT"}


def validate(record: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return ["record: must be an object"]

    required = {
        "schema_version", "pathology_id", "run_id", "rail", "pathology_type",
        "severity", "observed_evidence", "observer_judgment", "provenance",
        "scope", "promotion_effect",
    }
    for key in sorted(required - record.keys()):
        errors.append(f"{key}: required")

    if record.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version: must equal {SCHEMA_VERSION}")
    if record.get("pathology_type") not in PATHOLOGY_TYPES:
        errors.append("pathology_type: unsupported value")
    if record.get("rail") not in {"reference-transfer", "evidence-transfer", "cross-rail"}:
        errors.append("rail: unsupported value")
    severity = record.get("severity")
    if severity not in {"INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"}:
        errors.append("severity: unsupported value")
    effect = record.get("promotion_effect")
    if effect not in EFFECTS:
        errors.append("promotion_effect: unsupported value")
    if severity in {"HIGH", "CRITICAL"} and effect not in BLOCKING_EFFECTS:
        errors.append("promotion_effect: HIGH/CRITICAL pathology must block promotion")
    state = record.get("epistemic_state")
    if state is not None and state not in STATES:
        errors.append("epistemic_state: exceeds constitutional vocabulary")

    evidence = record.get("observed_evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("observed_evidence: must contain at least one item")
    else:
        for index, item in enumerate(evidence):
            if not isinstance(item, dict) or not all(item.get(k) for k in ("evidence_id", "kind", "source_ref")) or "value" not in item:
                errors.append(f"observed_evidence[{index}]: incomplete evidence envelope")

    judgment = record.get("observer_judgment")
    if not isinstance(judgment, dict) or not all(k in judgment for k in ("observer_id", "judgment", "confidence")):
        errors.append("observer_judgment: incomplete or collapsed into evidence")
    elif not isinstance(judgment["confidence"], (int, float)) or isinstance(judgment["confidence"], bool) or not 0 <= judgment["confidence"] <= 1:
        errors.append("observer_judgment.confidence: must be between 0 and 1")

    provenance = record.get("provenance")
    if not isinstance(provenance, dict):
        errors.append("provenance: required object")
    else:
        if provenance.get("constitutional_root_sha") != ROOT_SHA:
            errors.append("provenance.constitutional_root_sha: root identity mismatch")
        if "root_freeze_sha" in provenance and provenance["root_freeze_sha"] != FREEZE_SHA:
            errors.append("provenance.root_freeze_sha: freeze identity mismatch")
        for key in ("parent_refs", "transform_refs"):
            if not isinstance(provenance.get(key), list):
                errors.append(f"provenance.{key}: required array")

    scope = record.get("scope")
    if not isinstance(scope, dict) or not isinstance(scope.get("supports"), list) or not isinstance(scope.get("does_not_support"), list):
        errors.append("scope: must separate supports and does_not_support arrays")

    contradictions = record.get("contradictions", [])
    if record.get("pathology_type") == "CONTRADICTION_ERASURE" and not contradictions:
        errors.append("contradictions: erasure pathology must retain at least one contradiction")
    if isinstance(contradictions, list):
        for index, item in enumerate(contradictions):
            if not isinstance(item, dict) or item.get("status") not in {"OPEN", "EXPLAINED", "RESOLVED"}:
                errors.append(f"contradictions[{index}]: invalid status")

    replay = record.get("replay")
    if record.get("pathology_type") == "REPLAY_DIVERGENCE":
        if not isinstance(replay, dict) or replay.get("match") is not False:
            errors.append("replay.match: divergence requires explicit false")

    if state == "VERIFIED_WITHIN_SCOPE" and effect != "NO_EFFECT":
        errors.append("promotion: blocked pathology cannot be VERIFIED_WITHIN_SCOPE")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records", nargs="+", type=Path)
    args = parser.parse_args(argv)
    failed = False
    for path in args.records:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            errors = validate(record)
        except (OSError, json.JSONDecodeError) as exc:
            errors = [f"unreadable JSON: {exc}"]
        if errors:
            failed = True
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
