import copy
import hashlib
import json
import random
import unittest
from pathlib import Path

from adversarial.full_payload_mutation_tournament import (
    OPERATORS,
    apply_operator,
    baseline_envelope,
    detect_pathologies,
    disposition,
)

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "omnipath" / "recognition" / "v4" / "O28_1_v4_genesis.json"
V3_PARENT = "ba8a83d3b2def74ded2bbf9154c6190940ebd888"
V4_PARENT = "e031ff386c426b6644c01d94da3009628c0cf1e4"


def version_baseline(parent: str, self_id: str) -> dict:
    value = baseline_envelope()
    value["lineage"]["parent"] = parent
    value["lineage"]["self"] = self_id
    return value


def mutate(value: dict, operators: tuple[str, ...]) -> dict:
    result = copy.deepcopy(value)
    for operator in operators:
        result = apply_operator(result, operator)
    return result


class O28V4GenesisTests(unittest.TestCase):
    def test_v4_cross_version_differential_is_stable(self):
        expected = json.loads(MANIFEST.read_text(encoding="utf-8"))
        config = expected["cross_version_differential"]
        rng = random.Random(config["seed"])
        v3 = version_baseline(V3_PARENT, "candidate-v3-promoted")
        v4 = version_baseline(V4_PARENT, "candidate-v4")
        rows = []
        mismatches = 0

        for trial in range(1, config["trials"] + 1):
            width = rng.choice(config["mutation_widths"])
            operators = tuple(sorted(rng.sample(OPERATORS, width)))
            v3_pathologies = sorted(detect_pathologies(mutate(v3, operators), v3))
            v4_pathologies = sorted(detect_pathologies(mutate(v4, operators), v4))
            v3_disposition = disposition(set(v3_pathologies))
            v4_disposition = disposition(set(v4_pathologies))
            mismatch = v3_pathologies != v4_pathologies or v3_disposition != v4_disposition
            mismatches += int(mismatch)
            rows.append({
                "trial": trial,
                "operators": list(operators),
                "v3_pathologies": v3_pathologies,
                "v4_pathologies": v4_pathologies,
                "v3_disposition": v3_disposition,
                "v4_disposition": v4_disposition,
                "mismatch": mismatch,
            })

        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        self.assertEqual(mismatches, config["expected_mismatches"])
        self.assertEqual(digest, config["expected_digest_sha256"])

    def test_v4_authority_is_reset(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        authority = manifest["authority_reset"]
        self.assertFalse(authority["inherits_promotion_authority"])
        self.assertTrue(authority["self_promotion_forbidden"])
        self.assertFalse(authority["main_mutation_authority"])
        self.assertEqual(authority["promotion_state"], "OBSERVED")
        self.assertTrue(authority["fresh_descendant_ci_required"])
        self.assertTrue(authority["new_promotion_tribunal_required"])


if __name__ == "__main__":
    unittest.main()
