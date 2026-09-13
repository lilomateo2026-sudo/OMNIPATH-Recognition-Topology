import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from promotion_artifact_registry import ENTRY_SCHEMA, ORDER as REGISTRY_ORDER, empty_registry, seal_entry, seal_registry
from promotion_genealogy_common import ORDER
from promotion_genealogy_registry import audit_genealogy_registry
from promotion_genealogy_tribunal import reconstruct_promotion_genealogy
from promotion_manifest_gate import canonical_sha256, manifest_material


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


class O276ReconstructionTests(unittest.TestCase):
    def test_unlinked_entry_is_nonconformant(self):
        entry = seal_entry({
            "schema": ENTRY_SCHEMA, "order": REGISTRY_ORDER, "accepted_by_gate": "O22.7",
            "lineage_version": 1, "candidate_id": "x", "candidate_commit_sha": "1"*40,
            "parent_commit_sha": "2"*40, "rollback_commit_sha": "2"*40,
            "constitutional_root_sha": "3"*40, "checkpoint_commits": {},
            "promotion_manifest_sha256": "4"*64, "promotion_decision_sha256": "5"*64,
            "o22_6_attestation_sha256": "6"*64, "o22_6_workflow_run_id": "7",
            "o22_6_replay_artifact_id": "8", "o22_6_replay_artifact_digest": "9"*64,
            "previous_entry_sha256": None,
        })
        registry = empty_registry()
        registry["entries"] = [entry]
        registry["head_entry_sha256"] = entry["entry_sha256"]
        registry["next_lineage_version"] = 2
        registry = seal_registry(registry)
        result = audit_genealogy_registry(registry)
        self.assertFalse(result["valid"])
        self.assertTrue(any("durable_evidence_record_set_sha256" in x for x in result["failures"]))

    def test_candidate_only_reconstruction_and_tamper_detection(self):
        candidate, parent, root_sha = "1"*40, "2"*40, "3"*40
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            recognition = repo / "omnipath/recognition"
            ledger = recognition / "attestation_ledger/v1/candidate"
            specimens = recognition / "regression/o22_5"
            ledger.mkdir(parents=True)
            specimens.mkdir(parents=True)

            names = ("false_consensus.json", "observer_collapse.json", "contradiction_erasure.json", "replay_divergence.json")
            specimen_hashes = {name: write_json(specimens / name, {"case": i}) for i, name in enumerate(names, 1)}
            report_hash = write_json(ledger / "o22_5_report.json", {"verdict": "CERTIFIED"})
            replay = {
                "order": "O22.6", "replay_status": "VERIFIED", "variant_count": 378,
                "cross_product_variant_count": 342, "final_pass_count": 0,
                "minimal_counterexample_count": 4, "specimen_count": 4,
                "specimen_sha256": specimen_hashes, "o22_5_report_sha256": report_hash, "failures": [],
            }
            replay_hash = write_json(ledger / "replay_manifest.json", replay)
            attestation = {
                "schema": "omnipath.o22-6-ci-attestation/v1", "order": "O22.6",
                "source_commit": candidate, "workflow_run_id": "100", "workflow_run_attempt": "1",
                "replay_job_result": "success", "external_ci_status": "SUCCESS", "promotion_eligible": True,
                "replay_artifact_id": "200", "replay_artifact_digest": "a"*64,
                "replay_manifest_sha256": replay_hash, "o22_5_report_sha256": report_hash,
                "specimen_sha256": specimen_hashes, "variant_count": 378,
                "cross_product_variant_count": 342, "final_pass_count": 0, "failures": [],
            }
            write_json(ledger / "ci_attestation.json", attestation)
            write_json(ledger / "specimen_hashes.json", specimen_hashes)
            write_json(ledger / "checkpoint_lineage.json", {"O21.3": root_sha})
            write_json(ledger / "promotion_record.json", {
                "recorded_promotion_allowed": True, "recorded_epistemic_state": "VERIFIED_WITHIN_SCOPE",
                "candidate_self_promoted": False,
            })
            write_json(ledger / "index.json", {
                "schema": "omnipath.durable-attestation-ledger/v1", "source_commit": candidate,
                "workflow_conclusion": "success", "recorded_epistemic_state": "VERIFIED_WITHIN_SCOPE",
            })

            component_names = (
                "index.json", "ci_attestation.json", "replay_manifest.json", "o22_5_report.json",
                "specimen_hashes.json", "checkpoint_lineage.json", "promotion_record.json",
            )
            durable = {
                "schema": "omnipath.durable-promotion-evidence-manifest/v1", "order": "fixture",
                "source_commit": candidate, "integration_parent_commit": parent,
                "components": {name: hashlib.sha256((ledger/name).read_bytes()).hexdigest() for name in component_names},
            }
            durable["record_set_sha256"] = canonical_sha256(durable)
            write_json(ledger / "promotion_manifest.json", durable)

            pmanifest = {
                "schema": "omnipath.o22-7-promotion-manifest/v1", "order": "O22.7",
                "candidate_id": "candidate-1", "candidate_commit_sha": candidate,
            }
            pmanifest["manifest_sha256"] = canonical_sha256(manifest_material(pmanifest))
            manifest_ref = "omnipath/recognition/promotion_manifests/candidate-1.json"
            write_json(repo / manifest_ref, pmanifest)
            write_json(recognition / "CONSTITUTIONAL_ROOT.lock.json", {"constitutional_root": {"commit_sha": root_sha}})

            entry = seal_entry({
                "schema": ENTRY_SCHEMA, "order": REGISTRY_ORDER, "accepted_by_gate": "O22.7",
                "lineage_version": 1, "candidate_id": "candidate-1", "candidate_commit_sha": candidate,
                "parent_commit_sha": parent, "rollback_commit_sha": parent, "constitutional_root_sha": root_sha,
                "checkpoint_commits": {}, "promotion_manifest_sha256": pmanifest["manifest_sha256"],
                "promotion_decision_sha256": "d"*64, "o22_6_attestation_sha256": canonical_sha256(attestation),
                "o22_6_workflow_run_id": "100", "o22_6_replay_artifact_id": "200",
                "o22_6_replay_artifact_digest": "a"*64, "previous_entry_sha256": None,
                "genealogy_contract_order": ORDER, "promotion_manifest_ref": manifest_ref,
                "durable_evidence_ledger_ref": "omnipath/recognition/attestation_ledger/v1/candidate",
                "durable_evidence_record_set_sha256": durable["record_set_sha256"],
                "durable_evidence_source_commit_sha": candidate,
            })
            registry = empty_registry()
            registry["entries"] = [entry]
            registry["head_entry_sha256"] = entry["entry_sha256"]
            registry["next_lineage_version"] = 2
            registry = seal_registry(registry)

            result = reconstruct_promotion_genealogy(registry, candidate, repo)
            self.assertTrue(result["verified"], result["failures"])
            self.assertEqual(result["path"]["constitutional_root_sha"], root_sha)
            self.assertEqual(len(result["path"]["specimen_sha256"]), 4)

            (specimens / names[0]).write_text('{"tampered":true}\n', encoding="utf-8")
            result = reconstruct_promotion_genealogy(copy.deepcopy(registry), candidate, repo)
            self.assertFalse(result["verified"])
            self.assertTrue(any(x.startswith("SPECIMEN_HASH:") for x in result["failures"]))


if __name__ == "__main__":
    unittest.main()
