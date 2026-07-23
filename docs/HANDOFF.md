# SUDACHI Handoff

Updated: **2026-07-23**

This file is the operational restart point for current `main`, which contains Phase 1 Slices 1–28 and accepted ADR 0007. Read `AGENTS.md` first, then the normative contract and ADRs before changing implementation.

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

Conversation rollover is based on reliability signals, not an automatic count of two merged slices. Continue through multiple bounded slices while repository, branch, pull-request, and CI state remain directly reconstructable. Reassess after several substantial slices, normally around eight to twelve, or earlier after a long debugging trail, repeated CI repair, stale context, or state confusion. Do not deliberately approach a roughly twenty-slice conversation likely to hit the platform limit.

Do not introduce a paid runner, larger or GPU runner, private-repository Actions usage, paid external service, or model/API call without explicit owner approval.

## Current work streams

### Issue #13 — Phase 1 SUDACHI-0 metabolism

Primary implementation stream. Slices 1–28 are merged on `main`. The exact next implementation boundary is Slice 29 after a fresh repository and GitHub-state reconstruction.

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
- fail-fast ownership of the replaced body
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

### Slice 23 — single completed rollback admission guard

- preserves fail-fast `BEGIN IMMEDIATE` as the administrative ownership boundary
- validates canonical state before reading mutable rollback history
- counts exact canonical `rollback_completed` events
- requires zero completed rollback events before latest-source lookup or archive-root creation
- rejects one or more events with typed `RollbackPreparationRejectedError`
- consumes no clock and changes no canonical or artifact state on rejection
- proves selected-source validation is not reached on the second attempt
- proves the complete first rollback and first new-lineage stable checkpoint remain unchanged
- proves no second archive is created
- proves a separately initialized organism remains independently eligible for its first rollback

See `docs/phase1/SLICE23_SINGLE_COMPLETED_ROLLBACK_GUARD.md`.

### Slice 24 — backward wall-time event ordering

- runs the complete first-water lifecycle while wall timestamps repeatedly move backward
- keeps monotonic readings increasing for lifecycle and checkpoint deadlines
- preserves the canonical `water_plot(bed-a)` decision and positive evaluation
- stabilizes lifecycle checkpoint boundary 13 and returns to sleep
- requires exact event sequences 1–14 despite decreasing timestamps
- proves event sequence, not wall time, remains canonical order
- adds protected coverage only; no production behavior changes

See `docs/phase1/SLICE24_BACKWARD_WALL_TIME_ORDERING.md`.

### Slice 25 — declared seed independence

- initializes two independent but otherwise identical `seed-garden-v1` organisms
- supplies the same external tick and injected clock readings
- runs complete first-water wakes with declared seeds `1` and `2`
- preserves each declared seed in `WakeResult` and canonical `wake_accepted` audit history
- normalizes only the declared seed and digest-derived checkpoint identity fields
- requires identical policy, transition, evaluation, concrete budgets, canonical state, event history, SQLite sequences, pending boundary 13, checkpoint snapshot projection, stabilization event 14, and final sleeping wakeability
- proves distinct audited seed values produce distinct checkpoint database digests, manifest digests, and digest-derived identifiers without changing behavior
- adds protected coverage only; no production behavior changes

See `docs/phase1/SLICE25_SEED_INDEPENDENCE.md`.

### Slice 26 — exact repeated-run canonical equivalence

- initializes two independent runtime roots with identical organism identity, versions, genesis time, seed-garden state, external tick, seed, and fake-clock readings
- performs two complete first-water wakes
- normalizes no declared, audit, digest, identifier, timestamp, or artifact field
- requires exact `WakeResult`, status, schema, every canonical table row, SQLite sequence state, and `user_version`
- requires identical active SQLite SHA-256 digests
- requires identical checkpoint identifiers, manifests, database and manifest digests, and complete checkpoint-store relative file sets
- requires every checkpoint artifact size and SHA-256 digest to match
- proves both sleeping organisms accept the same next tick with exact continued canonical equivalence
- adds protected coverage only; no production behavior changes

See `docs/phase1/SLICE26_REPEATED_RUN_EQUIVALENCE.md`.

### Slice 27 — protected cleanup-grace boundary

