# SUDACHI Handoff

Updated: **2026-07-22**

This file is the operational restart point for repository state containing Phase 1 Slices 1–17. Read `AGENTS.md` first, then the normative contract and ADRs before changing implementation.

## Project thesis

SUDACHI asks whether a bounded artificial organism can convert finite external cognitive scaffolding into verified local competence and preserve capability while reducing justified caregiver dependence.

```text
parent reasoning -> verified experience -> reusable skill -> cheap local behavior
```

The repository is the organism's auditable body, developmental history, skill base, and lineage record. A language model is a possible future caregiver or organ, not the organism itself.

> As it becomes smarter, it should become smaller and quieter.

## Normative Phase 1 baseline

Use this precedence:

1. `docs/MINIMAL_ORGANISM_CONTRACT.md` v0.2
2. ADRs 0001–0006 in `docs/decisions/`
3. protected Phase 1 tests and `docs/PHASE1_TEST_MATRIX.md`

Architecture, roadmap, handoff, issues, and comments explain the baseline but do not override it.

Phase 1 has one canonical SQLite body, append-only sequence-ordered events, injected clocks, fail-fast write ownership, deterministic `seed-garden-v1`, concrete budgets, protected evaluation, exact checkpoint boundaries, immutable checkpoints, bounded retention, rollback lineage rules, and explicit administrative boundaries.

Phase 1 has no caregiver, model adapter, chat interface, network access, subprocess access, arbitrary generated code, learning, memory, skills, continuous execution, or generic autonomous loop.

## Current work streams

### Issue #13 — Phase 1 SUDACHI-0 metabolism

Primary implementation stream. Slices 1–17 are implemented in repository state containing this handoff.

### Issue #3 — prior work and provider review

Research stream. Preliminary evidence and provider-neutral strategy exist, but no strong novelty claim and no live caregiver selection are authorized. This stream does not block deterministic caregiver-free Phase 1 mechanics.

## Implemented Phase 1 slices

### Slice 1 — package, genesis, and stable checkpoint

- Python 3.12 package and CLI
- canonical SQLite schema and validators
- real and fake clocks
- deterministic initialization
- append-only event triggers
- immutable genesis checkpoint
- `init` and `status`

### Slice 2 — inbox, wake acquisition, and observation

- idempotent synthetic garden ticks
- fail-fast ownership before mutable reads
- one oldest input claim
- rollback-only incomplete wake context
- deterministic sorted observation

### Slices 3–5 — canonical garden run

- first wake waters `bed-a`, pending boundary `13`
- second wake harvests `bed-b`, pending boundary `24`
- third wake records `objective_already_complete`, pending boundary `34`
- action budgets reserve before mutation
- mutating actions use savepoints
- independent evaluators verify transitions and abstention
- every committed wake stabilizes a checkpoint before another wake

The canonical three-wake sequence is water, harvest, justified abstention.

### Slices 6–9 — classified failure and recovery

- typed `no_applicable_action` with one failure increment
- resource-aware harvest fallback and failure reset
- injected partial action failure with savepoint rollback and preserved attempt cost
- monotonic lifecycle deadline exhaustion before action or mutation
- unchanged-state independent evaluation and stable checkpointing

### Slices 10–12 — maintenance

- exact third-failure transition into `maintenance_required`
- later wake rejection before clock or claim
- read-only maintenance inspection with zero file changes
- explicit administrative maintenance clear
- atomic state reset plus typed audit event
- preservation of environment, checkpoints, and queued input

### Slices 13–15 — checkpoint retention and repair

- retention limit four
- newest checkpoint stabilizes before pruning
- genesis and latest preservation
- oldest eligible non-genesis pruning
- classified pruning failure with staged-artifact restoration and maintenance warning
- explicit registration repair for exactly one valid published orphan checkpoint
- rejection of missing, ambiguous, foreign, corrupt, busy, or repeated repairs without mutation

### Slice 16 — deterministic non-canonical JSONL event export

- `export_stable_events(...)`
- `sudachi export events <organism_id> --event-sequence <N>`
- caller-declared registered stable boundary
- read-only SQLite snapshot transaction
- exact active, registry, checkpoint, lineage, version, digest, and event-range validation
- canonical manifest and event serialization
- byte-identical repeated output
- temporary-file validation and atomic replacement
- proof that export creation, modification, deletion, and failure cannot alter canonical state or wakeability

