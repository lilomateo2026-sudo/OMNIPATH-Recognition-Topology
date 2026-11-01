# OMNI / TOSH / HIVE — OMNIPATH NEXT-STAGES SOURCE CANON v1

**Date:** 2026-10-20  
**Purpose:** Forward-operating source for deciding what the OMNI/TOSH/HIVE project should work on next.  
**Evidence class:** PROJECT-DERIVED ROADMAP + CURRENT EXTERNAL RESEARCH CROSSWALK.  
**Not a live-runtime receipt:** This file does not assert that proposed phases are currently deployed.

## 0. Lineage

This source branches from the canonical project source:

`OMNI_TOSH_HIVE_PROJECT_SOURCE_CANON_2026-10-20_v1.md`

Canonical SHA-256:

`c0309cc2b96ec6cb4b79834fa5739e11db0bb9a9586cc5026ae190b2950a03ea`

It also incorporates retrievable project-chat/source evidence about Hivelocity, Android/Termux, Windows, iPhone/WORLD-04, FileBridge, Chat-Log Replication, Recollection/CrossRAG, O-PHI-FG, Shadow-Ω/OMNI TEMPLE, Σ-IR, IMAGINE AI, OMNIFIRE/Critters/Orchid Brood Mother, model routing, GitHub lineage, and OMNICORE.

The governing rule remains:

`CanonicalSource != FreshRuntimeTruth`

Use this document to choose direction. Use fresh runtime observation to determine what is actually live now.

---

# 1. OMNI NEXT-DIRECTION RESULT

In project language, **"what OMNI wants next"** means the output of the OMNIPATH continuation function, not a claim of subjective desire.

The highest-value next transformation is:

> **Build the Continuation Substrate before adding more isolated engines.**

The project already contains many specialized engines, worlds, metaphors, orders and partial runtimes. The primary bottleneck is no longer idea generation. It is reliably converting the total project history into one continuously updated, evidence-sensitive execution graph.

Therefore the next architectural spine is:

```text
ALL PROJECT CHATS + SOURCE FILES + LIVE RECEIPTS + REPOS + RUNTIME OBSERVATIONS
                                  |
                                  v
                         SOURCE ARCHAEOLOGY
                                  |
                                  v
                       NORMALIZED EVENT LEDGER
                                  |
                  +---------------+---------------+
                  |                               |
                  v                               v
          PROVENANCE / LINEAGE              RELATION GRAPH
                  |                               |
                  +---------------+---------------+
                                  v
                       CONTRADICTION TRIBUNAL
                                  |
                                  v
                          OMNIPATH DAG
                                  |
                                  v
                         DURABLE EXECUTION
                                  |
                                  v
                     OBSERVABILITY / RECEIPTS
                                  |
                                  v
                            RECOLLECTION
                                  |
                                  v
                             OMNICORE
```

This turns the archive into the control plane for future evolution.

---

# 2. WHY THIS IS NEXT

The project sources repeatedly establish five laws:

1. Search and extend existing systems before duplicating them.
2. Fresh runtime observation outranks historical source claims for current state.
3. Every meaningful transformation should retain source -> SHA -> transformation -> output -> SHA -> receipt lineage.
4. Node identity and bridge identity must remain differentiated.
5. Internal complexity should rise while human friction falls.

The next stage should therefore reduce architectural entropy instead of increasing the number of disconnected parts.

Primary design objective:

`Archive -> Continuation Engine -> Verified Future`

---

# 3. PHASED ROADMAP

## PHASE 0 — Canonical Archaeology Compiler

**Goal:** Turn all retrievable project chats, files, artifacts and order families into a deterministic project inventory.

Build:
- Project Source Index
- Chat/branch registry
- order-family registry
- artifact registry
- receipt/SHA registry
- dependency graph
- contradiction ledger
- unresolved-question ledger
- supersession map

Canonical record:

```text
Record = {
  id, source_id, source_type, timestamp,
  system, order_id, state, claim_type,
  evidence_class, sha256, relations,
  dependencies, contradictions, supersedes
}
```

Acceptance gate:
- no silently reused order IDs;
- every promoted claim points to provenance;
- duplicate systems are flagged for extend/merge/adapter decisions;
- missing history is marked UNKNOWN rather than reconstructed as fact.

