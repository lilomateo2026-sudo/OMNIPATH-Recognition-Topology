# O31.8 — Content-Addressed Historical Evidence Recovery Vault

O31.8 converts O31.7 historical recoverability into durable current-tree preservation without restoring the legacy source path.

The preserved chain is:

`historical Git object → exact recovered bytes → Git blob identity → SHA-256 address → recovery vault → attestation-ledger cross-link → deterministic reconstruction`

The vault payload path is derived from SHA-256. Its tree entry points directly to the historical Git blob `f10f0cb3c9e670237914e5d502bce9f9b9dbb871`, so the bytes are preserved without reserialization. The content SHA-256 remains `486993dc1843c8f35876ed3dc02c1d2ce4c3a66ed96a3d27c00bd08c42a57eb6`.

The original path `omnipath/recognition/promotion/O23_5_ci_attested_promotion_manifest.json` remains absent. Vaulting therefore changes recoverability, not the historical fact recorded by O29.6 and O31.7.

The O31.8 verifier checks the content address, Git blob identity, O31.7 proof linkage, vault record, attestation-ledger link, legacy-path absence, and deterministic reconstruction. The dedicated CI workflow uses a depth-1 checkout and performs reconstruction from the current-tree vault without fetching the historical commit.
