"""Audit O22.8 registry integrity."""
import copy
from promotion_artifact_registry import ENTRY_SCHEMA, ORDER, REGISTRY_SCHEMA, _hash_without, _is_sha256
from promotion_manifest_gate import canonical_sha256


def audit_registry(registry):
    before = copy.deepcopy(registry)
    failures = []
    if registry.get("schema") != REGISTRY_SCHEMA:
        failures.append("REGISTRY_SCHEMA")
    if registry.get("order") != ORDER:
        failures.append("REGISTRY_ORDER")
    entries = registry.get("entries")
    if not isinstance(entries, list):
        failures.append("ENTRIES_TYPE")
        entries = []
    prev = None
    candidates, manifests = set(), set()
    for i, entry in enumerate(entries, 1):
        p = f"ENTRY_{i}"
        if not isinstance(entry, dict):
            failures.append(p + ":TYPE")
            continue
        if entry.get("schema") != ENTRY_SCHEMA or entry.get("order") != ORDER:
            failures.append(p + ":CONTRACT")
        if entry.get("lineage_version") != i:
            failures.append(p + ":VERSION")
        if entry.get("previous_entry_sha256") != prev:
            failures.append(p + ":LINK")
        candidate = entry.get("candidate_commit_sha")
        manifest = entry.get("promotion_manifest_sha256")
        if candidate in candidates:
            failures.append(p + ":DUPLICATE_CANDIDATE")
        if manifest in manifests:
            failures.append(p + ":DUPLICATE_MANIFEST")
        candidates.add(candidate)
        manifests.add(manifest)
        digest = entry.get("entry_sha256")
        if not _is_sha256(digest) or digest != _hash_without(entry, "entry_sha256"):
            failures.append(p + ":HASH")
        prev = digest
    head = entries[-1].get("entry_sha256") if entries and isinstance(entries[-1], dict) else None
    if registry.get("head_entry_sha256") != head:
        failures.append("HEAD")
    if registry.get("next_lineage_version") != len(entries) + 1:
        failures.append("NEXT_VERSION")
    digest = registry.get("registry_sha256")
    if not _is_sha256(digest) or digest != _hash_without(registry, "registry_sha256"):
        failures.append("REGISTRY_HASH")
    result = {"gate": ORDER, "valid": not failures, "failures": sorted(set(failures)), "entry_count": len(entries), "head_entry_sha256": head, "registry_sha256": digest}
    result["audit_sha256"] = canonical_sha256(result)
    if registry != before:
        raise RuntimeError("audit mutated registry")
    return result
