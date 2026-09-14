from __future__ import annotations
import hashlib, json, os, pathlib, platform, sys

ROOT = pathlib.Path(__file__).resolve().parent
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)

BASELINE = {
    "certified_commit": "5c5010459dee0b801d6b28335e187f51e1dcdb02",
    "canonical_runner_blob_sha": "9c2b47fd4db4bbf96ce982ae2ddbf28eef9654ac",
    "report_digest": "5ee98bf9d0e90b4eec7eec45bf28e33b2296f010bd1cb5690b7b951d7e410ce6",
    "manifest_digest": "fa2d8eb05e3d9934c8df1deccf9d5e24a1a900d26734904d5e63d5c11fefa904",
    "semantic_trace_digest": "945900bad3070247d1d240c9b3e5f8a25743f52d99a4d250dde3ce3d53234daa",
    "o91_certificate_digest": "3b1f0b0c5060391bf49fecc66ca711c924db50d5498c3b6fb4b4bd6096809643",
}

def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def load(name):
    return json.loads((ART / name).read_text())

report=load("conformance_report.json")
manifest=load("v5_attestation.json")
trace=load("o89_transition_trace.json")
att=load("o87_external_attestation.json")
observed={
    "report_digest": report["report_digest"],
    "manifest_digest": manifest["manifest_digest"],
    "semantic_trace_digest": trace["semantic_trace_digest"],
}
expected={k:BASELINE[k] for k in observed}
semantic_match=observed == expected
source_lineage_changed=att.get("source",{}).get("commit_sha") != BASELINE["certified_commit"]
if not semantic_match:
    classification="SEMANTIC_REGRESSION"
elif source_lineage_changed:
    classification="ENVIRONMENT_OR_LINEAGE_DRIFT_ONLY"
else:
    classification="NO_DRIFT"

record={
    "version":"O95-v1",
    "baseline":BASELINE,
    "observed":observed,
    "semantic_match":semantic_match,
    "source_lineage_changed":source_lineage_changed,
    "classification":classification,
    "environment":att.get("environment",{}),
    "environment_identity_digest":att.get("environment_identity_digest"),
    "runner_id":att.get("runner_id"),
    "github_run_id":os.environ.get("GITHUB_RUN_ID","local"),
}
record["drift_record_digest"]=digest(record)
(ART/"o95_drift_report.json").write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")
print(json.dumps(record,indent=2,sort_keys=True))
if not semantic_match:
    raise SystemExit(4)
