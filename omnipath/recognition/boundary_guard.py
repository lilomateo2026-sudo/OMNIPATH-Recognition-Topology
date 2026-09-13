from tribunal_contract import REQUIRED_PATHOLOGIES

GUARD_REASON = "O22_4_BOUNDARY_HOLD"


def apply_boundary_guard(record, base_result):
    decision = base_result.get("decision")
    reasons = []
    if decision == "PASS" and record.get("pathology_type") in REQUIRED_PATHOLOGIES:
        decision = "QUARANTINE"
        reasons.append(GUARD_REASON)
    return {
        "decision": decision,
        "guard_reasons": reasons,
        "base_decision": base_result.get("decision"),
    }
