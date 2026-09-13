import copy
import hashlib
import json
import random
import unittest

from adversarial.full_payload_mutation_tournament import (
    OPERATORS,
    apply_operator,
    baseline_envelope,
    detect_pathologies,
    disposition,
)

GEN2_PARENT = "dc296965c43e75fd3fab53eea3a96aaccc381a10"
V3_PARENT = "7da284d50db46457a17bc259186332394b95583f"
EXPECTED_DIGEST = "57464c74724323dc02fad7cea7dee901f2d40cca65ef74d4d9cf58750281626f"


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


class O26V3GenesisTests(unittest.TestCase):
    def test_cross_version_differential_mutation_is_stable(self):
        rng = random.Random(2601001)
        gen2 = version_baseline(GEN2_PARENT, "candidate-o24")
        v3 = version_baseline(V3_PARENT, "candidate-o26-v3")
        rows = []
        mismatches = 0

        for trial in range(1, 2501):
            width = rng.choice([1, 2, 3, 4, 5])
            operators = tuple(sorted(rng.sample(OPERATORS, width)))
            gen2_pathologies = sorted(detect_pathologies(mutate(gen2, operators), gen2))
            v3_pathologies = sorted(detect_pathologies(mutate(v3, operators), v3))
            gen2_disposition = disposition(set(gen2_pathologies))
            v3_disposition = disposition(set(v3_pathologies))
            mismatch = (
                gen2_pathologies != v3_pathologies
                or gen2_disposition != v3_disposition
            )
            mismatches += int(mismatch)
            rows.append(
                {
                    "trial": trial,
                    "operators": list(operators),
                    "gen2_pathologies": gen2_pathologies,
                    "v3_pathologies": v3_pathologies,
                    "gen2_disposition": gen2_disposition,
                    "v3_disposition": v3_disposition,
                    "differential_mismatch": mismatch,
                }
            )

        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        self.assertEqual(mismatches, 0)
        self.assertEqual(digest, EXPECTED_DIGEST)

    def test_v3_has_no_inherited_promotion_authority(self):
        v3 = version_baseline(V3_PARENT, "candidate-o26-v3")
        self.assertEqual(v3["promotion_state"], "OBSERVED")
        self.assertIn("no-self-promotion", v3["scope_constraints"])
        self.assertNotEqual(v3["observer_boundary"]["authority"], "promote")


if __name__ == "__main__":
    unittest.main()
