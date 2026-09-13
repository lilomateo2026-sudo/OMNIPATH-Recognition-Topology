import unittest

from attestation_gate import check_attestation


class O226GateTests(unittest.TestCase):
    def valid(self):
        return {
            "schema": "omnipath.o22-6-ci-attestation/v1",
            "order": "O22.6",
            "source_commit": "a" * 40,
            "workflow_run_id": "12345",
            "replay_job_result": "success",
            "replay_artifact_id": "67890",
            "replay_artifact_digest": "sha256:" + "b" * 64,
            "external_ci_status": "SUCCESS",
            "promotion_eligible": True,
            "replay_manifest_sha256": "c" * 64,
            "o22_5_report_sha256": "d" * 64,
            "specimen_sha256": {
                "a.json": "1" * 64,
                "b.json": "2" * 64,
                "c.json": "3" * 64,
                "d.json": "4" * 64,
            },
            "variant_count": 378,
            "cross_product_variant_count": 342,
            "final_pass_count": 0,
        }

    def test_accepts_complete_external_attestation(self):
        data = self.valid()
        result = check_attestation(data, data["source_commit"])
        self.assertTrue(result["promotion_allowed"])
        self.assertEqual(result["failures"], [])

    def test_rejects_missing_external_identity(self):
        data = self.valid()
        data["workflow_run_id"] = ""
        data["replay_artifact_id"] = ""
        result = check_attestation(data, data["source_commit"])
        self.assertFalse(result["promotion_allowed"])
        self.assertIn("workflow_run_id", result["failures"])
        self.assertIn("replay_artifact_id", result["failures"])

    def test_rejects_wrong_source_commit(self):
        data = self.valid()
        result = check_attestation(data, "f" * 40)
        self.assertFalse(result["promotion_allowed"])
        self.assertIn("source_commit", result["failures"])


if __name__ == "__main__":
    unittest.main()
