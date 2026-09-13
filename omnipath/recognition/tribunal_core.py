from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

from tribunal_contract import ALLOWED_CORRUPTED_DECISIONS, PARENT_SHA, REQUIRED_PATHOLOGIES, VERSION


def digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def run_cases(corpus, schema, root_lock, validate_pathology):
    failures = []
    results = []
    counts = {"PASS": 0, "QUARANTINE": 0, "REJECT": 0}
    original = copy.deepcopy(corpus)

    if corpus.get("order") != "O22.3":
        failures.append("ORDER_MISMATCH")
    if corpus.get("parent_commit_sha") != PARENT_SHA:
        failures.append("PARENT_MISMATCH")
    if corpus.get("corrupted_case_must_never_pass") is not True:
        failures.append("POLICY_MISSING")

    cases = corpus.get("cases", [])
    present = {c.get("record", {}).get("pathology_type") for c in cases if isinstance(c, dict)}
    for item in sorted(REQUIRED_PATHOLOGIES - present):
        failures.append("MISSING:" + item)

    seen = set()
    for case in cases:
        case_id = case.get("case_id")
        if not case_id or case_id in seen:
            failures.append("BAD_CASE_ID:" + str(case_id))
            continue
        seen.add(case_id)
        record = case.get("record")
        if not isinstance(record, dict):
            failures.append("BAD_RECORD:" + case_id)
            continue

        before = copy.deepcopy(record)
        first = validate_pathology(record, schema, root_lock)
        second = validate_pathology(record, schema, root_lock)
        decision = first.get("decision")

        if first != second:
            failures.append("NONDETERMINISTIC:" + case_id)
        if record != before:
            failures.append("INPUT_CHANGED:" + case_id)
        if decision in counts:
            counts[decision] += 1
        else:
            failures.append("UNKNOWN_DECISION:" + case_id)
        if case.get("corruption_expected") is True and decision not in ALLOWED_CORRUPTED_DECISIONS:
            failures.append("UNSAFE_PASS:" + case_id)
        if decision != case.get("expected_decision"):
            failures.append("DECISION_MISMATCH:" + case_id)

        reasons = [x.get("code") for x in first.get("reasons", [])]
        for code in case.get("expected_reason_codes", []):
            if code not in reasons:
                failures.append("MISSING_REASON:" + case_id + ":" + code)

        contradictions = before.get("contradictions", [])
        preserved = first.get("preserved_contradictions", [])
        if contradictions != preserved:
            failures.append("CONTRADICTION_CHANGED:" + case_id)

        results.append({
            "case_id": case_id,
            "pathology_type": before.get("pathology_type"),
            "decision": decision,
            "deterministic": first == second,
            "contradictions_preserved": contradictions == preserved,
        })

    if corpus != original:
        failures.append("CORPUS_CHANGED")
    failures = sorted(failures)
    results = sorted(results, key=lambda x: x["case_id"])
    verdict = "CERTIFIED" if not failures else "FAILED"
    material = {"version": VERSION, "verdict": verdict, "counts": counts, "results": results, "failures": failures, "corpus_sha256": digest(original), "schema_sha256": digest(schema), "root_lock_sha256": digest(root_lock)}
    return {**material, "report_sha256": digest(material)}
