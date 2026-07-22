# SUDACHI Handoff

Updated: **2026-07-22**

This file is the operational restart point for the repository state that includes Phase 1 Slices 1–16. Read `AGENTS.md` first, then the normative contract and ADRs before changing implementation.

## Project thesis

SUDACHI asks whether a bounded artificial organism can convert finite external cognitive scaffolding into verified local competence and preserve capability while reducing justified caregiver dependence.

The developmental direction remains:

```text
parent reasoning -> verified experience -> reusable skill -> cheap local behavior
```

The repository is the organism's auditable body, developmental history, skill base, and lineage record. A language model is a possible future caregiver or organ, not the organism itself.

The governing phrase remains:

> As it becomes smarter, it should become smaller and quieter.

## Normative Phase 1 baseline

The accepted implementation authority is:

1. `docs/MINIMAL_ORGANISM_CONTRACT.md` v0.2
2. ADRs 0001–0006 in `docs/decisions/`
3. protected Phase 1 tests and `docs/PHASE1_TEST_MATRIX.md`

Architecture, roadmap, handoff, issue discussion, and code comments explain the baseline but do not override it.

No unresolved seed-architecture choice may be invented in implementation code. If code reveals a contradiction with the contract or ADRs, stop and resolve it through repository review.

## Accepted architecture

Phase 1 uses:

- one canonical SQLite database per organism
- append-only canonical event history ordered by integer `event_sequence`
- injected wall and monotonic clocks
- fail-fast `BEGIN IMMEDIATE` wake ownership
- a deterministic two-plot `seed-garden-v1`
- explicit concrete budgets and no scalar `energy`
- protected action definitions and independent evaluation
- exact pending checkpoint boundaries
- verified immutable SQLite checkpoints
- bounded checkpoint retention
- explicit administrative maintenance and repair boundaries
- non-canonical deterministic JSONL event export

Phase 1 has no caregiver, model adapter, chat interface, network access, subprocess access, arbitrary generated code, learning, memory, skills, continuous execution, or generic autonomous loop.

## Current work streams

### Issue #13 — Phase 1 SUDACHI-0 metabolism

Primary implementation stream. Slices 1–16 are implemented in repository state containing this handoff.

### Issue #3 — prior work and provider review

Research stream. Preliminary evidence and provider-neutral strategy exist, but no strong novelty claim and no live caregiver selection are authorized. This stream does not block deterministic caregiver-free Phase 1 mechanics.

## Implemented Phase 1 slices

### Slice 1 — package, canonical genesis, and stable checkpoint

Established:

- Python 3.12 package and CLI
- canonical SQLite schema
- protected constants and validators
- real and fake clocks
- deterministic initialization
- append-only event triggers
- immutable stable genesis checkpoint
- initial `init` and `status` commands

### Slice 2 — inbox, wake acquisition, and observation

Established:

- idempotent `synthetic:garden_tick` enqueue
- fail-fast wake ownership before mutable reads
- one oldest eligible tick claim
- rollback-only incomplete wake context
- deterministic complete sorted garden observation

### Slice 3 — first canonical water wake

Established the complete first lifecycle:

- fixed policy chooses `water_plot(bed-a)`
- action and mutation budgets reserve before change
- action executes inside a savepoint
- independent evaluation proves positive progress
- exact pending boundary `13`
- stable lifecycle checkpoint and return to sleep

### Slice 4 — canonical harvest wake

Established the second lifecycle:

- fixed policy skips unavailable watering
- chooses `harvest_plot(bed-b)`
- independent evaluation proves objective completion
- exact pending boundary `24`
- stable checkpoint and return to sleep

### Slice 5 — objective-complete abstention

Established the third canonical lifecycle:

- typed `objective_already_complete` abstention
- zero action attempts and zero mutations
- independent unchanged-state evaluation
- exact pending boundary `34`
- stable checkpoint and return to sleep

The canonical three-wake run is deterministic: water, harvest, justified abstention.

### Slice 6 — classified no-applicable-action abstention

Established:

- protected blocked-state fixture
- typed `no_applicable_action`
- unchanged environment
- one failure-streak increment
- stable checkpoint below maintenance threshold

### Slice 7 — resource-aware recovery

Established:

- unavailable watering does not hide an executable harvest
- harvest produces positive progress
- prior failure streak resets to zero
- stable checkpoint and return to sleep

### Slice 8 — classified action failure

Established:

- protected failure injection after partial plot write
- savepoint removes partial mutation
- action attempt cost remains charged
- successful mutation cost returns to zero
- typed failure and independent rollback evaluation commit canonically

### Slice 9 — classified lifecycle budget exhaustion

Established:

- injected monotonic pre-action deadline check
- typed exhaustion before proposal, attempt, savepoint, or mutation
- nonnegative exact ledger
- unchanged environment and stable checkpoint

### Slice 10 — maintenance threshold

Established:

- exact failure streak transition `2 -> 3`
- checkpoint stabilizes before `maintenance_required`
- typed maintenance reason
- later normal wake rejects before clock use or input claim

### Slice 11 — read-only maintenance inspection

Established:

- explicit administrative `mode=ro` inspection API and CLI
- exact maintenance, checkpoint, and queued-input report
- zero clock reads
- byte-identical organism files before and after inspection

