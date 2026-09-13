"""Append and reconstruct O22.8 registry state."""
import copy
from promotion_artifact_registry import seal_registry
from promotion_registry_audit import audit_registry
from promotion_registry_entry import build_entry
from promotion_manifest_gate import canonical_sha256


def append_promotion(registry, manifest, attestation, root_lock):
    before = copy.deepcopy(registry)
    if not audit_registry(registry)["valid"]:
        raise ValueError("invalid registry")
    candidate = manifest.get("candidate_commit_sha")
    manifest_hash = manifest.get("manifest_sha256")
    for entry in registry["entries"]:
        if entry.get("candidate_commit_sha") == candidate:
            raise ValueError("candidate already registered")
        if entry.get("promotion_manifest_sha256") == manifest_hash:
            raise ValueError("manifest already registered")
    result = copy.deepcopy(registry)
    entry = build_entry(manifest, attestation, root_lock, registry["next_lineage_version"], registry["head_entry_sha256"])
    result["entries"].append(entry)
    result["head_entry_sha256"] = entry["entry_sha256"]
    result["next_lineage_version"] = entry["lineage_version"] + 1
    result = seal_registry(result)
    if not audit_registry(result)["valid"]:
        raise RuntimeError("constructed invalid registry")
    if registry != before:
        raise RuntimeError("append mutated source registry")
    return result


def reconstruct_promotion(registry, candidate_commit_sha):
    if not audit_registry(registry)["valid"]:
        raise ValueError("invalid registry")
    by_hash = {e["entry_sha256"]: e for e in registry["entries"]}
    target = next((e for e in registry["entries"] if e["candidate_commit_sha"] == candidate_commit_sha), None)
    if target is None:
        raise KeyError(candidate_commit_sha)
    chain, current = [], target
    while current is not None:
        chain.append(copy.deepcopy(current))
        previous = current["previous_entry_sha256"]
        current = by_hash.get(previous) if previous is not None else None
    return {"candidate_commit_sha": candidate_commit_sha, "entry": copy.deepcopy(target), "ancestry_to_genesis": chain, "registry_sha256": registry["registry_sha256"], "reconstruction_sha256": canonical_sha256(chain)}
