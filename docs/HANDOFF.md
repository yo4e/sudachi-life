# SUDACHI Handoff

Updated: **2026-07-23**

This file is the operational restart point for current `main`, which contains Phase 1 Slices 1–32 and accepted ADR 0007. Read `AGENTS.md` first, then the normative contract and ADRs before changing implementation.

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

Phase 1 has no caregiver, model adapter, chat interface, network access, organism subprocess access, organism-writable external workspace, arbitrary generated code, learning, memory, skills, continuous execution, or generic autonomous loop.

## AI collaboration operations

Read `docs/AI_COLLABORATION_OPERATIONS.md`.

Conversation rollover is based on reliability signals, not an automatic count of two merged slices. Continue through multiple bounded slices while repository, branch, pull-request, and CI state remain directly reconstructable. Reassess normally around eight to twelve substantial slices, or earlier after a long debugging trail, repeated CI repair, stale context, or state confusion. Do not deliberately approach a roughly twenty-slice conversation likely to hit the platform limit.

Do not introduce a paid runner, larger or GPU runner, private-repository Actions usage, paid external service, or model/API call without explicit owner approval.

## Current work streams

### Issue #13 — Phase 1 SUDACHI-0 metabolism

Primary implementation stream. Slices 1–32 are merged on `main`. The exact next implementation boundary is Slice 33 after a fresh repository and GitHub-state reconstruction.

### Issue #3 — prior work and provider review

Research stream. Preliminary evidence and provider-neutral strategy exist, but no strong novelty claim and no live caregiver selection are authorized.

## Implemented Phase 1 summary

### Slices 1–23 — canonical metabolism, bounded storage, and rollback

- canonical SQLite body, append-only events, injected clocks, and fail-fast write ownership
- deterministic seed-garden water, harvest, abstention, classified failure, and recovery paths
- concrete budgets, lifecycle deadline, savepoint rollback, maintenance, and checkpoint retention/repair
- deterministic non-canonical JSONL export
- complete bounded rollback path from verified archive through restored wakeability
- one-completed-rollback retention boundary under ADR 0007

### Slices 24–26 — declared determinism

- backward wall time cannot reorder canonical events
- different declared seeds do not change fixed seed-garden behavior
- identical declared inputs produce exact canonical and checkpoint-artifact equivalence

### Slice 27 — protected cleanup grace

- organism work stops at the 2000 ms deadline
- typed terminalization may finish through exactly 2250 ms
- one nanosecond beyond cleanup capacity rolls back all uncommitted lifecycle state

### Slice 28 — insertion-order-independent tie breaking

- physical rowid order is `bed-b`, then `bed-a`
- both are executable watering targets
- canonical observation and fixed policy still choose lexicographically smallest `bed-a`

### Slice 29 — consumed-input replay protection

- duplicate enqueue after the original action consumes zero clock and returns the existing row
- database bytes, canonical state, sequences, registry, and artifacts remain exact
- no-input wake rolls back tentative history
- only a later distinct identifier creates the second action

### Slice 30 — real process-crash rollback

- a spawned external test process owns and mutates one uncommitted wake
- it exits through `os._exit(73)` without cleanup
- the parent reacquires `BEGIN IMMEDIATE`
- exact canonical/database/artifact state returns to the pre-crash snapshot
- the original tick then completes normally

### Slice 31 — nested wake and hidden writer rejection

- nested `WakeTransaction.acquire(...)` raises typed `WakeBusyError` and is not queued
- a separate hidden connection cannot acquire `BEGIN IMMEDIATE`
- both paths consume zero organism clock input and preserve exact state
- after outer close, the original tick completes exactly once

### Slice 32 — second wake blocked behind pending checkpoint

- two distinct ticks are queued before the first wake
- the first water action commits pending boundary 14 while checkpoint stabilization times out
- the second tick remains unclaimed and unconsumed
- a second wake raises typed `CheckpointRequiredError` before any clock read or event append
- active database bytes, canonical state, sequences, registry, and artifacts remain exact
- existing orphan registration repair restores stable sleep and records audit event 15
- the already queued second tick then harvests `bed-b`, completes the objective, stabilizes boundary 24, and returns to sleep

See `docs/phase1/SLICE32_PENDING_SECOND_WAKE_REJECTION.md`.

## Accepted ADR 0007 retention boundary

Phase 1 permits at most one completed rollback per organism. The complete pre-rollback archive and candidate evidence set remains immutable and retained. There is no rollback-artifact deletion or pruning in Phase 1.

## Validation state

Slice 32 final replacement PR #50 passed the exact complete head on Python 3.12 twice:

- run 293: **127 protected tests passed in 6.73 seconds**
- run 294: **127 protected tests passed in 13.73 seconds**
- clean editable installation passed
- source and test compilation passed
- genesis CLI smoke passed

No Slice 32 production correction was required. Existing pending-state validation and administrative repair passed unchanged.

Draft PRs #48 and #49 were closed without merge after GitHub failed to attach workflow runs to their later branch-head updates. PR #50 used a fresh branch created directly from the complete recorded commit and received exact-head validation before merge. No code or history was discarded.

The workflow remains the public-repository standard `ubuntu-latest` runner with a ten-minute timeout and seven-day small pytest-log artifact. No paid runner or expanded artifact retention is enabled.

## Known incomplete Phase 1 work

Major incomplete areas are the remaining protected-authority evaluations:

- no organism-writable external workspace
- broader proof that organism actions cannot modify protected authority
- complete proof that administrative effects are distinguishable from organism effects

Do not weaken existing tests to make these easier.

## Exact next task: Slice 33

The next bounded subject is evaluation 40: Phase 1 exposes no organism-writable external workspace.

Before implementation:

1. reconstruct current `main`, Issue #13, and open pull requests
2. inspect `OrganismPaths`, the registered action executor signature, and imports reachable from `execute_garden_action(...)`
3. acquire a normal wake transaction, claim the queued tick, build the canonical observation, and select the fixed action before installing guards
4. during action execution only, fail closed on Python filesystem mutation, network connection, and subprocess APIs
5. require the valid SQLite action transition to succeed without invoking any guarded external interface
6. require the action executor surface to receive no path or workspace handle
7. pass a path-like target identifier and require typed rejection as a nonexistent SQLite plot without creating or touching an external path
8. require no export, diagnostics, rollback archive, restore candidate, or other workspace directory to be created by organism action execution
9. roll back the probe and prove a normal complete wake still succeeds with hard-zero external capability budgets
10. add protected tests before changing production code
11. make a production correction only if organism action execution can reach an external effect or workspace
12. update the Slice 33 note, matrix, this handoff, `AGENTS.md`, and Issue #13
13. run GitHub Actions through a pull request

Checkpoint publication, export, diagnostics, and rollback artifacts remain explicit runtime or administrative operations outside the guarded organism-action boundary.

Do not add a workspace API, connection pool, subprocess access, generic sandbox framework, schema changes, caregiver integration, learning, memory, skills, or generic recovery machinery.

## Restart protocol

At the next session or clean reconstruction point:

1. read `AGENTS.md`
2. read `docs/AI_COLLABORATION_OPERATIONS.md`
3. read this handoff and normative documents in order
4. inspect current open issues and pull requests
5. verify PR #50 is merged on current `main`, or reconcile newer repository truth
6. begin only from the exact Slice 33 boundary above

At the end of substantial work, leave updated continuity documents, protected-test mapping, Issue status, CI results, exact unfinished work, and one precise next action. Apply calibrated rollover guidance instead of an automatic two-slice cutoff.

No critical decision may remain only in chat history.