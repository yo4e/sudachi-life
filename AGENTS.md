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

Primary implementation stream. Repository state containing this file includes Slices 1–21:

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

GitHub Actions for the PR #35 implementation head passed clean install, compileall, genesis CLI smoke, and **107 protected tests** after one collection-time module-name correction.

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

## Established rollback boundaries

### Pre-rollback archive and durable intent

Rollback archive preparation validates one retained source, snapshots the complete active future through SQLite Online Backup, and publishes immutable `rollback-archives/pre-rb-.../` without canonical mutation.

Rollback begin revalidates the archive and active body, atomically changes status to `rollback_in_progress`, appends exactly one `rollback_started`, and blocks normal wakes.

### Source-restored and lineage-transformed candidates

Source-candidate construction restores the selected checkpoint through SQLite Online Backup and publishes an exact `source_restored_untransformed` candidate.

Candidate transformation derives `abandoned_active_generation + 1`, mutates only an isolated working candidate, clears source pending fields, reconstructs the selected registry row, preserves all source history, appends one candidate-local `rollback_lineage_prepared`, and publishes a `lineage_transformed_replacement_ready` candidate.

Both candidate forms are non-canonical and immutable after publication.

### Active authority transfer

Active replacement:

- exposes `replace_active_with_candidate(...)` and `sudachi rollback replace-active`
- acquires fail-fast ownership of the old blocked active body
- revalidates the complete intent, archive, checkpoint, source-candidate, and transformed-candidate chain
- stages an exact transformed-candidate copy through SQLite Online Backup in the organism directory
- validates staging before authority transfer
- closes old SQLite handles and rechecks old active and candidate digests
- atomically replaces canonical `organism.sqlite3` through same-filesystem `os.replace()`
- preserves the archive and both candidate artifacts
- immediately reopens and validates exact active-versus-candidate logical equality
- leaves the new active body in `rollback_in_progress` with `rollback_lineage_prepared` at the tip
- distinguishes pre-transfer failure from post-transfer incomplete validation
- recognizes and revalidates an exact already-replaced body without rewriting it

The pre-rollback archive remains the authoritative abandoned future. Active replacement creates no event and does not complete rollback.

## Exact restart point: Slice 22

After reconciling current `main`, Issue #13, and open pull requests, implement only rollback completion on the already replaced and fully validated active body.

Required Slice 22 boundary:

1. create a new `agent/...` branch from current `main`
2. add an explicit offline administrative Python API and narrow CLI command accepting one transformed-candidate identifier
3. acquire fail-fast ownership of the replaced active database before mutable reads
4. require canonical status `rollback_in_progress`, no pending checkpoint, the new lineage generation, and exact `rollback_lineage_prepared` at the active tip
5. revalidate the complete checkpoint, archive, source-candidate, transformed-candidate, and active-replacement provenance chain, including exact active-versus-candidate logical equality
6. reject missing, foreign, drifted, unsafe, ambiguous, busy, incomplete, already-completed-with-different-input, or inconsistent state before clock use or mutation
7. read exactly one injected administrative clock only after complete validation
8. in one bounded SQLite transaction, change the restored body from `rollback_in_progress` to the correct stable wakeable status and append exactly one next-sequence `rollback_completed` event
9. bind the administrative reason, selected target, abandoned archive and boundary, old and new lineage generations, source and transformed candidate identifiers and digests, replacement validation, implementation version, and final status in the completion payload
10. preserve organism identity, new lineage, source lifecycle, environment, inbox restored at the selected boundary, selected registry row, protected versions, and all prior history
11. validate canonical state and exact event order before commit
12. prove injected failure after status update and completion-event insertion rolls back both together and leaves normal wakes blocked
13. make an exact repeated completion request detectable and idempotent without a second clock read; reject incompatible repeated input
14. prove normal wake rejection before completion and normal wakeability only after completion
15. preserve every checkpoint, archive, source candidate, and transformed candidate; do not delete or prune artifacts
16. update `docs/phase1/`, `docs/PHASE1_TEST_MATRIX.md`, `docs/HANDOFF.md`, and Issue #13
17. run GitHub Actions through a pull request

Slice 22 must stop before:

- deleting or pruning rollback archives or candidates
- introducing a new rollback-artifact retention policy
- JSONL import
- caregiver consultation
- learning, memory, skills, or generic recovery machinery

Do not privately decide long-term rollback-artifact retention or broader Phase 1 evaluation closure while implementing completion and wakeability.

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
