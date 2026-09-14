import json
import unittest
from pathlib import Path
from v5.genome_quintet import run

ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / "omnipath" / "recognition" / "v5" / "O30_3_genome_quintet.json"

class O303GenomeQuintetTests(unittest.TestCase):
    def test_quintet_is_deterministic_and_disjoint(self):
        expected = json.loads(REPORT.read_text(encoding="utf-8"))
        observed = run(expected["events_per_genome"])
        self.assertEqual(observed["shared_discovery_ids"], 0)
        self.assertEqual(observed["shared_source_event_ids"], 0)
        self.assertEqual(observed["digest_sha256"], expected["digest_sha256"])
        for genome, data in expected["genomes"].items():
            self.assertEqual(observed["genomes"][genome]["stream_digest_sha256"], data["stream_digest_sha256"])

    def test_all_forks_share_only_the_declared_parent(self):
        expected = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertTrue(expected["experimental_only"])
        self.assertEqual(len({item["namespace"] for item in expected["genomes"].values()}), 5)
        self.assertEqual(len({item["seed"] for item in expected["genomes"].values()}), 5)

if __name__ == "__main__":
    unittest.main()
