import json, unittest
from pathlib import Path
from v4.tri_generation_differential import run
ROOT=Path(__file__).resolve().parents[3]
MANIFEST=ROOT/"omnipath"/"recognition"/"v4"/"O28_2_tri_generation_differential.json"
class O282TriGenerationTests(unittest.TestCase):
    def test_tri_generation_differential(self):
        m=json.loads(MANIFEST.read_text(encoding="utf-8")); f=m["full_payload"]; s=m["semantic"]
        r=run(f["seed"],f["trials"],s["seed"],s["source_cases"])
        self.assertEqual(r["full_payload"]["mismatches"],f["expected_mismatches"])
        self.assertEqual(r["full_payload"]["digest_sha256"],f["expected_digest_sha256"])
        self.assertEqual(r["semantic"]["checks"],s["expected_checks"])
        self.assertEqual(r["semantic"]["semantic_mismatches"],s["expected_semantic_mismatches"])
        self.assertEqual(r["semantic"]["cross_version_mismatches"],s["expected_cross_version_mismatches"])
        self.assertEqual(r["semantic"]["digest_sha256"],s["expected_digest_sha256"])
        self.assertFalse(m["authority"]["promotion_authority"])
if __name__=="__main__": unittest.main()
