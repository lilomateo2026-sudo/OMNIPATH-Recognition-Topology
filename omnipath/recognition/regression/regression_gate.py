#!/usr/bin/env python3
"""O23.3 regression gate for OMNIPATH recognition topology."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO_ROOT = HERE.parents[3]
sys.path.insert(0, str(REPO_ROOT / "omnipath" / "recognition" / "tribunal"))
sys.path.insert(0, str(REPO_ROOT / "omnipath" / "recognition" / "adversarial"))
sys.path.insert(0, str(REPO_ROOT / "omnipath" / "recognition" / "replay"))

import cross_rail_tribunal
import pathology_mutation_tournament
import dual_rail_replay_harness

EXPECTED_MUTATION_DIGEST = "b5ddd42b8d815454145069e07e18cbc3b8134f4ff950b3c3859c57c0a8c171b4"
EXPECTED_REPLAY_DIGEST = "337ede2d7527d27f7bfd33069664e4ac07a34f2bb8f1894d19d7cb7ad70bbe6b"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("reference_report", type=Path)
    parser.add_argument("evidence_report", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    ref = json.loads(args.reference_report.read_text(encoding="utf-8"))
    evd = json.loads(args.evidence_report.read_text(encoding="utf-8"))
    errors: list[str] = []

    for name, report in [("reference", ref), ("evidence", evd)]:
        if report.get("all_passed") is not True:
            errors.append(f"{name} O22.4 attestation is not fully passing")
        if report.get("fixture_count") != 8 or report.get("passed_count") != 8:
            errors.append(f"{name} O22.4 fixture count/regression mismatch")

    tribunal = cross_rail_tribunal.adjudicate(ref, evd)
    if tribunal.get("pair_count") != 8:
        errors.append("tribunal pair count changed")
    if tribunal.get("pathology_asymmetry_pairs") != 1:
        errors.append("expected exactly one preserved pathology asymmetry")
    if tribunal.get("disposition_conflict_pairs") != 0:
        errors.append("unexpected cross-rail disposition conflict")
    false_consensus = next(
        (p for p in tribunal["pairs"] if p.get("pair_id") == "FALSE-CONSENSUS-001"),
        None,
    )
    if false_consensus is None or false_consensus.get("status") != "ASYMMETRIC_PATHOLOGY":
        errors.append("false-consensus asymmetry was lost")

    mutation = pathology_mutation_tournament.run(seed=2301001, trials=1000)
    if mutation.get("unique_combinations") != 91:
        errors.append("mutation combination coverage changed")
    if mutation.get("tournament_digest_sha256") != EXPECTED_MUTATION_DIGEST:
        errors.append("mutation tournament digest changed")
    if mutation.get("all_pathologies_covered") is not True:
        errors.append("mutation tournament lost pathology coverage")

    replay = dual_rail_replay_harness.run(tribunal, rounds=1000)
    if replay.get("all_rounds_stable") is not True:
        errors.append("dual-rail replay is not stable")
    if replay.get("canonical_pairs_digest_sha256") != EXPECTED_REPLAY_DIGEST:
        errors.append("dual-rail replay digest changed")
    if replay.get("pathology_divergence_pairs") != 1:
        errors.append("replay no longer preserves exactly one pathology divergence")
    if replay.get("disposition_divergence_pairs") != 0:
        errors.append("replay introduced disposition divergence")

    result = {
        "schema": "omnipath.validator-regression-gate/v1",
        "order": "O23.3",
        "passed": not errors,
        "errors": errors,
        "checks": {
            "reference_fixtures": 8,
            "evidence_fixtures": 8,
            "tribunal_pairs": tribunal.get("pair_count"),
            "pathology_asymmetry_pairs": tribunal.get("pathology_asymmetry_pairs"),
            "mutation_trials": mutation.get("trials"),
            "mutation_unique_combinations": mutation.get("unique_combinations"),
            "replay_rounds": replay.get("rounds"),
            "replay_stable_rounds": replay.get("stable_rounds"),
        },
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
