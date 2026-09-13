#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

from promotion_manifest_gate import evaluate_promotion

HERE = Path(__file__).resolve().parent


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description="Run the O22.7 promotion manifest gate")
    parser.add_argument("manifest")
    parser.add_argument("attestation")
    parser.add_argument("--root-lock", default=str(HERE / "CONSTITUTIONAL_ROOT.lock.json"))
    args = parser.parse_args()

    result = evaluate_promotion(
        load(args.manifest),
        load(args.attestation),
        load(args.root_lock),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["promotion_allowed"] else 7


if __name__ == "__main__":
    raise SystemExit(main())
