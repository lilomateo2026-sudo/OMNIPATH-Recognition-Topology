"""O22.7 Recognition Promotion Manifest Gate."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

from attestation_gate import check_attestation

MANIFEST_SCHEMA = "omnipath.o22-7-promotion-manifest/v1"
ORDER = "O22.7"
EXPECTED_EPISTEMIC_CEILING = "VERIFIED_WITHIN_SCOPE"

CANONICAL_CHECKPOINTS = {
    "O22.2": "e469b447d497f6533487fbf9098b1a6152d2d494",
    "O22.3": "12c3ff5c362ba7c8fcdd33f3c7089243e468abfc",
    "O22.4": "8875873a3eb8420a5e16a43fde285e2ca20c3423",
    "O22.5": "f8ca61a8e08723232afd8037f9eb9a639847d0b7",
    "O22.6": "ab1235e5cd90a9d327e7dca94464f35b71fdcde1",
}


def canonical_sha256(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def manifest_material(manifest: dict[str, Any]) -> dict[str, Any]:
    material = copy.deepcopy(manifest)
    material.pop("manifest_sha256", None)
    material.pop("promotion_status", None)
    return material


def seal_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    sealed = copy.deepcopy(manifest)
    sealed.pop("promotion_status", None)
    sealed["manifest_sha256"] = canonical_sha256(manifest_material(sealed))
    return sealed