- detects the exhausted normal-work budget before executor entry
- preserves zero action attempts, zero environment mutations, zero retries, and zero caregiver or external effects after the 2000 ms deadline
- adds one declared injected clock read after terminal events are prepared
- records the complete terminalization elapsed time in the budget ledger
- accepts typed terminalization at exactly 2250 ms
- rejects 2250 ms plus one nanosecond with typed `BudgetExhaustedError`
- prevents checkpoint work after cleanup-capacity exhaustion
- rolls back every uncommitted lifecycle event, SQLite sequence increment, state change, and inbox claim on overrun
- leaves the queued input unclaimed and unconsumed

See `docs/phase1/SLICE27_CLEANUP_GRACE_BOUNDARY.md`.

### Slice 28 — insertion-order-independent tie breaking

- stabilizes a protected fixture whose physical rowid order is `bed-b`, then `bed-a`
- makes both plots executable watering targets
- requires canonical observation and applicable-target order `bed-a`, `bed-b`
- requires fixed-policy selection of lexicographically smallest `bed-a`
- verifies one exact successful mutation, concrete budgets, event order, checkpoint boundary 16, stabilization event 17, and final sleep
- preserves the reversed physical row order after action
- preserves the declared seed as audit input without using it as a tie breaker
- accepts a later distinct input
- adds protected coverage only; no production behavior changes

See `docs/phase1/SLICE28_INSERTION_ORDER_TIE_BREAKING.md`.

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

Slice 28 GitHub Actions run 263 on Python 3.12 completed twice on the exact test-first head:

- initial attempt: **123 protected tests passed in 99.70 seconds**
- exact rerun: **123 protected tests passed in 6.92 seconds**
- clean editable installation passed
- source and test compilation passed
- genesis CLI smoke passed

The slow initial attempt did not reproduce on the exact rerun and is treated as transient runner latency. No Slice 28 production correction was required.

The workflow remains the public-repository standard `ubuntu-latest` runner with a ten-minute timeout and seven-day small pytest-log artifact. No paid runner or expanded artifact retention is enabled.

## Known incomplete Phase 1 work

Major incomplete areas include:

- complete post-action duplicate-input replay scenario
- process-crash-before-commit execution test
- nested-wake rejection
- explicit second-wake rejection while a prior checkpoint is pending
- broader protected-authority tests

Do not weaken existing tests to make these easier.

## Exact next task: Slice 29

After reconstructing current `main`, Issue #13, and open pull requests, implement only the next incomplete fixed Phase 1 evaluation as a separate branch.

The next bounded subject is evaluation 16: replaying a consumed external tick identifier after its successful action must never produce another action.

Before implementation:

1. confirm no newer repository decision or open pull request changes this ordering
2. run and stabilize one complete successful action for a declared external event identifier
3. capture exact canonical state, event history, inbox row, SQLite sequence state, checkpoint registry, and immutable checkpoint artifacts
4. replay the same consumed external identifier through `enqueue_garden_tick(...)` with a fake clock that has no readings
5. require `inserted=False`, the original inbox identity and received timestamp, zero clock reads, no new event, no new inbox row, and no canonical or artifact change
6. prove no claimable duplicate input, second lifecycle, or second action can result from the replay
7. prove a later distinct event identifier remains accepted and processable
8. add the protected scenario before changing production code
9. make a production correction only if the existing implementation violates the accepted contract
10. update the Slice 29 note, matrix, this handoff, `AGENTS.md`, and Issue #13
11. run GitHub Actions through a pull request

Do not begin generic replay machinery, rollback-artifact deletion, pruning, schema or contract changes, repeated rollback support, JSONL import, caregiver integration, learning, memory, skills, or generic recovery machinery.

## Restart protocol

At the next session or clean reconstruction point:

1. read `AGENTS.md`
2. read `docs/AI_COLLABORATION_OPERATIONS.md`
3. read this handoff and normative documents in order
4. inspect current open issues and pull requests
5. verify PR #44 is merged on current `main`, or reconcile newer repository truth
6. begin only from the exact Slice 29 boundary above

At the end of substantial work, leave updated continuity documents, protected-test mapping, Issue status, CI results, exact unfinished work, and one precise next action. Apply calibrated rollover guidance instead of an automatic two-slice cutoff.

No critical decision may remain only in chat history.
