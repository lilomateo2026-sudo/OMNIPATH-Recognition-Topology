"""O22.7 Recognition Promotion Manifest Gate."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

from attestation_gate import check_attestation

MANIFEST_SCHEMA = "omnipath.o22-7-promotion-manifest/v1"
ORDER = "O22.7"
EXPECTED_EPISTEMIC_CEILING = "VERIFIED_WITHIN_SCOPE"

CANONICAL_CHECKPOINTS = {
    "O22.2": "e469b447d497f6533487fbf9098b1a6152d2d494",
    "O22.3": "12c3ff5c362ba7c8fcdd33f3c7089243e468abfc",
    "O22.4": "8875873a3eb8420a5e16a43fde285e2ca20c3423",
    "O22.5": "f8ca61a8e08723232afd8037f9eb9a639847d0b7",
    "O22.6": "ab1235e5cd90a9d327e7dca94464f35b71fdcde1",
}


def canonical_sha256(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def manifest_material(manifest: dict[str, Any]) -> dict[str, Any]:
    material = copy.deepcopy(manifest)
    material.pop("manifest_sha256", None)
    material.pop("promotion_status", None)
    return material


def seal_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    sealed = copy.deepcopy(manifest)
    sealed.pop("promotion_status", None)
    sealed["manifest_sha256"] = canonical_sha256(manifest_material(sealed))
    return sealed


def _is_hex(value: Any, length: int) -> bool:
    if not isinstance(value, str) or len(value) != length:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True


def evaluate_promotion(
    manifest: dict[str, Any],
    attestation: dict[str, Any],
    root_lock: dict[str, Any],
) -> dict[str, Any]:
    """Derive PROMOTABLE/BLOCKED from frozen evidence without mutation."""
    original_manifest = copy.deepcopy(manifest)
    original_attestation = copy.deepcopy(attestation)
    failures: list[str] = []

    if manifest.get("schema") != MANIFEST_SCHEMA:
        failures.append("MANIFEST_SCHEMA")
    if manifest.get("order") != ORDER:
        failures.append("MANIFEST_ORDER")
    if not isinstance(manifest.get("candidate_id"), str) or not manifest.get("candidate_id"):
        failures.append("CANDIDATE_ID")

    candidate = manifest.get("candidate_commit_sha")
    parent = manifest.get("parent_commit_sha")
    rollback = manifest.get("rollback_commit_sha")
    if not _is_hex(candidate, 40):
        failures.append("CANDIDATE_COMMIT_SHA")
    if not _is_hex(parent, 40):
        failures.append("PARENT_COMMIT_SHA")
    if not _is_hex(rollback, 40):
        failures.append("ROLLBACK_COMMIT_SHA")
    if _is_hex(candidate, 40) and candidate == parent:
        failures.append("CANDIDATE_EQUALS_PARENT")
    if _is_hex(parent, 40) and rollback != parent:
        failures.append("ROLLBACK_NOT_PARENT")

    root = root_lock.get("constitutional_root", {})
    expected_root = root.get("commit_sha")
    if root.get("root_order") != "O21.3":
        failures.append("ROOT_ORDER")
    if root_lock.get("order") != "O21.4" or root_lock.get("status") != "FROZEN":
        failures.append("ROOT_NOT_FROZEN")
    if manifest.get("constitutional_root_sha") != expected_root:
        failures.append("CONSTITUTIONAL_ROOT_SHA")
    if manifest.get("epistemic_ceiling") != root_lock.get("epistemic_ceiling"):
        failures.append("EPISTEMIC_CEILING")
    if manifest.get("epistemic_ceiling") != EXPECTED_EPISTEMIC_CEILING:
        failures.append("EPISTEMIC_CEILING_VALUE")

    if manifest.get("checkpoint_commits") != CANONICAL_CHECKPOINTS:
        failures.append("CHECKPOINT_LINEAGE")
    if manifest.get("independent_attestation_required") is not True:
        failures.append("INDEPENDENT_ATTESTATION_DISABLED")
    if manifest.get("candidate_self_promoted") is not False:
        failures.append("SELF_PROMOTION_FORBIDDEN")
    if manifest.get("unresolved_contradictions") != 0:
        failures.append("UNRESOLVED_CONTRADICTIONS")
    if manifest.get("unresolved_escape_specimens") != 0:
        failures.append("UNRESOLVED_ESCAPE_SPECIMENS")

    expected_attestation_hash = canonical_sha256(attestation)
    if manifest.get("o22_6_attestation_sha256") != expected_attestation_hash:
        failures.append("O22_6_ATTESTATION_HASH")

    attestation_result = check_attestation(
        attestation, candidate if _is_hex(candidate, 40) else None
    )
    if not attestation_result["promotion_allowed"]:
        failures.extend(
            f"O22_6:{failure}" for failure in attestation_result["failures"]
        )

    expected_manifest_hash = canonical_sha256(manifest_material(manifest))
    supplied_manifest_hash = manifest.get("manifest_sha256")
    if not _is_hex(supplied_manifest_hash, 64):
        failures.append("MANIFEST_SHA256")
    elif supplied_manifest_hash != expected_manifest_hash:
        failures.append("MANIFEST_HASH_MISMATCH")

    if "promotion_status" in manifest:
        failures.append("SELF_ASSERTED_PROMOTION_STATUS")

    failures = sorted(set(failures))
    result = {
        "gate": ORDER,
        "candidate_id": manifest.get("candidate_id"),
        "candidate_commit_sha": candidate,
        "promotion_status": "PROMOTABLE" if not failures else "BLOCKED",
        "promotion_allowed": not failures,
        "failures": failures,
        "manifest_sha256": supplied_manifest_hash,
        "o22_6_attestation_sha256": expected_attestation_hash,
        "constitutional_root_sha": expected_root,
        "rollback_commit_sha": rollback,
    }
    result["decision_sha256"] = canonical_sha256(result)

    if manifest != original_manifest:
        raise RuntimeError("O22.7 mutated the promotion manifest")
    if attestation != original_attestation:
        raise RuntimeError("O22.7 mutated the O22.6 attestation")
    return result
