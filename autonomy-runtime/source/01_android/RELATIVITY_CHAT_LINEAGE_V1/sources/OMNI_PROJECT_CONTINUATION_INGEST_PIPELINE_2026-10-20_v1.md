# OMNI PROJECT CONTINUATION INGEST PIPELINE v1

**Date:** 2026-10-20  
**Role:** Machine-oriented design for carrying all project chats, sources, runtime receipts and research into the next OMNIPATH state.

## 1. Purpose

The continuation pipeline converts the project from a set of historical artifacts into an evidence-sensitive evolving graph.

```text
SOURCE -> NORMALIZE -> IDENTIFY -> RELATE -> VERIFY -> RANK -> EXECUTE -> RECEIPT -> RECOLLECT
```

It must preserve raw source identity and never treat summaries as replacements for originals.

## 2. Inputs

Adapters should exist for:

- ChatGPT project chats / Project Sources
- canonical Markdown source files
- local Hivelocity files and receipts
- Android/Termux evidence
- Windows evidence
- iPhone/WORLD-04 evidence
- GitHub repositories/issues/PRs/releases
- Google Drive archives when authorized
- FileBridge records
- runtime telemetry
- web research citations
- experiment datasets and result capsules

## 3. Canonical Source Record

```json
{
  "record_id": "sha256-or-stable-id",
  "source_id": "original identity",
  "source_kind": "chat|file|repo|runtime|research|receipt|dataset",
  "source_uri": null,
  "source_sha256": null,
  "created_at": null,
  "observed_at": null,
  "node_id": null,
  "world_id": null,
  "system": null,
  "order_id": null,
  "order_state": null,
  "evidence_class": "OBSERVED|VERIFIED|SOURCE_DERIVED|INFERRED|DESIGNED|SIMULATED",
  "content_type": "claim|decision|artifact|code|receipt|status|question|order",
  "summary": "",
  "relations": [],
  "dependencies": [],
  "contradictions": [],
  "supersedes": [],
  "raw_pointer": ""
}
```

## 4. Ingestion Stages

### Stage A — Capture
Copy or reference the original source. Never destroy the original.

### Stage B — Fingerprint
Calculate SHA-256 when bytes are available. For connector-native records without bytes, retain the provider ID/version/time.

### Stage C — Parse
Extract names, order IDs, nodes, engines, file paths, receipts, dates, states, dependencies, decisions and unresolved questions.

### Stage D — Normalize
Map synonyms and aliases without deleting original terminology.

Example:
`Hivelocity Node 1`, `omni-hv1`, `flagship coordinator` may relate to one entity but the aliases remain visible.

### Stage E — Evidence Classification
Use:
`Fresh Observation > Verified/Sealed Receipt > Canonical Source > Implemented > Running > Staged > Designed > Simulation > Metaphor`

Do not infer a higher state from wording alone.

### Stage F — Relation Graph
Create explicit edge types:

```text
DEPENDS_ON
PRODUCED_BY
OBSERVED_BY
RUNS_ON
MIRRORS
SUPERSEDES
CONTRADICTS
VERIFIES
DERIVED_FROM
BLOCKS
UNBLOCKS
NEXT_OF
BRANCH_OF
```

### Stage G — Contradiction Tribunal
For conflicts:
1. preserve both claims;
2. compare provenance/time/evidence rank;
3. use fresh observation if current state matters;
4. resolve or mark unresolved;
5. never erase the losing historical record.

### Stage H — OMNIPATH Candidate Generation
Generate candidate next states from:
- unresolved dependencies;
- stale runtime evidence;
- blocked orders;
- missing provenance;
- high-reuse integration opportunities;
- research questions with falsifiable tests;
- human-friction bottlenecks.

### Stage I — Ranking
Score impact, feasibility, evidence gain, dependency unlock, interoperability, reliability, human friction, cost and risk.

### Stage J — Execution Handoff
Only admitted orders enter an executor. Each executor must advertise capabilities/permissions/resource limits.

### Stage K — Receipt
Every execution returns:

```json
{
  "run_id": "",
  "order_id": "",
  "executor": "",
  "inputs": [],
  "input_digests": [],
  "outputs": [],
  "output_digests": [],
  "started_at": "",
  "ended_at": "",
  "status": "",
  "tests": [],
  "evidence": [],
  "parent_receipts": []
}
```

### Stage L — Recollection
Write the result back into memory and regenerate the next-state graph.

## 5. Durable State Machine

```text
PROPOSED
 -> DEPENDENCY_CHECK
 -> AUTHORITY_CHECK
 -> RESOURCE_CHECK
 -> ADMITTED
 -> DISPATCHED
 -> RUNNING
 -> RECEIPT_PENDING
 -> VERIFIED | FAILED | HOLD | BLOCKED
 -> SEALED (optional tribunal)
 -> NEXT_PATH_GENERATED
```

Use an append-only event history. Never mutate history to make a later state look cleaner.

## 6. Node/World Contract

Every executor should publish:

```json
{
  "node_id": "",
  "world_id": "",
  "platform": "",
  "native": true,
  "capabilities": [],
  "models": [],
  "tools": [],
  "permissions": [],
  "resource_limits": {},
  "heartbeat": {},
  "evidence_endpoint": "",
  "supported_protocols": []
}
```

Mirrors must set `native=false` for the mirrored execution claim.

## 7. Observability Contract

Every operation should correlate:
- trace_id
- span_id
- run_id
- order_id
- node_id
- model_id/tool_id
- source IDs
- receipt IDs

Operations include `invoke_agent`, `chat/model`, `execute_tool`, `retrieval`, `node_rpc`, `file_transfer`, `order_transition`, `receipt_write` and `verification`.

Sensitive content is opt-in, not default telemetry.

## 8. Project Memory Architecture

Use hybrid memory:

```text
RAW ARCHIVE
  + lexical index
  + vector index
  + knowledge graph
  + event history
  + receipt store
  = RECOLLECTION
```

Query types:
- exact archaeology;
- semantic retrieval;
- whole-project global synthesis;
- drift/change analysis;
- dependency lookup;
- continuation search.

## 9. Stop Conditions

Do not auto-continue when:
- required permission is absent;
- evidence conflicts at the same rank;
- resource limits fail;
- irreversible/destructive mutation lacks approval;
- source identity is ambiguous;
- execution would overwrite sealed history.

## 10. Minimal First Implementation

Create these durable stores before advanced autonomy:

```text
sources.jsonl
entities.jsonl
relations.jsonl
orders.jsonl
receipts.jsonl
contradictions.jsonl
events.jsonl
```

Then add SQLite/Postgres/graph/vector backends behind the same schema.

The first implementation should optimize for auditability and migration, not scale theater.
