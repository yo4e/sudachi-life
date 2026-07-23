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

SUDACHI's organism, metabolism, body, lineage, growth, and caregiver vocabulary describes deterministic local software. Phase 1 uses Python, SQLite, immutable artifacts, and a synthetic garden only. It has no wet-lab biology, pathogens, genetic engineering, medical intervention, weapons work, offensive cybersecurity, third-party system access, network activity, or organism subprocess execution.

Do not evade product safeguards. State the concrete benign software context when sensitive vocabulary could be misread. Accept delayed, blocked, or refused requests. Follow `docs/AI_COLLABORATION_OPERATIONS.md` for safety context, cost awareness, and conversation rollover.

Two merged slices are not an automatic rollover trigger. Continue through multiple bounded slices while repository and CI state remain directly reconstructable. Reassess after several substantial slices, normally around eight to twelve, or earlier when a long debugging trail, repeated CI repair, stale context, or branch-state confusion creates a material reliability risk. Do not deliberately approach a roughly twenty-slice conversation limit.

## Current work streams

### Issue #13 — Phase 1 implementation

Repository state containing this file includes Slices 1–34:

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
30. real process-exit rollback of an uncommitted wake with released write ownership
31. nested wake and hidden writer fail-fast rejection with restored normal wakeability
32. explicit second-wake rejection behind a committed pending checkpoint and resumed progress after repair
33. guarded proof that registered organism actions have no external workspace or effect route
34. action-scoped SQLite authority restricted to exact registered garden transition columns

ADR 0007 is accepted: Phase 1 permits at most one completed rollback per organism and retains the complete archive and candidate evidence set without pruning.

PR #53 closes Contract evaluation 39. GitHub Actions run 307 passes clean installation, compileall, genesis CLI smoke, and **139 protected tests in 7.69 seconds** on Python 3.12.

Phase 1 remains incomplete.

### Issue #3 — prior work and provider review

Research stream. Preliminary review is active, but no strong novelty claim and no live caregiver selection are authorized.

Do not connect a human or model caregiver to Phase 1. Do not treat ChatGPT and an API as the same product. Provider permissions, retention, pricing, limits, and transformation classes must be re-verified from current first-party sources before any live integration.

## Phase 1 invariants

Phase 1 remains deterministic, local, network-free, organism-subprocess-free, caregiver-free, bounded, auditable, SQLite-canonical, and checkpointed after every committed wake.

The organism runtime must not:

- dual-write canonical SQLite and JSONL
- write authoritative mutable files outside SQLite
- consult a caregiver
- execute arbitrary generated code
- run continuously
- add unrestricted retries or backtracking
- weaken protected tests or budgets
- modify protected actions, evaluators, schema, contract, or environment

Administration is distinct from organism autonomy. Administrative operations and protected test harnesses have narrow typed boundaries and preserve authority separation.

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

## Fixed-evaluation closures in Slices 24–34

- Slice 24: backward wall time cannot reorder canonical events.
- Slice 25: different declared seeds do not change fixed seed-garden behavior.
- Slice 26: identical declared inputs produce exact canonical and artifact equivalence.
- Slice 27: cleanup grace permits terminalization only and rejects overrun atomically.
- Slice 28: lexicographic action tie breaking ignores physical row insertion order.
- Slice 29: replay of a consumed external identifier cannot create a duplicate action.
- Slice 30: a real child-process exit rolls back an uncommitted wake and releases ownership.
- Slice 31: nested wakes and hidden write connections fail fast without queueing or mutation.
- Slice 32: a second wake cannot advance behind a pending boundary; existing repair restores progress.
- Slice 33: registered actions receive no workspace handle, invoke no guarded filesystem/network/subprocess interface, and treat a path-like target only as a nonexistent SQLite identifier.
- Slice 34: registered actions execute under an action-scoped SQLite authorizer; valid actions change only their exact declared columns, while identity, budgets, registry, inbox, history, schema, triggers, source, contract, ADRs, and administrative artifacts remain protected.

Read the corresponding durable notes in `docs/phase1/` for exact boundaries and CI evidence.

## Exact restart point: Slice 35

After reconstructing current `main`, Issue #13, and open pull requests, implement only the next incomplete fixed Phase 1 evaluation as a separate Slice 35 branch.

The next bounded subject is Contract evaluation 41: administrative actions are distinguishable from organism actions in records and reports.

Required selection discipline:

1. confirm no newer repository decision or open pull request changes the ordering
2. inventory every canonical event-creation boundary and every explicit administrative API or CLI operation
3. inventory operations that intentionally create no canonical event and the external typed result or artifact that identifies them as administration
4. define and protect the Phase 1 source namespaces, at minimum `organism:` and `administration:`
5. add protected tests before changing production code
6. run representative organism lifecycle, input, checkpoint, maintenance, export, and rollback paths and require their records, results, manifests, and reports to preserve the correct authority category
7. require organism action and lifecycle records never to claim an administrative source
8. require administrative records never to claim an organism source
9. require unknown, empty, or cross-category source values to fail before canonical append or report publication
10. preserve operations that intentionally have no canonical event without inventing false history; prove their typed result or immutable artifact still identifies administrative provenance
11. make a production correction only where source/category validation is incomplete
12. do not redesign the event schema, add a generic identity framework, or force every read-only or pre-authority rejection into canonical history
13. update the Slice 35 note, matrix, this handoff, `AGENTS.md`, and Issue #13
14. run GitHub Actions through a pull request

Evaluation 41 concerns authority provenance, not merely string prefixes. Existing source fields are substantial partial coverage; Slice 35 must make the distinction complete across canonical records and non-event administrative reports without fabricating events for operations that had no write authority.

Do not add caregiver integration, learning, memory, skills, self-modification, generic recovery machinery, or a generic autonomous-agent framework.

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
