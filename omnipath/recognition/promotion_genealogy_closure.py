"""O29.6 genealogy closure and missing-evidence tribunal."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from promotion_genealogy_common import is_git_sha, read_json, safe_ref
from promotion_genealogy_index import (
    SOURCE_ROOT,
    generate_genealogy_index,
    verify_genealogy_index,
)
from promotion_manifest_gate import canonical_sha256

ORDER = "O29.6"
CLOSURE_SCHEMA = "omnipath.genealogy-closure-tribunal/v1"
GAP_SCHEMA = "omnipath.legacy-evidence-gap/v1"
GAP_REGISTRY_SCHEMA = "omnipath.legacy-evidence-gap-registry/v1"
INDEX_REF = "omnipath/recognition/promotion_genealogy/index.json"
GAP_REGISTRY_REF = "omnipath/recognition/promotion_genealogy/legacy_evidence_gaps.json"


def _without(value: dict[str, Any], field: str) -> dict[str, Any]:
    result = copy.deepcopy(value)
    result.pop(field, None)
    return result


def _verify_gap_registry(gaps: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if gaps.get("schema") != GAP_REGISTRY_SCHEMA:
        failures.append("GAP_REGISTRY_SCHEMA")
    if gaps.get("order") != ORDER:
        failures.append("GAP_REGISTRY_ORDER")
    if gaps.get("manifest_sha256") != canonical_sha256(_without(gaps, "manifest_sha256")):
        failures.append("GAP_REGISTRY_SEAL")
    records = gaps.get("gaps")
    if not isinstance(records, list):
        return failures + ["GAP_REGISTRY_RECORDS"]
    seen: set[str] = set()
    for position, gap in enumerate(records, 1):
        prefix = f"GAP_{position}"
        if not isinstance(gap, dict):
            failures.append(prefix + ":TYPE")
            continue
        gap_id = gap.get("gap_id")
        if not isinstance(gap_id, str) or not gap_id:
            failures.append(prefix + ":ID")
        elif gap_id in seen:
            failures.append(prefix + ":DUPLICATE_ID")
        else:
            seen.add(gap_id)
        if gap.get("schema") != GAP_SCHEMA:
            failures.append(prefix + ":SCHEMA")
        if gap.get("classification") != "LEGACY_MISSING_REPOSITORY_PATH":
            failures.append(prefix + ":CLASSIFICATION")
        if gap.get("expected_current_state") != "ABSENT":
            failures.append(prefix + ":EXPECTED_STATE")
        if gap.get("gap_sha256") != canonical_sha256(_without(gap, "gap_sha256")):
            failures.append(prefix + ":SEAL")
    return failures


def _ledger_manifest_declaration(ledger: dict[str, Any]) -> dict[str, Any] | None:
    value = ledger.get("promotion_manifest")
    if not isinstance(value, dict):
        return None
    path = value.get("path")
    if not isinstance(path, str) or not path:
        return None
    return {
        "path": path,
        "commit": value.get("commit"),
        "blob_sha": value.get("blob_sha"),
    }


def audit_genealogy_closure(
    repository_root: Path | str,
    committed_index: dict[str, Any] | None = None,
    gap_registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    failures: list[str] = []

    if committed_index is None:
        committed_index = read_json(safe_ref(root, INDEX_REF))
    if gap_registry is None:
        gap_registry = read_json(safe_ref(root, GAP_REGISTRY_REF))

    index_verification = verify_genealogy_index(root, committed_index)
    if not index_verification.get("valid"):
        failures.extend(f"INDEX:{item}" for item in index_verification.get("failures", []))
    failures.extend(_verify_gap_registry(gap_registry))

    entries = committed_index.get("entries") if isinstance(committed_index.get("entries"), list) else []
    ledger_source = safe_ref(root, SOURCE_ROOT)
    actual_ledger_paths = sorted(
        path.relative_to(root).as_posix() for path in ledger_source.glob("*/index.json") if path.is_file()
    )
    indexed_ledger_refs = [entry.get("ledger_ref") for entry in entries if isinstance(entry, dict)]

    if committed_index.get("entry_count") != len(entries):
        failures.append("INDEX_ENTRY_COUNT")
    if len(indexed_ledger_refs) != len(set(indexed_ledger_refs)):
        failures.append("DUPLICATE_LEDGER_REF")

    actual_set = set(actual_ledger_paths)
    indexed_set = {value for value in indexed_ledger_refs if isinstance(value, str)}
    for ref in sorted(actual_set - indexed_set):
        failures.append("ORPHAN_LEDGER:" + ref)
    for ref in sorted(indexed_set - actual_set):
        failures.append("STALE_INDEX_LEDGER:" + ref)

    entry_ids: set[str] = set()
    alias_owner: dict[str, str] = {}
    promoted_with_evidence = 0
    for position, entry in enumerate(entries, 1):
        prefix = f"ENTRY_{position}"
        if not isinstance(entry, dict):
            failures.append(prefix + ":TYPE")
            continue
        entry_id = entry.get("entry_id")
        if not isinstance(entry_id, str) or not entry_id:
            failures.append(prefix + ":ID")
        elif entry_id in entry_ids:
            failures.append(prefix + ":DUPLICATE_ID")
        else:
            entry_ids.add(entry_id)
        promoted = entry.get("promoted_main_sha")
        aliases = entry.get("aliases") if isinstance(entry.get("aliases"), list) else []
        if not is_git_sha(promoted):
            failures.append(prefix + ":PROMOTED_SHA")
        elif promoted not in aliases:
            failures.append(prefix + ":PROMOTED_ALIAS")
        ledger_ref = entry.get("ledger_ref")
        if isinstance(ledger_ref, str) and ledger_ref in actual_set and is_git_sha(promoted):
            promoted_with_evidence += 1
        else:
            failures.append(prefix + ":PROMOTED_WITHOUT_LEDGER")
        for alias in aliases:
            if not is_git_sha(alias):
                failures.append(prefix + ":ALIAS_SHA")
                continue
            previous = alias_owner.get(alias)
            if previous is not None and previous != entry_id:
                failures.append("AMBIGUOUS_ALIAS:" + alias)
            else:
                alias_owner[alias] = str(entry_id)
        for ref_field in ("ledger_ref", "registry_ref", "promotion_manifest_ref"):
            ref = entry.get(ref_field)
            if ref is None and ref_field == "promotion_manifest_ref":
                continue
            if not isinstance(ref, str):
                failures.append(prefix + f":REF_TYPE:{ref_field}")
                continue
            try:
                present = safe_ref(root, ref).is_file()
            except ValueError:
                present = False
            if not present:
                failures.append(prefix + f":MISSING_REF:{ref_field}:{ref}")

    alias_map = committed_index.get("alias_map") if isinstance(committed_index.get("alias_map"), dict) else {}
    if alias_map != dict(sorted(alias_owner.items())):
        failures.append("ALIAS_MAP_MISMATCH")

    gap_records = gap_registry.get("gaps") if isinstance(gap_registry.get("gaps"), list) else []
    gaps_by_key: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for gap in gap_records:
        if isinstance(gap, dict):
            key = (str(gap.get("ledger_ref")), str(gap.get("declared_ref")))
            gaps_by_key.setdefault(key, []).append(gap)

    required_gap_keys: set[tuple[str, str]] = set()
    for ledger_ref in actual_ledger_paths:
        ledger = read_json(safe_ref(root, ledger_ref))
        declaration = _ledger_manifest_declaration(ledger)
        if declaration is None:
            continue
        declared_ref = declaration["path"]
        try:
            exists = safe_ref(root, declared_ref).is_file()
        except ValueError:
            exists = False
        key = (ledger_ref, declared_ref)
        matching = gaps_by_key.get(key, [])
        if exists:
            if matching:
                failures.append("STALE_GAP_PRESENT_SOURCE:" + declared_ref)
            continue
        required_gap_keys.add(key)
        if len(matching) != 1:
            failures.append("UNCLASSIFIED_MISSING_SOURCE:" + declared_ref)
            continue
        gap = matching[0]
        if gap.get("generation_order") != ledger.get("order"):
            failures.append("GAP_ORDER_DRIFT:" + declared_ref)
        if gap.get("declared_commit") != declaration.get("commit"):
            failures.append("GAP_COMMIT_DRIFT:" + declared_ref)
        if gap.get("declared_blob_sha") != declaration.get("blob_sha"):
            failures.append("GAP_BLOB_DRIFT:" + declared_ref)
        if not isinstance(gap.get("declared_blob_sha"), str) or len(gap.get("declared_blob_sha")) != 40:
            failures.append("GAP_BLOB_IDENTITY:" + declared_ref)

    for key in sorted(gaps_by_key):
        if key not in required_gap_keys:
            ledger_ref, declared_ref = key
            failures.append("ORPHAN_OR_STALE_GAP:" + ledger_ref + ":" + declared_ref)
        if len(gaps_by_key[key]) != 1:
            failures.append("DUPLICATE_GAP:" + key[0] + ":" + key[1])

    try:
        regenerated = generate_genealogy_index(root)
        if regenerated != committed_index:
            failures.append("INDEX_NOT_SOURCE_DERIVED")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        failures.append("INDEX_REGENERATION:" + type(exc).__name__)

    failures = sorted(set(failures))
    result = {
        "schema": CLOSURE_SCHEMA,
        "order": ORDER,
        "closed": not failures,
        "failures": failures,
        "ledger_count": len(actual_ledger_paths),
        "index_entry_count": len(entries),
        "alias_count": len(alias_owner),
        "promoted_main_with_durable_evidence": promoted_with_evidence,
        "legacy_gap_count": len(gap_records),
        "legacy_gap_ids": sorted(
            gap.get("gap_id") for gap in gap_records if isinstance(gap, dict) and isinstance(gap.get("gap_id"), str)
        ),
        "index_sha256": committed_index.get("index_sha256"),
        "gap_registry_sha256": gap_registry.get("manifest_sha256"),
    }
    result["closure_sha256"] = canonical_sha256(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", default=".")
    args = parser.parse_args()
    result = audit_genealogy_closure(args.repository_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["closed"] else 7


if __name__ == "__main__":
    raise SystemExit(main())