### Slice 12 — explicit maintenance clear

Established:

- bounded caller-supplied recovery reason
- fail-fast administrative transaction
- atomic state reset plus `maintenance_cleared` audit event
- preserved environment, checkpoints, and queued input
- later normal wake permitted

### Slice 13 — successful checkpoint retention

Established:

- checkpoint retention limit four
- newest checkpoint becomes stable before pruning
- genesis and latest preservation
- same-filesystem staging of oldest eligible artifact
- atomic registry deletion and `checkpoint_pruned` event
- exact retained artifact and byte accounting

### Slice 14 — classified retention failure

Established:

- deterministic failure after artifact staging and before registry mutation
- staged artifact restoration
- no false pruning success
- five valid artifacts and rows preserved
- typed maintenance warning and blocked later wakes

### Slice 15 — pending checkpoint registration repair

Established:

- explicit administrative repair for exactly one valid published orphan
- exact matching of identity, lineage, versions, boundary, digests, protected configuration, and snapshot contents
- atomic registry insertion, pending clear, sleeping restoration, and typed repair event
- rejection of zero, multiple, foreign, corrupt, busy, or repeated candidates without mutation
- later normal wakeability

### Slice 16 — deterministic non-canonical JSONL event export

Established:

- explicit Python API `export_stable_events(...)`
- narrow CLI `sudachi export events <organism_id> --event-sequence <N>`
- caller-declared registered stable checkpoint boundary
- active SQLite opened read-only inside one snapshot transaction
- exact validation of canonical state, registry, immutable checkpoint, lineage, versions, digests, and complete event range
- manifest plus event records ordered by canonical `event_sequence`
- canonical JSON serialization with no export-time clock metadata
- byte-identical repeated output from unchanged canonical state
- bounded same-directory temporary file
- validation before same-filesystem atomic replacement
- preservation of a previous final export on injected partial temporary write failure
- proof that export creation, modification, deletion, and failure cannot change canonical SQLite, checkpoint registry, checkpoint artifacts, inbox, events, status, or later wakeability

JSONL remains disposable and non-canonical. There is no import path and no lifecycle dual-write.

See `docs/phase1/SLICE16_JSONL_EVENT_EXPORT.md` for the exact boundary.

## Validation state

GitHub Actions on Python 3.12 for PR #30 completed:

- clean editable installation
- source and test compilation
- genesis CLI smoke test
- **55 protected tests**

`docs/PHASE1_TEST_MATRIX.md` maps the implemented coverage. Phase 1 is still incomplete; passing 55 tests does not imply all 41 contract evaluations are fully satisfied.

## Known incomplete Phase 1 work

Major incomplete areas include:

- offline rollback, pre-rollback archive, active replacement, new lineage generation, and abandoned-future preservation
- complete repeated-run canonical equivalence
- backward-wall-time ordering scenario
- explicit seed-independence comparison
- cleanup-grace boundary coverage
- altered insertion-order tie-breaking scenario
- post-action duplicate-input replay scenario
- process-crash-before-commit test
- nested-wake rejection
- explicit second-wake rejection while a prior checkpoint is pending
- broader protected-authority tests

Do not weaken existing tests to make these easier.

## Exact next task: Slice 17

Implement only the rollback foundation accepted by ADR 0004:

1. create a new `agent/...` branch from current `main`
2. add an explicit offline administrative Python boundary and narrow CLI command for selecting one retained stable checkpoint as a rollback source
3. require the active organism to be stable, closed to normal wake work, and free of a pending checkpoint
4. acquire fail-fast administrative ownership before any rollback preparation
5. validate exactly one selected checkpoint registry row and immutable artifact
6. prove organism identity, source lineage, contract, schema, environment, budget configuration, event boundary, manifest digest, database digest, and snapshot integrity
7. reject missing, pruned, foreign, mismatched, unsafe, or invalid sources before active mutation
8. create a complete verified pre-rollback archive of the current active database and current rollback-relevant metadata through a same-filesystem bounded temporary artifact
9. publish the archive atomically only after full validation
10. prove archive creation failure leaves active SQLite, current lineage, event history, inbox, registry, checkpoints, status, and wakeability unchanged
11. update protected tests, `docs/PHASE1_TEST_MATRIX.md`, this handoff, Issue #13, and a dedicated Slice 17 implementation note
12. run GitHub Actions from a pull request

Slice 17 stops before:

- replacing the active database
- incrementing lineage generation
- writing rollback-completed canonical history
- preserving the abandoned future through final lineage transition
- deleting or pruning any checkpoint
- adding JSONL import
- adding caregiver consultation, learning, memory, skills, or generic recovery machinery

The purpose is to isolate and protect source selection plus pre-rollback preservation before the destructive replacement boundary is introduced.

## Restart protocol

At the next session:

1. read `AGENTS.md`
2. read this handoff and the normative documents in the required order
3. inspect current open issues and pull requests
4. verify that PR #30 is merged or otherwise reconcile repository truth before Slice 17
5. begin from the exact Slice 17 boundary above

At the end of substantial work, always leave:

- updated `docs/HANDOFF.md`
- updated test matrix
- related Issue checklist or status update
- durable implementation or decision note
- tests and CI result
- exact unfinished work and next action

No critical decision may remain only in chat history.
