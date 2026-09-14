from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ORDER = "O31.8"
ROOT = Path(__file__).resolve().parents[2]
VAULT_INDEX = ROOT / "omnipath/recognition/recovery_vault/index.json"
O31_7_PROOFS = ROOT / "omnipath/recognition/promotion_genealogy/historical_recovery_proofs.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify() -> dict:
    index = _load(VAULT_INDEX)
    assert index["schema"] == "omnipath.content-addressed-recovery-vault/v1"
    assert index["order"] == ORDER
    assert len(index["entries"]) == 1
    entry = index["entries"][0]

    payload_path = ROOT / entry["payload_path"]
    record_path = ROOT / entry["record_path"]
    ledger_path = ROOT / entry["ledger_path"]
    assert payload_path.is_file() and record_path.is_file() and ledger_path.is_file()

    payload = payload_path.read_bytes()
    content_sha256 = _sha256(payload)
    payload_git_sha = _git_blob_sha(payload)
    record_git_sha = _git_blob_sha(record_path.read_bytes())
    ledger_git_sha = _git_blob_sha(ledger_path.read_bytes())

    assert payload_path.parent.name == content_sha256
    assert entry["sha256"] == content_sha256
    assert entry["payload_git_blob_sha"] == payload_git_sha
    assert entry["record_git_blob_sha"] == record_git_sha
    assert entry["ledger_git_blob_sha"] == ledger_git_sha

    record = _load(record_path)
    ledger = _load(ledger_path)
    proofs = _load(O31_7_PROOFS)
    proof = next(p for p in proofs["proofs"] if p["gap_id"] == entry["gap_id"])

    assert record["order"] == ORDER and ledger["order"] == ORDER
    assert record["storage"]["content_sha256"] == content_sha256
    assert record["preservation"]["vault_payload_git_blob_sha"] == payload_git_sha
    assert record["reconstruction"]["expected_git_blob_sha"] == payload_git_sha
    assert record["source"]["o31_7_proof_set_sha256"] == proofs["proof_set_sha256"]

    assert ledger["source"]["content_sha256"] == content_sha256
    assert ledger["source"]["git_blob_sha"] == payload_git_sha
    assert ledger["source"]["o31_7_proof_set_sha256"] == proofs["proof_set_sha256"]
    assert ledger["vault"]["record_git_blob_sha"] == record_git_sha
    assert ledger["vault"]["payload_git_blob_sha"] == payload_git_sha

    assert proof["classification"] == "HISTORICALLY_REACHABLE"
    assert proof["content_sha256"] == content_sha256
    assert proof["expected_blob_sha"] == payload_git_sha
    assert proof["git_hash_object_sha"] == payload_git_sha

    original_path = ROOT / record["source"]["original_path"]
    assert not original_path.exists()
    assert record["preservation"]["original_path_restored"] is False
    assert ledger["vault"]["original_path_restored"] is False
    assert record["reconstruction"]["requires_historical_git_object"] is False
    assert ledger["reconstruction"]["historical_git_required"] is False

    return {
        "schema": "omnipath.recovery-vault-verification/v1",
        "order": ORDER,
        "gap_id": entry["gap_id"],
        "content_sha256": content_sha256,
        "payload_git_blob_sha": payload_git_sha,
        "record_git_blob_sha": record_git_sha,
        "ledger_git_blob_sha": ledger_git_sha,
        "o31_7_proof_set_sha256": proofs["proof_set_sha256"],
        "original_path_present": False,
        "historical_git_required_for_reconstruction": False,
        "verdict": "PASS",
    }


def reconstruct(destination: Path) -> dict:
    report = verify()
    entry = _load(VAULT_INDEX)["entries"][0]
    payload = (ROOT / entry["payload_path"]).read_bytes()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    rebuilt = destination.read_bytes()
    assert _sha256(rebuilt) == report["content_sha256"]
    assert _git_blob_sha(rebuilt) == report["payload_git_blob_sha"]
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path)
    parser.add_argument("--reconstruct", type=Path)
    args = parser.parse_args()
    report = reconstruct(args.reconstruct) if args.reconstruct else verify()
    rendered = json.dumps(report, sort_keys=True, indent=2) + "\n"
    if args.report:
        args.report.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
