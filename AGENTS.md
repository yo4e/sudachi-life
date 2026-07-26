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
18. for Phase 2: proposed ADR 0008, `docs/phase2/CONSULTATION_PROTOCOL_V1.md`, `docs/PHASE2_CONSULTATION_TEST_MATRIX.md`, and `docs/phase2/CODEX_PHASE2_DESIGN_AUDIT.md`

Repository and GitHub state outrank conversation history.

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
3. protected tests and `docs/PHASE1_TEST_MATRIX.md`
4. explicit current repository decisions

Phase 1 passed final independent read-only audit at `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338`: all six findings were resolved, no new blocker/high/medium defect was found, and 152 tests passed. Issue #56 is closed.

Phase 1 body and trusted kernel are frozen. A Phase 2 extension must be explicit, versioned, reviewed, and protected.

If implementation reveals a contradiction, stop and resolve it through reviewed contract or ADR work. Code must not choose a private interpretation.

## Completed Phase 1

Issue #13 is completed and closed. Slices 1–35 and PR #57 provide:

- one canonical SQLite body and append-only sequence-ordered events
- injected clocks and deterministic seed garden
- fail-fast `BEGIN IMMEDIATE` ownership
- bounded action, abstention, failure, maintenance, and concrete budgets
- stable checkpoints, repair, retention, rollback lineage, and retained evidence
- ordering, seed independence, and repeated-run equivalence
- cleanup, replay, process-crash, nested-writer, and pending-checkpoint protections
- no organism-writable external workspace
- narrow action-scoped SQL authority
- exact organism and administration provenance
- repaired schema validation, orphan repair, shared retention, enqueue reserve, crash-retryable reconciliation, and complete working-set accounting

PR #57 merged as `c92aa8efd0b9800afd637ce1f1d16d3223bdeb3b`.

Final Issue #56 conclusion:

> Phase 1 is ready to freeze and Phase 2 design may begin.

Do not reopen Phase 1 Issues to add Phase 2 features.

## Phase 2 Consultation Boundary

Issue #59 and draft PR #60 define the first deterministic fixture consultation boundary. No Phase 2 implementation or Slice 36 is authorized while ADR 0008 remains Proposed.

The design keeps five explicit operational boundaries:

1. **Garden request wake**
   - preserves the unchanged Phase 1 `no_applicable_action` result and failure increment
   - creates no request on the wake that enters maintenance
   - commits and checkpoints before dispatch
2. **Administrative dispatch admission**
   - uses a fresh fail-fast transaction
   - records and conservatively charges one current-lineage dispatch before external work
   - releases SQLite write ownership before fixture execution
3. **External deterministic fixture**
   - receives only the request envelope and declared fixture case
   - has no DB, path, workspace, executor, evaluator, checkpoint, rollback, network, subprocess, or ambient-randomness capability
4. **Administrative ingress or terminalization**
   - records immutable untrusted data or one terminal reason
   - keeps writer authority and protected cost separate from caregiver provenance
   - permits explicit same-byte ingress resubmission after busy or pending-checkpoint rejection without recalling the fixture
   - never automatically retries an admitted fixture invocation
5. **Explicit disposition wake**
   - is caller-selected separately from a garden wake
   - claims no garden input
   - considers at most one proposal
   - preserves the garden failure streak
   - checkpoints normally

The first implementation stops at disposition. An accepted proposal does not enter the existing action selector or execute an action.

Protocol v1 proposal types are `action_candidate`, `abstain`, and `defer`. Final dispositions are `accepted`, `rejected`, `deferred`, and `clarification_requested`. Clarification rounds are zero.

## Authority, identifiers, and budgets

Canonical writer categories remain exactly `organism` and `administration`. Caregiver and adapter identity are provenance only. External packages contain no canonical writer-authority fields and no authoritative cost or budget fields.

Identifier derivation is acyclic:

1. request
2. dispatch
3. proposal content and proposal ID
4. response ID
5. final package digest
6. disposition

Consultation budget epoch is current `lineage_generation`:

- at most four requests and four charged fixture invocations per lineage
- one current-lineage outstanding request
- 64 KiB consultation logical payload per lineage
- old-lineage rows remain immutable historical evidence and are inactive
- rollback starts a fresh bounded lineage epoch
- ADR 0007 permits one completed rollback, bounding the physical organism to at most eight charged fixture invocations

Logical limits supplement inherited physical limits:

- request at most 16 KiB
- response plus proposal at most 16 KiB
- external provenance at most 8 KiB
- zero human minutes, model units, money, and declared latency for the fixture
- 8 MiB active database
- 40 MiB checkpoint store
- 64 MiB runtime working set
- every Phase 2 administrative write preserves the existing 1 MiB next-wake reserve before and after mutation

Expiry is lifecycle-based. A request created in lifecycle `N` is eligible through `N+2`.

## Codex audit cadence

Codex audits are high-cost phase gates, not per-slice or per-PR review. Follow `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`.

Phase 2 has two planned independent read-only audits:

1. one design audit after Issue #59, proposed ADR 0008, protocol v1, authority and provenance rules, budgets, expiry, initialization policy, zero-caregiver comparison, and the Phase 2 matrix are internally coherent
2. one implementation audit after the complete Phase 2 implementation, protected matrix, unchanged Phase 1 suite, and CI evidence are ready to freeze

Avoid audit-repair-reaudit ping-pong unless a gate conclusion blocks progress, evidence is insufficient, or accepted repairs change the same critical boundary being certified.

## Exact restart point

1. verify Issues #13 and #56 are closed and PR #57 is merged
2. verify the final Phase 1 audit and unchanged 152-test baseline
3. inspect Issues #3 and #59 and draft PR #60
4. read proposed ADR 0008, protocol v1, matrix, and design-audit brief
5. complete ordinary internal review of the design package
6. run one read-only Codex Phase 2.0 design audit against one exact PR head
7. resolve accepted findings, accept ADR 0008, and merge PR #60 only after a satisfactory design conclusion
8. open a separate test-first Phase 2 implementation Issue
9. implement bounded slices mapped to matrix IDs
10. run one later Codex implementation audit only after the complete Phase 2 candidate is ready to freeze

Do not begin live caregiver or API integration, human chat, memory, skills, model training, arbitrary Python, shell, SQL, continuous execution, personality or emotion features, or a generic agent framework.

## End-of-work protocol

- update `docs/HANDOFF.md`
- update matrices and durable notes
- update relevant Issues and PRs
- report tests, CI, failures, and skipped checks honestly
- keep no critical decision only in chat
- preserve the repository language policy

Repository prose, code, Issues, ADRs, and tests are English. Intentional Japanese README lines remain the standing exception.
