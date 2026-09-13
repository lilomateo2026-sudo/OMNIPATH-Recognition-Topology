from __future__ import annotations

from boundary_guard import apply_boundary_guard
from boundary_runner import run_one
from cross_product_contract import CROSS_PRODUCT_VARIANTS, EXPECTED_MINIMAL_SPECIMENS, TOTAL_VARIANTS, VERSION
from cross_product_generator import generate_cross_product
from escape_minimizer import minimal_base_passes
from specimen_registry import specimen_key
from specimen_verifier import verify_specimens
from tribunal_core import digest


def run_cross_product(corpus, specimens, schema, root_lock, checker):
    variants = generate_cross_product(corpus)
    failures = []
    results = []
    base_passes = []
    final_passes = []

    if len(variants) != TOTAL_VARIANTS:
        failures.append("TOTAL_VARIANT_COUNT")
    if sum(1 for item in variants if item["cross_product"]) != CROSS_PRODUCT_VARIANTS:
        failures.append("CROSS_PRODUCT_COUNT")

    for item in variants:
        outcome = run_one(item["record"], schema, root_lock, checker, apply_boundary_guard)
        first = outcome["first"]
        second = outcome["second"]
        final = outcome["final"]
        base_decision = first.get("decision")
        final_decision = final.get("decision")
        if first != second:
            failures.append("NONDETERMINISTIC:" + item["variant_id"])
        if base_decision == "PASS":
            base_passes.append(item["variant_id"])
        if final_decision == "PASS":
            final_passes.append(item["variant_id"])
            failures.append("FINAL_PASS:" + item["variant_id"])
        results.append({
            "variant_id": item["variant_id"],
            "case_id": item["case_id"],
            "dimensions": item["dimensions"],
            "width": item["width"],
            "cross_product": item["cross_product"],
            "base_decision": base_decision,
            "final_decision": final_decision,
            "deterministic": first == second,
        })

    minimal = minimal_base_passes(results)
    minimal_keys = {(item["case_id"], tuple(item["dimensions"])) for item in minimal}
    specimen_keys = {specimen_key(item) for item in specimens}
    if len(minimal) != EXPECTED_MINIMAL_SPECIMENS:
        failures.append("MINIMAL_SPECIMEN_COUNT")
    if minimal_keys != specimen_keys:
        failures.append("SPECIMEN_SET_MISMATCH")

    specimen_failures, specimen_results = verify_specimens(corpus, specimens, schema, root_lock, checker)
    failures.extend(specimen_failures)

    material = {
        "version": VERSION,
        "order": "O22.5",
        "variant_count": len(variants),
        "cross_product_variant_count": sum(1 for item in variants if item["cross_product"]),
        "base_pass_count": len(base_passes),
        "base_passes": sorted(base_passes),
        "final_pass_count": len(final_passes),
        "final_passes": sorted(final_passes),
        "minimal_counterexamples": minimal,
        "specimen_results": specimen_results,
        "failures": sorted(set(failures)),
        "corpus_sha256": digest(corpus),
        "specimens_sha256": digest(specimens),
        "schema_sha256": digest(schema),
        "root_lock_sha256": digest(root_lock),
    }
    material["verdict"] = "CERTIFIED" if not material["failures"] else "FAILED"
    return {**material, "report_sha256": digest(material)}
