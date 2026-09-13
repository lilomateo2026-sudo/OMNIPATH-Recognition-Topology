"""Verify O22.8A-style durable evidence for O27.6 genealogy."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from attestation_gate import check_attestation
from promotion_manifest_gate import canonical_sha256
from promotion_genealogy_common import (
    LEDGER_INDEX_SCHEMA,
    LEDGER_MANIFEST_SCHEMA,
    ORDER,
    is_git_sha,
    read_json,
    safe_ref,
    sealed_record_set_sha256,
    sha256_bytes,
)


def verify_durable_ledger(repository_root: Path | str, ledger_ref: str) -> dict[str, Any]:
    root = Path(repository_root)
    ledger_dir = safe_ref(root, ledger_ref)
    failures: list[str] = []
    if not ledger_dir.is_dir():
        return {"gate": ORDER, "valid": False, "failures": ["LEDGER_REF_NOT_DIRECTORY"], "ledger_ref": ledger_ref}

    try:
        manifest = read_json(ledger_dir / "promotion_manifest.json")
    except (OSError, ValueError, json.JSONDecodeError):
        return {"gate": ORDER, "valid": False, "failures": ["LEDGER_MANIFEST_UNREADABLE"], "ledger_ref": ledger_ref}

    if manifest.get("schema") != LEDGER_MANIFEST_SCHEMA:
        failures.append("LEDGER_MANIFEST_SCHEMA")
    record_set = manifest.get("record_set_sha256")
    if not isinstance(record_set, str) or len(record_set) != 64:
        failures.append("RECORD_SET_SHA256")
    elif sealed_record_set_sha256(manifest) != record_set:
        failures.append("RECORD_SET_HASH_MISMATCH")

    source_commit = manifest.get("source_commit")
    if not is_git_sha(source_commit):
        failures.append("LEDGER_SOURCE_COMMIT")

    components = manifest.get("components")
    if not isinstance(components, dict) or not components:
        failures.append("LEDGER_COMPONENTS")
        components = {}

    required = {
        "index.json", "ci_attestation.json", "replay_manifest.json",
        "o22_5_report.json", "specimen_hashes.json",
        "checkpoint_lineage.json", "promotion_record.json",
    }
    for name in sorted(required.difference(components)):
        failures.append(f"LEDGER_COMPONENT_MISSING:{name}")

    for name, expected in sorted(components.items()):
        if not isinstance(name, str) or Path(name).name != name or not isinstance(expected, str) or len(expected) != 64:
            failures.append(f"LEDGER_COMPONENT_DECLARATION:{name}")
            continue
        try:
            actual = sha256_bytes((ledger_dir / name).read_bytes())
        except OSError:
            failures.append(f"LEDGER_COMPONENT_UNREADABLE:{name}")
            continue
        if actual != expected:
            failures.append(f"LEDGER_COMPONENT_HASH:{name}")

    def load(name: str) -> dict[str, Any]:
        try:
            return read_json(ledger_dir / name)
        except (OSError, ValueError, json.JSONDecodeError):
            failures.append(f"LEDGER_JSON_UNREADABLE:{name}")
            return {}

    index = load("index.json")
    attestation = load("ci_attestation.json")
    replay = load("replay_manifest.json")
    specimen_hashes = load("specimen_hashes.json")
    lineage = load("checkpoint_lineage.json")
    promotion_record = load("promotion_record.json")

    if index.get("schema") != LEDGER_INDEX_SCHEMA:
        failures.append("LEDGER_INDEX_SCHEMA")
    if index.get("source_commit") != source_commit:
        failures.append("LEDGER_INDEX_SOURCE_COMMIT")
    if index.get("recorded_epistemic_state") != "VERIFIED_WITHIN_SCOPE":
        failures.append("LEDGER_EPISTEMIC_STATE")
    if index.get("workflow_conclusion") != "success":
        failures.append("LEDGER_WORKFLOW_CONCLUSION")

    attestation_result = check_attestation(attestation, source_commit if is_git_sha(source_commit) else None)
    if not attestation_result.get("promotion_allowed"):
        failures.extend(f"ATTESTATION:{x}" for x in attestation_result.get("failures", []))

    if replay.get("replay_status") != "VERIFIED":
        failures.append("REPLAY_STATUS")
    if replay.get("variant_count") != 378:
        failures.append("REPLAY_VARIANT_COUNT")
    if replay.get("cross_product_variant_count") != 342:
        failures.append("REPLAY_CROSS_PRODUCT_COUNT")
    if replay.get("final_pass_count") != 0:
        failures.append("REPLAY_FINAL_PASS_COUNT")

    hashes = specimen_hashes if isinstance(specimen_hashes, dict) else {}
    if len(hashes) != 4:
        failures.append("SPECIMEN_HASH_COUNT")
    for name, digest in sorted(hashes.items()):
        if not isinstance(name, str) or not isinstance(digest, str) or len(digest) != 64:
            failures.append(f"SPECIMEN_HASH:{name}")
    if attestation.get("specimen_sha256") != hashes:
        failures.append("ATTESTATION_SPECIMEN_HASHES")
    if replay.get("specimen_sha256") != hashes:
        failures.append("REPLAY_SPECIMEN_HASHES")

    try:
        report_hash = sha256_bytes((ledger_dir / "o22_5_report.json").read_bytes())
        replay_hash = sha256_bytes((ledger_dir / "replay_manifest.json").read_bytes())
    except OSError:
        report_hash = replay_hash = ""
    if replay.get("o22_5_report_sha256") != report_hash:
        failures.append("REPLAY_REPORT_HASH")
    if attestation.get("o22_5_report_sha256") != report_hash:
        failures.append("ATTESTATION_REPORT_HASH")
    if attestation.get("replay_manifest_sha256") != replay_hash:
        failures.append("ATTESTATION_REPLAY_HASH")

    constitutional_root = lineage.get("O21.3")
    if not is_git_sha(constitutional_root):
        failures.append("LEDGER_CONSTITUTIONAL_ROOT")
    if promotion_record.get("recorded_promotion_allowed") is not True:
        failures.append("RECORDED_PROMOTION_NOT_ALLOWED")
    if promotion_record.get("candidate_self_promoted") is not False:
        failures.append("RECORDED_SELF_PROMOTION")
    if promotion_record.get("recorded_epistemic_state") != "VERIFIED_WITHIN_SCOPE":
        failures.append("RECORDED_EPISTEMIC_STATE")

    failures = sorted(set(failures))
    result = {
        "gate": ORDER,
        "valid": not failures,
        "failures": failures,
        "ledger_ref": ledger_ref,
        "record_set_sha256": record_set,
        "source_commit": source_commit,
        "constitutional_root_sha": constitutional_root,
        "specimen_sha256": copy.deepcopy(hashes),
        "replay_manifest_sha256": replay_hash,
        "o22_5_report_sha256": report_hash,
        "o22_6_attestation_sha256": canonical_sha256(attestation) if attestation else None,
    }
    result["verification_sha256"] = canonical_sha256(result)
    return result
