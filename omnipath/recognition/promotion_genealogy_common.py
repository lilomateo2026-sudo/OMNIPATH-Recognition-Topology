"""Shared O27.6 promotion-genealogy primitives."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from promotion_manifest_gate import canonical_sha256

ORDER = "O27.6"
GENEALOGY_SCHEMA = "omnipath.promotion-genealogy/v1"
LEDGER_MANIFEST_SCHEMA = "omnipath.durable-promotion-evidence-manifest/v1"
LEDGER_INDEX_SCHEMA = "omnipath.durable-attestation-ledger/v1"
CROSS_LINK_FIELDS = (
    "genealogy_contract_order",
    "promotion_manifest_ref",
    "durable_evidence_ledger_ref",
    "durable_evidence_record_set_sha256",
    "durable_evidence_source_commit_sha",
)


def is_git_sha(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 40:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def safe_ref(repository_root: Path, ref: str) -> Path:
    if not isinstance(ref, str) or not ref or Path(ref).is_absolute():
        raise ValueError("invalid repository ref")
    root = repository_root.resolve()
    resolved = (root / ref).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("repository ref escapes root") from exc
    return resolved


def ledger_material(manifest: dict[str, Any]) -> dict[str, Any]:
    material = copy.deepcopy(manifest)
    material.pop("record_set_sha256", None)
    return material


def sealed_record_set_sha256(manifest: dict[str, Any]) -> str:
    return canonical_sha256(ledger_material(manifest))
