"""O22.4 mutation tournament contract."""

ORDER = "O22.4"
PARENT_ORDER = "O22.3"
PARENT_SHA = "12c3ff5c362ba7c8fcdd33f3c7089243e468abfc"
VERSION = "omnipath.boundary-tournament/v1"
DIMENSIONS = (
    "severity",
    "promotion_effect",
    "provenance",
    "replay",
    "contradictions",
    "epistemic_state",
)
NONPASS = frozenset({"QUARANTINE", "REJECT"})
