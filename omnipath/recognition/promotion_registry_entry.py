"""Construct one O22.8 registry entry from O22.7 evidence."""
import copy
from promotion_artifact_registry import ACCEPTING_GATE, ENTRY_SCHEMA, ORDER, _is_sha256, seal_entry
from promotion_manifest_gate import evaluate_promotion


def build_entry(manifest, attestation, root_lock, version, previous_hash):
    decision = evaluate_promotion(manifest, attestation, root_lock)
    if decision.get("promotion_status") != "PROMOTABLE" or not decision.get("promotion_allowed"):
        raise ValueError("promotion not accepted")
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        raise ValueError("invalid version")
    if previous_hash is not None and not _is_sha256(previous_hash):
        raise ValueError("invalid previous hash")
    entry = {
        "schema": ENTRY_SCHEMA, "order": ORDER, "accepted_by_gate": ACCEPTING_GATE,
        "lineage_version": version, "candidate_id": manifest["candidate_id"],
        "candidate_commit_sha": manifest["candidate_commit_sha"],
        "parent_commit_sha": manifest["parent_commit_sha"],
        "rollback_commit_sha": manifest["rollback_commit_sha"],
        "constitutional_root_sha": manifest["constitutional_root_sha"],
        "checkpoint_commits": copy.deepcopy(manifest["checkpoint_commits"]),
        "promotion_manifest_sha256": manifest["manifest_sha256"],
        "promotion_decision_sha256": decision["decision_sha256"],
        "o22_6_attestation_sha256": decision["o22_6_attestation_sha256"],
        "o22_6_workflow_run_id": attestation["workflow_run_id"],
        "o22_6_replay_artifact_id": attestation["replay_artifact_id"],
        "o22_6_replay_artifact_digest": attestation["replay_artifact_digest"],
        "previous_entry_sha256": previous_hash,
    }
    return seal_entry(entry)
