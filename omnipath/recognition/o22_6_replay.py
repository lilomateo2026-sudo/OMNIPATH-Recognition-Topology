from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from cross_product_runner import run_cross_product
from pathology_validator import DEFAULT_LOCK, DEFAULT_SCHEMA, _load_json, validate_pathology
from specimen_registry import load_specimens
from tribunal_loader import load_corpus

HERE = Path(__file__).resolve().parent
SPECIMEN_DIR = HERE / "regression" / "o22_5"
EXPECTED_VARIANTS = 378
EXPECTED_CROSS_PRODUCT = 342
EXPECTED_MINIMAL = 4


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_clean_replay(output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    report = run_cross_product(
        load_corpus(),
        load_specimens(),
        _load_json(DEFAULT_SCHEMA),
        _load_json(DEFAULT_LOCK),
        validate_pathology,
    )
    failures = []
    if report.get("verdict") != "CERTIFIED":
        failures.append("O22_5_NOT_CERTIFIED")
    if report.get("variant_count") != EXPECTED_VARIANTS:
        failures.append("VARIANT_COUNT")
    if report.get("cross_product_variant_count") != EXPECTED_CROSS_PRODUCT:
        failures.append("CROSS_PRODUCT_COUNT")
    if report.get("final_pass_count") != 0:
        failures.append("FINAL_PASS_PRESENT")
    if len(report.get("minimal_counterexamples", [])) != EXPECTED_MINIMAL:
        failures.append("MINIMAL_COUNTEREXAMPLE_COUNT")

    report_path = output_dir / "o22_5_report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    specimen_hashes = {
        path.name: sha256_file(path)
        for path in sorted(SPECIMEN_DIR.glob("*.json"))
    }
    manifest = {
        "order": "O22.6",
        "replay_status": "VERIFIED" if not failures else "FAILED",
        "o22_5_report_sha256": sha256_file(report_path),
        "specimen_sha256": specimen_hashes,
        "specimen_count": len(specimen_hashes),
        "variant_count": report.get("variant_count"),
        "cross_product_variant_count": report.get("cross_product_variant_count"),
        "final_pass_count": report.get("final_pass_count"),
        "minimal_counterexample_count": len(report.get("minimal_counterexamples", [])),
        "failures": failures,
    }
    (output_dir / "replay_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def main(argv=None) -> int:
    target = Path(argv[1]) if argv and len(argv) > 1 else Path("o22_6_evidence")
    manifest = run_clean_replay(target)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0 if manifest["replay_status"] == "VERIFIED" else 5


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
