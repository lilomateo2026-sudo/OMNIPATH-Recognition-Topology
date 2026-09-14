import tempfile
import unittest
from pathlib import Path

from recovery_replica_quorum import (
    EXPECTED_CONTENT_SHA256,
    EXPECTED_GIT_BLOB_SHA,
    quorum_restore,
    seed_replica,
)


class ReplicaQuorumTests(unittest.TestCase):
    def test_two_media_reconstruct_exact_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            a = root / "a"
            b = root / "b"
            out = root / "out"
            seed_replica("A", "raw", a)
            seed_replica("B", "base64", b)
            report = quorum_restore(a, b, out)
            self.assertEqual(report["verdict"], "PASS")
            self.assertEqual(report["quorum"], "2-of-2")
            self.assertEqual(report["content_sha256"], EXPECTED_CONTENT_SHA256)
            self.assertEqual(report["git_blob_sha"], EXPECTED_GIT_BLOB_SHA)
            self.assertFalse(report["primary_vault_required_during_restore"])
            self.assertTrue((out / "restored-evidence.bin").is_file())


if __name__ == "__main__":
    unittest.main()
