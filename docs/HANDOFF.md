# SUDACHI Handoff

Updated: **2026-07-26**

This is the operational restart point after Phase 1 SUDACHI-0 completion and the Phase 2.0 Consultation Boundary design audit.

Phase 1 is frozen. Current work is closing Issue #59 and draft PR #60 after bounded documentation and test-matrix corrections requested by the independent design audit. No Phase 2 implementation or Slice 36 is authorized until ADR 0008 is accepted and the design PR is merged.

Read `AGENTS.md`, `docs/AI_COLLABORATION_OPERATIONS.md`, this handoff, Minimal Organism Contract v0.2, accepted ADRs 0001–0007, the Phase 1 matrix, `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`, and current Issues/PRs. For Phase 2 also read proposed ADR 0008, the corrected Consultation Protocol v1, the corrected Phase 2 matrix, and the complete Issue #59 audit report.

## Project thesis

SUDACHI asks whether a bounded artificial organism can convert finite external cognitive scaffolding into verified local competence and preserve capability while reducing justified caregiver dependence.

```text
parent reasoning -> verified experience -> reusable skill -> cheap local behavior
```

The repository is the organism's auditable body, developmental history, skill base, and lineage record. A model may later be caregiver or organ; it is not the organism.

> As it becomes smarter, it should become smaller and quieter.

## Frozen Phase 1

Normative precedence:

1. Minimal Organism Contract v0.2
2. accepted ADRs 0001–0007
3. protected Phase 1 tests and `docs/PHASE1_TEST_MATRIX.md`

Phase 1 provides one canonical SQLite body, append-only sequence-ordered events, injected clocks, fail-fast write ownership, deterministic garden behavior, concrete budgets, protected evaluation, exact checkpoint boundaries, immutable checkpoint/rollback evidence, exact authority provenance, no organism-writable external workspace, and narrow action-scoped SQL authority.

It has no caregiver, model adapter, chat UI, organism network/subprocess, arbitrary generated code, learning, memory, skills, continuous loop, or generic agent framework.

Issue #13 and Issue #56 are completed and closed. PR #57 merged as `c92aa8efd0b9800afd637ce1f1d16d3223bdeb3b`.

The final Phase 1 audit checked `main` at `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338` and reported:

- Findings 1–6 resolved
- no new blocker/high/medium defect
- Python 3.12 protected suite: 152 passed
- real 8 MiB storage boundary reproduced
- retention-reconciliation interruption/retry reproduced
- tracked files and index unchanged

Conclusion:

> Phase 1 is ready to freeze and Phase 2 design may begin.

## Phase 2.0 design audit

Issue #59 is the design decision record. Draft PR #60 contains:

- proposed ADR 0008
- `docs/phase2/CONSULTATION_PROTOCOL_V1.md`
- `docs/PHASE2_CONSULTATION_TEST_MATRIX.md`
- the design-audit brief and continuity updates

The independent read-only audit reviewed exact head:

`8cfd65d6e6b153a9dd028333ddf898e7dd4b0647`

Evidence at that head:

- local protected suite: 152 passed
- GitHub Actions run 378: 152 passed
- installation, compilation, and genesis CLI smoke: passed
- head unchanged during audit
- tracked files/index clean

Conclusion:

> Phase 2.0 Consultation Boundary is ready after specified documentation or test-matrix corrections.

The audit required four correction groups:

1. resolve the zero-caregiver comparison contradiction
2. constrain proposal schemas and proposal expiry exactly
3. define digest preimages and the 64 KiB formula exactly
4. require a real request-wake storage-boundary test

## Corrections incorporated on PR #60

### Exact zero-caregiver projection

`phase1-projection-v1` now:

- compares paired schema-v1/schema-v2-zero runs with identical inputs/clocks
- permits only original columns named exactly `schema_version` and `budget_config_version` to differ as declared
- normalizes only top-level original event-payload keys with those exact names
- compares nested keys, other spellings, added/missing keys, event types, sequences, authority, sources, parents, and all other values exactly
- requires consultation tables empty and without sequence entries
- requires no consultation event/source/cost/adapter/terminal/disposition/effect
- explicitly does not claim raw SQLite/checkpoint-digest equality because schema-v2 adds empty objects

No wildcard or recursive normalization is permitted.

### Exact proposal and expiry boundary

Every proposal has an exact common field set and exact type-specific shape.

- proposal expiry equals request expiry exactly
- fixture cannot shorten or extend expiry
- confidence basis exactly links the declared fixture case
- protected evaluator IDs are fixed per type
- `action_candidate` can name only one allowed registered action and schema-valid parameters
- `abstain` carries only `no_supported_action`
- `defer` carries only `await_state_change` and no scheduling/retry command
- no undeclared field is accepted

### Exact digest and payload accounting

Every protocol digest now uses:

```text
H(label, value) = sha256(
    UTF8("sudachi.consultation/v1\n" + label + "\n")
    || canonical_json(value)
)
```

Labels, separators, identity fields, exclusions, package preimage, and derivation order are exact.

Current-lineage logical payload is exactly:

```text
sum(final request envelope bytes)
+ sum(successfully ingressed complete external package bytes)
```

