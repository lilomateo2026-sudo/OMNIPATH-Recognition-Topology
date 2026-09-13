"""O27.7 deterministic promotion genealogy index generator."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from promotion_genealogy_common import is_git_sha, read_json, safe_ref
from promotion_manifest_gate import canonical_sha256

ORDER = "O27.7"
INDEX_SCHEMA = "omnipath.promotion-genealogy-index/v1"
SOURCE_ROOT = "omnipath/recognition/attestation_ledger/v1"
REGISTRY_REF = "omnipath/recognition/promotion_registry/registry.json"


def _nested(value: dict[str, Any], *keys: str) -> Any:
    current: Any = value
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _candidate_sha(ledger: dict[str, Any]) -> str:
    value = _nested(ledger, "candidate", "head_sha") or ledger.get("source_commit") or _nested(ledger, "merge", "candidate_parent")
    if not is_git_sha(value):
        raise ValueError("ledger has no valid candidate SHA")
    return value


def _promoted_main_sha(ledger: dict[str, Any]) -> str:
    value = _nested(ledger, "merge", "commit") or _nested(ledger, "postmerge_ci", "attested_main_sha") or _nested(ledger, "postmerge_ci", "main_sha") or ledger.get("source_commit")
    if not is_git_sha(value):
        raise ValueError("ledger has no valid promoted-main SHA")
    return value


def _epistemic_state(ledger: dict[str, Any]) -> str | None:
    value = ledger.get("epistemic_state") or ledger.get("recorded_epistemic_state")
    return value if isinstance(value, str) else None


def _relationship(ledger: dict[str, Any]) -> str:
    value = ledger.get("relationship") or ledger.get("status") or "durable_promotion_ledger"
    return str(value)


def _workflow_run_id(ledger: dict[str, Any]) -> int | None:
    value = _nested(ledger, "postmerge_ci", "workflow_run_id")
    if value is None:
        value = _nested(ledger, "postmerge_ci", "run_id")
    if value is None:
        value = ledger.get("workflow_run_id")
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _promotion_manifest_ref(repository_root: Path, ledger_path: Path, ledger: dict[str, Any]) -> str | None:
    declared = _nested(ledger, "promotion_manifest", "path")
    if isinstance(declared, str):
        try:
            if safe_ref(repository_root, declared).is_file():
                return declared
        except ValueError:
            pass
    sibling = ledger_path.parent / "promotion_manifest.json"
    if sibling.is_file():
        return sibling.relative_to(repository_root).as_posix()
    return None


def _registry_entries(repository_root: Path) -> dict[str, dict[str, Any]]:
    path = safe_ref(repository_root, REGISTRY_REF)
    if not path.is_file():
        return {}
    registry = read_json(path)
    entries = registry.get("entries") if isinstance(registry.get("entries"), list) else []
    result: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        candidate = entry.get("candidate_commit_sha")
        if is_git_sha(candidate):
            result[candidate] = entry
    return result


def _normalize_ledger(repository_root: Path, ledger_path: Path, registry: dict[str, dict[str, Any]]) -> dict[str, Any]:
    ledger = read_json(ledger_path)
    candidate = _candidate_sha(ledger)
    promoted = _promoted_main_sha(ledger)
    aliases = sorted({candidate, promoted})
    matched_registry = next((registry[a] for a in aliases if a in registry), None)
    generation_order = ledger.get("source_order") or ledger.get("order")
    ledger_order = ledger.get("order")
    if not isinstance(generation_order, str) or not isinstance(ledger_order, str):
        raise ValueError("ledger order is missing")
    return {
        "entry_id": f"{generation_order}:{promoted}",
        "generation_order": generation_order,
        "ledger_order": ledger_order,
        "candidate_commit_sha": candidate,
        "promoted_main_sha": promoted,
        "aliases": aliases,
        "ledger_ref": ledger_path.relative_to(repository_root).as_posix(),
        "promotion_manifest_ref": _promotion_manifest_ref(repository_root, ledger_path, ledger),
        "registry_ref": REGISTRY_REF,
        "registry_entry_sha256": matched_registry.get("entry_sha256") if matched_registry else None,
        "epistemic_state": _epistemic_state(ledger),
        "relationship": _relationship(ledger),
        "postmerge_workflow_run_id": _workflow_run_id(ledger),
    }


def index_material(index: dict[str, Any]) -> dict[str, Any]:
    material = copy.deepcopy(index)
    material.pop("index_sha256", None)
    return material


def generate_genealogy_index(repository_root: Path | str) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    source = safe_ref(root, SOURCE_ROOT)
    registry = _registry_entries(root)
    paths = sorted(source.glob("*/index.json"), key=lambda path: path.as_posix())
    if not paths:
        raise ValueError("no durable ledger indexes found")
    entries = [_normalize_ledger(root, path, registry) for path in paths]
    entries.sort(key=lambda entry: (entry["generation_order"], entry["promoted_main_sha"], entry["ledger_ref"]))

    aliases: dict[str, str] = {}
    for entry in entries:
        for alias in entry["aliases"]:
            previous = aliases.get(alias)
            if previous is not None and previous != entry["entry_id"]:
                raise ValueError(f"ambiguous candidate alias: {alias}")
            aliases[alias] = entry["entry_id"]

    index = {
        "schema": INDEX_SCHEMA,
        "order": ORDER,
        "source_root": SOURCE_ROOT,
        "registry_ref": REGISTRY_REF,
        "entry_count": len(entries),
        "entries": entries,
        "alias_map": dict(sorted(aliases.items())),
    }
    index["index_sha256"] = canonical_sha256(index)
    return index


def verify_genealogy_index(repository_root: Path | str, committed: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    if committed.get("schema") != INDEX_SCHEMA:
        failures.append("SCHEMA")
    if committed.get("order") != ORDER:
        failures.append("ORDER")
    supplied = committed.get("index_sha256")
    if supplied != canonical_sha256(index_material(committed)):
        failures.append("INDEX_SEAL")
    try:
        regenerated = generate_genealogy_index(repository_root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        regenerated = None
        failures.append(f"REGENERATION:{type(exc).__name__}")
    if regenerated is not None and committed != regenerated:
        failures.append("STALE_OR_NONDETERMINISTIC")
    return {
        "order": ORDER,
        "valid": not failures,
        "failures": sorted(set(failures)),
        "entry_count": committed.get("entry_count"),
        "index_sha256": supplied,
    }


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--check")
    parser.add_argument("--write")
    args = parser.parse_args()
    root = Path(args.repository_root).resolve()
    generated = generate_genealogy_index(root)
    if args.write:
        _write_json(safe_ref(root, args.write), generated)
    if args.check:
        committed = read_json(safe_ref(root, args.check))
        result = verify_genealogy_index(root, committed)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["valid"] else 7
    if not args.write:
        print(json.dumps(generated, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
