#!/usr/bin/env python3
"""O22.2 OMNIPATH Recognition Pathology Validator.

Validates O22.1 pathology records against the JSON schema and O21.3/O21.4
constitutional lineage. The validator never mutates the submitted record.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Iterable

VALIDATOR_VERSION = "omnipath.recognition-pathology-validator/v1"
EXPECTED_SCHEMA_VERSION = "omnipath.recognition-pathology/v1"
EXPECTED_ROOT_ORDER = "O21.3"
EXPECTED_FREEZE_ORDER = "O21.4"

HERE = Path(__file__).resolve().parent
DEFAULT_SCHEMA = HERE / "RECOGNITION_PATHOLOGY.schema.json"
DEFAULT_LOCK = HERE / "CONSTITUTIONAL_ROOT.lock.json"

_DECISION_RANK = {"PASS": 0, "QUARANTINE": 1, "REJECT": 2}


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _json_type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def _validate_schema(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    """Validate the JSON-Schema subset used by O22.1.

    Supported keywords: type, const, enum, required, properties,
    additionalProperties=false, minLength, minimum, maximum, minItems, items,
    allOf, if, then. This is intentionally small and dependency-free.
    """
    errors: list[str] = []

    expected_type = schema.get("type")
    if expected_type is not None:
        options = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(_json_type_matches(instance, option) for option in options):
            errors.append(f"{path}: type must be one of {options!r}")
            return errors

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: value must equal const {schema['const']!r}")

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: value must be one of {schema['enum']!r}")

    if isinstance(instance, str) and "minLength" in schema:
        if len(instance) < int(schema["minLength"]):
            errors.append(f"{path}: string shorter than minLength={schema['minLength']}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: number below minimum={schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: number above maximum={schema['maximum']}")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < int(schema["minItems"]):
            errors.append(f"{path}: array shorter than minItems={schema['minItems']}")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(instance):
                errors.extend(_validate_schema(item, item_schema, f"{path}[{index}]"))

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                errors.append(f"{path}: missing required property {key!r}")

        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extras = sorted(set(instance) - set(properties))
            for key in extras:
                errors.append(f"{path}: additional property {key!r} is forbidden")

        for key, child_schema in properties.items():
            if key in instance and isinstance(child_schema, dict):
                errors.extend(_validate_schema(instance[key], child_schema, f"{path}.{key}"))

    # JSON Schema "if" does not itself contribute errors.
    if_schema = schema.get("if")
    if isinstance(if_schema, dict):
        condition_errors = _validate_schema(instance, if_schema, path)
        if not condition_errors and isinstance(schema.get("then"), dict):
            errors.extend(_validate_schema(instance, schema["then"], path))

    for subschema in schema.get("allOf", []):
        if isinstance(subschema, dict):
            errors.extend(_validate_schema(instance, subschema, path))

    return errors


def _schema_contract_errors(
    schema: dict[str, Any], root_lock: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    root = root_lock.get("constitutional_root", {})
    expected_root_sha = root.get("commit_sha")
    expected_ceiling = root_lock.get("epistemic_ceiling")

    if root.get("root_order") != EXPECTED_ROOT_ORDER:
        errors.append("ROOT_LOCK_ORDER_MISMATCH")
    if root_lock.get("order") != EXPECTED_FREEZE_ORDER:
        errors.append("FREEZE_ORDER_MISMATCH")
    if root_lock.get("status") != "FROZEN":
        errors.append("ROOT_LOCK_NOT_FROZEN")

    try:
        schema_version = schema["properties"]["schema_version"]["const"]
    except (KeyError, TypeError):
        schema_version = None
    if schema_version != EXPECTED_SCHEMA_VERSION:
        errors.append("SCHEMA_VERSION_DRIFT")

    try:
        schema_root_sha = schema["properties"]["provenance"]["properties"][
            "constitutional_root_sha"
        ]["const"]
    except (KeyError, TypeError):
        schema_root_sha = None
    if not expected_root_sha or schema_root_sha != expected_root_sha:
        errors.append("SCHEMA_ROOT_SHA_DRIFT")

    rules = schema.get("x-omnipath-constitutional-rules", {})
    for key in (
        "evidence_judgment_separation",
        "contradictions_must_be_retained",
        "agreement_is_not_absolute_proof",
        "self_promotion_forbidden",
    ):
        if rules.get(key) is not True:
            errors.append(f"SCHEMA_RULE_DISABLED:{key}")
    if rules.get("verification_ceiling") != expected_ceiling:
        errors.append("SCHEMA_EPISTEMIC_CEILING_DRIFT")

    freeze_rules = root_lock.get("freeze_rules", {})
    for key in (
        "descendants_must_retain_root_as_ancestor",
        "root_contract_must_not_be_silently_rewritten",
        "constitutional_changes_require_explicit_amendment_lineage",
        "recognition_promotions_must_reference_root_or_valid_amendment",
        "force_replacement_of_root_identity_is_nonconformant",
    ):
        if freeze_rules.get(key) is not True:
            errors.append(f"ROOT_FREEZE_RULE_DISABLED:{key}")

    return errors


def _escalate(current: str, target: str) -> str:
    return target if _DECISION_RANK[target] > _DECISION_RANK[current] else current


def _add_reason(reasons: list[dict[str, str]], code: str, detail: str) -> None:
    reasons.append({"code": code, "detail": detail})


def validate_pathology(
    record: dict[str, Any],
    schema: dict[str, Any],
    root_lock: dict[str, Any],
) -> dict[str, Any]:
    """Return a deterministic PASS/QUARANTINE/REJECT decision.

    PASS is only a gate disposition; it never means "absolute truth". The
    underlying promotion_effect remains authoritative and is echoed verbatim.
    """
    original = copy.deepcopy(record)
    decision = "PASS"
    reasons: list[dict[str, str]] = []

    config_errors = _schema_contract_errors(schema, root_lock)
    if config_errors:
        decision = "REJECT"
        for code in sorted(config_errors):
            _add_reason(reasons, code, "validator schema/root lock contract drift detected")
        schema_errors: list[str] = []
    else:
        schema_errors = sorted(set(_validate_schema(record, schema)))
        if schema_errors:
            decision = "REJECT"
            for error in schema_errors:
                _add_reason(reasons, "SCHEMA_VIOLATION", error)

    if decision != "REJECT":
        pathology_type = record["pathology_type"]
        severity = record["severity"]
        promotion_effect = record["promotion_effect"]
        contradictions = record.get("contradictions", [])
        replay = record.get("replay")

        if pathology_type == "LINEAGE_CORRUPTION":
            decision = _escalate(decision, "REJECT")
            _add_reason(
                reasons,
                "LINEAGE_CORRUPTION",
                "corrupted lineage cannot satisfy reconstructable ancestry",
            )
        elif pathology_type == "PROVENANCE_LOSS":
            decision = _escalate(decision, "QUARANTINE")
            _add_reason(
                reasons,
                "PROVENANCE_REPAIR_REQUIRED",
                "provenance loss must remain non-promotable until repaired",
            )

        if severity in {"MEDIUM", "HIGH"}:
            decision = _escalate(decision, "QUARANTINE")
            _add_reason(reasons, "SEVERITY_HOLD", f"severity={severity}")
        elif severity == "CRITICAL":
            decision = _escalate(decision, "REJECT")
            _add_reason(reasons, "CRITICAL_PATHOLOGY", "severity=CRITICAL")

        if promotion_effect in {"HOLD", "REQUIRE_REPLAY", "REQUIRE_ADJUDICATION"}:
            decision = _escalate(decision, "QUARANTINE")
            _add_reason(
                reasons,
                "PROMOTION_BLOCKED",
                f"promotion_effect={promotion_effect}",
            )
        elif promotion_effect in {"REJECT", "ROLLBACK"}:
            decision = _escalate(decision, "REJECT")
            _add_reason(
                reasons,
                "PROMOTION_REJECTED",
                f"promotion_effect={promotion_effect}",
            )

        active_contradictions = [
            item for item in contradictions if item.get("status") != "RESOLVED"
        ]
        if active_contradictions:
            decision = _escalate(decision, "QUARANTINE")
            _add_reason(
                reasons,
                "CONTRADICTIONS_RETAINED",
                f"{len(active_contradictions)} contradiction(s) remain OPEN/EXPLAINED",
            )

        if replay and replay.get("claimed_deterministic") is True:
            if replay.get("match") is not True:
                decision = _escalate(decision, "QUARANTINE")
                _add_reason(
                    reasons,
                    "DETERMINISTIC_REPLAY_MISMATCH",
                    "claimed deterministic replay did not produce an exact match",
                )

        epistemic_state = record.get("epistemic_state")
        if epistemic_state in {"REJECTED", "ROLLED_BACK"}:
            decision = _escalate(decision, "REJECT")
            _add_reason(
                reasons,
                "TERMINAL_EPISTEMIC_STATE",
                f"epistemic_state={epistemic_state}",
            )

    # The exact contradiction payload is preserved in the result.
    preserved_contradictions = copy.deepcopy(original.get("contradictions", []))
    root = root_lock.get("constitutional_root", {})
    input_hash = _sha256(original)
    schema_hash = _sha256(schema)
    lock_hash = _sha256(root_lock)

    reason_codes = [item["code"] for item in reasons]
    decision_material = {
        "validator_version": VALIDATOR_VERSION,
        "input_sha256": input_hash,
        "schema_sha256": schema_hash,
        "root_lock_sha256": lock_hash,
        "decision": decision,
        "reason_codes": reason_codes,
    }

    result = {
        "validator_version": VALIDATOR_VERSION,
        "decision": decision,
        "promotion_effect": original.get("promotion_effect"),
        "epistemic_state": original.get("epistemic_state"),
        "reasons": reasons,
        "preserved_contradictions": preserved_contradictions,
        "provenance": {
            "input_sha256": input_hash,
            "schema_sha256": schema_hash,
            "root_lock_sha256": lock_hash,
            "constitutional_root_sha": root.get("commit_sha"),
            "constitutional_root_order": root.get("root_order"),
            "root_freeze_order": root_lock.get("order"),
            "decision_sha256": _sha256(decision_material),
        },
    }

    # Guardrail: validation must not mutate the caller's record.
    if record != original:
        raise RuntimeError("validator mutated the input record")

    return result


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _emit(result: dict[str, Any], pretty: bool) -> None:
    if pretty:
        text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False)
    else:
        text = json.dumps(
            result, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
    sys.stdout.write(text + "\n")


def _parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate an O22.1 OMNIPATH recognition pathology record."
    )
    parser.add_argument("record", type=Path, help="path to pathology JSON record")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--root-lock", type=Path, default=DEFAULT_LOCK)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = _parse_args(argv)
    schema = _load_json(args.schema)
    root_lock = _load_json(args.root_lock)

    try:
        record = _load_json(args.record)
    except (OSError, json.JSONDecodeError) as exc:
        raw = b""
        try:
            raw = args.record.read_bytes()
        except OSError:
            pass
        result = {
            "validator_version": VALIDATOR_VERSION,
            "decision": "REJECT",
            "promotion_effect": None,
            "epistemic_state": None,
            "reasons": [
                {"code": "UNREADABLE_RECORD", "detail": exc.__class__.__name__}
            ],
            "preserved_contradictions": [],
            "provenance": {
                "input_sha256": hashlib.sha256(raw).hexdigest(),
                "schema_sha256": _sha256(schema),
                "root_lock_sha256": _sha256(root_lock),
                "constitutional_root_sha": root_lock.get(
                    "constitutional_root", {}
                ).get("commit_sha"),
                "constitutional_root_order": root_lock.get(
                    "constitutional_root", {}
                ).get("root_order"),
                "root_freeze_order": root_lock.get("order"),
                "decision_sha256": hashlib.sha256(
                    b"UNREADABLE_RECORD:" + hashlib.sha256(raw).digest()
                ).hexdigest(),
            },
        }
    else:
        if not isinstance(record, dict):
            result = {
                "validator_version": VALIDATOR_VERSION,
                "decision": "REJECT",
                "promotion_effect": None,
                "epistemic_state": None,
                "reasons": [
                    {
                        "code": "SCHEMA_VIOLATION",
                        "detail": "$: top-level record must be an object",
                    }
                ],
                "preserved_contradictions": [],
                "provenance": {
                    "input_sha256": _sha256(record),
                    "schema_sha256": _sha256(schema),
                    "root_lock_sha256": _sha256(root_lock),
                    "constitutional_root_sha": root_lock.get(
                        "constitutional_root", {}
                    ).get("commit_sha"),
                    "constitutional_root_order": root_lock.get(
                        "constitutional_root", {}
                    ).get("root_order"),
                    "root_freeze_order": root_lock.get("order"),
                    "decision_sha256": _sha256(
                        {
                            "validator_version": VALIDATOR_VERSION,
                            "decision": "REJECT",
                            "input": _sha256(record),
                            "reason": "TOP_LEVEL_NOT_OBJECT",
                        }
                    ),
                },
            }
        else:
            result = validate_pathology(record, schema, root_lock)

    _emit(result, args.pretty)
    return {"PASS": 0, "QUARANTINE": 2, "REJECT": 3}[result["decision"]]


if __name__ == "__main__":
    raise SystemExit(main())
