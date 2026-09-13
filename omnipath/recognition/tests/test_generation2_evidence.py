import copy
import hashlib
import json
import random
import unittest
from pathlib import Path

from adversarial.full_payload_mutation_tournament import OPERATORS, baseline_envelope, detect_pathologies, disposition, mutate, run as run_payload
from evolution.cross_rail_evolution import run as run_rails

ROOT = Path(__file__).resolve().parents[3]
META = ROOT / "omnipath" / "recognition" / "reports" / "O24_4_metamorphic_invariants.json"
VAULT = ROOT / "omnipath" / "recognition" / "counterexample_vault" / "O24_5_manifest.json"
TRANSFORMS = ("reverse_scope", "reverse_constraints", "metadata", "reverse_contradictions", "reorder", "clone_observer")


def classify(value):
    paths = detect_pathologies(value, baseline_envelope())
    return sorted(paths), disposition(paths)


def equivalent(value, name):
    item = copy.deepcopy(value)
    if name == "reverse_scope": item["evidence_scope"] = list(reversed(item["evidence_scope"]))
    elif name == "reverse_constraints": item["scope_constraints"] = list(reversed(item["scope_constraints"]))
    elif name == "metadata": item["non_semantic_metadata"] = {"version": 1}
    elif name == "reverse_contradictions": item["contradictory_evidence"] = list(reversed(item["contradictory_evidence"]))
    elif name == "reorder": item = {key: item[key] for key in reversed(list(item.keys()))}
    elif name == "clone_observer": item["observer_boundary"] = dict(item["observer_boundary"])
    return item


def ddmin(values, fails):
    current = list(values)
    changed = True
    while changed and len(current) > 1:
        changed = False
        for index in range(len(current)):
            candidate = current[:index] + current[index + 1:]
            if candidate and fails(candidate):
                current = candidate
                changed = True
                break
    return current


class Generation2EvidenceTests(unittest.TestCase):
    def test_o243_rails_are_disjoint(self):
        result = run_rails(512)
        self.assertTrue(result["independence_pass"])
        self.assertEqual(result["shared_discovery_ids"], [])
        self.assertEqual(result["shared_source_event_ids"], [])
        self.assertEqual(result["reference"]["digest_sha256"], "45d17e6b7ebb0ace2a997a68d330d295a647e056aee7884e1d945e7638835b58")
        self.assertEqual(result["evidence"]["digest_sha256"], "dcf76ad3ab76a1c2c6ba7f9259c5350c098f795a26b8fc1c44da127ecc5b6ca7")

    def test_o244_metamorphic_invariants(self):
        expected = json.loads(META.read_text(encoding="utf-8"))
        rng = random.Random(expected["seed"])
        baseline = baseline_envelope()
        rows = []
        for case in range(1, expected["source_cases"] + 1):
            width = rng.choice([0, 1, 2, 3])
            ops = tuple(sorted(rng.sample(OPERATORS, width))) if width else ()
            source = mutate(baseline, ops)
            before = classify(source)
            for name in TRANSFORMS:
                after = classify(equivalent(source, name))
                rows.append({"case": case, "transformation": name, "operators": list(ops), "expected": before, "actual": after, "pass": after == before})
        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":"))
        self.assertEqual(len(rows), expected["expected_checks"])
        self.assertEqual(sum(not row["pass"] for row in rows), expected["expected_violations"])
        self.assertEqual(hashlib.sha256(canonical.encode("utf-8")).hexdigest(), expected["expected_digest_sha256"])
        controls = ("drop_provenance_source", "drift_replay_seed", "escalate_observer_authority", "widen_scope", "swap_lineage_parent", "erase_contradiction")
        self.assertTrue(all(classify(mutate(baseline, (operator,)))[0] for operator in controls))

    def test_o245_minimization_vault(self):
        vault = json.loads(VAULT.read_text(encoding="utf-8"))
        payload = run_payload(seed=2402001, trials=3000)
        self.assertEqual(payload["escape_count"], vault["discovered_escape_count"])
        control = vault["synthetic_minimizer_control"]
        minimized = ddmin(control["input"], lambda values: "swap_lineage_parent" in values)
        self.assertEqual(minimized, control["expected_minimal"])
        self.assertFalse(control["production_evidence"])


if __name__ == "__main__":
    unittest.main()
