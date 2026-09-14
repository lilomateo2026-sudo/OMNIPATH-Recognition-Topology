# O29.7 — Historical Git-Object Reachability & Recovery Proof

O29.7 extends O29.6 without changing the closure or legacy-gap records.

For every classified legacy evidence gap, verify the chain:

`gap → historical commit → historical tree/path → expected Git blob → recovered bytes → SHA-256 digest → recovery classification`

Allowed classifications:

- `CURRENTLY_PRESENT`: the current tree contains the declared path at the expected blob identity.
- `HISTORICALLY_REACHABLE`: the current tree lacks the path, but the declared historical commit is retrievable and its declared path resolves to the expected blob whose bytes can be recovered.
- `HASH_KNOWN_BUT_UNREACHABLE`: the durable gap retains commit/path/blob identity, but the historical object chain cannot currently be recovered.
- `PERMANENTLY_UNRECOVERED`: reserved for an explicitly adjudicated permanent-loss record; transient fetch failure is insufficient.

The verifier must recompute Git blob identity from recovered bytes and SHA-256 hash those bytes. It must not restore a historical source file into `main` merely to make a gap disappear.
