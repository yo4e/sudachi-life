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

Primary implementation stream. Repository state containing this file includes Slices 1–19:

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

GitHub Actions for the final PR #33 head passed clean install, compileall, genesis CLI smoke, and **81 protected tests**.

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

Restore-candidate construction:

- exposes `build_restore_candidate(...)` and `sudachi rollback build-candidate`
- acquires fail-fast active ownership before mutable reads
- requires `rollback_in_progress`, no pending checkpoint, and `rollback_started` at the active tip
- revalidates the intent, abandoned-future archive, exact blocked active state, selected registry row, and immutable checkpoint
- restores the selected checkpoint through SQLite Online Backup into a bounded temporary candidate
- validates integrity, foreign keys, protected versions, identity, source lineage, lifecycle, pending boundary, and exact source-checkpoint equality
- publishes deterministic `restore-candidates/rc-.../` only after validation and atomic rename
- changes no canonical active row and creates no canonical event
- leaves no candidate on injected construction or publication failure

The candidate is non-canonical and remains `source_restored_untransformed`. It is not yet a new lineage and is never used by normal organism runtime.

## Exact restart point: Slice 20

After reconciling current `main`, Issue #13, and open pull requests, implement only administrative lineage transformation of one verified source-restored candidate.

Required Slice 20 boundary:

1. create a new `agent/...` branch from current `main`
2. add an explicit offline administrative Python API and narrow CLI command accepting one published candidate identifier
3. acquire fail-fast ownership of the blocked active database before reading mutable rollback intent
4. require active status `rollback_in_progress`, no pending checkpoint, and the same current-lineage `rollback_started` event at the active tip
5. revalidate the rollback archive, abandoned future, selected immutable checkpoint, source-restored candidate manifest and database, and exact source-checkpoint equality
6. reject missing, foreign, drifted, unsafe, ambiguous, busy, already transformed, or inconsistent input before candidate mutation or publication
7. perform transformation through a bounded same-filesystem temporary working candidate; do not mutate the selected checkpoint, archive, or published source-restored candidate
8. derive the new lineage generation exactly from the abandoned active generation according to ADR 0004
9. update only the isolated working candidate through one bounded administrative transaction, preserving organism identity and protected contract, schema, environment, and budget configuration
10. clear the source checkpoint-pending fields in the transformed candidate, keep it non-wakeable for the later replacement boundary, and append one typed candidate-local administrative restoration fact containing target and abandoned boundaries; do not record `rollback_completed`
11. validate transformed-candidate integrity, foreign keys, new lineage, lifecycle, event order, source history, target boundary, abandoned-future references, protected configuration, and deterministic manifest
12. publish the transformed candidate atomically only after complete validation
13. prove transformation or publication failure leaves active `rollback_in_progress`, `rollback_started`, archive, source checkpoint, source-restored candidate, inbox, registry, environment, and all history unchanged
14. update `docs/phase1/`, `docs/PHASE1_TEST_MATRIX.md`, `docs/HANDOFF.md`, and Issue #13
15. run GitHub Actions through a pull request

Slice 20 must stop before:

- replacing the active database
- clearing the active body's `rollback_in_progress`
- recording rollback completion in the active path
- deleting or pruning checkpoints, archives, or candidates
- JSONL import
- caregiver consultation
- learning, memory, skills, or generic recovery machinery

Do not privately decide the active-replacement, post-replacement validation, or rollback-completion protocol while implementing isolated candidate transformation.

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
