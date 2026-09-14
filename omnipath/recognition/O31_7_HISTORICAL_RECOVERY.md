# O31.7 — Historical Git-Object Reachability & Recovery Proof

O31.7 realizes the earlier O29.7 objective on the live lineage after O31.6. It extends O29.6 without changing the closure or legacy-gap records.

For each classified legacy gap, verify:

`gap → historical commit → historical tree/path → expected Git blob → recovered bytes → SHA-256 digest → recovery classification`

Allowed classifications are `CURRENTLY_PRESENT`, `HISTORICALLY_REACHABLE`, `HASH_KNOWN_BUT_UNREACHABLE`, and `PERMANENTLY_UNRECOVERED`.

Transient fetch failure is never sufficient for `PERMANENTLY_UNRECOVERED`. The verifier recomputes Git blob identity from recovered bytes and hashes those bytes with SHA-256. Historical material is verified in place; it is not restored into current `main` merely to erase a classified gap.
