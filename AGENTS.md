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

Do not evade product safeguards. State the concrete benign software context when sensitive vocabulary could be misread. Follow `docs/AI_COLLABORATION_OPERATIONS.md` for safety context, cost awareness, and conversation rollover.

Continue through multiple bounded slices only while repository, branch, pull-request, and CI state remain directly reconstructable. Phase 1 is now complete; do not create an automatic next slice merely to continue activity.

## Current work streams

### Issue #13 — Phase 1 implementation

Repository state containing this file includes Slices 1–35:

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
35. protected organism and administration provenance across canonical sources and public reports

All 41 fixed Contract v0.2 evaluations have complete protected coverage. PR #54 closes the final row with **142 protected tests** on its verified implementation head.

After PR #54 is merged, Issue #13 is complete. Do not reopen it to add Phase 2 features.

### Issue #3 — prior work and provider review

Research stream. Preliminary review is active, but no strong novelty claim and no live caregiver selection are authorized.

Do not connect a human or model caregiver automatically. Do not treat ChatGPT and an API as the same product. Provider permissions, retention, pricing, limits, and transformation classes must be reverified from current first-party sources before any live integration.

## Phase 1 invariants

Phase 1 is deterministic, local, network-free, organism-subprocess-free, caregiver-free, bounded, auditable, SQLite-canonical, checkpointed after every committed wake, and explicit about organism versus administrative authority.

The organism runtime must not:

- dual-write canonical SQLite and JSONL
- write authoritative mutable files outside SQLite
- consult a caregiver
- execute arbitrary generated code
- run continuously
- add unrestricted retries or backtracking
- weaken protected tests or budgets
- modify protected actions, evaluators, schema, contract, or environment
- claim administrative authority

Administration is distinct from organism autonomy. Canonical and report sources use protected `organism:` and `administration:` namespaces. Administrative operations and protected test harnesses retain narrow typed boundaries.

## Complete protected rollback path

Rollback archive preparation validates one retained source, snapshots the complete active future through SQLite Online Backup, and publishes immutable evidence without canonical mutation.

Rollback begin records durable intent. Candidate construction restores the selected checkpoint. Candidate transformation creates a distinct lineage and records `rollback_lineage_prepared`. Active replacement transfers authority atomically and remains blocked. Completion records `rollback_completed`, restores wakeability, and preserves the abandoned future.

ADR 0007 permits at most one completed rollback per organism and retains the complete archive and candidate evidence set without pruning.

## Fixed-evaluation closures in Slices 24–35

- Slice 24: backward wall time cannot reorder canonical events.
- Slice 25: different declared seeds do not change fixed behavior.
- Slice 26: identical declared inputs produce exact canonical and artifact equivalence.
- Slice 27: cleanup grace permits terminalization only and rejects overrun atomically.
- Slice 28: lexicographic selection ignores physical row insertion order.
- Slice 29: consumed input replay cannot create duplicate action.
- Slice 30: a real process exit rolls back uncommitted wake state.
- Slice 31: nested wakes and hidden writers fail fast.
- Slice 32: pending checkpoint state blocks later wakes until repair.
- Slice 33: registered actions have no external workspace or effect route.
- Slice 34: action SQL authority is restricted to exact declared garden transitions.
- Slice 35: organism and administration are distinguishable in canonical records and public reports.

Read the corresponding durable notes in `docs/phase1/` for exact boundaries and CI evidence.

## Exact restart point — Phase 2 decision gate

There is no authorized Slice 36.

After reconstructing current `main`, Issue #13, and open pull requests:

1. verify PR #54 is merged and Issue #13 is closed
2. verify all 41 matrix rows and the complete Phase 1 regression suite
3. read Issue #3 and current research documents
4. decide through an explicit reviewed issue or ADR whether Phase 2 caregiver-neutral consultation plumbing should begin
5. define source-neutral request/response schemas, consultation budgets, provenance, evaluation separation, and adoption boundaries before code
6. preserve the Phase 1 zero-caregiver path and its full regression suite

Do not begin live human or model caregiving, API integration, learning, memory, skills, self-modification, or a generic agent framework without that reviewed scope decision.

## End-of-work protocol

Before ending substantial work:

- update `docs/HANDOFF.md` with the true state and one exact next gate
- update protected-test mapping and durable notes
- update relevant Issue and PR status
- report tests, CI, failures, and skipped checks honestly
- ensure no critical decision exists only in chat or model memory
- preserve the repository language policy

Repository prose, code, issues, ADRs, and tests are written in English. The intentional Japanese lines in `README.md` remain the only standing exception.
