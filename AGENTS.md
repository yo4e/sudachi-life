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
18. for Phase 2: ADR 0008, `docs/phase2/CONSULTATION_PROTOCOL_V1.md`, `docs/PHASE2_CONSULTATION_TEST_MATRIX.md`, and the Issue #59 design-audit report

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

Issue #59 and draft PR #60 define the first deterministic fixture consultation boundary. ADR 0008 remains Proposed until the audit corrections are reviewed and the design PR is accepted.

The independent design audit reviewed exact head `8cfd65d6e6b153a9dd028333ddf898e7dd4b0647` and concluded:

> Phase 2.0 Consultation Boundary is ready after specified documentation or test-matrix corrections.

The required corrections are now incorporated in the ADR, protocol, and matrix:

- exact `phase1-projection-v1` zero-caregiver comparison with only two exact version-key exceptions
- exact proposal field sets, type-specific values, protected evaluator sets, and proposal expiry equal to request expiry
- exact domain-separated digest preimages and package object
- exact 64 KiB per-lineage formula without double counting
- optional request-extension savepoint and real 8 MiB/reserve boundary evidence

These are bounded documentation and matrix repairs. Under the audit policy, ordinary review and CI verify them; no automatic second design audit is required unless the repairs materially invalidate the audit conclusion.

### Five operational boundaries

1. **Garden request wake**
   - preserves unchanged Phase 1 `no_applicable_action` and failure accounting
   - creates no request on maintenance entry
   - treats request metadata as an optional savepoint extension
   - commits the core Phase 1 wake and checkpoint even when the extension alone cannot fit
2. **Administrative dispatch admission**
   - fresh fail-fast transaction
   - stable current-lineage request required
   - conservative charge before external work
   - releases SQLite ownership before fixture execution
3. **External deterministic fixture**
   - receives only final request envelope and declared fixture case
   - has no DB, path, workspace, executor, evaluator, checkpoint, rollback, network, subprocess, credential, tool, or randomness capability
4. **Administrative ingress or terminalization**
   - independently verifies exact schemas, preimages, IDs, sizes, expiry, lineage, proposal shape, and physical budgets
   - keeps writer authority and protected cost separate from caregiver provenance
   - permits explicit same-byte ingress resubmission after busy/pending rejection without fixture recall
   - never automatically retries admitted fixture work
5. **Explicit disposition wake**
   - caller-selected separately from garden work
   - claims no garden input
   - considers one proposal at most
   - preserves garden failure streak
   - checkpoints normally
   - produces no selector/action/memory/skill effect in the first implementation

Protocol v1 proposal types are `action_candidate`, `abstain`, and `defer`. Final dispositions are `accepted`, `rejected`, `deferred`, and `clarification_requested`. Clarification rounds are zero.

## Authority, identifiers, expiry, and budgets

Canonical writer categories remain exactly `organism` and `administration`. Caregiver/adapter identity is provenance only. External packages contain no canonical writer-authority or authoritative cost/budget/permission/evaluator fields.

Identifiers use the exact domain-separated digest function and acyclic order fixed in the protocol:

1. request
2. dispatch
3. proposal content and proposal ID
4. response ID
5. final package digest over exactly `response` and `proposals`
6. current-state digest
7. disposition

Proposal expiry equals request expiry exactly. A request created at lifecycle `N` is eligible through `N+2`; disposition at considering lifecycle `N+3` rejects as expired.

Consultation budget epoch is current `lineage_generation`:

- at most four requests and four charged fixture invocations per lineage
- one current-lineage outstanding request
- 64 KiB logical payload per lineage, exactly request-envelope bytes plus successfully ingressed complete-package bytes
- provenance is inside, not added to, the package limit
- duplicate ingress adds zero logical bytes
- old-lineage rows remain immutable historical evidence and inactive
- rollback starts a fresh bounded epoch
- ADR 0007 bounds one physical organism to at most eight charged fixture invocations

Physical limits remain:

- request envelope at most 16 KiB
- complete external package at most 16 KiB
- provenance at most 8 KiB within package limit
- zero human/model/money/declared latency for deterministic fixture
- 8 MiB active database
- 40 MiB checkpoint store
- 64 MiB working set
- 1 MiB next-wake active-database reserve

## Codex audit cadence

Codex audits are high-cost phase gates, not per-slice or per-PR review. Follow `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`.

Phase 2 has two planned independent audits:

1. the completed design audit in Issue #59
2. one implementation audit after accepted ADR 0008 is fully implemented, every accepted matrix requirement has protected evidence, the unchanged Phase 1 suite passes, and one exact CI-green candidate is ready to freeze

Avoid audit-repair-reaudit ping-pong unless evidence is insufficient, the gate remains blocked, or a repair materially changes the same critical boundary being certified.

## Exact restart point

1. verify Issues #13/#56 are closed and PR #57 is merged
2. verify the frozen 152-test Phase 1 baseline
3. inspect Issues #3/#59 and PR #60
4. read proposed ADR 0008, corrected protocol, corrected matrix, and design-audit report
5. verify audit corrections and green CI
6. if satisfactory, change ADR 0008 to Accepted, merge PR #60, close Issue #59, and open a separate test-first Phase 2 implementation Issue
7. implement bounded slices mapped to matrix IDs
8. run one implementation audit only after the complete Phase 2 candidate is ready to freeze

Do not begin live caregiver/API integration, human chat, memory, skills, model training, arbitrary Python/shell/SQL, continuous execution, personality/emotion features, or a generic agent framework.

## End-of-work protocol

- update `docs/HANDOFF.md`
- update matrices and durable notes
- update relevant Issues and PRs
- report tests, CI, failures, and skipped checks honestly
- keep no critical decision only in chat
- preserve the repository language policy

Repository prose, code, Issues, ADRs, and tests are English. Intentional Japanese README lines remain the standing exception.
