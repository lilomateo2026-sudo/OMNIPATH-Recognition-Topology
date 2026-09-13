import json

from cross_product_runner import run_cross_product
from pathology_validator import DEFAULT_LOCK, DEFAULT_SCHEMA, _load_json, validate_pathology
from specimen_registry import load_specimens
from tribunal_loader import load_corpus


def main():
    report = run_cross_product(load_corpus(), load_specimens(), _load_json(DEFAULT_SCHEMA), _load_json(DEFAULT_LOCK), validate_pathology)
    print(json.dumps(report, indent=2, sort_keys=True))
    return report["verdict"]


if __name__ == "__main__":
    main()
