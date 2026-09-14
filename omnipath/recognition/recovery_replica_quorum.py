from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path

ORDER = "O31.9"
PARENT_ORDER = "O31.8"
PARENT_MAIN_SHA = "822085dee5ee7761fcfb29bb296cc4f4f401fba8"
EXPECTED_CONTENT_SHA256 = "486993dc1843c8f35876ed3dc02c1d2ce4c3a66ed96a3d27c00bd08c42a57eb6"
EXPECTED_GIT_BLOB_SHA = "f10f0cb3c9e670237914e5d502bce9f9b9dbb871"
ROOT = Path(__file__).resolve().parents[2]
VAULT_INDEX = ROOT / "omnipath/recognition/recovery_vault/index.json"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def canonical_payload() -> bytes:
    index = _load(VAULT_INDEX)
    entry = index["entries"][0]
    payload = (ROOT / entry["payload_path"]).read_bytes()
    assert _sha256(payload) == EXPECTED_CONTENT_SHA256
    assert _git_blob_sha(payload) == EXPECTED_GIT_BLOB_SHA
    return payload


def seed_replica(replica_id: str, medium: str, output: Path) -> dict:
    payload = canonical_payload()
    output.mkdir(parents=True, exist_ok=True)
    if medium == "raw":
        stored = payload
        relative_path = "payload.bin"
    elif medium == "base64":
        stored = base64.b64encode(payload) + b"\n"
        relative_path = "payload.b64"
    else:
        raise ValueError("unsupported medium")
    (output / relative_path).write_bytes(stored)
    manifest = {
        "schema": "omnipath.recovery-replica/v1",
        "order": ORDER,
        "parent_order": PARENT_ORDER,
        "parent_main_sha": PARENT_MAIN_SHA,
        "replica_id": replica_id,
        "medium": medium,
        "payload_ref": relative_path,
        "stored_representation_sha256": _sha256(stored),
        "content_sha256": EXPECTED_CONTENT_SHA256,
        "git_blob_sha": EXPECTED_GIT_BLOB_SHA,
        "byte_count": len(payload),
        "source_vault_required_only_at_seed_time": True,
    }
    _write_json(output / "manifest.json", manifest)
    return manifest


def _decode_replica(replica_dir: Path) -> tuple[dict, bytes]:
    manifest = _load(replica_dir / "manifest.json")
    assert manifest["schema"] == "omnipath.recovery-replica/v1"
    assert manifest["order"] == ORDER
    stored = (replica_dir / manifest["payload_ref"]).read_bytes()
    assert _sha256(stored) == manifest["stored_representation_sha256"]
    if manifest["medium"] == "raw":
        payload = stored
    elif manifest["medium"] == "base64":
        payload = base64.b64decode(stored, validate=False)
    else:
        raise AssertionError("unsupported medium")
    assert len(payload) == manifest["byte_count"]
    assert _sha256(payload) == EXPECTED_CONTENT_SHA256 == manifest["content_sha256"]
    assert _git_blob_sha(payload) == EXPECTED_GIT_BLOB_SHA == manifest["git_blob_sha"]
    return manifest, payload


def quorum_restore(replica_a: Path, replica_b: Path, output: Path) -> dict:
    manifest_a, payload_a = _decode_replica(replica_a)
    manifest_b, payload_b = _decode_replica(replica_b)
    assert manifest_a["replica_id"] != manifest_b["replica_id"]
    assert manifest_a["medium"] != manifest_b["medium"]
    assert payload_a == payload_b
    output.mkdir(parents=True, exist_ok=True)
    restored = output / "restored-evidence.bin"
    restored.write_bytes(payload_a)
    report = {
        "schema": "omnipath.recovery-replica-quorum-attestation/v1",
        "order": ORDER,
        "replica_ids": sorted([manifest_a["replica_id"], manifest_b["replica_id"]]),
        "media": sorted([manifest_a["medium"], manifest_b["medium"]]),
        "content_sha256": _sha256(payload_a),
        "git_blob_sha": _git_blob_sha(payload_a),
        "byte_count": len(payload_a),
        "quorum": "2-of-2",
        "uses_only_replica_inputs_during_restore": True,
        "primary_vault_required_during_restore": False,
        "verdict": "PASS",
    }
    _write_json(output / "quorum-attestation.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    seed = sub.add_parser("seed")
    seed.add_argument("--replica-id", required=True)
    seed.add_argument("--medium", choices=["raw", "base64"], required=True)
    seed.add_argument("--output", type=Path, required=True)
    quorum = sub.add_parser("quorum")
    quorum.add_argument("--replica-a", type=Path, required=True)
    quorum.add_argument("--replica-b", type=Path, required=True)
    quorum.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "seed":
        result = seed_replica(args.replica_id, args.medium, args.output)
    else:
        result = quorum_restore(args.replica_a, args.replica_b, args.output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
