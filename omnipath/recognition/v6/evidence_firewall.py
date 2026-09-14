#!/usr/bin/env python3
"""O32.2 read-only evidence firewall for consciousness_space and HITM provenance."""
from __future__ import annotations

import copy
import hashlib
import json

EVIDENCE_CLASSES = {"consciousness_space", "HITM"}
AUTHORITY_KEYS = {
    "promotion_authority",
    "merge_authority",
    "main_mutation_authority",
    "repository_write",
    "self_promote",
    "expected_head_sha",
    "git_ref_update",
}


def _contains_authority(value) -> bool:
    if isinstance(value, dict):
        if any(str(key) in AUTHORITY_KEYS for key in value):
            return True
        return any(_contains_authority(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_authority(item) for item in value)
    return False


def admit(record: dict) -> dict:
    value = copy.deepcopy(record)
    evidence_class = value.get("evidence_class")
    if evidence_class not in EVIDENCE_CLASSES:
        raise ValueError("unknown evidence class")
    if _contains_authority(value):
        raise ValueError("authority-bearing evidence rejected")
    if not isinstance(value.get("source_id"), str) or not value["source_id"]:
        raise ValueError("source_id required")
    if not isinstance(value.get("content_digest"), str) or not value["content_digest"]:
        raise ValueError("content_digest required")
    return {
        "evidence_class": evidence_class,
        "source_id": value["source_id"],
        "content_digest": value["content_digest"],
        "payload": copy.deepcopy(value.get("payload")),
        "read_only": True,
        "repository_capabilities": {
            "promote": False,
            "merge": False,
            "mutate_main": False,
            "update_ref": False,
        },
    }


def run_injection_matrix() -> dict:
    rows = []
    for evidence_class in sorted(EVIDENCE_CLASSES):
        for key in sorted(AUTHORITY_KEYS):
            for depth in (0, 1, 2):
                packet = {
                    "evidence_class": evidence_class,
                    "source_id": "fixture",
                    "content_digest": "sha256:fixture",
                    "payload": {"observation": "safe"},
                }
                target = packet
                if depth == 1:
                    target = packet["payload"]
                elif depth == 2:
                    packet["payload"]["nested"] = {}
                    target = packet["payload"]["nested"]
                target[key] = True
                try:
                    admit(packet)
                    decision = "ESCAPE"
                except ValueError:
                    decision = "REJECT"
                rows.append({"class": evidence_class, "key": key, "depth": depth, "decision": decision})
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    return {
        "schema": "omnipath.evidence-firewall-matrix/v1",
        "order": "O32.2",
        "attempts": len(rows),
        "escape_count": sum(row["decision"] == "ESCAPE" for row in rows),
        "digest_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    }
