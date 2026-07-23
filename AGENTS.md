# AGENTS.md

This file is the continuity contract for AI collaborators working on SUDACHI.

## Cold-start rule

Assume you remember nothing about SUDACHI.

Do not rely on conversation memory, prior model context, an issue title, or one code fragment. Reconstruct the project from repository state before proposing or changing anything.

## Before doing any work

Read these files in order:

1. `README.md`
2. `docs/CHATGPT_PROJECT_HANDOFF.md`
3. `docs/AI_COLLABORATION_OPERATIONS.md`
4. `docs/ORIGIN.md`
5. `docs/MINIMAL_ORGANISM_CONTRACT.md`
6. accepted files in `docs/decisions/`, in numeric order
7. `docs/ARCHITECTURE.md`
8. `docs/ROADMAP.md`
9. `docs/IMPLEMENTATION_DISCIPLINE.md`
10. `docs/PHASE1_TEST_MATRIX.md`
11. implemented notes in `docs/phase1/`, in slice order
12. `docs/RESEARCH_QUESTIONS.md`
13. `docs/PARENT_MODEL_PROVIDER_REVIEW.md`
14. preliminary notes in `docs/research/`
15. `docs/HANDOFF.md`
16. current open GitHub issues and pull requests

Repository state and current GitHub state outrank conversation history.

## Core project question

SUDACHI asks whether a bounded artificial organism can convert finite external cognitive scaffolding into verified local competence and retain capability while requiring less justified caregiver assistance.

```text
parent reasoning -> verified experience -> reusable skill -> cheap local behavior
```

The repository is the organism's auditable body, developmental history, skill base, and lineage record. A model may later be a caregiver or organ; it is not the whole organism.

> As it becomes smarter, it should become smaller and quieter.

Do not flatten SUDACHI into a generic autonomous agent, chatbot, virtual pet, or self-modifying loop.

## Normative authority

For Phase 1, use this precedence:

1. Minimal Organism Contract v0.2
2. accepted ADRs 0001–0007
3. protected tests and `docs/PHASE1_TEST_MATRIX.md`
4. explicit current repository decisions

Do not hide a new architecture inside implementation code. If implementation reveals a contradiction, stop and resolve the contract or ADR through review before proceeding.

## AI collaboration safety and continuity

SUDACHI's organism, metabolism, body, lineage, growth, and caregiver vocabulary describes deterministic local software. Phase 1 uses Python, SQLite, immutable artifacts, and a synthetic garden only. It has no wet-lab biology, pathogens, genetic engineering, medical intervention, weapons work, offensive cybersecurity, third-party system access, network activity, or subprocess execution.

Do not evade product safeguards. State the concrete benign software context when sensitive vocabulary could be misread. Accept delayed, blocked, or refused requests. Follow `docs/AI_COLLABORATION_OPERATIONS.md` for safety context, cost awareness, and conversation rollover.

Two merged slices are not an automatic rollover trigger. Continue through multiple bounded slices while repository and CI state remain directly reconstructable. Reassess after several substantial slices, normally around eight to twelve, or earlier when a long debugging trail, repeated CI repair, stale context, or branch-state confusion creates a material reliability risk. Do not deliberately approach a roughly twenty-slice conversation limit.

## Current work streams

### Issue #13 — Phase 1 implementation

Primary implementation stream. Current `main` includes Slices 1–29:

1. package, schema, initialization, status, genesis checkpoint
2. inbox, fail-fast wake acquisition, deterministic observation
3. first canonical water wake
4. canonical harvest wake
5. objective-complete abstention
6. classified no-applicable-action abstention
7. resource-aware harvest recovery
8. classified action failure with savepoint rollback
9. classified lifecycle budget exhaustion
10. maintenance-threshold entry
11. read-only maintenance inspection
12. explicit administrative maintenance clear
13. successful bounded checkpoint retention
14. classified checkpoint-retention failure
15. pending checkpoint registration repair
16. deterministic non-canonical JSONL event export
17. retained rollback-source validation and verified pre-rollback archive
18. durable rollback intent with atomic `rollback_started`
19. verified source-restored candidate construction
20. isolated candidate lineage transformation with `rollback_lineage_prepared`
21. atomic active-database replacement with immediate validation and recoverable interruption
22. atomic `rollback_completed`, restored wakeability, and first new-lineage stable checkpoint
23. single-completed-rollback admission enforcement at preparation
24. complete first-wake event ordering under backward wall time
25. complete first-wake behavior independence from different declared seeds
26. exact repeated-run canonical and artifact equivalence for identical declared inputs
27. protected cleanup-grace terminalization boundary and overrun rollback
28. complete lexicographic action tie breaking under reversed physical row insertion order
29. complete consumed-input replay rejection without duplicate action

