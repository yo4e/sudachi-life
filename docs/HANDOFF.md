# SUDACHI Handoff

Updated: **2026-07-22**

This file is the operational restart point for repository state containing Phase 1 Slices 1–22. Read `AGENTS.md` first, then the normative contract and ADRs before changing implementation.

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

Primary implementation stream. Slices 1–22 are implemented in repository state containing this handoff.

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

### Slices 17–18 — abandoned future and durable intent

- exact retained rollback-source validation
- complete active SQLite Online Backup snapshot
- immutable abandoned-future and source metadata
- bounded deterministic archive publication
- complete archive and active-body revalidation
- exact canonical SQLite logical equality
- atomic `rollback_in_progress` plus `rollback_started`
- zero-clock rejection paths
- blocked normal wake

### Slices 19–20 — source restoration and new-lineage candidate

- selected checkpoint restored through Online Backup
- exact source equality and protected provenance validation
- deterministic immutable `source_restored_untransformed` candidate
- explicit bounded administrative reason
- exact `abandoned_active_generation + 1` derivation
- candidate-only transformation transaction
- source pending fields cleared in isolation
- selected registry row reconstructed
- source history preserved
- one new-lineage `rollback_lineage_prepared` event
- deterministic immutable `lineage_transformed_replacement_ready` candidate
- active and all immutable inputs unchanged

See:

- `docs/phase1/SLICE19_RESTORE_CANDIDATE_CONSTRUCTION.md`
- `docs/phase1/SLICE20_CANDIDATE_LINEAGE_TRANSFORMATION.md`

### Slice 21 — protected active-database authority transfer

- `replace_active_with_candidate(...)`
- `sudachi rollback replace-active <organism_id> --candidate-id <ID>`
- fail-fast ownership of the old blocked active body
- complete provenance-chain revalidation
- bounded same-filesystem staging through SQLite Online Backup
- staged integrity, foreign-key, canonical, and exact equality validation
- old-active and candidate digest recheck after closing SQLite handles
- one same-filesystem atomic `os.replace()` of canonical `organism.sqlite3`
- immutable archive and candidate artifacts preserved
- immediate reopened active validation
- exact active-versus-transformed-candidate logical equality
- new active remains blocked with `rollback_lineage_prepared` at the tip
- pre-transfer failure preservation
- detectable and exactly recoverable post-transfer interruption

See `docs/phase1/SLICE21_ACTIVE_DATABASE_REPLACEMENT.md`.

### Slice 22 — atomic rollback completion and wakeability

- `complete_rollback(...)`
- `sudachi rollback complete <organism_id> --candidate-id <ID>`
- fail-fast ownership of the replaced active body
- complete checkpoint, archive, source-candidate, transformed-candidate, and active-replacement revalidation before clock use
- one injected administrative clock read only after validation
- atomic `rollback_in_progress -> sleeping` transition plus one exact `rollback_completed`
- restored failure count reset and maintenance clear
- exact payload binding original reason, target, abandoned future, old and new lineages, candidate identifiers and digests, and replacement validation
- environment, inbox, registry, protected versions, and prior history preserved
- injected failure proving status and completion history roll back together
- exact repeated completion with zero clock reads and no mutation
- incompatible completed history rejected
- normal wake blocked before completion
- normal wake enabled only after completion
- first new-lineage wake creates and registers a new stable lifecycle checkpoint
- pre-rollback archive and both candidates remain unchanged through that checkpoint

See `docs/phase1/SLICE22_ROLLBACK_COMPLETION.md`.

## Validation state

GitHub Actions on Python 3.12 for the PR #36 implementation head completed:

- clean editable installation
- source and test compilation
- genesis CLI smoke test
- **115 protected tests**

The first Slice 22 run found one failure: archive drift was detected correctly but escaped as the lower-level `RollbackArchiveError`. The completion boundary was corrected to preserve the exact cause while classifying subsystem failures as `RollbackCompletionRejectedError`. The subsequent implementation run passed all 115 tests.

The final continuity head must remain green before merge.

`docs/PHASE1_TEST_MATRIX.md` maps implemented coverage. Phase 1 is incomplete; passing 115 tests does not imply all 41 contract evaluations are complete.

The workflow remains the existing public-repository standard `ubuntu-latest` runner with a ten-minute timeout and seven-day small pytest-log artifact. Slices 20–22 introduced no paid runner, larger runner, GPU runner, private-repository usage, or expanded artifact retention.

## Known incomplete Phase 1 work

Major incomplete areas include:

- accepted rollback archive and candidate retention policy
- bounded behavior across multiple completed rollbacks
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

## Exact next task: rollback-artifact retention decision

Do not implement rollback archive or candidate deletion yet.

The next work must be a reviewed decision boundary:

1. reconcile current `main`, Issue #13, and open pull requests
2. review Contract v0.2 rollback retention requirements, ADR 0004, the runtime working-set limit, and Slices 17–22
3. draft a new decision record before implementation
4. define which abandoned-future archive and candidate artifacts remain protected after the first post-rollback stable checkpoint
5. define whether source and transformed candidates are reconstructible or independently required for audit
6. define how multiple completed rollbacks remain bounded
7. define what evidence permits an abandoned-future archive to be removed
8. define same-filesystem atomic pruning and classified pruning-failure restoration
9. decide whether Phase 1 permits pruning or instead imposes a bounded completed-rollback count while retaining every artifact
10. update roadmap, matrix, this handoff, and Issue #13 after acceptance

No deletion implementation, remote backup assumption, or generic cleanup machinery may precede the accepted decision.

## Restart protocol

At the next session:

1. read `AGENTS.md`
2. read this handoff and normative documents in order
3. inspect current open issues and pull requests
4. verify PR #36 is merged or reconcile repository truth
5. begin with the rollback-artifact retention decision, not deletion code

At the end of substantial work, leave updated continuity documents, protected-test mapping, Issue status, CI results, exact unfinished work, and one precise next action.

No critical decision may remain only in chat history.
