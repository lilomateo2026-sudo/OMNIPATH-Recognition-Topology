#!/usr/bin/env python3
"""O23.1 deterministic pathology mutation tournament."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter
from pathlib import Path

PATHOLOGIES = [
    "FALSE_CONSENSUS",
    "PROVENANCE_LOSS",
    "SCOPE_INFLATION",
    "OBSERVER_COLLAPSE",
    "CONTRADICTION_ERASURE",
    "REPLAY_DIVERGENCE",
    "LINEAGE_CORRUPTION",
]
DEFAULT_SEED = 2301001
DEFAULT_TRIALS = 1000


def disposition(pathologies: set[str]) -> str:
    if "LINEAGE_CORRUPTION" in pathologies:
        return "REJECT"
    if "REPLAY_DIVERGENCE" in pathologies:
        return "REQUIRE_REPLAY"
    if "FALSE_CONSENSUS" in pathologies or "CONTRADICTION_ERASURE" in pathologies:
        return "REQUIRE_ADJUDICATION"
    if "SCOPE_INFLATION" in pathologies:
        return "REJECT"
    return "HOLD"


def run(seed: int = DEFAULT_SEED, trials: int = DEFAULT_TRIALS) -> dict:
    rng = random.Random(seed)
    rows = []
    for index in range(1, trials + 1):
        width = rng.choice([2, 3, 4])
        combo = tuple(sorted(rng.sample(PATHOLOGIES, width)))
        rows.append({
            "trial": index,
            "pathologies": list(combo),
            "disposition": disposition(set(combo)),
        })

    unique = {tuple(row["pathologies"]) for row in rows}
    distribution = Counter(row["disposition"] for row in rows)
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    return {
        "schema": "omnipath.pathology-mutation-tournament/v1",
        "order": "O23.1",
        "seed": seed,
        "trials": trials,
        "mutation_widths": [2, 3, 4],
        "unique_combinations": len(unique),
        "all_pathologies_covered": set(PATHOLOGIES) == set().union(*(set(x) for x in unique)),
        "disposition_distribution": dict(sorted(distribution.items())),
        "tournament_digest_sha256": digest,
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--trials", type=int, default=DEFAULT_TRIALS)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = run(args.seed, args.trials)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if result["all_pathologies_covered"] and result["trials"] >= 1000 else 1


if __name__ == "__main__":
    raise SystemExit(main())
