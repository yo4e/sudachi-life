# AGENTS.md

This file is the continuity contract for AI collaborators working on SUDACHI.

## Cold-start rule

Assume you remember nothing about SUDACHI.

Do not rely on conversation memory, prior model context, an issue title, or one code fragment. Reconstruct the project from repository state before proposing or changing anything.

## Before doing any work

Read these files in order:

1. `README.md`
2. `docs/CHATGPT_PROJECT_HANDOFF.md`
3. `docs/ORIGIN.md`
4. `docs/MINIMAL_ORGANISM_CONTRACT.md`
5. accepted files in `docs/decisions/`, in numeric order
6. `docs/ARCHITECTURE.md`
7. `docs/ROADMAP.md`
8. `docs/IMPLEMENTATION_DISCIPLINE.md`
9. `docs/PHASE1_TEST_MATRIX.md`
10. implemented notes in `docs/phase1/`, in slice order
11. `docs/RESEARCH_QUESTIONS.md`
12. `docs/PARENT_MODEL_PROVIDER_REVIEW.md`
13. preliminary notes in `docs/research/`
14. `docs/HANDOFF.md`
15. current open GitHub issues and pull requests

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
2. accepted ADRs 0001–0006
3. protected tests and `docs/PHASE1_TEST_MATRIX.md`
4. explicit current repository decisions

Do not hide a new architecture inside implementation code. If implementation reveals a contradiction, stop and resolve the contract or ADR through review before proceeding.

## Current work streams

### Issue #13 — Phase 1 implementation

Primary implementation stream. Repository state containing this file includes Slices 1–20:

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

GitHub Actions for the PR #34 implementation head passed clean install, compileall, genesis CLI smoke, and **96 protected tests**.

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

## Established non-canonical and rollback boundaries

### JSONL export

JSONL export is explicit administration, read-only with respect to SQLite, derived from one caller-declared registered stable checkpoint boundary, ordered by canonical `event_sequence`, published atomically, disposable, and non-canonical.

There is no JSONL import, lifecycle dual-write, organism-controlled export, or export-triggered canonical event.

### Pre-rollback archive

Rollback archive preparation acquires fail-fast ownership, validates one retained source, snapshots the complete active future through SQLite Online Backup, publishes immutable `rollback-archives/pre-rb-.../`, and rolls back its ownership transaction without changing canonical state.

The archive is not a stable checkpoint and does not participate in ordinary checkpoint retention.

### Durable rollback intent

Rollback begin revalidates the archive and active body, changes status to `rollback_in_progress`, appends exactly one next-sequence `rollback_started` event in the same transaction, and blocks normal wakes before clock use or input claim.

SQLite backup artifacts are not assumed to have the same raw file bytes as their source. Equality is established through validated artifact digests plus exact canonical SQLite schema, row, and sequence-state comparison.

### Source-restored candidate

Restore-candidate construction exposes `build_restore_candidate(...)` and `sudachi rollback build-candidate`, revalidates the blocked intent and immutable source, restores the selected checkpoint through SQLite Online Backup, validates exact source equality, and publishes deterministic `restore-candidates/rc-.../` only after validation and atomic rename.

The candidate is non-canonical and remains `source_restored_untransformed`. It is never used by normal organism runtime.

### Lineage-transformed candidate

Candidate transformation:

- exposes `transform_restore_candidate(...)` and `sudachi rollback transform-candidate`
- requires an explicit bounded administrative reason
- acquires fail-fast ownership of the blocked active database before mutable reads
- revalidates the intent, abandoned-future archive, selected checkpoint, and exact source-restored candidate
- derives the new generation as `abandoned_active_generation + 1`
- copies the immutable source candidate through SQLite Online Backup into a temporary working database
- changes only the working candidate through one bounded administrative transaction
- clears source pending fields, restores the selected registry row, and keeps status `rollback_in_progress`
- preserves all source history and appends one exact candidate-local `rollback_lineage_prepared` event in the new lineage
- validates declared schema, table, organism, event, registry, and `sqlite_sequence` differences
- publishes deterministic `restore-candidates/rtc-.../` only after complete validation and atomic rename
- changes no active row and never edits the checkpoint, archive, or source candidate

The transformed candidate is non-canonical and remains `lineage_transformed_replacement_ready`. It is not wakeable and has not replaced the active database.

## Exact restart point: Slice 21

After reconciling current `main`, Issue #13, and open pull requests, implement only protected active-database replacement with one verified lineage-transformed candidate and immediate post-replacement validation.

Required Slice 21 boundary:

1. create a new `agent/...` branch from current `main`
2. add an explicit offline administrative Python API and narrow CLI command accepting one published transformed-candidate identifier
3. acquire fail-fast ownership of the blocked active database before reading mutable rollback intent
4. require active status `rollback_in_progress`, no pending checkpoint, and the same current-lineage `rollback_started` event at the active tip
5. revalidate the archive, abandoned future, selected checkpoint, source-restored candidate, transformed-candidate manifest and database, new-lineage derivation, candidate-local restoration event, and replacement-ready state
6. reject missing, foreign, drifted, unsafe, ambiguous, busy, already replaced, or inconsistent input before crossing the replacement boundary
7. prove the verified pre-rollback archive still exactly preserves the active body before replacement except for the deliberate durable-intent transition already protected by Slices 18–20
8. close all validation handles before replacement and use only bounded same-filesystem atomic filesystem operations; do not copy a live active SQLite file naively
9. atomically replace `organism.sqlite3` with the verified transformed-candidate database while preserving the immutable candidate artifact
10. reopen the new active database immediately and validate integrity, foreign keys, protected versions, organism identity, new lineage, source lifecycle, selected stable boundary, candidate-local restoration history, and status `rollback_in_progress`
11. define and protect explicit recovery behavior for injected failure immediately before replacement and after replacement but before post-replacement validation completes; never claim rollback completion on these paths
12. leave the successfully replaced active body non-wakeable in `rollback_in_progress`
13. preserve archive, selected checkpoint, source candidate, transformed candidate, inbox restored at the selected boundary, registry, environment, and history exactly as represented by the validated transformed body
14. update `docs/phase1/`, `docs/PHASE1_TEST_MATRIX.md`, `docs/HANDOFF.md`, and Issue #13
15. run GitHub Actions through a pull request

Slice 21 must stop before:

- appending active-path `rollback_completed`
- clearing the restored active body's `rollback_in_progress`
- enabling normal wakes
- deleting or pruning checkpoints, archives, or candidates
- JSONL import
- caregiver consultation
- learning, memory, skills, or generic recovery machinery

Do not privately decide rollback-completion, maintenance-clear, post-rollback checkpoint, or artifact-retention protocol while implementing the destructive replacement boundary.

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

Repository prose, code, issues, ADRs, and tests are written in English. The intentional Japanese lines in `README.md` remain the only standing exception.