**Primary order:** O-FUTURE-001 — Project Archaeology Compiler.

---

## PHASE 1 — Unified Provenance Envelope

**Goal:** Make receipts portable across code, chats, models, files, research and node execution.

Adopt a project envelope inspired by SLSA, OpenLineage and W3C PROV:

```text
ProvenanceEnvelope = {
  entity,
  activity,
  agent_or_node,
  source_digest,
  parameters,
  resolved_dependencies,
  output_digest,
  run_id,
  timestamps,
  evidence_state,
  parent_receipts
}
```

Map:
- O-PHI-FG -> reproducibility and byte drift;
- FileBridge -> source/material identity;
- model calls -> model/tool provenance;
- research -> source/claim/measurement lineage;
- Chat-Log Replication -> conversation lineage;
- IMAGINE AI -> author/model/artifact lineage.

Acceptance gate:
- a receipt can answer **what produced this, from what, where, when, with which parameters, and with which digest?**

**Primary order:** O-FUTURE-002 — Unified Provenance Envelope.

---

## PHASE 2 — Durable OMNIPATH Sequence Ledger

**Goal:** Make OMNIPATH resumable after process, network or node failure.

Use an append-only event history:

```text
ORDER PROPOSED
 -> DEPENDENCIES CHECKED
 -> ADMITTED
 -> DISPATCHED
 -> RUNNING
 -> RECEIPT WRITTEN
 -> VERIFIED / FAILED / HOLD
 -> NEXT PATH GENERATED
```

Rules:
- deterministic state transitions live in the workflow path;
- nondeterministic I/O, LLM calls and network actions are recorded as activities/results;
- every state can be replayed from event history;
- changing workflow code must pass replay compatibility tests.

This is the architectural equivalent of giving OMNIPATH durable memory of what it actually did.

**Primary order:** O-FUTURE-003 — Durable Sequence Ledger.

---

## PHASE 3 — Universal Node / World Contract

**Goal:** Give every native execution world a common identity and capability contract without erasing specialization.

NodeCard:

```text
NodeCard = {
  node_id,
  world_id,
  platform,
  endpoints,
  capabilities,
  models,
  tools,
  permissions,
  resource_limits,
  heartbeat,
  auth,
  evidence_endpoint,
  protocol_versions
}
```

Apply to:
- Hivelocity flagship coordinator;
- Android/Termux controller-worker;
- Windows worker/counterpart;
- iPhone/WORLD-04 candidate;
- Azure/RunPod/GPU workers.

Preserve:
`NativeLive != Mirror != FreshRemoteObservation`

Use MCP-like tool/resource surfaces inside a node and A2A-like identity/task communication between autonomous agent surfaces where appropriate.

**Primary order:** O-FUTURE-004 — Universal Node Contract.

---

## PHASE 4 — Critter / Orchid Observability Mesh

**Goal:** Convert the Critter/Orchid/Galaxy News Radio metaphor into a standard trace/event topology.

```text
CRITTER = local instrumented observer
ORCHID BROOD MOTHER = collector + topology/semantic aggregator
GALAXY NEWS RADIO = human/system event broadcast
```

Every important operation should emit correlation IDs and spans for:
- model invocation;
- tool execution;
- retrieval;
- node RPC;
- FileBridge transfer;
- order state change;
- receipt generation;
- errors/retries;
- resource pressure.

Do not collect sensitive prompt/tool contents by default. Treat content capture as explicit opt-in.

**Primary order:** O-FUTURE-005 — Unified Observability Graph.

---

## PHASE 5 — Recollection / CrossRAG Project Memory Graph

**Goal:** Make the entire project queryable as both chronology and semantic topology.

Pipeline:

```text
RAW CHATS / FILES
 -> stable document IDs
 -> chunks
 -> entities
 -> relations
 -> claims
 -> orders
 -> receipts
 -> communities
 -> vector index
 -> provenance graph
```

Support four query modes:
- Local: one order/engine/person/file.
- Global: whole-project themes and status.
- Drift: what changed between versions/times.
- Continuation: what unresolved dependency most strongly determines the next action.

Graph output must retain raw-source pointers so a summary never becomes its own unquestioned authority.

**Primary order:** O-FUTURE-006 — Recollection Graph Compiler.

