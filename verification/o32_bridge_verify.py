#!/usr/bin/env python3
"""Fail-closed verification for the O32 cross-repository bridge."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
BRIDGE_PATH = ROOT / "registry" / "omniverse_design_pathology_o32_bridge.json"


def git_blob_sha(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode()
    return hashlib.sha1(header + payload).hexdigest()


def load_evidence(bridge: dict, evidence_file: str | None) -> tuple[bytes, str]:
    if evidence_file:
        path = Path(evidence_file)
        return path.read_bytes(), str(path)

    repository = bridge["source_repository"]
    commit = bridge["authoritative_evidence_commit"]
    path = bridge["release_candidate_evidence"]
    url = f"https://raw.githubusercontent.com/{repository}/{commit}/{path}"
    with urlopen(url, timeout=30) as response:
        return response.read(), url


def verify(evidence_file: str | None = None) -> dict:
    bridge = json.loads(BRIDGE_PATH.read_text(encoding="utf-8"))
    required = {
        "source_repository": "lilomateo2026-sudo/Omni-verses-",
        "source_commit": "9ef1f2645aa18af412a7a5290a939eaac5109c27",
        "authoritative_evidence_commit": "82479057c38139a19cb963a3715ac3dd4ea55f3b",
        "source_evidence_blob_sha": "dde4da5bb71407c8ea35504386519a1dba08a097",
        "authority_transfer": False,
        "promotion_state": "AWAITING_AUTHORIZED_HUMAN_SIGNATURE",
        "release_state": "RELEASE_CANDIDATE_NOT_PROMOTED",
    }
    for key, expected in required.items():
        actual = bridge.get(key)
        if actual != expected:
            raise SystemExit(f"bridge {key}: expected {expected!r}, got {actual!r}")

    payload, origin = load_evidence(bridge, evidence_file)
    actual_blob = git_blob_sha(payload)
    if actual_blob != bridge["source_evidence_blob_sha"]:
        raise SystemExit(
            f"evidence blob mismatch: expected {bridge['source_evidence_blob_sha']}, got {actual_blob}"
        )

    evidence = json.loads(payload)
    pairs = {
        "certificate_hash": "certificate_hash",
        "constitutional_root": "constitutional_root",
        "release_seal_hash": "source_release_seal",
    }
    for bridge_key, evidence_key in pairs.items():
        if bridge[bridge_key] != evidence[evidence_key]:
            raise SystemExit(f"identity mismatch: {bridge_key} != {evidence_key}")

    if evidence["o29"]["authority_transfer"] is not False:
        raise SystemExit("source evidence attempts authority transfer")
    if evidence["o29"]["promoted"] is not False:
        raise SystemExit("source evidence unexpectedly claims promotion")

    return {
        "result": "PASS",
        "bridge": str(BRIDGE_PATH.relative_to(ROOT)),
        "evidence_origin": origin,
        "source_commit": bridge["source_commit"],
        "authoritative_evidence_commit": bridge["authoritative_evidence_commit"],
        "source_evidence_blob_sha": actual_blob,
        "authority_transfer": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-file")
    args = parser.parse_args()
    print(json.dumps(verify(args.evidence_file), sort_keys=True))


if __name__ == "__main__":
    main()
