# SUDACHI Handoff

Updated: **2026-07-22**

This file is the operational restart point for repository state containing Phase 1 Slices 1–20. Read `AGENTS.md` first, then the normative contract and ADRs before changing implementation.

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

Primary implementation stream. Slices 1–20 are implemented in repository state containing this handoff.

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
- complete active SQLite snapshot through the Online Backup API
- immutable abandoned-future and source metadata
- bounded deterministic `rollback-archives/pre-rb-.../` publication
- injected post-snapshot failure cleanup
- unchanged active state and wakeability after success or failure

Slice 17 creates no canonical event and does not enter rollback state.

### Slice 18 — durable rollback intent

- `begin_rollback(...)`
- `sudachi rollback begin <organism_id> --archive-id <ID>`
- fail-fast ownership before mutable reads
- exact archive and selected-source revalidation
- exact active-versus-archive SQLite comparison covering `user_version`, schema, every canonical row, and `sqlite_sequence`
- zero-clock rejection paths
- atomic stable-state to `rollback_in_progress` plus one next-sequence `rollback_started` event
- injected failure proving status and audit history roll back together
- preserved archive, checkpoint artifacts, environment, inbox, registry, lineage, lifecycle, and prior history
- later normal-wake rejection before clock use or input claim

SQLite Online Backup is a complete logical snapshot but is not assumed to be raw-file-byte-identical to its source.

### Slice 19 — verified source-restored candidate

- `build_restore_candidate(...)`
- `sudachi rollback build-candidate <organism_id>`
- fail-fast active ownership before mutable reads
- exact durable-intent, archive, blocked-active, selected-registry, and immutable-checkpoint revalidation
- SQLite Online Backup restoration from the selected checkpoint into a bounded same-filesystem temporary candidate
- integrity, foreign-key, protected-version, identity, source-lineage, lifecycle, pending-boundary, schema, row, and `sqlite_sequence` validation
- deterministic immutable `restore-candidates/rc-.../` representation
- validation before atomic directory publication
- idempotent repeated construction
- no canonical active mutation or event
- injected construction and publication failures leave no partial candidate

The candidate is `source_restored_untransformed`. It is an isolated logical copy of the selected checkpoint, not yet a new lineage or active organism body.

See `docs/phase1/SLICE19_RESTORE_CANDIDATE_CONSTRUCTION.md`.

### Slice 20 — isolated candidate lineage transformation

- `transform_restore_candidate(...)`
- `sudachi rollback transform-candidate <organism_id> --candidate-id <ID> --reason <TEXT>`
- explicit bounded administrative reason validation and binding
- fail-fast ownership of the blocked active database before mutable reads
- complete active intent, archive, selected checkpoint, and source-candidate revalidation before clock use
- exact `abandoned_active_generation + 1` lineage derivation under ADR 0004
- SQLite Online Backup from the immutable source candidate into a temporary working candidate
- one bounded candidate-only administrative transaction
- source pending fields cleared only in the working candidate
- exact selected stable checkpoint registry row reconstructed from the blocked active body
- status retained as non-wakeable `rollback_in_progress`
- all restored source history preserved without rewriting lineage values
- one exact next-sequence `rollback_lineage_prepared` event in the new lineage
- event payload records reason, source target, archive, abandoned future, and source-candidate provenance
- complete integrity, foreign-key, schema, protected-version, table-difference, event-order, registry, and `sqlite_sequence` validation
- deterministic immutable `restore-candidates/rtc-.../` publication after validation
- exact repeated request is idempotent without a second clock read
- different reason or corrupted existing candidate is rejected
- transaction, pre-publication, and atomic-publication failure injection leave no transformed artifact
- active body, archive, selected checkpoint, and source candidate remain unchanged on success and failure

The candidate is `lineage_transformed_replacement_ready`. It is non-canonical, non-wakeable, and has not replaced the active organism body.

See `docs/phase1/SLICE20_CANDIDATE_LINEAGE_TRANSFORMATION.md`.

## Validation state

GitHub Actions on Python 3.12 for the PR #34 implementation head completed:

- clean editable installation
- source and test compilation
- genesis CLI smoke test
- **96 protected tests**

The final continuity head must remain green before merge.

`docs/PHASE1_TEST_MATRIX.md` maps implemented coverage. Phase 1 is incomplete; passing 96 tests does not imply all 41 contract evaluations are complete.

The workflow remains the existing public-repository standard `ubuntu-latest` runner with a ten-minute timeout and seven-day small pytest-log artifact. Slice 20 adds no paid runner, larger runner, GPU runner, private-repository usage, or expanded artifact retention.

## Known incomplete Phase 1 work

Major incomplete areas include:

- active database replacement
- post-replacement validation and explicit failure recovery
- rollback-completion history and final abandoned-future linkage
- maintenance clear and restored wakeability
- post-rollback stable checkpoint policy
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

## Exact next task: Slice 21

Implement only protected active-database replacement with one verified lineage-transformed candidate and immediate post-replacement validation.

1. create a new `agent/...` branch from current `main`
2. expose an offline administrative Python API and narrow CLI command accepting one published transformed-candidate identifier
3. acquire fail-fast ownership of the blocked active database before mutable rollback-intent reads
4. require active status `rollback_in_progress`, no pending checkpoint, and the same current-lineage `rollback_started` event at the active tip
5. revalidate the archive, abandoned future, selected immutable checkpoint, source-restored candidate, transformed candidate, exact new-lineage derivation, candidate-local restoration event, and replacement-ready state
6. reject missing, foreign, drifted, unsafe, ambiguous, busy, already replaced, or inconsistent input before replacement
7. preserve the verified pre-rollback archive as the authoritative abandoned active future; do not create a naive live-file backup
8. close validation handles before replacement and use bounded same-filesystem atomic operations only
9. atomically replace the active `organism.sqlite3` with the verified transformed-candidate database while leaving the immutable transformed-candidate artifact intact
10. reopen the new active database immediately and validate integrity, foreign keys, protected versions, organism identity, new lineage, source lifecycle, selected stable boundary, candidate-local restoration history, and status `rollback_in_progress`
11. provide protected pre-replacement and post-replacement failure injection with explicit detectable recovery state; never claim rollback completion
12. leave the successfully replaced body non-wakeable in `rollback_in_progress`
13. preserve every immutable archive, checkpoint, source candidate, and transformed candidate
14. update tests, matrix, this handoff, Issue #13, and a Slice 21 note
15. run GitHub Actions through a pull request

Slice 21 stops before:

- appending active-path `rollback_completed`
- clearing `rollback_in_progress`
- enabling normal wakes
- creating or declaring the first post-rollback stable checkpoint
- deleting or pruning checkpoints, archives, or candidates
- JSONL import
- caregiver consultation, learning, memory, skills, or generic recovery machinery

The purpose is to isolate and verify the destructive filesystem authority transfer before rollback completion or wakeability.

## Restart protocol

At the next session:

1. read `AGENTS.md`
2. read this handoff and normative documents in order
3. inspect current open issues and pull requests
4. verify PR #34 is merged or reconcile repository truth
5. begin only from the Slice 21 boundary above

At the end of substantial work, leave updated continuity documents, protected-test mapping, Issue status, CI results, exact unfinished work, and one precise next action.

No critical decision may remain only in chat history.
