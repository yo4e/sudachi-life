# SUDACHI Handoff

Updated: **2026-07-23**

This file is the operational restart point for current `main`, which contains Phase 1 Slices 1–31 and accepted ADR 0007. Read `AGENTS.md` first, then the normative contract and ADRs before changing implementation.

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

Phase 1 has no caregiver, model adapter, chat interface, network access, organism subprocess access, arbitrary generated code, learning, memory, skills, continuous execution, or generic autonomous loop.

## AI collaboration operations

Read `docs/AI_COLLABORATION_OPERATIONS.md`.

Conversation rollover is based on reliability signals, not an automatic count of two merged slices. Continue through multiple bounded slices while repository, branch, pull-request, and CI state remain directly reconstructable. Reassess normally around eight to twelve substantial slices, or earlier after a long debugging trail, repeated CI repair, stale context, or state confusion. Do not deliberately approach a roughly twenty-slice conversation likely to hit the platform limit.

Do not introduce a paid runner, larger or GPU runner, private-repository Actions usage, paid external service, or model/API call without explicit owner approval.

## Current work streams

### Issue #13 — Phase 1 SUDACHI-0 metabolism

Primary implementation stream. Slices 1–31 are merged on `main`. The exact next implementation boundary is Slice 32 after a fresh repository and GitHub-state reconstruction.

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

Read the corresponding durable notes in `docs/phase1/`.

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

- one outer `WakeTransaction` owns the body
- nested acquisition raises typed `WakeBusyError` and is explicitly not queued
- a separate hidden connection cannot acquire `BEGIN IMMEDIATE`
- both paths consume zero organism clock input
- database bytes, canonical state, inbox, events, sequences, registry, and artifacts remain exact
- after outer rollback and close, the original tick completes normally exactly once

See `docs/phase1/SLICE31_NESTED_WAKE_REJECTION.md`.

## Accepted ADR 0007 retention boundary

Phase 1 permits at most one completed rollback per organism. The complete pre-rollback archive and candidate evidence set remains immutable and retained. There is no rollback-artifact deletion or pruning in Phase 1.

## Validation state

Slice 31 GitHub Actions run 286 on Python 3.12 completed:

- clean editable installation
- source and test compilation
- genesis CLI smoke test
- **126 protected tests passed in 8.88 seconds**

No Slice 31 production correction was required. Existing `BEGIN IMMEDIATE`, typed wake-busy translation, and connection isolation passed unchanged.

The workflow remains the public-repository standard `ubuntu-latest` runner with a ten-minute timeout and seven-day small pytest-log artifact. No paid runner or expanded artifact retention is enabled.

## Known incomplete Phase 1 work

Major incomplete areas include:

- complete explicit second-wake rejection while a prior checkpoint is pending
- broader protected-authority tests

Do not weaken existing tests to make these easier.

## Exact next task: Slice 32

The next bounded subject is evaluation 31: an explicit second wake must not advance while the prior committed lifecycle remains `checkpoint_pending`.

Before implementation:

1. reconstruct current `main`, Issue #13, and open pull requests
2. enqueue two distinct ticks before the first wake
3. use an existing protected checkpoint-failure or deferred-stabilization path so the first action commits an exact pending boundary
4. capture both inbox rows, canonical events and state, SQLite sequences, registry, database bytes, and checkpoint artifacts
5. attempt a second normal wake and require typed rejection before the second tick is claimed or consumed
6. require exact pending-body and artifact equality after rejection
7. repair or stabilize the existing pending boundary through the current administrative path
8. prove the second tick then proceeds normally
9. add the protected scenario before changing production code
10. make a production correction only if the accepted pending-state boundary is violated
11. update the Slice 32 note, matrix, this handoff, `AGENTS.md`, and Issue #13
12. run GitHub Actions through a pull request

Do not add queued wakes, automatic checkpoint repair, hidden retries, reentrant wake support, schema changes, new crash hooks, caregiver integration, learning, memory, skills, or generic recovery machinery.

## Restart protocol

At the next session or clean reconstruction point:

1. read `AGENTS.md`
2. read `docs/AI_COLLABORATION_OPERATIONS.md`
3. read this handoff and normative documents in order
4. inspect current open issues and pull requests
5. verify PR #47 is merged on current `main`, or reconcile newer repository truth
6. begin only from the exact Slice 32 boundary above

At the end of substantial work, leave updated continuity documents, protected-test mapping, Issue status, CI results, exact unfinished work, and one precise next action. Apply calibrated rollover guidance instead of an automatic two-slice cutoff.

No critical decision may remain only in chat history.
