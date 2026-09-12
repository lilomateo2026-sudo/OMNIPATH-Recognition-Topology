# OMNIPATH Recognition Transfer Contract

Status: CONSTITUTIONAL ROOT
Order: O21.3
Repository: lilomateo2026-sudo/OMNIPATH-Recognition-Topology

## Purpose

This contract defines the minimum evidence envelope and constitutional invariants for transferring recognition results between model runs, observer layers, topology rails, and later promotion tribunals.

A transfer is evidence transport, not proof of absolute knowledge. Agreement between systems, branches, observers, or repeated runs MUST NOT be represented as certainty beyond the evidence and scope recorded here.

## Required Transfer Envelope

Every recognition transfer MUST preserve or explicitly mark unavailable:

1. `run_id` — unique execution identity.
2. `model_identity` — model family/name plus immutable version or revision when available.
3. `quantization` — quantization/runtime representation when applicable.
4. `seed` — generation or simulation seed when applicable.
5. `prompt_hash` — digest of the exact normalized input/prompt used for the run.
6. `trajectory_representation` — ordered representation of the reasoning/recognition trajectory that is safe and intended for system inspection.
7. `recognition_vector` — structured recognition/features emitted by the run.
8. `c_observer_judgment` — C-position observer judgment kept distinct from raw observations.
9. `provenance` — source lineage, transforms, parent artifacts, and evidence origins.
10. `replay_metadata` — runtime/configuration values required to reproduce or compare the result.
11. `promotion_state` — lifecycle state of the artifact or candidate.
12. `evidence_scope` — what the evidence does and does not support.

## Epistemic State

The highest constitutional assertion permitted by this root contract is:

`VERIFIED_WITHIN_SCOPE`

That state is valid only when the record includes:

- supporting evidence references;
- exact configuration and model versions;
- relevant invariants checked;
- replay or comparison metadata;
- declared scope and known limitations.

The labels `ABSOLUTE`, `ABSOLUTELY_KNOWN`, `INFALLIBLE`, or semantic equivalents MUST NOT be used as promotion states.

## Constitutional Invariants

### I1 — Evidence / Judgment Separation
Raw observation, derived recognition, C-observer judgment, and promotion decision MUST remain separately identifiable. A later judgment may reference evidence but MUST NOT silently rewrite the evidence that preceded it.

### I2 — Provenance Preservation
Every transferred artifact MUST retain reconstructable ancestry sufficient to identify its source run, model/configuration, parent artifact where applicable, and transformations applied in transit.

### I3 — Replay Identity
When deterministic replay is claimed, the record MUST contain enough metadata to test that claim. A replay mismatch MUST be recorded as a mismatch rather than normalized into agreement.

### I4 — Dual-Rail Independence
Reference-transfer and evidence-transfer rails MAY compare results but MUST preserve distinct lineage. Agreement across rails increases evidence only within the recorded scope; it does not convert correlation into certainty.

### I5 — No Authority by Self-Assertion
A candidate, model run, observer, branch, or descendant MUST NOT promote itself solely because it produced the evidence under review. Promotion authority remains external to the candidate being evaluated.

### I6 — Contradiction Retention
Material contradictions between runs, rails, observers, or replay outcomes MUST remain represented until adjudicated. Contradictory evidence MUST NOT be discarded merely to produce a cleaner consensus.

### I7 — Scope-Bound Verification
Any verified state MUST identify the exact evidence/configuration/model versions/invariants under which verification was reached. Changes to those inputs create a new verification context.

### I8 — Promotion Is Reversible
Promotion state MUST be reconstructable and reversible through preserved lineage. Rollback MUST NOT destroy the evidence required to explain the prior promotion.

## Canonical Promotion States

- `OBSERVED`
- `COMPARED`
- `REPLAYED`
- `CONTRADICTED`
- `VERIFIED_WITHIN_SCOPE`
- `REJECTED`
- `ROLLED_BACK`

Additional states MAY be introduced by later constitutional orders, but they MUST NOT weaken the invariants in this root contract without an explicit constitutional amendment process.

## Transfer Rule

A transfer is admissible only when the receiving layer can distinguish:

`source evidence -> derived recognition -> observer judgment -> promotion state`

If any boundary is collapsed, provenance is incomplete, or the claimed verification scope cannot be reconstructed, the transfer MUST remain non-promotable until repaired.

## Root Boundary

This O21.3 document is the initial constitutional transfer contract for the recognition topology. Later schemas, pathology rules, A/B branch experiments, and tribunals may extend its representation, but they MUST preserve the evidence/judgment separation, provenance, replay identity, contradiction retention, and scope-bound verification defined above unless a later explicit constitutional amendment supersedes this root.
