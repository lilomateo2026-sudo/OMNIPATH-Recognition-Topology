# O22.5 Cross-Product Boundary Fuzzer

Parent: O22.4 integration commit `8875873a3eb8420a5e16a43fde285e2ca20c3423`.

O22.5 evaluates the complete non-empty power set of the six O22.4 mutation dimensions for every O22.3 corpus case. This yields 63 variants per case, 378 total variants, and 342 pairwise-or-higher cross-product variants.

The raw O22.2 decision is retained separately from the O22.4 guarded decision. O22.5 identifies every raw PASS, reduces each escape to its inclusion-minimal mutation set, and verifies that every committed regression specimen still reproduces the raw PASS while each one-dimension reduction no longer does.

The current minimized specimen set is:

- false-consensus-cross-rail: severity + promotion_effect + contradictions
- observer-collapse: severity + promotion_effect
- contradiction-erasure: severity + promotion_effect + contradictions
- replay-divergence: severity + promotion_effect + replay

Certification requires deterministic evaluation, exactly 378 generated variants, exactly 342 pairwise-or-higher variants, zero final PASS decisions after the existing O22.4 guard, and exact agreement between discovered minimal counterexamples and the permanent O22.5 regression specimens.
