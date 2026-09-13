"""O22.8 append-only Promotion Artifact Registry."""

from __future__ import annotations

import copy
from typing import Any

from promotion_manifest_gate import canonical_sha256

REGISTRY_SCHEMA = "omnipath.o22-8-promotion-artifact-registry/v1"
ENTRY_SCHEMA = "omnipath.o22-8-promotion-artifact/v1"
ORDER = "O22.8"
ACCEPTING_GATE = "O22.7"
REQUIRED_ENTRY_FIELDS = (
    "schema", "order", "accepted_by_gate", "lineage_version", "candidate_id",
    "candidate_commit_sha", "parent_commit_sha", "rollback_commit_sha",
    "constitutional_root_sha", "checkpoint_commits", "promotion_manifest_sha256",
    "promotion_decision_sha256", "o22_6_attestation_sha256", "o22_6_workflow_run_id",
    "o22_6_replay_artifact_id", "o22_6_replay_artifact_digest",
    "previous_entry_sha256", "entry_sha256",
)


def _hash_without(value: dict[str, Any], key: str) -> str:
    material = copy.deepcopy(value)
    material.pop(key, None)
    return canonical_sha256(material)


def empty_registry() -> dict[str, Any]:
    registry = {
        "schema": REGISTRY_SCHEMA,
        "order": ORDER,
        "entries": [],
        "head_entry_sha256": None,
        "next_lineage_version": 1,
    }
    registry["registry_sha256"] = _hash_without(registry, "registry_sha256")
    return registry


def seal_entry(entry: dict[str, Any]) -> dict[str, Any]:
    sealed = copy.deepcopy(entry)
    sealed.pop("entry_sha256", None)
    sealed["entry_sha256"] = canonical_sha256(sealed)
    return sealed


def seal_registry(registry: dict[str, Any]) -> dict[str, Any]:
    sealed = copy.deepcopy(registry)
    sealed.pop("registry_sha256", None)
    sealed["registry_sha256"] = canonical_sha256(sealed)
    return sealed


def _is_sha256(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True
