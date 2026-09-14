#!/usr/bin/env python3
"""O32.3 deterministic replay-identity audit across all durable promotion ledgers."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

INDEX_REF = "omnipath/recognition/promotion_genealogy/index.json"


def _read(root: Path, ref: str) -> dict:
    return json.loads((root / ref).read_text(encoding="utf-8"))


def _candidate(ledger: dict) -> str | None:
    candidate = ledger.get("candidate") if isinstance(ledger.get("candidate"), dict) else {}
    return candidate.get("head_sha") or candidate.get("canonical_sha") or ledger.get("source_commit")


def _promoted(ledger: dict) -> str | None:
    merge = ledger.get("merge") if isinstance(ledger.get("merge"), dict) else {}
    post = ledger.get("postmerge") if isinstance(ledger.get("postmerge"), dict) else {}
    post_ci = ledger.get("postmerge_ci") if isinstance(ledger.get("postmerge_ci"), dict) else {}
    return merge.get("commit") or post.get("main_sha") or post_ci.get("attested_main_sha") or post_ci.get("main_sha") or ledger.get("source_commit")


def _postmerge(ledger: dict) -> dict:
    if isinstance(ledger.get("postmerge"), dict):
        return ledger["postmerge"]
    if isinstance(ledger.get("postmerge_ci"), dict):
        return ledger["postmerge_ci"]
    return ledger


def _run_id(post: dict) -> int | None:
    return post.get("recognition_run_id") or post.get("workflow_run_id") or post.get("run_id")


def _artifact(post: dict, name: str) -> dict | None:
    value = post.get(name)
    return value if isinstance(value, dict) else None


def audit(repository_root: str | Path = ".") -> dict:
    root = Path(repository_root).resolve()
    index = _read(root, INDEX_REF)
    rows = []
    replay_ids = []
    for entry in index["entries"]:
        ledger = _read(root, entry["ledger_ref"])
        candidate = _candidate(ledger)
        promoted = _promoted(ledger)
        post = _postmerge(ledger)
        replay = _artifact(post, "replay_artifact")
        attestation = _artifact(post, "attestation_artifact")
        historical = ledger.get("relationship") == "historical_evidence_backfill_not_registry_entry"
        lineage_ok = candidate == entry["candidate_commit_sha"] and promoted == entry["promoted_main_sha"]
        alias_ok = all(index["alias_map"].get(alias) == entry["entry_id"] for alias in entry["aliases"])
        artifact_ok = historical or (
            isinstance(replay, dict)
            and isinstance(replay.get("id"), int)
            and isinstance(replay.get("digest"), str)
            and replay["digest"].startswith("sha256:")
            and isinstance(attestation, dict)
            and isinstance(attestation.get("id"), int)
            and isinstance(attestation.get("digest"), str)
            and attestation["digest"].startswith("sha256:")
        )
        if replay:
            replay_ids.append(replay["id"])
        rows.append({
            "entry_id": entry["entry_id"],
            "candidate": candidate,
            "promoted": promoted,
            "run_id": _run_id(post),
            "replay_id": replay.get("id") if replay else None,
            "replay_digest": replay.get("digest") if replay else None,
            "attestation_id": attestation.get("id") if attestation else None,
            "attestation_digest": attestation.get("digest") if attestation else None,
            "identity_level": "workflow_only_historical_backfill" if historical else "artifact_bound",
            "lineage_ok": lineage_ok,
            "alias_ok": alias_ok,
            "replay_identity_ok": artifact_ok,
        })
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    return {
        "schema": "omnipath.cross-ledger-replay-identity-audit/v1",
        "order": "O32.3",
        "ledger_count": len(rows),
        "artifact_bound_count": sum(row["identity_level"] == "artifact_bound" for row in rows),
        "workflow_only_historical_count": sum(row["identity_level"] == "workflow_only_historical_backfill" for row in rows),
        "lineage_mismatches": sum(not row["lineage_ok"] for row in rows),
        "alias_mismatches": sum(not row["alias_ok"] for row in rows),
        "replay_identity_failures": sum(not row["replay_identity_ok"] for row in rows),
        "duplicate_replay_ids": len(replay_ids) - len(set(replay_ids)),
        "audit_digest_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "rows": rows,
    }