ADR 0007 is accepted: Phase 1 permits at most one completed rollback per organism and retains the complete archive and candidate evidence set without pruning.

GitHub Actions run 269 for the Slice 29 test-first head passed clean install, compileall, genesis CLI smoke, and **124 protected tests in 10.15 seconds** on Python 3.12. No production correction was required.

Phase 1 remains incomplete.

### Issue #3 — prior work and provider review

Research stream. Preliminary review is active, but no strong novelty claim and no live caregiver selection are authorized.

Do not connect a human or model caregiver to Phase 1. Do not treat ChatGPT and an API as the same product. Provider permissions, retention, pricing, limits, and transformation classes must be re-verified from current first-party sources before any live integration.

## Phase 1 invariants

Phase 1 remains deterministic, local, network-free, subprocess-free, caregiver-free, bounded, auditable, SQLite-canonical, and checkpointed after every committed wake.

The organism runtime must not:

- dual-write canonical SQLite and JSONL
- write authoritative mutable files outside SQLite
- consult a caregiver
- execute arbitrary generated code
- run continuously
- add unrestricted retries or backtracking
- weaken protected tests or budgets
- modify protected actions, evaluators, schema, contract, or environment

Administration is distinct from organism autonomy. Administrative operations have narrow typed boundaries and preserve authority separation.

## Complete protected rollback path

### Archive and intent

Rollback archive preparation validates one retained source, snapshots the complete active future through SQLite Online Backup, and publishes immutable `rollback-archives/pre-rb-.../` without canonical mutation.

Rollback begin revalidates the archive and active body, atomically changes status to `rollback_in_progress`, appends exactly one `rollback_started`, and blocks normal wakes.

### Candidate construction and lineage transformation

Source-candidate construction restores the selected checkpoint through SQLite Online Backup and publishes an exact immutable `source_restored_untransformed` candidate.

Candidate transformation derives `abandoned_active_generation + 1`, changes only an isolated working candidate, clears source pending fields, reconstructs the selected registry row, preserves source history, appends one candidate-local `rollback_lineage_prepared`, and publishes an immutable `lineage_transformed_replacement_ready` candidate.

### Canonical authority transfer

Active replacement revalidates the complete provenance chain, stages an exact candidate copy through SQLite Online Backup, atomically replaces canonical `organism.sqlite3`, immediately validates the new active body, preserves every artifact, and leaves the new body blocked in `rollback_in_progress`.

A post-transfer interruption is detectable and exact repeated validation recovers without rewriting.

### Completion and wakeability

Rollback completion:

- exposes `complete_rollback(...)` and `sudachi rollback complete`
- acquires fail-fast ownership of the replaced body
- revalidates the checkpoint, archive, both candidates, and exact active-candidate equality
- reads one administrative clock only after validation
- atomically changes `rollback_in_progress` to `sleeping`
- clears restored failure and maintenance state
- appends exactly one next-sequence `rollback_completed`
- binds target, abandoned future, lineages, candidate identifiers and digests, replacement validation, and the original administrative reason
- rolls back status and event together on injected failure
- recognizes an exact completed state without another clock read or mutation
- restores normal wakeability only after commit

Protected tests prove the first post-rollback wake runs in the new lineage and creates a new stable lifecycle checkpoint while every rollback artifact remains unchanged.

### Accepted retention boundary and Slice 23 enforcement

ADR 0007 resolves rollback-artifact retention for Phase 1:

- one organism may contain at most one completed rollback
- the pre-rollback archive, source-restored candidate, and lineage-transformed candidate remain immutable and retained
- rollback artifacts are not pruned or deleted
- repeated rollback experiments use separate organism identities
- later phases require a new accepted decision before repeated rollback or artifact pruning

Slice 23 enforces that boundary at rollback preparation. After fail-fast ownership and canonical validation, preparation counts canonical `rollback_completed` events and requires zero before latest-source lookup, source selection, or archive-root creation. Rejection is typed, zero-clock, and non-mutating. A separately initialized organism remains eligible for its own first rollback.

## Canonical event ordering under backward wall time

Slice 24 closes Contract evaluation 3 without production changes. One protected complete first-water wake uses decreasing wall timestamps from genesis through enqueue, wake, lifecycle completion, and checkpoint stabilization while monotonic readings increase. The organism still waters `bed-a`, commits boundary 13, stabilizes event 14, and returns to sleep. Canonical event identity and order remain the exact database sequence 1–14; timestamps are metadata only.

