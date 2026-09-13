# O22.8 Promotion Artifact Registry

Parent: O22.7 integration commit `645483dc20cd7cb245df183ea3c8c9d54fa4ea5c`.

O22.8 adds an append-only, content-addressed registry for recognition-topology promotions accepted by the O22.7 Promotion Manifest Gate. It does not change the O21.3/O21.4 constitutional root or rewrite O22.1-O22.7.

## Registry invariant

A registry entry may exist only when the supplied O22.7 manifest independently evaluates to `PROMOTABLE`. The registry never trusts a caller-supplied promotion status.

Each accepted entry preserves:

- monotonic `lineage_version`
- candidate ID and candidate commit SHA
- immediate parent commit SHA
- rollback commit SHA
- O21.3 constitutional root SHA
- O22.7 promotion manifest SHA-256
- O22.7 promotion decision SHA-256
- exact O22.6 attestation SHA-256
- O22.6 workflow run ID
- O22.6 replay artifact ID and artifact digest
- canonical O22.2-O22.6 checkpoint map inherited from the accepted manifest
- previous registry-entry SHA-256
- the entry's own SHA-256

The registry document also records its current head entry hash, next lineage version, and a deterministic registry SHA-256.

## Append-only rules

1. Entries are ordered by `lineage_version`, beginning at 1.
2. A new entry must link to the exact previous head hash; the first entry links to `null`.
3. Candidate commit SHAs and promotion-manifest hashes are unique.
4. Existing entries are never edited during append; appending returns a new registry value.
5. Any broken entry hash, previous-entry link, lineage sequence, duplicate identity, head pointer, or registry hash makes the registry nonconformant.
6. File persistence uses atomic replacement after the complete candidate registry passes audit.
7. Registry acceptance is evidentiary bookkeeping only. O22.8 cannot amend constitutional invariants or self-authorize a different promotion rule.

## Reconstruction

A promotion can be reconstructed by candidate commit SHA. Reconstruction verifies the complete registry first, locates the accepted entry, and returns its hash-linked ancestry from that entry back to registry genesis.

## Genesis

`promotion_registry/registry.json` is the empty O22.8 genesis registry. Historical constitutional checkpoints remain preserved by their existing commits; O22.8 does not retroactively manufacture promotion records for events that predate the registry.
