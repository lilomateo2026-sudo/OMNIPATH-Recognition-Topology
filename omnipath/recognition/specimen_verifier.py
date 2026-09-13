from __future__ import annotations

from boundary_guard import apply_boundary_guard
from boundary_runner import run_one
from cross_product_generator import apply_dimensions


def verify_specimens(corpus, specimens, schema, root_lock, checker):
    cases = {item["case_id"]: item for item in corpus.get("cases", [])}
    failures = []
    results = []

    for specimen in specimens:
        case_id = specimen["source_case_id"]
        case = cases.get(case_id)
        if case is None:
            failures.append("MISSING_SOURCE_CASE:" + case_id)
            continue

        dimensions = tuple(specimen["mutation_dimensions"])
        record = apply_dimensions(case["record"], dimensions)
        outcome = run_one(record, schema, root_lock, checker, apply_boundary_guard)
        base_decision = outcome["first"].get("decision")
        final_decision = outcome["final"].get("decision")

        if base_decision != specimen.get("expected_base_decision"):
            failures.append("SPECIMEN_BASE_MISMATCH:" + case_id)
        if final_decision != specimen.get("expected_final_decision"):
            failures.append("SPECIMEN_FINAL_MISMATCH:" + case_id)

        reduced_results = []
        for removed in dimensions:
            reduced = tuple(item for item in dimensions if item != removed)
            reduced_record = apply_dimensions(case["record"], reduced)
            reduced_result = checker(reduced_record, schema, root_lock)
            reduced_decision = reduced_result.get("decision")
            reduced_results.append({"removed": removed, "decision": reduced_decision})
            if reduced_decision == "PASS":
                failures.append("SPECIMEN_NOT_MINIMAL:" + case_id + ":" + removed)

        results.append({
            "source_case_id": case_id,
            "mutation_dimensions": list(dimensions),
            "base_decision": base_decision,
            "final_decision": final_decision,
            "reduced_results": reduced_results,
        })

    return sorted(failures), sorted(results, key=lambda item: item["source_case_id"])