JSONL remains disposable and non-canonical. There is no import or lifecycle dual-write.

### Slice 17 — rollback source validation and pre-rollback archive

- `prepare_rollback_archive(...)`
- `sudachi rollback prepare <organism_id> --event-sequence <N>`
- fail-fast `BEGIN IMMEDIATE` administrative ownership
- stable `sleeping` or `maintenance_required` active-state requirement
- no pending checkpoint
- exact selection of one retained protected checkpoint by canonical boundary
- rejection of missing/pruned, ambiguous, foreign, mismatched, unsafe, busy, or pending sources
- full selected-checkpoint identity, lineage, version, digest, size, and integrity validation
- complete active SQLite snapshot through the Online Backup API
- immutable manifest containing active and selected-source rollback metadata
- bounded `rollback-archives/pre-rb-.../` temporary publication and atomic rename
- deterministic idempotent archive identity
- injected post-snapshot failure cleanup
- unchanged active SQLite digest, lineage, status, events, inbox, registry, checkpoints, and wakeability after success or failure

The ownership transaction is rolled back. Slice 17 creates no canonical event and does not enter `rollback_in_progress`.

See `docs/phase1/SLICE17_ROLLBACK_ARCHIVE_PREPARATION.md`.

## Validation state

GitHub Actions on Python 3.12 for PR #31 completed:

- clean editable installation
- source and test compilation
- genesis CLI smoke test
- **63 protected tests**

`docs/PHASE1_TEST_MATRIX.md` maps implemented coverage. Phase 1 is incomplete; passing 63 tests does not imply all 41 contract evaluations are fully satisfied.

## Known incomplete Phase 1 work

Major incomplete areas include:

- durable rollback intent and `rollback_in_progress`
- restore-candidate creation and validation
- candidate lineage transformation
- active database replacement
- rollback-completion history and abandoned-future linkage
- post-replacement failure recovery
- rollback/archive retention policy
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

## Exact next task: Slice 18

Implement only durable adoption of one verified pre-rollback archive as an active rollback intent.

1. create a new `agent/...` branch from current `main`
2. add an offline administrative Python API and narrow CLI command, preferably `rollback begin`, taking one archive identifier
3. acquire fail-fast write ownership before mutable active reads
4. validate the archive directory, manifest, archived SQLite digest and integrity, selected checkpoint, and all recorded active metadata
5. prove the current active SQLite body still exactly matches the archive's organism identity, database digest, lineage, lifecycle, status, active event boundary, latest-stable checkpoint, and latest-stable boundary
6. reject active drift, missing or foreign archive, unsafe content, selected-source mismatch, busy database, pending checkpoint, and incompatible repeated begin before mutation
7. atomically set active status to `rollback_in_progress`
8. atomically append one typed administrative `rollback_started` event containing archive identity, selected source, and exact pre-rollback active boundary
9. prove state and audit event roll back together on injected failure
10. prove normal wakes reject before clock use, claim, event creation, or environment change
11. preserve the archive, checkpoint artifacts, environment, inbox, registry, and prior event history
12. update tests, matrix, handoff, Issue #13, and a Slice 18 note
13. run GitHub Actions through a pull request

Slice 18 stops before:

- copying the selected checkpoint into a candidate database
- modifying a restore candidate
- active database replacement
- lineage-generation increment
- rollback-completed history
- final abandoned-future linkage from the restored branch
- checkpoint or archive pruning
- JSONL import
- caregiver consultation, learning, memory, skills, or generic recovery machinery

The purpose is to make rollback intent durable and crash-visible before candidate transformation or replacement is introduced.

## Restart protocol

At the next session:

1. read `AGENTS.md`
2. read this handoff and normative documents in the required order
3. inspect current open issues and pull requests
4. verify PR #31 is merged or reconcile repository truth
5. begin only from the Slice 18 boundary above

At the end of substantial work, always leave updated continuity documents, protected-test mapping, Issue status, CI results, exact unfinished work, and one precise next action.

No critical decision may remain only in chat history.
