from __future__ import annotations

import json
from pathlib import Path

from cross_product_contract import SPECIMEN_SCHEMA

HERE = Path(__file__).resolve().parent
SPECIMEN_DIR = HERE / "regression" / "o22_5"


def load_specimens():
    specimens = []
    for path in sorted(SPECIMEN_DIR.glob("*.json")):
        with path.open("r", encoding="utf-8") as handle:
            item = json.load(handle)
        if item.get("schema") != SPECIMEN_SCHEMA:
            raise ValueError("unexpected specimen schema: " + path.name)
        specimens.append(item)
    return specimens


def specimen_key(item):
    return (item["source_case_id"], tuple(item["mutation_dimensions"]))
