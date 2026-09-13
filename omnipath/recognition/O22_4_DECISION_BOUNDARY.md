# O22.4 Decision-Boundary Mutation Tournament

Parent: O22.3 integration commit `12c3ff5c362ba7c8fcdd33f3c7089243e468abfc`.

The tournament mutates severity, promotion effect, provenance references, replay metadata, contradiction status, and epistemic state for every O22.3 corpus case. Each case receives six single-axis variants and one compound variant.

The unmodified O22.2 decision remains recorded as `base_decision`. O22.4 adds a descendant boundary guard: a record that still belongs to the O22.3 pathology set cannot receive a final PASS merely because surrounding metadata was loosened.

Certification requires deterministic evaluation, complete dimension coverage, and zero final PASS results across all generated variants. Raw base PASS results are retained in the report rather than erased.