## Declared seed independence

Slice 25 closes Contract evaluation 4 without production changes. Two independently initialized organisms receive identical external input and injected clock readings but declare seeds `1` and `2`. The seed remains visible in `WakeResult` and canonical `wake_accepted` history, so snapshot digests and digest-derived checkpoint identifiers differ. After normalizing only those declared and derived identity fields, the complete active bodies, pending checkpoint snapshots, policy choice, transition, evaluation, budgets, event history, boundary 13, stabilization event 14, and final sleeping wakeability are identical.

## Exact repeated-run equivalence

Slice 26 closes Contract evaluation 1 without production changes. Two independent runtime roots receive identical organism identity, versions, genesis time, external tick, seed, and fake-clock readings. Without normalizing any field, they produce identical `WakeResult`, status, schema, canonical rows, SQLite sequence state, active database SHA-256, checkpoint identifiers, manifests, checkpoint database digests, complete checkpoint-store file sets and digests, final sleeping state, and acceptance of the same next tick.

## Protected cleanup-grace boundary

Slice 27 closes Contract evaluation 7. Normal work detected at 2001 ms stops before executor entry with zero action, mutation, retry, caregiver, or external effects. One explicit injected reading measures terminalization completion. Exactly 2250 ms is accepted and recorded in the budget ledger; 2250 ms plus one nanosecond raises `BudgetExhaustedError`, performs no checkpoint work, and rolls back every uncommitted event, sequence, state, and inbox-claim change.

## Insertion-order-independent tie breaking

Slice 28 closes Contract evaluation 13 without production changes. A protected stable fixture physically stores `bed-b` before `bed-a` while both are executable water targets. Canonical observation sorts plots and applicable targets as `bed-a`, `bed-b`; the policy waters `bed-a`, commits exact lifecycle boundary 16, stabilizes event 17, preserves reversed physical row order, returns to sleep, and accepts a later distinct input.

## Consumed-input replay protection

Slice 29 closes Contract evaluation 16 without production changes. After the original identifier produces and stabilizes one water action, replay returns the original inbox row with zero clock reads and no canonical, database-byte, sequence, registry, or checkpoint-artifact change. A wake with no distinct input raises `NoInputEventError` after one declared start reading and rolls back all tentative history. Only a later distinct identifier produces the second harvest action.

## Exact restart point: Slice 30

After reconstructing current `main`, Issue #13, and open pull requests, implement only the next incomplete fixed Phase 1 evaluation as a separate Slice 30 branch.

The next bounded subject is the remaining execution proof for Contract evaluation 27: a real process exit while a wake transaction is uncommitted must restore the exact prior canonical state and release the SQLite write lock.

Required selection discipline:

1. confirm no newer repository decision or open pull request changes the ordering
2. use an external protected test harness process, not an organism subprocess capability
3. initialize and enqueue one normal tick, then capture exact stable canonical and artifact state
4. in the child process acquire `WakeTransaction`, claim the tick, create representative uncommitted wake/event/state changes, and exit without commit or connection cleanup
5. require the parent to observe the child exit within a strict timeout
6. require exact rollback of inbox claim, events, state, SQLite sequences, active database bytes, and checkpoint artifacts
7. require the parent to acquire the released lock and complete the original tick normally
8. add the narrow process-crash test before changing production code
9. make a production correction only if the existing SQLite/transaction boundary violates the accepted contract
10. update `docs/phase1/`, `docs/PHASE1_TEST_MATRIX.md`, `docs/HANDOFF.md`, and Issue #13
11. run GitHub Actions through a pull request

Do not add subprocess access to the organism, production crash hooks, generic fault injection, replay machinery, rollback artifact deletion, schema changes, caregiver integration, learning, memory, skills, or generic recovery machinery.

## End-of-work protocol

Before ending substantial work:

- update `docs/HANDOFF.md` with the true state and one exact next action
- update `docs/PHASE1_TEST_MATRIX.md`
- add or update a durable slice or decision note
- update the relevant Issue checklist or status
- report tests and CI honestly
- report failures, skipped checks, and incomplete work
- ensure no critical decision exists only in chat or model memory
- preserve the repository language policy
- apply the calibrated rollover guidance in `docs/AI_COLLABORATION_OPERATIONS.md`

Repository prose, code, issues, ADRs, and tests are written in English. The intentional Japanese lines in `README.md` remain the only standing exception.
