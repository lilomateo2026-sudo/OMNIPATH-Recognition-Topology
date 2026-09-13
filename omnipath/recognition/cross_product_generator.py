from __future__ import annotations

import copy
from itertools import combinations

from boundary_contract import DIMENSIONS
from boundary_mutator import _MUTATORS


def apply_dimensions(record, dimensions):
    candidate = copy.deepcopy(record)
    selected = set(dimensions)
    for dimension in DIMENSIONS:
        if dimension in selected:
            _MUTATORS[dimension](candidate)
    return candidate


def generate_cross_product(corpus):
    variants = []
    for case in corpus.get("cases", []):
        for width in range(1, len(DIMENSIONS) + 1):
            for dimensions in combinations(DIMENSIONS, width):
                suffix = "+".join(dimensions)
                variants.append({
                    "variant_id": case["case_id"] + "::" + suffix,
                    "case_id": case["case_id"],
                    "dimensions": list(dimensions),
                    "width": width,
                    "cross_product": width >= 2,
                    "record": apply_dimensions(case["record"], dimensions),
                })
    return sorted(variants, key=lambda item: item["variant_id"])
