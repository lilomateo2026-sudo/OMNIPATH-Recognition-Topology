# O31.9 — Independent Recovery Replica Quorum

O31.9 extends the O31.8 content-addressed recovery vault into a survivability proof that does not require the primary repository worktree or Git object database during restoration.

## Canonical identity

- Parent: O31.8 main `822085dee5ee7761fcfb29bb296cc4f4f401fba8`
- Content SHA-256: `486993dc1843c8f35876ed3dc02c1d2ce4c3a66ed96a3d27c00bd08c42a57eb6`
- Git blob: `f10f0cb3c9e670237914e5d502bce9f9b9dbb871`
- Payload size: 5527 bytes

## Replica rails

Replica A is seeded on an isolated runner as raw bytes. Replica B is seeded on a separate runner as base64 text. Each is uploaded as a distinct immutable workflow artifact with its own artifact ID and artifact digest.

The quorum restore job performs no repository checkout. It downloads only the two replica artifacts, reconstructs each independently, requires byte equality, recomputes SHA-256 and Git blob identity, and uploads the restored copies plus a quorum attestation.

## Destructive restore invariant

The restore job must observe all three conditions before restoration:

- `.git` is absent.
- `omnipath/recognition/recovery_vault` is absent.
- reconstruction inputs are only replica A and replica B.

## Cross-provider closure

The in-repository workflow proves independence from the Git worktree/object database and runner-local storage. Final O31.9 closure additionally requires replica B to be exported to an external provider, currently Google Drive, then re-read and verified against the same content identity. This distinguishes provider-independent survival from merely having two artifacts in one hosting domain.

O31.9 does not restore the historical source path and does not weaken O31.8, O31.7, genealogy, closure, or replay gates.
