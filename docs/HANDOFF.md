# SUDACHI Handoff

Updated: **2026-07-22**

This file is the operational restart point for repository state containing Phase 1 Slices 1–21. Read `AGENTS.md` first, then the normative contract and ADRs before changing implementation.

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

Phase 1 has one canonical SQLite body, append-only sequence-ordered events, injected clocks, fail-fast write ownership, deterministic `seed-garden-v1`, concrete budgets, protected evaluation, exact checkpoint boundaries, immutable checkpoints, bounded retention, rollback lineage rules, and explicit administrative boundaries.

Phase 1 has no caregiver, model adapter, chat interface, network access, subprocess access, arbitrary generated code, learning, memory, skills, continuous execution, or generic autonomous loop.

## Current work streams

### Issue #13 — Phase 1 SUDACHI-0 metabolism

Primary implementation stream. Slices 1–21 are implemented in repository state containing this handoff.

### Issue #3 — prior work and provider review

Research stream. Preliminary evidence and provider-neutral strategy exist, but no strong novelty claim and no live caregiver selection are authorized.

## Implemented Phase 1 slices

### Slices 1–5 — canonical body and garden run

- Python 3.12 package and CLI
- canonical SQLite schema and append-only events
- injected clocks and fail-fast wake ownership
- deterministic inbox claim and observation
- stable genesis checkpoint
- canonical water, harvest, and objective-complete abstention run
- protected budgets, savepoints, evaluation, and checkpointing

### Slices 6–9 — classified failure and recovery

- typed no-action abstention
- resource-aware fallback
- action-failure savepoint rollback with preserved attempt cost
- monotonic lifecycle deadline exhaustion before mutation
- unchanged-state evaluation and stable checkpointing

### Slices 10–12 — maintenance

- exact failure-threshold entry into `maintenance_required`
- blocked later wake
- read-only inspection
- explicit atomic administrative clear

### Slices 13–15 — checkpoint retention and repair

- bounded retention limit four
- newest-before-prune stabilization
- genesis and latest preservation
- oldest eligible pruning
- classified pruning failure with artifact restoration
- explicit exact pending registration repair

### Slice 16 — deterministic non-canonical JSONL export

- declared stable-boundary export
- read-only canonical source
- exact checkpoint and event-range validation
- byte-identical canonical JSONL
- bounded atomic publication
- no import or dual-write

### Slice 17 — rollback source and pre-rollback archive

- exact retained source validation
- complete active SQLite Online Backup snapshot
- immutable abandoned-future and source metadata
- bounded deterministic archive publication
- no canonical mutation or event

### Slice 18 — durable rollback intent

- complete archive and active-body revalidation
- exact canonical SQLite logical equality
- atomic `rollback_in_progress` plus `rollback_started`
- zero-clock rejection paths
- preserved inputs and blocked normal wake

### Slice 19 — verified source-restored candidate

- selected checkpoint restored through Online Backup
- exact source equality and protected provenance validation
- deterministic immutable `source_restored_untransformed` candidate
- atomic publication, idempotence, and failure cleanup
- no active mutation

### Slice 20 — isolated candidate lineage transformation

- explicit bounded administrative reason
- exact `abandoned_active_generation + 1` derivation
- candidate-only transformation transaction
- source pending fields cleared in isolation
- selected registry row reconstructed
- source history preserved
- one new-lineage `rollback_lineage_prepared` event
- deterministic immutable `lineage_transformed_replacement_ready` candidate
- complete table-difference and sequence validation
- active and all immutable inputs unchanged

See `docs/phase1/SLICE20_CANDIDATE_LINEAGE_TRANSFORMATION.md`.

### Slice 21 — protected active-database authority transfer

- `replace_active_with_candidate(...)`
- `sudachi rollback replace-active <organism_id> --candidate-id <ID>`
- fail-fast ownership of the old blocked active body
- complete intent, archive, selected checkpoint, source-candidate, and transformed-candidate revalidation
- bounded same-filesystem staging through SQLite Online Backup
- full staged integrity, foreign-key, canonical, and exact candidate-equality validation
- old active and candidate digest recheck after closing SQLite handles
- one same-filesystem atomic `os.replace()` of canonical `organism.sqlite3`
- immutable archive and candidate artifacts preserved
- immediate reopened active validation
- exact active-versus-transformed-candidate logical equality
- new active body remains `rollback_in_progress` with `rollback_lineage_prepared` at the tip
- normal wakes remain blocked before clock or claim
- pre-transfer failure preserves the old active body and removes staging
- post-transfer interruption leaves the valid new blocked body detectable
- exact repeat revalidates and recovers without rewriting
- incompatible post-replacement drift is rejected

