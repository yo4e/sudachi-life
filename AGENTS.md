# AGENTS.md

This file is the continuity contract for AI collaborators working on SUDACHI.

## Cold-start rule

Assume you remember nothing about SUDACHI. Reconstruct the project from repository and current GitHub state before proposing or changing anything.

Do not rely on conversation memory, prior model context, an Issue title, or one code fragment.

## Read order

1. `README.md`
2. `docs/CHATGPT_PROJECT_HANDOFF.md`
3. `docs/AI_COLLABORATION_OPERATIONS.md`
4. `docs/ORIGIN.md`
5. `docs/MINIMAL_ORGANISM_CONTRACT.md`
6. accepted `docs/decisions/` files in numeric order
7. `docs/ARCHITECTURE.md`
8. `docs/ROADMAP.md`
9. `docs/IMPLEMENTATION_DISCIPLINE.md`
10. `docs/PHASE1_TEST_MATRIX.md`
11. implemented `docs/phase1/` notes
12. `docs/RESEARCH_QUESTIONS.md`
13. `docs/PARENT_MODEL_PROVIDER_REVIEW.md`
14. preliminary `docs/research/` notes
15. `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`
16. `docs/HANDOFF.md`
17. current Issues and PRs
18. for Phase 2.0: proposed ADR 0008, `docs/phase2/CONSULTATION_PROTOCOL_V1.md`, and `docs/PHASE2_CONSULTATION_TEST_MATRIX.md`

Repository/GitHub state outrank conversation history.

## Core question

SUDACHI asks whether a bounded artificial organism can convert finite external cognitive scaffolding into verified local competence and retain capability while requiring less justified caregiver assistance.

```text
parent reasoning -> verified experience -> reusable skill -> cheap local behavior
```

The repository is the organism's auditable body, developmental history, skill base, and lineage record. A model may later be caregiver or organ; it is not the organism.

> As it becomes smarter, it should become smaller and quieter.

Do not flatten SUDACHI into a generic agent, chatbot, virtual pet, or self-modifying loop.

## Frozen Phase 1 authority

Precedence:

1. Minimal Organism Contract v0.2
2. accepted ADRs 0001–0007
3. protected tests and Phase 1 matrix
4. explicit current repository decisions

Phase 1 passed final independent read-only audit at `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338`: all six findings resolved, no new blocker/high/medium defect, 152 tests passed. Issue #56 is closed.

Phase 1 body/trusted kernel are frozen. Proposed ADR 0008 is non-normative until accepted and merged.

If implementation reveals contradiction, stop and resolve through reviewed contract/ADR work.

## Safety and continuity

SUDACHI vocabulary describes deterministic local software: Python, SQLite, immutable artifacts, synthetic garden. It has no wet-lab biology, pathogens, genetic engineering, medical intervention, weapons, offensive cybersecurity, third-party system access, organism network activity, or organism subprocess execution.

Follow `docs/AI_COLLABORATION_OPERATIONS.md`. Do not evade safeguards. Do not create automatic next slices merely to continue activity.

## Completed Phase 1

Issue #13 is completed/closed. Slices 1–35 provide:

- canonical SQLite + append-only events
- injected clocks and deterministic garden
- fail-fast `BEGIN IMMEDIATE` ownership
- bounded actions/abstention/failure/maintenance/budgets
- stable checkpoints, repair, retention, export
- protected rollback lineage and one retained evidence set
- ordering/seed/repeat equivalence
- cleanup/replay/process-crash/nested-writer/pending-checkpoint protections
- no organism-writable external workspace
- narrow action SQL authority
- exact organism/administration provenance

PR #57 fixed all six audit defects and merged as `c92aa8efd0b9800afd637ce1f1d16d3223bdeb3b`.

Issue #56 final conclusion:

> Phase 1 is ready to freeze and Phase 2 design may begin.

Do not reopen Phase 1 Issues for Phase 2 features.

## Current Phase 2.0 gate

Issue #59 and draft PR #60 contain documentation-only design. There is no authorized Slice 36 or implementation.

### Proposed operational boundaries

