import json
import unittest
from pathlib import Path
from v5.replay_pathology_tournament import run

ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / "omnipath" / "recognition" / "v5" / "O30_5_replay_pathology_tournament.json"

class O305ReplayTournamentTests(unittest.TestCase):
    def test_replay_tournament_is_stable(self):
        expected = json.loads(REPORT.read_text(encoding="utf-8"))
        observed = run()
        self.assertEqual(observed["total_replays"], expected["total_replays"])
        self.assertEqual(observed["real_counterexample_count"], 0)
        self.assertEqual(observed["unminimized_real_counterexamples"], 0)
        self.assertEqual(observed["selected_genome"], "C")
        self.assertEqual(observed["tournament_digest_sha256"], expected["tournament_digest_sha256"])
        for genome in expected["genomes"]:
            self.assertEqual(observed["genomes"][genome], expected["genomes"][genome])

if __name__ == "__main__":
    unittest.main()