The pre-rollback archive remains the authoritative abandoned future. Slice 21 transfers canonical authority but does not record rollback completion.

See `docs/phase1/SLICE21_ACTIVE_DATABASE_REPLACEMENT.md`.

## Validation state

GitHub Actions on Python 3.12 for the PR #35 implementation head completed:

- clean editable installation
- source and test compilation
- genesis CLI smoke test
- **107 protected tests**

The first PR run failed during test collection because the new module imported singular `checkpoint` instead of the existing canonical `checkpoints` module. No protected test behavior ran in that attempt. The import was corrected and the next implementation run passed all 107 tests.

The final continuity head must remain green before merge.

`docs/PHASE1_TEST_MATRIX.md` maps implemented coverage. Phase 1 is incomplete; passing 107 tests does not imply all 41 contract evaluations are complete.

The workflow remains the existing public-repository standard `ubuntu-latest` runner with a ten-minute timeout and seven-day small pytest-log artifact. Slice 21 adds no paid runner, larger runner, GPU runner, private-repository usage, or expanded artifact retention.

## Known incomplete Phase 1 work

Major incomplete areas include:

- rollback-completion transaction
- restored wakeability
- first post-rollback stable checkpoint and archive-protection confirmation
- rollback archive and candidate retention policy
- complete repeated-run canonical equivalence
- backward-wall-time ordering scenario
- explicit seed-independence comparison
- cleanup-grace boundary coverage
- altered insertion-order tie-breaking scenario
- post-action duplicate-input replay scenario
- process-crash-before-commit execution test
- nested-wake rejection
- explicit second-wake rejection while a prior checkpoint is pending
- broader protected-authority tests

Do not weaken existing tests to make these easier.

## Exact next task: Slice 22

Implement only rollback completion on the already replaced and fully validated active body.

1. create a new `agent/...` branch from current `main`
2. expose an offline administrative Python API and narrow CLI command accepting one transformed-candidate identifier
3. acquire fail-fast ownership of the replaced active database before mutable reads
4. require `rollback_in_progress`, no pending checkpoint, the new lineage generation, and exact `rollback_lineage_prepared` at the active tip
5. revalidate the complete selected-checkpoint, archive, source-candidate, transformed-candidate, and active-replacement provenance chain, including exact active-versus-candidate equality
6. reject missing, foreign, drifted, unsafe, ambiguous, busy, incomplete, or incompatible repeated state before clock use or mutation
7. read one injected administrative clock only after complete validation
8. atomically change the restored body to the correct stable wakeable status and append exactly one next-sequence `rollback_completed` event
9. bind administrative reason, selected target, abandoned future, old and new lineages, candidate identifiers and digests, replacement validation, implementation version, and final status in the payload
10. preserve organism identity, new lineage, source lifecycle, environment, selected-boundary inbox, registry, protected versions, and all prior history
11. prove injected post-event failure rolls back status and completion history together and leaves wake blocked
12. make exact repeated completion idempotent without a second clock read and reject incompatible repeat
13. prove wake rejection before completion and normal wakeability after completion
14. preserve every rollback artifact; do not delete or prune
15. update tests, matrix, this handoff, Issue #13, and a Slice 22 note
16. run GitHub Actions through a pull request

Slice 22 stops before:

- rollback archive or candidate deletion or pruning
- a new long-term artifact-retention policy
- JSONL import
- caregiver consultation, learning, memory, skills, or generic recovery machinery

The purpose is to make the already transferred body explicitly complete and wakeable without conflating completion with later artifact retention or broader Phase 1 closure.

## Restart protocol

At the next session:

1. read `AGENTS.md`
2. read this handoff and normative documents in order
3. inspect current open issues and pull requests
4. verify PR #35 is merged or reconcile repository truth
5. begin only from the Slice 22 boundary above

At the end of substantial work, leave updated continuity documents, protected-test mapping, Issue status, CI results, exact unfinished work, and one precise next action.

No critical decision may remain only in chat history.
