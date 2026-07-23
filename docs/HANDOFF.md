# SUDACHI Handoff

Updated: **2026-07-23**

This file is the operational restart point for current `main`, which contains Phase 1 Slices 1–30 and accepted ADR 0007. Read `AGENTS.md` first, then the normative contract and ADRs before changing implementation.

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

Primary implementation stream. Slices 1–30 are merged on `main`. The exact next implementation boundary is Slice 31 after a fresh repository and GitHub-state reconstruction.

### Issue #3 — prior work and provider review

Research stream. Preliminary evidence and provider-neutral strategy exist, but no strong novelty claim and no live caregiver selection are authorized.

## Implemented Phase 1 summary

### Slices 1–16 — canonical metabolism and bounded storage

- Python 3.12 package and CLI
- canonical SQLite schema and append-only events
- injected clocks and fail-fast wake ownership
- deterministic inbox claim and seed-garden observation
- stable genesis and lifecycle checkpoints
- canonical water, harvest, completion abstention, classified no-action, and resource-aware recovery
- savepoint action rollback and lifecycle deadline exhaustion
- maintenance threshold, inspection, and administrative clear
- bounded checkpoint retention, classified pruning failure, and pending registration repair
- deterministic non-canonical JSONL export

### Slices 17–23 — complete bounded rollback path

- retained-source validation and verified pre-rollback archive
- durable `rollback_started`
- exact source restoration and isolated new-lineage candidate transformation
- atomic active database replacement with immediate validation
- atomic `rollback_completed`, restored wakeability, and first new-lineage stable checkpoint
- one-completed-rollback admission guard under accepted ADR 0007
- complete immutable archive and candidate evidence retained without pruning

See the corresponding notes in `docs/phase1/` and accepted ADR 0007.

### Slices 24–26 — declared determinism

- decreasing wall time cannot reorder canonical events
- different declared seeds do not change fixed seed-garden behavior
- identical declared inputs produce exact canonical and artifact equivalence, including active SQLite bytes, checkpoint manifests, digests, and identifiers

See:

- `docs/phase1/SLICE24_BACKWARD_WALL_TIME_ORDERING.md`
- `docs/phase1/SLICE25_SEED_INDEPENDENCE.md`
- `docs/phase1/SLICE26_REPEATED_RUN_EQUIVALENCE.md`

### Slice 27 — protected cleanup grace

- normal organism work stops at the 2000 ms deadline before executor entry
- one explicit injected reading measures terminalization completion
- exactly 2250 ms is accepted
- 2250 ms plus one nanosecond raises and rolls back all uncommitted lifecycle state

See `docs/phase1/SLICE27_CLEANUP_GRACE_BOUNDARY.md`.

### Slice 28 — insertion-order-independent tie breaking

- physical rowid order `bed-b`, `bed-a`
- both plots executable water targets
- canonical observation and policy still choose lexicographically smallest `bed-a`
- exact transition, budgets, event order, checkpoint, final sleep, and later input acceptance

See `docs/phase1/SLICE28_INSERTION_ORDER_TIE_BREAKING.md`.

### Slice 29 — consumed-input replay protection

- duplicate enqueue after the original successful action consumes zero clock and returns the existing row
- active database bytes, canonical state, sequences, registry, and checkpoint artifacts remain exact
- no-input wake rolls back tentative history
- only a later distinct identifier produces the second action

See `docs/phase1/SLICE29_POST_ACTION_DUPLICATE_REPLAY.md`.

### Slice 30 — real process-crash rollback

- a spawned external test harness acquires `WakeTransaction`
- it claims the tick and creates representative uncommitted event, sequence, garden, inventory, environment, inbox, and organism changes
- it proves those changes inside its transaction and exits through `os._exit(73)` without commit or cleanup
- the parent reacquires `BEGIN IMMEDIATE`, proving write-lock release
- exact active SQLite bytes, canonical rows, inbox, events, sequences, registry, and checkpoint artifacts return to the pre-crash snapshot
- the original tick remains unclaimed and completes normally afterward
- no production crash hook or organism subprocess capability was added

See `docs/phase1/SLICE30_PROCESS_CRASH_ROLLBACK.md`.

## Accepted ADR 0007 retention boundary

Phase 1 permits at most one completed rollback per organism. The pre-rollback archive, source-restored candidate, lineage-transformed candidate, rollback events, and first post-rollback checkpoint remain immutable and retained. There is no rollback-artifact deletion or pruning in Phase 1.

## Validation state

Slice 30 test-first validation on Python 3.12:

- run 275: 124 existing tests passed; one new assertion failed because it overconstrained SQLite rollback-journal pathname deletion
- the contract-external pathname assertion was removed without production changes
- run 276: **125 protected tests passed in 6.38 seconds**
- clean editable installation passed
- source and test compilation passed
- genesis CLI smoke passed

No Slice 30 production correction was required. SQLite process-exit rollback and lock release passed unchanged.

The workflow remains the public-repository standard `ubuntu-latest` runner with a ten-minute timeout and seven-day small pytest-log artifact. No paid runner or expanded artifact retention is enabled.

## Known incomplete Phase 1 work

Major incomplete areas include:

- nested-wake and hidden-write-connection rejection
- explicit second-wake rejection while a prior checkpoint is pending
- broader protected-authority tests

Do not weaken existing tests to make these easier.

## Exact next task: Slice 31

The next bounded subject is evaluation 28: nested wakes and hidden write connections must be rejected without queued work or canonical mutation.

Before implementation:

1. reconstruct current `main`, Issue #13, and open pull requests
2. acquire one outer `WakeTransaction`
3. require nested `WakeTransaction.acquire(...)` for the same organism to fail with typed `WakeBusyError`
4. require a separate hidden write connection's `BEGIN IMMEDIATE` to fail while the outer wake owns the body
5. require zero organism clock reads and no queued request, event, inbox row, sequence, state, database-byte, or artifact change from either rejection
6. roll back and close the outer transaction
7. prove a normal wake then acquires ownership and processes the original tick
8. add protected tests before changing production code
9. make a production correction only if the existing locking boundary violates the contract
10. update the Slice 31 note, matrix, this handoff, `AGENTS.md`, and Issue #13
11. run GitHub Actions through a pull request

Do not add reentrant wake support, queued wakes, hidden connection pools, subprocess access, generic concurrency machinery, retries, schema changes, caregiver integration, learning, memory, skills, or generic recovery machinery.

## Restart protocol

At the next session or clean reconstruction point:

1. read `AGENTS.md`
2. read `docs/AI_COLLABORATION_OPERATIONS.md`
3. read this handoff and normative documents in order
4. inspect current open issues and pull requests
5. verify PR #46 is merged on current `main`, or reconcile newer repository truth
6. begin only from the exact Slice 31 boundary above

At the end of substantial work, leave updated continuity documents, protected-test mapping, Issue status, CI results, exact unfinished work, and one precise next action. Apply calibrated rollover guidance instead of an automatic two-slice cutoff.

No critical decision may remain only in chat history.
