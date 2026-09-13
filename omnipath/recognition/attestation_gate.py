def check_attestation(data, expected_commit=None):
    failures = []
    required = {
        "schema": "omnipath.o22-6-ci-attestation/v1",
        "order": "O22.6",
        "replay_job_result": "success",
        "external_ci_status": "SUCCESS",
        "variant_count": 378,
        "cross_product_variant_count": 342,
        "final_pass_count": 0,
    }
    for key, expected in required.items():
        if data.get(key) != expected:
            failures.append(key)
    if data.get("promotion_eligible") is not True:
        failures.append("promotion_eligible")
    if not data.get("workflow_run_id"):
        failures.append("workflow_run_id")
    if not data.get("replay_artifact_id"):
        failures.append("replay_artifact_id")
    artifact_digest = data.get("replay_artifact_digest")
    if not isinstance(artifact_digest, str) or not artifact_digest.startswith("sha256:") or len(artifact_digest) != 71:
        failures.append("replay_artifact_digest")
    hashes = data.get("specimen_sha256")
    if not isinstance(hashes, dict) or len(hashes) != 4:
        failures.append("specimen_sha256")
    else:
        for value in hashes.values():
            if not isinstance(value, str) or len(value) != 64:
                failures.append("specimen_hash")
                break
    for key in ("replay_manifest_sha256", "o22_5_report_sha256"):
        value = data.get(key)
        if not isinstance(value, str) or len(value) != 64:
            failures.append(key)
    if expected_commit and data.get("source_commit") != expected_commit:
        failures.append("source_commit")
    return {"gate": "O22.6", "promotion_allowed": not failures, "failures": sorted(set(failures))}
