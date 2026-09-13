"""O27.7 candidate-only promotion genealogy resolver."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from promotion_genealogy_common import is_git_sha, read_json, safe_ref
from promotion_genealogy_index import ORDER, verify_genealogy_index
from promotion_genealogy_tribunal import reconstruct_promotion_genealogy
from promotion_manifest_gate import canonical_sha256

DEFAULT_INDEX_REF = "omnipath/recognition/promotion_genealogy/index.json"
ROOT_LOCK_REF = "omnipath/recognition/CONSTITUTIONAL_ROOT.lock.json"
RESOLUTION_SCHEMA = "omnipath.promotion-genealogy-resolution/v1"


def _registry_entry(registry: dict[str, Any], entry_sha256: str | None) -> dict[str, Any] | None:
    if not isinstance(entry_sha256, str):
        return None
    entries = registry.get("entries") if isinstance(registry.get("entries"), list) else []
    for entry in entries:
        if isinstance(entry, dict) and entry.get("entry_sha256") == entry_sha256:
            return copy.deepcopy(entry)
    return None


def resolve_candidate(
    repository_root: Path | str,
    candidate_sha: str,
    index_ref: str = DEFAULT_INDEX_REF,
) -> dict[str, Any]:
    if not is_git_sha(candidate_sha):
        raise ValueError("candidate SHA must be a 40-character Git SHA")
    root = Path(repository_root).resolve()
    index = read_json(safe_ref(root, index_ref))
    verification = verify_genealogy_index(root, index)
    if not verification["valid"]:
        raise ValueError("committed genealogy index is not current")

    entry_id = index.get("alias_map", {}).get(candidate_sha)
    if not isinstance(entry_id, str):
        raise KeyError(candidate_sha)
    entries = index.get("entries") if isinstance(index.get("entries"), list) else []
    entry = next((value for value in entries if isinstance(value, dict) and value.get("entry_id") == entry_id), None)
    if entry is None:
        raise ValueError("genealogy index alias points to no entry")

    ledger = read_json(safe_ref(root, entry["ledger_ref"]))
    manifest = None
    manifest_ref = entry.get("promotion_manifest_ref")
    if isinstance(manifest_ref, str):
        manifest = read_json(safe_ref(root, manifest_ref))

    registry = read_json(safe_ref(root, entry["registry_ref"]))
    registry_entry = _registry_entry(registry, entry.get("registry_entry_sha256"))
    tribunal = None
    if registry_entry is not None:
        tribunal = reconstruct_promotion_genealogy(registry, entry["candidate_commit_sha"], root)

    root_lock = read_json(safe_ref(root, ROOT_LOCK_REF))
    constitutional_root = root_lock.get("constitutional_root", {}).get("commit_sha")

    result = {
        "schema": RESOLUTION_SCHEMA,
        "order": ORDER,
        "query_sha": candidate_sha,
        "matched_entry_id": entry_id,
        "canonical_candidate_sha": entry["candidate_commit_sha"],
        "promoted_main_sha": entry["promoted_main_sha"],
        "aliases": copy.deepcopy(entry["aliases"]),
        "generation_order": entry["generation_order"],
        "ledger_order": entry["ledger_order"],
        "ledger_ref": entry["ledger_ref"],
        "promotion_manifest_ref": manifest_ref,
        "registry_ref": entry["registry_ref"],
        "registry_entry_sha256": entry.get("registry_entry_sha256"),
        "epistemic_state": entry.get("epistemic_state"),
        "postmerge_workflow_run_id": entry.get("postmerge_workflow_run_id"),
        "constitutional_root_sha": constitutional_root,
        "ledger_record": ledger,
        "promotion_manifest": manifest,
        "registry_entry": registry_entry,
        "retention_proof_tribunal": tribunal,
        "index_sha256": index["index_sha256"],
    }
    result["resolution_sha256"] = canonical_sha256(result)
    return result
