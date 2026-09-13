# O29.6 Genealogy Closure & Missing-Evidence Tribunal

O29.6 realizes the earlier O27.8 closure objective on the live O29 lineage. It treats the durable attestation-ledger directories as the authoritative generation set and requires the committed genealogy index to be a complete, unique, deterministic projection of that set.

Certification requires every durable ledger to appear exactly once in the index, every alias to resolve to one generation, every promoted-main SHA to retain a durable ledger, and every repository reference to exist unless its historical absence is explicitly classified and hash-addressed.

The O23.9 promotion-manifest gap is preserved as a sealed legacy-evidence record. Its declared path, historical commit, and Git blob identity come from the O23.9 durable ledger. O29.6 fails if that declaration drifts, the gap record is removed, an unclassified missing source appears, or the historically missing path becomes present without explicit reconciliation.

No gap record grants promotion authority. O29.6 is an evidence-closure and integrity tribunal layered over O27.7 indexing and the existing promotion genealogy.
