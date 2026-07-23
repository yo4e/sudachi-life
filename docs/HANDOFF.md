# SUDACHI Handoff

Updated: **2026-07-23**

This file is the operational restart point for repository state containing Phase 1 Slices 1–34 and accepted ADR 0007. Read `AGENTS.md` first, then the normative contract and ADRs before changing implementation.

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

Phase 1 has one canonical SQLite body, append-only sequence-ordered events, injected clocks, fail-fast write ownership, deterministic `seed-garden-v1`, concrete budgets, protected evaluation, exact checkpoint boundaries, immutable checkpoints, bounded retention, rollback lineage rules, explicit administrative boundaries, no organism-writable external workspace, and action-scoped SQL authority.

Phase 1 has no caregiver, model adapter, chat interface, network access, organism subprocess access, arbitrary generated code, learning, memory, skills, continuous execution, or generic autonomous loop.

## AI collaboration operations

Read `docs/AI_COLLABORATION_OPERATIONS.md`.

Conversation rollover is based on reliability signals, not an automatic count of two merged slices. Continue through multiple bounded slices while repository, branch, pull-request, and CI state remain directly reconstructable. Reassess normally around eight to twelve substantial slices, or earlier after a long debugging trail, repeated CI repair, stale context, or state confusion. Do not deliberately approach a roughly twenty-slice conversation likely to hit the platform limit.

Do not introduce a paid runner, larger or GPU runner, private-repository Actions usage, paid external service, or model/API call without explicit owner approval.

## Current work streams

### Issue #13 — Phase 1 SUDACHI-0 metabolism

Primary implementation stream. Slices 1–34 are implemented. The exact next implementation boundary is Slice 35 after a fresh repository and GitHub-state reconstruction.

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

### Slice 33 — no organism-writable external workspace

- `execute_garden_action(...)` receives no path or workspace handle
- filesystem mutation, temporary-file, network, subprocess, and process-launch APIs are fail-closed during the action-only probe
- valid `water_plot(bed-a)` succeeds without invoking a guarded interface
- an absolute path-like target is rejected as a nonexistent SQLite plot without touching the path
- organism directory and administrative workspace entries remain exact
- the probe rolls back and the same tick later completes normally with hard-zero external budgets
- no production correction or generic sandbox framework was required

See `docs/phase1/SLICE33_NO_EXTERNAL_WORKSPACE.md`.

### Slice 34 — protected organism action authority

- `execute_garden_action(...)` installs a SQLite authorizer only during one registered action dispatch
- action reads are limited to registered action metadata and garden state
- `water_plot` may update only moisture, water units, and environment step
- `harvest_plot` may update only fruit, harvested fruit, and environment step
- the existing `garden_action` savepoint remains allowed
- all other SQL authorization requests fail closed with typed `ProtectedAuthorityViolationError`
- valid water execution changes exactly the three declared mutable values
- organism identity and versions, budget configuration, action definitions, inbox, events, checkpoint registry, SQLite sequences, `user_version`, schema objects, append-only triggers, protected source/evaluator/tests/contract/ADRs, and administrative artifacts remain exact
- ten representative protected mutations are denied before effect
- the probe rolls back and the same tick completes normally

See `docs/phase1/SLICE34_PROTECTED_AUTHORITY.md`.

## Accepted ADR 0007 retention boundary

Phase 1 permits at most one completed rollback per organism. The complete pre-rollback archive and candidate evidence set remains immutable and retained. There is no rollback-artifact deletion or pruning in Phase 1.

## Validation state

PR #53 closes Contract evaluation 39 with a narrow production correction. GitHub Actions run 307 on Python 3.12 passed:

- clean editable installation
- source and test compilation
- genesis CLI smoke
- **139 protected tests in 7.69 seconds**

No prior protected test, action signature, schema, evaluator, lifecycle boundary, checkpoint mechanism, rollback path, or external capability boundary was weakened.

The workflow remains the public-repository standard `ubuntu-latest` runner with a ten-minute timeout and seven-day small pytest-log artifact. No paid runner or expanded artifact retention is enabled.

## Known incomplete Phase 1 work

The remaining fixed evaluation is:

- complete proof that administrative effects are distinguishable from organism effects in records and reports

Do not weaken existing tests to make it easier.

## Exact next task: Slice 35

The next bounded subject is evaluation 41: administrative actions are distinguishable from organism actions in records and reports.

Before implementation:

1. reconstruct current `main`, Issue #13, and open pull requests
2. inventory every canonical event-creation boundary and explicit administrative API or CLI operation
3. inventory operations that intentionally create no canonical event and the typed result or immutable artifact that identifies them as administration
4. define and protect the Phase 1 source namespaces, at minimum `organism:` and `administration:`
5. add protected tests before changing production code
6. run representative organism lifecycle, input, checkpoint, maintenance, export, and rollback paths and require records, results, manifests, and reports to preserve the correct authority category
7. require organism action and lifecycle records never to claim an administrative source
8. require administrative records never to claim an organism source
9. require empty, unknown, or cross-category source values to fail before canonical append or report publication
10. preserve operations that intentionally have no canonical event without inventing false history; prove their typed result or immutable artifact still identifies administrative provenance
11. make a production correction only where source/category validation is incomplete
12. do not redesign the event schema, add a generic identity framework, or force read-only/pre-authority rejection into canonical history
13. update the Slice 35 note, matrix, this handoff, `AGENTS.md`, and Issue #13
14. run GitHub Actions through a pull request

Evaluation 41 concerns authority provenance, not merely string prefixes. Existing source fields provide substantial partial coverage; Slice 35 must make the distinction complete across canonical records and non-event administrative reports without fabricating events for operations that had no write authority.

Do not add caregiver integration, learning, memory, skills, self-modification, generic recovery machinery, or a generic autonomous-agent framework.

## Restart protocol

At the next session or clean reconstruction point:

1. read `AGENTS.md`
2. read `docs/AI_COLLABORATION_OPERATIONS.md`
3. read this handoff and normative documents in order
4. inspect current open issues and pull requests
5. verify PR #53 is merged on current `main`, or reconcile newer repository truth
6. begin only from the exact Slice 35 boundary above

At the end of substantial work, leave updated continuity documents, protected-test mapping, Issue status, CI results, exact unfinished work, and one precise next action. Apply calibrated rollover guidance instead of an automatic two-slice cutoff.

No critical decision may remain only in chat history.
