# SUDACHI Handoff

Updated: **2026-07-23**

This file is the operational restart point for repository state containing Phase 1 Slices 1–22 plus accepted ADR 0007. Read `AGENTS.md` first, then the normative contract and ADRs before changing implementation.

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
2. ADRs 0001–0007 in `docs/decisions/`
3. protected Phase 1 tests and `docs/PHASE1_TEST_MATRIX.md`

Phase 1 has one canonical SQLite body, append-only sequence-ordered events, injected clocks, fail-fast write ownership, deterministic `seed-garden-v1`, concrete budgets, protected evaluation, exact checkpoint boundaries, immutable checkpoints, bounded retention, rollback lineage rules, and explicit administrative boundaries.

Phase 1 has no caregiver, model adapter, chat interface, network access, subprocess access, arbitrary generated code, learning, memory, skills, continuous execution, or generic autonomous loop.

## AI collaboration operations

Read `docs/AI_COLLABORATION_OPERATIONS.md`.

SUDACHI's biological vocabulary describes local deterministic software and a synthetic garden, not wet-lab biology. Repository work must not evade product safeguards. State concrete benign software context when relevant, accept delayed or blocked requests, and never conceal material intent.

Use structural chat rollover instead of guessed token counts. Prefer a new chat at the next clean boundary after two substantial merged slices, a long debugging trail, or one major decision plus implementation. Do not exceed three substantial merged slices in one chat unless required to leave the current unit safe and explicit.

Do not introduce a paid runner, larger or GPU runner, private-repository Actions usage, paid external service, or model/API call without explicit owner approval.

## Current work streams

### Issue #13 — Phase 1 SUDACHI-0 metabolism

Primary implementation stream. Slices 1–22 are implemented. ADR 0007 is accepted and awaiting narrow enforcement in Slice 23.

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
- one same-filesystem atomic `os.replace()` of canonical `organism.sqlite3`
- immutable archive and candidate artifacts preserved
- immediate reopened active validation
- new active remains blocked with `rollback_lineage_prepared` at the tip
- pre-transfer failure preservation
- detectable and exactly recoverable post-transfer interruption

See `docs/phase1/SLICE21_ACTIVE_DATABASE_REPLACEMENT.md`.

### Slice 22 — atomic rollback completion and wakeability

- `complete_rollback(...)`
- `sudachi rollback complete <organism_id> --candidate-id <ID>`
- fail-fast ownership of the replaced active body
- complete provenance-chain revalidation before clock use
- one injected administrative clock read only after validation
- atomic `rollback_in_progress -> sleeping` plus one exact `rollback_completed`
- restored failure count reset and maintenance clear
- exact payload binding original reason, target, abandoned future, lineages, candidate identifiers and digests, and replacement validation
- injected failure proves status and history roll back together
- exact repeated completion consumes zero clock and performs no mutation
- normal wake blocked before completion and enabled only afterward
- first new-lineage wake creates and registers a stable lifecycle checkpoint
- all rollback artifacts remain unchanged

See `docs/phase1/SLICE22_ROLLBACK_COMPLETION.md`.

## Accepted ADR 0007 retention boundary

Phase 1 permits at most one completed rollback per organism.

The following evidence remains immutable and retained:

- the verified pre-rollback archive containing the abandoned future
- the source-restored candidate
- the lineage-transformed authority-transfer candidate
- canonical `rollback_lineage_prepared` and `rollback_completed` history
- the first post-rollback stable checkpoint

There is no rollback-artifact deletion or pruning in Phase 1. A second rollback experiment uses a new organism identity. This bounds evidence growth without introducing deletion authority or partial-pruning recovery.

## Validation state

GitHub Actions on Python 3.12 for the final PR #36 head completed:

- clean editable installation
- source and test compilation
- genesis CLI smoke test
- **115 protected tests**

The first Slice 22 run found one exception-classification failure. The lower-level archive drift detection was correct; the completion boundary was corrected to classify the cause as `RollbackCompletionRejectedError`. Subsequent implementation and final-continuity runs passed.

The workflow remains the public-repository standard `ubuntu-latest` runner with a ten-minute timeout and seven-day small pytest-log artifact. No paid runner or expanded artifact retention is enabled.

## Known incomplete Phase 1 work

Major incomplete areas include:

- ADR 0007 enforcement at rollback preparation
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

## Exact next task: Slice 23

Implement only the single-completed-rollback admission guard required by ADR 0007.

1. create a new `agent/...` branch from current `main`
2. acquire fail-fast ownership exactly as existing rollback preparation does
3. validate canonical state before reading mutable rollback history
4. count canonical `rollback_completed` events before source selection or archive-root creation
5. require exactly zero completed rollbacks for preparation eligibility
6. reject one or more with typed `RollbackPreparationRejectedError`
7. consume no clock and create or modify no archive, candidate, checkpoint, inbox, registry, environment, organism row, or event on rejection
8. prove the complete first rollback path remains unchanged
9. prove a second preparation attempt after completion and the first new-lineage checkpoint creates no second archive
10. prove a newly initialized separate organism remains eligible for its first rollback
11. update tests, matrix, this handoff, Issue #13, and a Slice 23 note
12. run GitHub Actions through a pull request

Slice 23 stops before artifact deletion, pruning, schema changes, repeated rollback support, JSONL import, caregiver integration, learning, memory, skills, or generic recovery machinery.

## Restart protocol

At the next session:

1. read `AGENTS.md`
2. read `docs/AI_COLLABORATION_OPERATIONS.md`
3. read this handoff and normative documents in order
4. inspect current open issues and pull requests
5. verify the ADR 0007 decision PR is merged or reconcile repository truth
6. begin only from the Slice 23 boundary above

At the end of substantial work, leave updated continuity documents, protected-test mapping, Issue status, CI results, exact unfinished work, and one precise next action. Apply the early chat-rollover triggers rather than waiting for a hard conversation limit.

No critical decision may remain only in chat history.
