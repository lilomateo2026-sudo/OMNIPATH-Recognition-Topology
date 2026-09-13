from boundary_contract import DIMENSIONS, PARENT_SHA, VERSION
from boundary_guard import apply_boundary_guard
from boundary_mutator import generate_variants
from boundary_runner import run_one
from tribunal_core import digest


def run_tournament(corpus, schema, root_lock, checker):
    variants = generate_variants(corpus)
    results = []
    failures = []
    base_passes = []
    final_passes = []

    coverage = {item["dimension"] for item in variants if not item["compound"]}
    if coverage != set(DIMENSIONS):
        failures.append("DIMENSION_COVERAGE")

    for item in variants:
        outcome = run_one(item["record"], schema, root_lock, checker, apply_boundary_guard)
        first = outcome["first"]
        second = outcome["second"]
        final = outcome["final"]
        if first != second:
            failures.append("NONDETERMINISTIC:" + item["variant_id"])
        if first.get("decision") == "PASS":
            base_passes.append(item["variant_id"])
        if final.get("decision") == "PASS":
            final_passes.append(item["variant_id"])
            failures.append("FINAL_PASS:" + item["variant_id"])
        results.append({
            "variant_id": item["variant_id"],
            "dimension": item["dimension"],
            "compound": item["compound"],
            "base_decision": first.get("decision"),
            "final_decision": final.get("decision"),
            "deterministic": first == second,
        })

    material = {
        "version": VERSION,
        "order": "O22.4",
        "parent_commit_sha": PARENT_SHA,
        "variant_count": len(variants),
        "dimension_count": len(DIMENSIONS),
        "base_pass_count": len(base_passes),
        "base_passes": sorted(base_passes),
        "final_pass_count": len(final_passes),
        "final_passes": sorted(final_passes),
        "failures": sorted(failures),
        "results": sorted(results, key=lambda value: value["variant_id"]),
        "corpus_sha256": digest(corpus),
        "schema_sha256": digest(schema),
        "root_lock_sha256": digest(root_lock),
    }
    material["verdict"] = "CERTIFIED" if not failures else "FAILED"
    return {**material, "report_sha256": digest(material)}
