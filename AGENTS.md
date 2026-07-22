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

Primary implementation stream. Repository state containing this file includes Slices 1–22:

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

GitHub Actions for the PR #36 implementation head passed clean install, compileall, genesis CLI smoke, and **115 protected tests** after one completion exception-classification correction.

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

## Exact restart point: rollback-artifact retention decision

The complete rollback path now preserves all artifacts. Do not implement deletion or pruning until an accepted decision record defines a bounded retention policy.

Required next work:

1. reconcile current `main`, Issue #13, and open pull requests
2. review Contract v0.2 rollback retention requirements, ADR 0004, runtime working-set limits, and Slices 17–22
3. author a proposed decision record before implementation
4. define which pre-rollback archives, source candidates, and transformed candidates remain protected after a first post-rollback stable checkpoint
5. define whether candidates are reconstructible or independently audit-critical
6. define how multiple completed rollbacks remain bounded
7. define what evidence permits abandoned-future archive removal
8. define atomic pruning and recoverable failure behavior
9. decide whether Phase 1 permits pruning at all or instead imposes a bounded completed-rollback count
10. update roadmap, handoff, and Issue #13 after review

No rollback artifact deletion, remote backup assumption, or generic cleanup machinery may precede that accepted decision.

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
