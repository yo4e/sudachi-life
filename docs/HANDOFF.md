# SUDACHI Handoff

Updated: **2026-07-22**

This file is the operational restart point for repository state containing Phase 1 Slices 1–18. Read `AGENTS.md` first, then the normative contract and ADRs before changing implementation.

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

Primary implementation stream. Slices 1–18 are implemented in repository state containing this handoff.

### Issue #3 — prior work and provider review

Research stream. Preliminary evidence and provider-neutral strategy exist, but no strong novelty claim and no live caregiver selection are authorized. This stream does not block deterministic caregiver-free Phase 1 mechanics.

## Implemented Phase 1 slices

### Slices 1–5 — canonical body and garden run

- Python 3.12 package and CLI
- canonical SQLite schema and append-only events
- injected clocks and fail-fast wake ownership
- deterministic inbox claim and observation
- stable genesis checkpoint
- first wake waters `bed-a`, boundary `13`
- second wake harvests `bed-b`, boundary `24`
- third wake records justified objective-complete abstention, boundary `34`
- protected budgets, savepoints, evaluation, and checkpointing

### Slices 6–9 — classified failure and recovery

- typed `no_applicable_action`
- resource-aware harvest fallback and failure reset
- injected partial action failure with savepoint rollback and preserved attempt cost
- monotonic lifecycle deadline exhaustion before action or mutation
- unchanged-state independent evaluation and stable checkpointing

### Slices 10–12 — maintenance

- exact third-failure transition into `maintenance_required`
- later wake rejection before clock or input claim
- read-only maintenance inspection
- explicit administrative maintenance clear
- atomic reset plus typed audit history
- preservation of environment, checkpoints, and queued input

### Slices 13–15 — checkpoint retention and repair

- retention limit four
- newest checkpoint stabilizes before pruning
- genesis and latest preservation
- oldest eligible non-genesis pruning
- classified pruning failure with staged-artifact restoration
- explicit registration repair for exactly one valid published orphan
- rejection of missing, ambiguous, foreign, corrupt, busy, or repeated repair without mutation

### Slice 16 — deterministic non-canonical JSONL event export

- `export_stable_events(...)`
- narrow `sudachi export events ...`
- caller-declared registered stable boundary
- read-only canonical SQLite source
- exact registry, checkpoint, lineage, version, digest, and event-range validation
- canonical byte-identical JSONL
- bounded temporary publication and atomic replacement
- proof that export creation, modification, deletion, and failure cannot alter canonical state or wakeability

JSONL remains disposable and non-canonical. There is no import or lifecycle dual-write.

### Slice 17 — rollback source and pre-rollback archive

- `prepare_rollback_archive(...)`
- `sudachi rollback prepare ...`
- fail-fast administrative ownership
- stable active state with no pending checkpoint
- exact retained protected source selection
- rejection of missing, pruned, ambiguous, foreign, mismatched, unsafe, busy, or pending source
- complete active SQLite snapshot through the Online Backup API
- immutable manifest containing active-future and selected-source metadata
- bounded `rollback-archives/pre-rb-.../` publication
- deterministic idempotent archive identity
- injected post-snapshot failure cleanup
- unchanged active state and wakeability after success or failure

Slice 17 creates no canonical event and does not enter rollback state.

### Slice 18 — durable rollback intent

- `begin_rollback(...)`
- `sudachi rollback begin <organism_id> --archive-id <ID>`
- fail-fast ownership before mutable reads
- exact archive directory, manifest, database digest, integrity, and provenance validation
- exact active metadata comparison
- exact active-versus-archive SQLite comparison covering `user_version`, schema, every canonical table row, and `sqlite_sequence`
- revalidation of latest-stable state and immutable selected checkpoint
- zero-clock rejection of active drift, foreign or unsafe archive, selected-source drift, busy state, pending state, and repeated begin
- one injected clock read only after complete validation
- atomic `sleeping|maintenance_required -> rollback_in_progress` plus one next-sequence `rollback_started` event
- injected post-event failure proving status and audit history roll back together
- preserved archive, checkpoint artifacts, environment, inbox, registry, lineage, lifecycle, and prior history
- later normal-wake rejection before clock use or input claim

SQLite Online Backup is a complete logical snapshot but not assumed to be raw-file-byte-identical to the active file. Slice 18 validates the archive artifact's own digest and proves exact canonical SQLite content equality instead.

See `docs/phase1/SLICE18_DURABLE_ROLLBACK_INTENT.md`.

## Validation state

GitHub Actions on Python 3.12 for the PR #32 implementation head completed:

- clean editable installation
- source and test compilation
- genesis CLI smoke test
- **72 protected tests**

The final continuity-only head must also remain green before merge.

`docs/PHASE1_TEST_MATRIX.md` maps implemented coverage. Phase 1 is incomplete; passing 72 tests does not imply all 41 contract evaluations are complete.

## Known incomplete Phase 1 work

Major incomplete areas include:

- restore-candidate construction and validation
- candidate lineage transformation
- active database replacement
- rollback-completion history and abandoned-future linkage
- post-replacement failure recovery
- rollback archive and candidate retention policy
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

## Exact next task: Slice 19

Implement only protected restore-candidate construction from the durable rollback intent.

1. create a new `agent/...` branch from current `main`
2. expose an offline administrative Python API and narrow CLI command for constructing one candidate from the active rollback intent
3. acquire fail-fast ownership before mutable active reads
4. require status `rollback_in_progress`, no pending checkpoint, and one current-lineage `rollback_started` event at the active tip
5. validate the event payload, referenced archive, archived abandoned future, selected checkpoint registry row, and immutable selected source
6. reject missing, foreign, drifted, unsafe, ambiguous, busy, or inconsistent intent before candidate creation
7. restore the selected checkpoint into a bounded same-filesystem temporary candidate through SQLite's Online Backup API
8. validate candidate integrity, foreign keys, protected versions and configuration, organism identity, source lineage, lifecycle, event boundary, and exact source-checkpoint equality
9. publish no candidate until validation and same-filesystem atomic publication succeed
10. prove creation or publication failure leaves active `rollback_in_progress`, `rollback_started`, archive, source checkpoint, inbox, registry, environment, and prior history unchanged
11. update tests, matrix, this handoff, Issue #13, and a Slice 19 note
12. run GitHub Actions through a pull request

Slice 19 stops before:

- changing candidate lineage generation
- appending restored-lineage or rollback-completed history
- replacing the active database
- clearing `rollback_in_progress`
- deleting or pruning checkpoints, archives, or candidates
- JSONL import
- caregiver consultation, learning, memory, skills, or generic recovery machinery

The purpose is to isolate source restoration and candidate integrity before lineage transformation or the destructive active-replacement boundary.

## Restart protocol

At the next session:

1. read `AGENTS.md`
2. read this handoff and normative documents in order
3. inspect current open issues and pull requests
4. verify PR #32 is merged or reconcile repository truth
5. begin only from the Slice 19 boundary above

At the end of substantial work, leave updated continuity documents, protected-test mapping, Issue status, CI results, exact unfinished work, and one precise next action.

No critical decision may remain only in chat history.
