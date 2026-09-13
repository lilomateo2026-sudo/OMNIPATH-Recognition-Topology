# O27.7 Deterministic Genealogy Index & Candidate Resolver

O27.7 derives a repository-resident promotion genealogy index from the durable ledgers under `omnipath/recognition/attestation_ledger/v1`.

The durable ledgers remain the source of truth. The committed index is a deterministic projection that maps every known candidate or promoted-main SHA to one normalized evidence entry. CI regenerates the projection from source evidence and fails if the committed index is stale, incomplete, ambiguous, or differently sealed.

The resolver accepts only a candidate/commit SHA from the caller. It discovers the ledger path, optional promotion-manifest path, registry linkage, promoted-main identity, workflow evidence, and epistemic state through the index. No caller-supplied ledger or manifest reference is required.

Current generations indexed at genesis are O22.6, O23.9, O25.5, and O27.5. Future durable ledger directories are automatically included by regeneration, subject to unique SHA aliases and valid Git identities.

O27.7 does not grant promotion authority. It is a deterministic navigation and reconstruction layer over already-recorded evidence and preserves the O27.6 retention-proof genealogy contract.
