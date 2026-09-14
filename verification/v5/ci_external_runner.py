from __future__ import annotations
import json, os, pathlib, platform, hashlib, sys

ROOT = pathlib.Path(__file__).resolve().parent
RUNNER = ROOT / "runner"
sys.path.insert(0, str(RUNNER))

from omni_v5.cross_machine import build_external_attestation, sha256_file
from omni_v5.conformance import baseline_state
from omni_v5.corpus import generate
from omni_v5.runtime import apply_event

art = RUNNER / "artifacts"
report = json.loads((art / "conformance_report.json").read_text())
manifest = json.loads((art / "v5_attestation.json").read_text())
source_zip = RUNNER / "source_immutable.zip"
runner_id = os.environ.get("O87_RUNNER_ID", "unknown-runner")
profile = {
    "python": platform.python_version(),
    "implementation": platform.python_implementation(),
    "os": platform.system(),
    "os_release": platform.release(),
    "machine": platform.machine(),
    "libc": platform.libc_ver(),
    "executable_name": pathlib.Path(sys.executable).name,
}
att = build_external_attestation(sha256_file(source_zip), report, manifest, runner_id, profile)

# O89 trace: deterministic state digest after every event for the fixed corpus.
traces = []
for seed in report.get("seeds", []):
    state = baseline_state()
    seed_trace = []
    for index, event in enumerate(generate(seed, report["events_per_seed"]), 1):
        state = apply_event(state, event)
        seed_trace.append({"index": index, "event": event, "state_digest": state.state_digest()})
    traces.append({"seed": seed, "trace": seed_trace})
trace_obj = {"version": "O89-trace-v1", "runner_id": runner_id, "environment_identity_digest": att["environment_identity_digest"], "traces": traces}
trace_obj["trace_digest"] = hashlib.sha256(json.dumps(trace_obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

art.mkdir(exist_ok=True)
(art / "o87_external_attestation.json").write_text(json.dumps(att, indent=2, sort_keys=True) + "\n")
(art / "o89_transition_trace.json").write_text(json.dumps(trace_obj, indent=2, sort_keys=True) + "\n")
print(json.dumps({"runner_id": runner_id, "status": att["reproduction_status"], "environment_identity": att["environment_identity_digest"], "trace_digest": trace_obj["trace_digest"]}, indent=2))
if att["reproduction_status"] != "PASS":
    raise SystemExit(2)
