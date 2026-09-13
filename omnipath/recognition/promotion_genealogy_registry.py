"""Mandatory O27.6 cross-link gate layered over the frozen O22.8 registry."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from promotion_artifact_registry import _is_sha256, seal_entry, seal_registry
from promotion_manifest_gate import canonical_sha256, manifest_material
from promotion_registry_audit import audit_registry
from promotion_registry_store import append_promotion
from promotion_genealogy_common import CROSS_LINK_FIELDS, ORDER, read_json, safe_ref
from promotion_ledger_verifier import verify_durable_ledger


def audit_genealogy_registry(registry: dict[str, Any]) -> dict[str, Any]:
    base = audit_registry(registry)
    failures = [] if base.get("valid") else [f"O22.8:{x}" for x in base.get("failures", [])]
    entries = registry.get("entries") if isinstance(registry.get("entries"), list) else []
    for index, entry in enumerate(entries, 1):
        prefix = f"ENTRY_{index}"
        if not isinstance(entry, dict):
            failures.append(prefix + ":TYPE")
            continue
        for field in CROSS_LINK_FIELDS:
            if field not in entry:
                failures.append(prefix + f":MISSING:{field}")
        if entry.get("genealogy_contract_order") != ORDER:
            failures.append(prefix + ":GENEALOGY_ORDER")
        if not _is_sha256(entry.get("durable_evidence_record_set_sha256")):
            failures.append(prefix + ":RECORD_SET_SHA256")
        if entry.get("durable_evidence_source_commit_sha") != entry.get("candidate_commit_sha"):
            failures.append(prefix + ":SOURCE_COMMIT")
        for field in ("promotion_manifest_ref", "durable_evidence_ledger_ref"):
            value = entry.get(field)
            if not isinstance(value, str) or not value or Path(value).is_absolute() or ".." in Path(value).parts:
                failures.append(prefix + f":REF:{field}")
    failures = sorted(set(failures))
    result = {
        "gate": ORDER,
        "valid": not failures,
        "failures": failures,
        "entry_count": len(entries),
        "head_entry_sha256": registry.get("head_entry_sha256"),
        "registry_sha256": registry.get("registry_sha256"),
    }
    result["audit_sha256"] = canonical_sha256(result)
    return result


def bind_latest_entry_to_ledger(
    registry: dict[str, Any],
    repository_root: Path | str,
    ledger_ref: str,
    promotion_manifest_ref: str,
) -> dict[str, Any]:
    if not audit_registry(registry).get("valid"):
        raise ValueError("invalid O22.8 registry")
    if not registry.get("entries"):
        raise ValueError("registry has no entry to bind")

    root = Path(repository_root)
    ledger = verify_durable_ledger(root, ledger_ref)
    if not ledger.get("valid"):
        raise ValueError("durable ledger did not verify")

    manifest = read_json(safe_ref(root, promotion_manifest_ref))
    latest = registry["entries"][-1]
    candidate = latest.get("candidate_commit_sha")
    if ledger.get("source_commit") != candidate:
        raise ValueError("ledger source commit does not match candidate")
    if manifest.get("candidate_commit_sha") != candidate:
        raise ValueError("promotion manifest candidate mismatch")
    supplied = manifest.get("manifest_sha256")
    if supplied != latest.get("promotion_manifest_sha256"):
        raise ValueError("promotion manifest hash mismatch")
    if canonical_sha256(manifest_material(manifest)) != supplied:
        raise ValueError("promotion manifest seal mismatch")
    if ledger.get("o22_6_attestation_sha256") != latest.get("o22_6_attestation_sha256"):
        raise ValueError("attestation hash mismatch")

    result = copy.deepcopy(registry)
    entry = copy.deepcopy(result["entries"][-1])
    entry.update({
        "genealogy_contract_order": ORDER,
        "promotion_manifest_ref": promotion_manifest_ref,
        "durable_evidence_ledger_ref": ledger_ref,
        "durable_evidence_record_set_sha256": ledger["record_set_sha256"],
        "durable_evidence_source_commit_sha": ledger["source_commit"],
    })
    entry = seal_entry(entry)
    result["entries"][-1] = entry
    result["head_entry_sha256"] = entry["entry_sha256"]
    result = seal_registry(result)
    audit = audit_genealogy_registry(result)
    if not audit["valid"]:
        raise RuntimeError("constructed nonconformant genealogy registry")
    return result


def append_cross_linked_promotion(
    registry: dict[str, Any],
    manifest: dict[str, Any],
    attestation: dict[str, Any],
    root_lock: dict[str, Any],
    repository_root: Path | str,
    ledger_ref: str,
    promotion_manifest_ref: str,
) -> dict[str, Any]:
    appended = append_promotion(registry, manifest, attestation, root_lock)
    return bind_latest_entry_to_ledger(appended, repository_root, ledger_ref, promotion_manifest_ref)
