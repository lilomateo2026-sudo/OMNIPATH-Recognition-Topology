# O-PHI-FG Cross-Ecosystem Synthesis — 2026-10-19

Status: PROPOSED RESEARCH HANDOFF. Does not modify sealed O-PHI-FG-011/-012 or running/armed state.

## Cross-ecosystem observations
1. Nix decade study: 1,321,000 package builds; 166,523 preserved diffoscope reports; bitwise reproducibility reached up to 93% in 2024. Lesson: rebuildability and byte identity are separate properties.
2. Binary-equivalence research: 14,156 independently built JAR pairs; 3,750 pairs (26.49%) contained at least one differing class. Lesson: SHA mismatch begins forensics; it does not finish equivalence analysis.
3. DALEQ: 2,714 JAR pairs / 265,690 class pairs; explanation proofs accompany equivalence normalization. Lesson: a drift verdict should carry a derivation.
4. Reproducible Builds Sep-2026: PGO profiling can become nondeterministic through runtime-randomized HashMap behavior; reprotest also fixed filesystem-order variation. Lesson: generated profiles, file ordering and runtime randomness are build inputs/variance dimensions.
5. Debian .buildinfo: records architecture, installed build dependencies and environment for forensic reconstruction. Lesson: preserve a portable environment receipt per build.
6. SLSA + in-toto: represent buildDefinition, resolvedDependencies, builder identity and ordered signed steps. Lesson: provenance is a graph/chain, not one checksum.
7. Google OSS Rebuild: independent rebuilders originate/validate build attestations for npm, PyPI and crates.io. Lesson: multiple witnesses can independently strengthen artifact confidence.
8. Sigstore Rekor: append-only transparency log for signed metadata. Lesson: receipts should be chained and externally auditable.
9. Red Hat Hummingbird: reproducibility must be exercised by rebuilding, not merely declared. Lesson: a dormant reproducibility claim is not evidence.
10. Kettle / Attestable Build Chain: attest toolchain, environment and actual build execution, not only final bytes. Lesson: artifact identity and process identity need separate evidence.

## New O-PHI sequence language
DECLARE -> OBSERVE -> BUILD -> PERTURB -> REBUILD -> COMPARE -> EXPLAIN -> ATTEST -> ANCHOR -> REPLAY

Formal sketch:
BUILD := DECLARED_INPUTS + RESOLVED_DEPS + OBSERVED_EXECUTION -> ARTIFACT
TWIN := BUILD(node_A) || BUILD(node_B)
DRIFT := SHA(ARTIFACT_A) != SHA(ARTIFACT_B)
EXPLANATION := NORMALIZE(DIFF, VARIANCE_VECTOR) -> {class, evidence, derivation}
TRUST := BYTE_IDENTITY + PROVENANCE_MATCH + EXECUTION_MATCH + WITNESS_CONSENSUS

## O-PHI-FG witness grammar v1
Every execution receipt should bind:
- order_id / parent_receipt_sha256
- source_sha256 / build_recipe_sha256
- compiler_binary_sha256 / linker_sha256
- resolved_dependency digests
- builder/node identity + architecture + kernel
- environment: locale, timezone, cwd, SOURCE_DATE_EPOCH, env digest
- runtime variance vector: file order, thread count, random seed, PGO profile digest, CPU feature set
- observed execution digest and relevant byproduct digests
- artifact_sha256
- first differing offset / diffoscope report digest
- equivalence level and drift class
- explanation/derivation digest
- witness signatures or node receipts

## Equivalence ladder
L0 BYTE_IDENTICAL
L1 CONTAINER_OR_METADATA_DRIFT
L2 STRUCTURAL_EQUIVALENCE
L3 SEMANTIC_EQUIVALENCE_SUPPORTED
L4 UNCLASSIFIED_DRIFT
L5 BEHAVIORAL_DIVERGENCE

Rule: normalization may classify a mismatch but must never erase the original bytes, original SHA, or raw diff evidence.

## Proposed next design function
O-PHI-FG-015 — WITNESS GRAPH TRIBUNAL (PROPOSED ONLY)
Input: two or more build receipts for the same declared source/build recipe.
Function: construct a DAG from source -> toolchain -> environment -> execution -> artifact -> diff -> explanation -> attestation.
Output: reproducibility verdict plus the smallest differing ancestor in the graph.
Acceptance: deliberately perturb exactly one known variance factor and prove the tribunal identifies that factor while retaining the raw artifact mismatch and evidence hashes.

## Highest-value experiment
Run the same tiny deterministic fixture repeatedly on Android ARM64 and Hivelocity x86_64. Change exactly one factor per cohort: SOURCE_DATE_EPOCH, cwd, locale/timezone, file creation order, thread count, random seed, PGO profile, compiler/linker version. Require repeated runs to produce the same drift class and evidence lineage for the same perturbation.

## Source anchors
- https://luj.fr/notes/20260522T000000%3D%3Dpublic--decade-of-software-reproducibility__research.org
- https://reproducible-builds.org/reports/2026-09/
- https://reproducible-builds.org/docs/reproducibility-troubleshooting/
- https://slsa.dev/spec/v1.2/build-provenance
- https://in-toto.io/docs/getting-started/
- https://docs.sigstore.dev/logging/overview/
- https://github.com/google/oss-rebuild
- https://developers.redhat.com/articles/2026/03/26/reproducible-builds-project-hummingbird
- https://confidential.ai/docs/resources/kettle
- https://arxiv.org/abs/2410.08427
- https://arxiv.org/abs/2508.01530
