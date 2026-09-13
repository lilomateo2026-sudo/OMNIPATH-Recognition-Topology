from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_attestation(evidence_dir: Path, output_path: Path) -> dict:
    manifest_path = evidence_dir / "replay_manifest.json"
    report_path = evidence_dir / "o22_5_report.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    replay_job_result = os.environ.get("REPLAY_JOB_RESULT", "")
    failures = []

    if replay_job_result != "success":
        failures.append("REPLAY_JOB_NOT_SUCCESS")
    if manifest.get("replay_status") != "VERIFIED":
        failures.append("REPLAY_NOT_VERIFIED")
    if manifest.get("o22_5_report_sha256") != sha256_file(report_path):
        failures.append("REPORT_HASH_MISMATCH")
    if manifest.get("specimen_count") != 4:
        failures.append("SPECIMEN_COUNT")
    if manifest.get("variant_count") != 378:
        failures.append("VARIANT_COUNT")
    if manifest.get("cross_product_variant_count") != 342:
        failures.append("CROSS_PRODUCT_COUNT")
    if manifest.get("final_pass_count") != 0:
        failures.append("FINAL_PASS_PRESENT")

    attestation = {
        "schema": "omnipath.o22-6-ci-attestation/v1",
        "order": "O22.6",
        "source_commit": os.environ.get("GITHUB_SHA", ""),
        "workflow_run_id": os.environ.get("GITHUB_RUN_ID", ""),
        "workflow_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", ""),
        "replay_job_result": replay_job_result,
        "external_ci_status": "SUCCESS" if not failures else "FAILED",
        "promotion_eligible": not failures,
        "replay_manifest_sha256": sha256_file(manifest_path),
        "o22_5_report_sha256": sha256_file(report_path),
        "specimen_sha256": manifest.get("specimen_sha256", {}),
        "variant_count": manifest.get("variant_count"),
        "cross_product_variant_count": manifest.get("cross_product_variant_count"),
        "final_pass_count": manifest.get("final_pass_count"),
        "failures": failures,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(attestation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return attestation


def main(argv=None) -> int:
    evidence = Path(argv[1]) if argv and len(argv) > 1 else Path("o22_6_evidence")
    output = Path(argv[2]) if argv and len(argv) > 2 else Path("o22_6_attestation/ci_attestation.json")
    attestation = build_attestation(evidence, output)
    print(json.dumps(attestation, indent=2, sort_keys=True))
    return 0 if attestation["promotion_eligible"] else 6


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
