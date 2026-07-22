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

Primary implementation stream. Repository state containing this file includes Slices 1–18:

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

GitHub Actions for PR #32 passed clean install, compileall, genesis CLI smoke, and **72 protected tests** on the implementation head.

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

Rollback archive preparation:

- acquires fail-fast SQLite ownership
- requires stable active state with no pending checkpoint
- selects exactly one retained protected checkpoint
- validates identity, active lineage, versions, boundaries, digests, and integrity
- snapshots the complete current active SQLite body through the Online Backup API
- publishes immutable `rollback-archives/pre-rb-.../`
- rolls back its ownership transaction without changing canonical state

The archive is not a stable checkpoint and does not participate in ordinary checkpoint retention.

### Durable rollback intent

Rollback begin:

- accepts one published archive identifier
- acquires fail-fast ownership before mutable reads
- validates the archive database and manifest
- compares archived and active `user_version`, protected schema, every canonical row, and `sqlite_sequence`
- revalidates the latest stable checkpoint and immutable selected source
- rejects drift, foreign or unsafe content, busy or pending state, and repeated begin before mutation
- changes status to `rollback_in_progress`
- appends exactly one next-sequence `rollback_started` event in the same transaction
- blocks later normal wakes before clock use or input claim

SQLite backup artifacts are not assumed to have the same raw file bytes as their source. Exact active equality is established by a validated archive digest plus exact canonical SQLite schema, row, and sequence-state comparison.

There is no restore candidate, lineage mutation, active replacement, or rollback completion in Slice 18.

## Exact restart point: Slice 19

After reconciling current `main`, Issue #13, and open pull requests, implement only protected restore-candidate construction required by Contract v0.2 §11.6 and ADR 0004.

Required Slice 19 boundary:

1. create a new `agent/...` branch from current `main`
2. add an explicit offline administrative Python API and narrow CLI command for constructing one restore candidate from the active rollback intent
3. acquire fail-fast ownership before reading mutable active state
4. require canonical status `rollback_in_progress`, no pending checkpoint, and exactly one current-lineage `rollback_started` event at the active tip
5. validate the event payload, referenced archive, archived active future, selected checkpoint registry row, and immutable selected checkpoint artifact
6. reject missing, foreign, drifted, unsafe, ambiguous, busy, or inconsistent intent before candidate creation
7. restore the selected checkpoint database into a bounded same-filesystem temporary candidate through SQLite's Online Backup API; do not use naive live-file copy
8. validate candidate SQLite integrity, foreign keys, protected configuration, organism identity, source lineage, source lifecycle, exact source event boundary, and equality with the selected checkpoint
9. expose no candidate as valid until complete validation and atomic publication succeed
10. prove candidate creation or publication failure leaves the active `rollback_in_progress` body, `rollback_started` event, archive, selected checkpoint, inbox, registry, environment, and prior history unchanged
11. update `docs/phase1/`, `docs/PHASE1_TEST_MATRIX.md`, `docs/HANDOFF.md`, and Issue #13
12. run GitHub Actions through a pull request

Slice 19 must stop before:

- changing the candidate lineage generation
- appending restored-lineage or rollback-completed history
- replacing the active database
- clearing `rollback_in_progress`
- deleting or pruning checkpoints, archives, or candidates
- JSONL import
- caregiver consultation
- learning, memory, skills, or generic recovery machinery

Do not privately decide the later candidate-transformation or active-replacement protocol while implementing source restoration and validation.

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
