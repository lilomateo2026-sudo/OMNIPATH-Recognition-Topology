#!/usr/bin/env python3
"""O23.2 deterministic fixture-level dual-rail replay harness."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

DEFAULT_ROUNDS = 1000


def run(tribunal: dict, rounds: int = DEFAULT_ROUNDS) -> dict:
    pairs = tribunal.get("pairs", [])
    canonical = json.dumps(pairs, sort_keys=True, separators=(",", ":"))
    expected_digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    stable = 0
    for _ in range(rounds):
        replayed = json.dumps(pairs, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(replayed.encode("utf-8")).hexdigest()
        if digest == expected_digest:
            stable += 1

    pathology_divergence = sum(1 for p in pairs if p.get("reference_pathologies") != p.get("evidence_pathologies"))
    disposition_divergence = sum(1 for p in pairs if p.get("reference_disposition") != p.get("evidence_disposition"))

    return {
        "schema": "omnipath.dual-rail-replay/v1",
        "order": "O23.2",
        "scope": "fixture-level-tribunal-state",
        "rounds": rounds,
        "stable_rounds": stable,
        "pair_count": len(pairs),
        "pathology_divergence_pairs": pathology_divergence,
        "disposition_divergence_pairs": disposition_divergence,
        "canonical_pairs_digest_sha256": expected_digest,
        "all_rounds_stable": stable == rounds,
        "note": "This replays deterministic tribunal/fixture state; it is not an LLM inference determinism claim."
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tribunal_report", type=Path)
    parser.add_argument("--rounds", type=int, default=DEFAULT_ROUNDS)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    tribunal = json.loads(args.tribunal_report.read_text(encoding="utf-8"))
    result = run(tribunal, args.rounds)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if result["all_rounds_stable"] and result["disposition_divergence_pairs"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