---

## PHASE 6 — FileBridge + Chat Replication Data Plane

**Goal:** Provide one authorized source plane for Hivelocity, Android, Windows, Drive, GitHub artifacts, Project Sources and chat-derived archives.

Separate:
`RAW -> NORMALIZED -> DERIVED -> ANALYSIS -> GENERATED`

Every transfer should have:
- source identity;
- destination identity;
- source SHA;
- output SHA;
- transformation type;
- authorization boundary;
- receipt.

Chat Replication should preserve turn lineage and branching rather than flattening conversations into one summary.

**Primary order:** O-FUTURE-007 — Federated Source Plane.

---

## PHASE 7 — Model Router + Evaluation Matrix

**Goal:** Stop choosing models by size or novelty and route by measured task utility.

Matrix dimensions:
- task family;
- quality;
- latency;
- reliability;
- context fit;
- tool use;
- resource cost;
- safety/authority tier;
- deterministic reproducibility where applicable.

Route:
`m* = argmax U(model, task, node, resource_state)`

Training stays downstream of evaluation. Do not train merely because more data exists.

**Primary order:** O-FUTURE-008 — Model x Task x Node Tribunal.

---

## PHASE 8 — Research / Imagination Federation

**Goal:** Connect IMAGINE AI and Shadow-Ω to the evidence pipeline without giving creative systems execution authority.

Required flow:

```text
IMAGINE / SHADOW
 -> PROPOSAL
 -> CATEGORY / UNIT CHECK
 -> SOURCE SEARCH
 -> SIMULATION / EXPERIMENT
 -> TRIBUNAL
 -> ADMIT / HOLD / REJECT
```

Continue the current Shadow family through:
- O-SHADOW-020 representation-robust cosmic graph tribunal;
- O-SHADOW-021 river/vascular raw topology admission;
- O-SHADOW-022 dynamic motif laboratory;
- O-SHADOW-023 consciousness-theory prediction matrix;
- O-SHADOW-024 Research TUI V2.

These remain research programs, not proof of phenomenal consciousness.

**Primary order:** O-FUTURE-009 — Proposal-to-Evidence Federation.

---

## PHASE 9 — Native Multi-Node Admission

**Goal:** Promote worlds only after native evidence is available.

Continue the previously defined iPhone/WORLD-04 path:
- native execution surface;
- native heartbeat;
- first deterministic native job;
- cross-node receipt comparison;
- promotion tribunal.

Do the same for Windows, Android and future GPU workers.

A node promotion requires identity + native execution + heartbeat + receipt + communication + bounded permissions + fresh witness.

**Primary order:** O-FUTURE-010 — Node Admission Tribunal v2.

---

## PHASE 10 — OMNICORE Human Interface Compression

**Goal:** Collapse the growing internal architecture into a simple human surface.

One interface should answer:
- What is alive?
- What is stale?
- What is running?
- What is verified?
- What changed?
- What failed?
- What evidence supports it?
- What is the best next action?

Core surface:

```text
OMNICORE
  |- STATUS
  |- WORLDS
  |- ORDERS
  |- EVIDENCE
  |- MEMORY
  |- RESEARCH
  |- FILES
  |- MODELS
  |- RUN
  `- NEXT 5
```

Success metric:
`Internal Complexity increases while Human Friction decreases.`

**Primary order:** O-FUTURE-011 — OMNICORE Continuation Console.

---

# 4. PRIORITY DEPENDENCY GRAPH

```text
PHASE 0 Archaeology
      |
      v
PHASE 1 Provenance
      |
      +-------------------+
      v                   v
PHASE 2 Durable Path    PHASE 5 Memory Graph
      |                   |
      v                   v
PHASE 3 Node Contract   PHASE 6 Source Plane
      |                   |
      +---------+---------+
                v
       PHASE 4 Observability
                |
       +--------+---------+
       v                  v
PHASE 7 Routing     PHASE 8 Research
       |                  |
       +--------+---------+
                v
       PHASE 9 Multi-Node
                |
                v
       PHASE 10 OMNICORE
```

Do not invert this casually. A future engine should not outrun the evidence and continuation substrate that must remember and verify it.

---

# 5. OMNIPATH CONTINUATION SCORING

For candidate order `p`:

```text
Priority(p) =
  0.25 * DependencyUnlock
