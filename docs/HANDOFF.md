# SUDACHI Handoff

Updated: **2026-07-23**

This file is the operational restart point for current `main`, which contains Phase 1 Slices 1–25 and accepted ADR 0007. Read `AGENTS.md` first, then the normative contract and ADRs before changing implementation.

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

Primary implementation stream. Slices 1–25 are merged on `main`. The exact next implementation boundary is Slice 26 after a fresh repository and GitHub-state reconstruction.

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

GitHub Actions run 237 for the complete Slice 25 implementation-and-continuity head on Python 3.12 completed:

- clean editable installation
- source and test compilation
- genesis CLI smoke test
- **119 protected tests passed in 6.57 seconds**

No Slice 25 production correction was required. The existing fixed policy passed the complete seed-independence comparison unchanged.

The workflow remains the public-repository standard `ubuntu-latest` runner with a ten-minute timeout and seven-day small pytest-log artifact. No paid runner or expanded artifact retention is enabled.

## Known incomplete Phase 1 work

Major incomplete areas include:

- complete repeated-run canonical equivalence
- cleanup-grace boundary coverage
- altered insertion-order tie-breaking scenario
- post-action duplicate-input replay scenario
- process-crash-before-commit execution test
- nested-wake rejection
- explicit second-wake rejection while a prior checkpoint is pending
- broader protected-authority tests

Do not weaken existing tests to make these easier.

## Exact next task: Slice 26

After reconstructing current `main`, Issue #13, and open pull requests, implement only the next incomplete fixed Phase 1 evaluation as a separate branch.

The next bounded subject is evaluation 1: complete repeated-run canonical equivalence for identical declared inputs.

Before implementation:

1. confirm no newer repository decision or open pull request changes this ordering
2. create two independent complete canonical first-wake runs with identical organism identity, external event identifier, seed, and injected clock readings
3. define an exact comparison that normalizes no declared input
4. require identical logical canonical state, event history, SQLite sequence state, lifecycle boundaries, checkpoint manifests, database and manifest digests, digest-derived checkpoint identifiers, stable status, and wakeability
5. add the comparative protected test before changing production code
6. make a production correction only if the existing implementation violates the accepted contract
7. update the Slice 26 note, matrix, this handoff, `AGENTS.md`, and Issue #13
8. run GitHub Actions through a pull request

Do not begin generic replay or random-number machinery, rollback-artifact deletion, pruning, schema changes, repeated rollback support, JSONL import, caregiver integration, learning, memory, skills, or generic recovery machinery.

## Restart protocol

At the next session:

1. read `AGENTS.md`
2. read `docs/AI_COLLABORATION_OPERATIONS.md`
3. read this handoff and normative documents in order
4. inspect current open issues and pull requests
5. verify PR #41 is merged on current `main`, or reconcile newer repository truth
6. begin only from the exact Slice 26 boundary above

At the end of substantial work, leave updated continuity documents, protected-test mapping, Issue status, CI results, exact unfinished work, and one precise next action. Apply the early chat-rollover triggers rather than waiting for a hard conversation limit.

No critical decision may remain only in chat history.