The package already contains response, proposal, and provenance, so none is counted twice. Provenance is inside the 16 KiB package limit. Duplicate ingress adds zero logical bytes. Metadata remains subject to physical ceilings.

### Storage-safe optional request extension

Request metadata is an optional savepoint extension to the unchanged Phase 1 wake.

- preflight includes core wake, extension, checkpoint, sidecars, reserve, and working set
- if extension alone cannot fit, no consultation row/event/source is written
- if measured page growth crosses the limit, only the extension savepoint rolls back
- the Phase 1 core outcome and ordinary checkpoint still commit
- caller receives noncanonical `consultation_request_not_created_storage_budget`
- the 1 MiB next-wake reserve remains available

The matrix requires a real 8 MiB scenario where the core wake fits but the request extension does not, including WAL/SHM, checkpoint staging, and working-set measurement.

## Accepted design shape pending ADR status change

Phase 2 begins with newly initialized schema-v2 organisms only. It does not authorize Phase 1 migration, downgrade, or cross-version rollback. Base contract remains `0.2`.

Protected configurations:

- `phase2-zero-caregiver-v1`
- `phase2-fixture-v1`

### Five operational boundaries

1. **Garden request wake**
   - preserves exact Phase 1 outcome/failure truth
   - no request on maintenance entry
   - request is optional savepoint extension
   - core wake/checkpoint survive extension-only storage refusal
2. **Administrative dispatch admission**
   - fresh fail-fast transaction
   - stable current-lineage request required
   - conservative charge before external work
   - lock released before fixture
3. **External deterministic fixture**
   - receives only final request envelope and declared case
   - no DB/path/workspace/executor/evaluator/checkpoint/rollback/network/subprocess/credential/tool/randomness capability
4. **Administrative ingress or terminalization**
   - exact independent verification of schemas, preimages, IDs, sizes, proposal constraints, expiry, lineage, and physical budgets
   - external data has no writer authority or cost authority
   - same-byte resubmission after busy/pending rejection without fixture recall
   - no automatic retry
5. **Explicit disposition wake**
   - caller-selected, no garden claim, one proposal maximum
   - preserves garden failure streak and checkpoints
   - no selector/action/memory/skill effect in first implementation

Proposal types: `action_candidate`, `abstain`, `defer`.

Final dispositions: `accepted`, `rejected`, `deferred`, `clarification_requested`.

Clarification rounds: zero.

Canonical writer categories remain exactly `organism` and `administration`. Caregiver/adapter identity is provenance only.

## Budgets, expiry, and lineage

- request final envelope: at most 16 KiB
- complete external package: at most 16 KiB
- provenance: at most 8 KiB within package limit
- current-lineage logical payload: at most 64 KiB by exact formula
- requests/charged fixture calls: at most four per lineage
- outstanding requests: one per current lineage
- zero human/model/money/declared latency
- active database: 8 MiB
- checkpoint store: 40 MiB
- working set: 64 MiB
- next-wake reserve: 1 MiB

A request created at lifecycle `N` is eligible through `N+2`. Every proposal inherits that expiry exactly. Disposition at considering lifecycle `N+3` or later rejects as expired.

Rollback begins a fresh current-lineage epoch. Old-lineage rows remain immutable historical evidence and inactive. ADR 0007 permits one completed rollback, bounding one physical organism to at most eight charged fixture invocations.

## Audit cadence

Phase 2 has two independent audit gates:

1. the completed Phase 2.0 design audit
2. one later implementation audit after accepted ADR 0008 is fully implemented, every accepted matrix item has protected evidence, the unchanged Phase 1 suite passes, and one exact CI-green candidate is ready to freeze

Bounded audit corrections are verified through ordinary review and CI. Do not automatically request a second design audit. Re-audit only if evidence is insufficient, the gate remains blocked, or corrections materially change the same certified boundary.

## Issue #3 research

Research continues independently. Deterministic fixture plumbing is not blocked.

Live human/model experiments, provider automation, retained provider output, and strong novelty claims remain blocked pending current first-party review of privacy, consent, terms, retention, pricing, limits, and transformation rules.

## Explicit exclusions

Do not add:

- live API/model caregiver
- live human chat or unattended consumer automation
- memory or skill generation
- caregiver source/test generation
- model training, fine-tuning, imitation, distillation, or synthetic-data training
- arbitrary Python, shell, SQL, tools, paths, URLs, credentials, or executable payloads
- organism network or subprocess
- continuous/always-on execution
- autonomous internet use
- personality, emotion, affection, mood, or virtual-pet presentation
- caregiver-controlled budgets, permissions, evaluation, checkpoints, migration, or rollback
- generic agent framework

## Exact next gate

1. review the corrected ADR, protocol, and matrix for internal consistency
2. verify CI at the corrected PR head
3. record each design-audit finding as addressed in Issue #59
4. change ADR 0008 from Proposed to Accepted if corrections and CI are satisfactory
5. merge PR #60
6. close Issue #59 completed
7. open a separate test-first Phase 2 implementation Issue
8. map every implementation slice to matrix IDs
9. do not run the next Codex audit until the complete implemented Phase 2 candidate is ready to freeze

No critical decision may remain only in chat.
