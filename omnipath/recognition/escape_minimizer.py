from __future__ import annotations


def minimal_base_passes(results):
    by_case = {}
    for item in results:
        if item.get("base_decision") == "PASS":
            by_case.setdefault(item["case_id"], []).append(item)

    minimal = []
    for case_id, items in sorted(by_case.items()):
        dimension_sets = [(item, set(item["dimensions"])) for item in items]
        for item, current in dimension_sets:
            if any(other < current for _, other in dimension_sets):
                continue
            minimal.append({
                "case_id": case_id,
                "variant_id": item["variant_id"],
                "dimensions": list(item["dimensions"]),
                "width": len(item["dimensions"]),
                "base_decision": item["base_decision"],
                "final_decision": item["final_decision"],
            })
    return sorted(minimal, key=lambda item: (item["case_id"], item["width"], item["variant_id"]))
