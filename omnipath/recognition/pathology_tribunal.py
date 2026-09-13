#!/usr/bin/env python3
import json
import sys

try:
    from .pathology_validator import DEFAULT_LOCK, DEFAULT_SCHEMA, _load_json, validate_pathology
    from .tribunal_core import run_cases
    from .tribunal_loader import load_corpus
except ImportError:
    from pathology_validator import DEFAULT_LOCK, DEFAULT_SCHEMA, _load_json, validate_pathology
    from tribunal_core import run_cases
    from tribunal_loader import load_corpus


def main():
    report = run_cases(load_corpus(), _load_json(DEFAULT_SCHEMA), _load_json(DEFAULT_LOCK), validate_pathology)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "CERTIFIED" else 4


if __name__ == "__main__":
    sys.exit(main())
