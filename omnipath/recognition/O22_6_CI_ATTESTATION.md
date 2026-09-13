# O22.6 Independent Replay & CI Attestation Gate

Parent: O22.5 integration commit `f8ca61a8e08723232afd8037f9eb9a639847d0b7`.

O22.6 creates an external verification boundary around O22.2 through O22.5. A clean GitHub Actions runner executes the recognition test suite, recomputes the O22.5 378-case report, independently hashes the four permanent O22.5 regression specimens, and uploads the replay evidence as a content-addressed workflow artifact.

A second CI job runs only after the replay job succeeds. It downloads that artifact, verifies the replay report and specimen hashes, binds the GitHub artifact ID and SHA-256 artifact digest into a CI attestation, and evaluates the O22.6 attestation gate against the exact source commit.

Later recognition-topology promotion is nonconformant unless it references an O22.6 attestation for the promoted source commit and that attestation passes `attestation_gate.check_attestation`.

The gate requires: replay job result `success`; external CI status `SUCCESS`; 378 variants; 342 pairwise-or-higher variants; zero final PASS outcomes; exactly four specimen hashes; valid report/manifest hashes; a workflow run ID; a replay artifact ID and SHA-256 artifact digest; and exact source-commit identity.

O22.6 does not modify the O21.3 constitutional root or the historical O22.2-O22.5 implementations. It adds a descendant evidence requirement for future promotion decisions.