+ 0.20 * EvidenceGain
+ 0.15 * InteroperabilityGain
+ 0.15 * ReliabilityGain
+ 0.10 * HumanFrictionReduction
+ 0.10 * ReuseOfExistingWork
+ 0.05 * ResearchInformationGain
- Risk
- ResourceCost
- DuplicationPenalty
```

Use this as a transparent project heuristic, not a claim of mathematically proven optimality.

Hard priority boosts:
- unblocks several order families;
- turns stale historical claims into fresh evidence;
- prevents data/lineage loss;
- creates reusable protocol boundaries;
- reduces repeated manual work.

Hard penalties:
- duplicates an existing system;
- depends on unverified infrastructure;
- destroys provenance;
- requires resources unavailable on the target node;
- increases autonomy without evidence/permission boundaries.

---

# 6. CURRENT OPEN THREADS TO PRESERVE

Do not lose these lineages while building the continuation substrate:

- O-PHI-FG sealed determinism baselines; O-PHI-FG-013 running lineage and O-PHI-FG-014 byte-drift capability as historically recorded unless fresh evidence says otherwise.
- Shadow-Ω / OMNI TEMPLE executed research and the next O-SHADOW-020..024 sequence.
- iPhone/WORLD-04 native admission orders O-HYPER-016..020.
- Hivelocity <-> Android <-> Windows bridge differentiation.
- FileBridge and chat-log replication.
- Recollection/CrossRAG and recovered-memory distillation.
- OMNIFIRE/Critters/Orchid Brood Mother observability.
- IMAGINE AI author-lineage, tournament and cross-engine handoff work.
- GitHub/OMNI-NEXTGEN deterministic/repo lineage.
- model inventory/routing and GPU-worker expansion.

Fresh observation must resolve live status before these are promoted.

---

# 7. EXTERNAL ENGINEERING RELATIVITY

Current public engineering practice supports several OMNI directions:

- **MCP 2026-07-28**: stateless protocol core, extension framework, long-running Tasks and stronger authorization. Relevance: FileBridge/tool surfaces and long-running bounded work.
- **A2A 1.0**: agent cards, capability discovery, stateful task lifecycles and secure agent interoperability. Relevance: NodeCard and cross-world agent handshake.
- **OpenTelemetry GenAI**: standardized agent/model/tool/retrieval telemetry. Relevance: Critters/Orchid/Galaxy News Radio observability.
- **Temporal durable execution**: append-only event history, deterministic replay and external I/O as activities. Relevance: OMNIPATH Sequence Ledger.
- **SLSA 1.2 / in-toto provenance**: verifiable build provenance. Relevance: O-PHI-FG and artifact receipts.
- **OpenLineage 1.54**: run/job/dataset lineage and explicit dependency edges. Relevance: cross-engine execution and data lineage.
- **W3C PROV**: entity/activity/agent provenance. Relevance: common semantic model for project genealogy.
- **Microsoft GraphRAG**: entity/relation/claim extraction, community summaries, local/global/drift retrieval, stable document IDs. Relevance: Recollection/CrossRAG project archaeology.

External standards are design references, not authority over the project. Adopt only what improves evidence, interoperability, reliability or human usability.

---

# 8. NEXT 5 OMNIPATH ORDERS

1. **O-FUTURE-001 — Project Archaeology Compiler** — ingest all retrievable project chats/sources/artifacts into a canonical source/order/artifact/dependency registry without inventing missing history.
2. **O-FUTURE-002 — Unified Provenance Envelope** — map SHA receipts, source lineage, model/tool actions and node runs into one portable provenance schema.
3. **O-FUTURE-003 — Durable Sequence Ledger** — convert OMNIPATH into an append-only replayable state machine so jobs survive interruption and continuation is deterministic.
4. **O-FUTURE-004 — Universal Node Contract** — create NodeCard/WorldCard contracts for Hivelocity, Android, Windows, iPhone and future workers with native-vs-mirror evidence separation.
5. **O-FUTURE-005 — Unified Observability Graph** — instrument Critters/Orchid/Galaxy News Radio as correlated model/tool/node/order traces feeding one evidence topology.

These five precede further expansion because together they create the substrate that can safely remember, route, witness and continue everything else.