1. **Garden request wake** preserves the unchanged Phase 1 `no_applicable_action` outcome/failure increment. No request on maintenance entry.
2. **Dispatch admission** durably records and conservatively charges one current-lineage dispatch before external work.
3. **Fixture execution** runs outside SQLite write transactions with request envelope + declared case only.
4. **Ingress or terminalization** records immutable untrusted data or terminal reason. External package has no writer authority/cost authority.
5. **Explicit disposition wake** is caller-selected, claims no garden input, considers one proposal, preserves garden failure streak, and checkpoints.

Busy or pending-checkpoint ingress may be explicitly retried with the same already-produced bytes; fixture is never re-invoked automatically.

### Proposed proposal boundary

Types:

- `action_candidate`
- `abstain`
- `defer`

Final dispositions:

- `accepted`
- `rejected`
- `deferred`
- `clarification_requested`

The first slice stops at disposition. Accepted proposal does not enter existing selector or execute action. Clarification rounds are zero.

### Proposed authority boundary

Canonical writer categories remain exactly:

- `organism`
- `administration`

Caregiver/adapter are provenance only. External packages contain no authority fields or authoritative cost. Protected administrative receipt/event carries writer source.

### Proposed identifier boundary

Acyclic order:

1. request
2. dispatch
3. proposal content/ID
4. response ID
5. final package digest
6. disposition

Proposal ID excludes response ID. Pre-insert IDs exclude later event sequences.

### Proposed budget epoch

Consultation budget epoch is current `lineage_generation`.

- four requests/charged fixture invocations per lineage
- one current-lineage outstanding request
- 64 KiB logical payload per lineage
- old-lineage rows remain historical and inactive
- rollback starts fresh bounded epoch
- ADR 0007 permits one completed rollback, so whole physical organism is bounded to at most eight charged fixture invocations

A global cross-lineage four-call counter is not claimed because it would require changing frozen rollback semantics or introducing another authority.

### Proposed finite limits

- request <=16 KiB
- response+proposal <=16 KiB
- provenance <=8 KiB
- zero human/model/money/declared latency
- exact record/step caps in ADR/protocol
- inherited 8 MiB active DB, 40 MiB checkpoint store, 64 MiB working set
- administrative writes preserve 1 MiB next-wake reserve before/after

### Proposed rollback behavior

Only current-lineage consultation rows are active. Rollback increments lineage; restored prior consultation rows become historical. Abandoned-lineage packages cannot ingress or dispose.

## Audit cadence

Codex audits are high-cost phase gates, not per-slice/PR review. Follow `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`.

Next audit: one read-only Phase 2.0 design audit after PR #60 internal consistency is complete. A later one-time implementation audit occurs before freezing implemented Phase 2.

Avoid audit-repair-reaudit ping-pong unless gate conclusion blocks progress or evidence is insufficient.

## Frozen Phase 1 invariants

Phase 1 remains deterministic, local, network-free, subprocess-free, caregiver-free, bounded, auditable, SQLite-canonical, checkpointed per committed wake, and explicit about authority.

Phase 1 runtime must not:

- dual-write canonical stores
- write authoritative mutable files outside SQLite
- consult caregiver
- execute arbitrary generated code
- run continuously
- add unrestricted retry/backtracking
- weaken tests/budgets
- modify protected actions/evaluators/schema/contract/environment
- claim administration authority

ADR 0007 keeps one completed rollback and full evidence set.

## Exact restart point

1. verify Issues #13/#56 closed and PR #57 merged
2. verify final audit and unchanged 152-test baseline
3. inspect Issues #3/#59 and draft PR #60
4. read proposed ADR/protocol/matrix
5. verify failure honesty, dispatch pre-charge, ingress authority separation, acyclic IDs, explicit disposition wake, lineage epoch, reserve, checkpoint, and rollback rules
6. conduct one Phase 2.0 design audit when package is internally coherent
7. do not create code/Slice 36 before accepted merged design and separate implementation Issue

Do not begin live caregiver/API, human chat, memory, skills, training, arbitrary Python/shell/SQL, continuous execution, personality/emotion, or generic agent framework.

## End-of-work protocol

- update `docs/HANDOFF.md`
- update matrices/durable notes
- update Issues/PRs
- report tests/CI/failures/skips honestly
- keep no critical decision only in chat
- preserve repository language policy

Repository prose, code, Issues, ADRs, and tests are English. Intentional Japanese README lines remain the standing exception.
