"""O27.6 retention-proof promotion reconstruction tribunal."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from promotion_manifest_gate import canonical_sha256, manifest_material
from promotion_registry_store import reconstruct_promotion
from promotion_genealogy_common import GENEALOGY_SCHEMA, ORDER, read_json, safe_ref, sha256_bytes
from promotion_genealogy_registry import audit_genealogy_registry
from promotion_ledger_verifier import verify_durable_ledger


def reconstruct_promotion_genealogy(
    registry: dict[str, Any],
    candidate_commit_sha: str,
    repository_root: Path | str,
) -> dict[str, Any]:
    failures: list[str] = []
    audit = audit_genealogy_registry(registry)
    if not audit["valid"]:
        failures.extend(audit["failures"])

    try:
        base = reconstruct_promotion(registry, candidate_commit_sha)
        entry = base["entry"]
    except (KeyError, ValueError) as exc:
        result = {
            "schema": GENEALOGY_SCHEMA,
            "order": ORDER,
            "candidate_commit_sha": candidate_commit_sha,
            "verified": False,
            "failures": sorted(set(failures + [f"REGISTRY_LOOKUP:{type(exc).__name__}"])),
        }
        result["reconstruction_sha256"] = canonical_sha256(result)
        return result

    root = Path(repository_root)
    manifest: dict[str, Any] = {}
    try:
        manifest = read_json(safe_ref(root, entry["promotion_manifest_ref"]))
    except (KeyError, OSError, ValueError, json.JSONDecodeError):
        failures.append("PROMOTION_MANIFEST_UNREADABLE")

    if manifest:
        expected = entry.get("promotion_manifest_sha256")
        if manifest.get("candidate_commit_sha") != candidate_commit_sha:
            failures.append("PROMOTION_MANIFEST_CANDIDATE")
        if manifest.get("manifest_sha256") != expected:
            failures.append("PROMOTION_MANIFEST_HASH")
        elif canonical_sha256(manifest_material(manifest)) != expected:
            failures.append("PROMOTION_MANIFEST_SEAL")

    ledger_ref = entry.get("durable_evidence_ledger_ref")
    ledger = verify_durable_ledger(root, ledger_ref) if isinstance(ledger_ref, str) else {"valid": False, "failures": ["LEDGER_REF"]}
    if not ledger.get("valid"):
        failures.extend(f"LEDGER:{x}" for x in ledger.get("failures", []))
    if ledger.get("record_set_sha256") != entry.get("durable_evidence_record_set_sha256"):
        failures.append("LEDGER_RECORD_SET_CROSSLINK")
    if ledger.get("source_commit") != candidate_commit_sha:
        failures.append("LEDGER_SOURCE_COMMIT_CROSSLINK")
    if ledger.get("o22_6_attestation_sha256") != entry.get("o22_6_attestation_sha256"):
        failures.append("LEDGER_ATTESTATION_CROSSLINK")

    try:
        root_lock = read_json(root / "omnipath/recognition/CONSTITUTIONAL_ROOT.lock.json")
    except (OSError, ValueError, json.JSONDecodeError):
        root_lock = {}
        failures.append("CONSTITUTIONAL_ROOT_UNREADABLE")
    constitutional_root = root_lock.get("constitutional_root", {}).get("commit_sha")
    if constitutional_root != entry.get("constitutional_root_sha"):
        failures.append("REGISTRY_CONSTITUTIONAL_ROOT")
    if constitutional_root != ledger.get("constitutional_root_sha"):
        failures.append("LEDGER_CONSTITUTIONAL_ROOT_CROSSLINK")

    specimen_hashes = ledger.get("specimen_sha256")
    if isinstance(specimen_hashes, dict):
        for name, expected in sorted(specimen_hashes.items()):
            ref = f"omnipath/recognition/regression/o22_5/{name}"
            try:
                actual = sha256_bytes(safe_ref(root, ref).read_bytes())
            except (OSError, ValueError):
                failures.append(f"SPECIMEN_UNREADABLE:{name}")
                continue
            if actual != expected:
                failures.append(f"SPECIMEN_HASH:{name}")

    failures = sorted(set(failures))
    result = {
        "schema": GENEALOGY_SCHEMA,
        "order": ORDER,
        "candidate_commit_sha": candidate_commit_sha,
        "verified": not failures,
        "failures": failures,
        "path": {
            "registry_entry_sha256": entry.get("entry_sha256"),
            "promotion_manifest_sha256": entry.get("promotion_manifest_sha256"),
            "durable_evidence_record_set_sha256": entry.get("durable_evidence_record_set_sha256"),
            "o22_6_replay_manifest_sha256": ledger.get("replay_manifest_sha256"),
            "specimen_sha256": copy.deepcopy(specimen_hashes),
            "constitutional_root_sha": constitutional_root,
        },
        "registry_ancestry_to_genesis": base.get("ancestry_to_genesis"),
        "registry_sha256": base.get("registry_sha256"),
    }
    result["reconstruction_sha256"] = canonical_sha256(result)
    return result
