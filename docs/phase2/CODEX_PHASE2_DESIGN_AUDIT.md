# Codex Phase 2.0 Consultation Boundary Design Audit

Status: **Audit brief for proposed ADR 0008; no implementation authorization**

## Purpose

Perform one independent read-only design audit of the complete Phase 2.0 Consultation Boundary before ADR 0008 is accepted or any Slice 36 implementation issue is opened.

This is the single planned Phase 2 design-gate audit under `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`. It is not a request for code, fixes, implementation planning, or repeated per-edit review.

## Exact audit target

Audit the exact PR #60 head recorded in Issue #59 at the time the audit begins.

Record the full audited commit SHA in the report. If the head changes during the audit, stop and report that the target moved rather than silently reviewing mixed revisions.

Do not modify tracked files or Git index.

## Reconstruct from repository state

Read in order:

1. `AGENTS.md`
2. `docs/AI_COLLABORATION_OPERATIONS.md`
3. `docs/HANDOFF.md`
4. `docs/MINIMAL_ORGANISM_CONTRACT.md`
5. accepted ADRs 0001–0007
6. `docs/PHASE1_TEST_MATRIX.md`
7. `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`
8. Issue #56 final audit report and closure
9. Issue #59 current body and comments
10. draft PR #60 body and complete diff
11. proposed `docs/decisions/0008-caregiver-consultation-boundary.md`
12. `docs/phase2/CONSULTATION_PROTOCOL_V1.md`
13. `docs/PHASE2_CONSULTATION_TEST_MATRIX.md`
14. relevant Phase 1 implementation and tests for authority, locking, failure streak, storage reserve, checkpoint, and rollback claims

Repository and GitHub state outrank conversation history.

## Audit objectives

### A. Frozen Phase 1 baseline

Determine whether the proposed design preserves:

- unchanged schema-v1 behavior and all 152 tests
- one canonical SQLite body
- append-only event order
- injected time
- fail-fast write ownership
- Phase 1 action, selector, and evaluator authority
- failure and maintenance truth
- checkpoint and rollback semantics
- no external workspace, network, or subprocess path in organism execution
- exact organism-versus-administration provenance

### B. Five operational boundaries

Review separation and crash behavior for:

1. garden request wake
2. administrative dispatch admission and conservative charge
3. fixture execution outside the write transaction
4. administrative response ingress or dispatch terminalization
5. explicit organism disposition wake

Check that no boundary implicitly waits, retries, queues a second wake, executes an action, or grants caregiver authority.

### C. Garden failure and maintenance accounting

Verify that:

- request creation does not convert `no_applicable_action` into success
- the Phase 1 failure streak increments exactly once
- request creation never resets it
- a maintenance-entering garden wake creates no request
- disposition wake neither resets nor increments the garden failure streak
- disposition cannot bypass maintenance

### D. Non-atomic fixture boundary

Examine:

- durable dispatch admission before fixture work
- conservative cost charging before invocation
- no refund after crash
- no automatic fixture retry
- explicit terminal reconciliation after interruption
- same-byte ingress resubmission after busy or pending-checkpoint rejection without fixture recall
- absence of an unsupported exactly-once claim

### E. Authority and envelope separation

Verify that:

- external response and proposal contain no canonical writer authority
- external packages cannot declare authoritative cost, budget, or permission
- administrative receipt and event own ingress writer provenance
- caregiver identity remains untrusted provenance only
- ingress cannot adopt, act, clear maintenance, checkpoint, migrate, or roll back

### F. Identifier and digest graph

Reconstruct the complete derivation graph and check:

- request ID event-sequence exclusion is safe and exact
- dispatch ID linkage is complete
- proposal ID excludes response ID
- response ID depends only on already-derived proposal IDs and content digests
- final package digest is calculated after response linkage is inserted
- disposition ID excludes the later event sequence
- no circular, ambiguous, or under-specified normalization exists

### G. Lineage budget epoch and rollback

Verify that:

- current `lineage_generation` is the consultation budget epoch
- only current-lineage rows can be active or budget-counting
- old-lineage rows remain immutable historical evidence
- rollback starts a fresh four-call epoch without changing Phase 1 rollback transformation
- abandoned-lineage packages and proposals fail before mutation
- ADR 0007 bounds one physical organism to at most two epochs and eight charged invocations
- the design does not make a false global four-call lifetime claim

### H. Expiry, work selection, and terminal state

Check:

- lifecycle `N` through `N+2` boundary
- considering lifecycle used at disposition
- deterministic explicit selection by ingress event sequence then proposal ID
- no hidden priority between garden and disposition work
- outstanding and terminal derivation for pre-dispatch expiry, admitted dispatch, unavailable, queued proposal, terminal dispatch, disposition, and historical lineage
- no caregiver-writable status authority

### I. Budgets and physical storage

Review all exact limits, including:

- request, response, provenance, and per-lineage payload limits
- record and semantic-step caps
- zero human, model, money, and declared-latency fixture condition
- 8 MiB active database
- 40 MiB checkpoint store
- 64 MiB working set
- inherited 1 MiB next-wake reserve
- requirement to prove maximum disposition wake and checkpoint fit the reserve

Identify any combination where individually valid logical limits cannot satisfy physical ceilings or where administrative writes can strand the organism.

### J. Checkpoint and rollback interactions

Check:

- stable request checkpoint before dispatch
- no checkpoint from dispatch, ingress, or terminal administration
- ordinary checkpoint after disposition
- pending-checkpoint exclusion
- schema-v2 checkpoint validation
- rollback before and after request, dispatch, ingress, and disposition
- lineage filtering after restored checkpoint
- preservation of ADR 0007 evidence and one-rollback rule

### K. Zero-caregiver control

Determine whether the projection is precise and implementable:

- normalize only existing schema and budget configuration values
- compare every original Phase 1 row, column, event payload, and original-table sequence
- require operational consultation tables and sequences empty
- require no consultation import, event, source, cost, or effect
- preserve status, checkpoint, rollback, and authority behavior

### L. Test matrix quality

Assess whether the proposed matrix:

- maps every design invariant
- covers cross-boundary shared assumptions
- covers real crash, concurrency, and storage boundaries rather than mocks alone
- preserves all 152 tests unchanged
- is implementable without silently changing scope
- avoids requiring behavior contradicted by ADR or protocol

### M. Explicit exclusions

Confirm the design does not authorize:

- live API, model, or human caregiver
- chat automation
- memory or skills
- caregiver source or test generation
- model training
- arbitrary Python, shell, SQL, tools, paths, URLs, or credentials
- organism network or subprocess
- continuous execution
- personality, emotion, or virtual-pet state
- caregiver-controlled authority
- generic agent framework

## Finding format

For each finding report:

- severity: blocker, high, medium, low, or informational
- affected invariant or decision
- exact file and section
- evidence and reasoning
- concrete contradiction or failure scenario
- whether the test matrix would catch it
- recommended disposition:
  - design repair required before acceptance
  - test-matrix addition required
  - wording or normalization clarification
  - later implementation concern
  - no action

Also report important areas inspected with no issue found.

For each major design group A–M, assign exactly one status:

- `sound`
- `sound after stated clarification`
- `requires redesign`
- `insufficient evidence`

## Final conclusion

Finish with exactly one:

- `Phase 2.0 Consultation Boundary is ready to accept and implementation planning may begin.`
- `Phase 2.0 Consultation Boundary is ready after specified documentation or test-matrix corrections.`
- `Phase 2.0 Consultation Boundary requires specified redesign before implementation.`
- `The available evidence is insufficient to conclude.`

Post the complete report to Issue #59.

Do not change ADR 0008 status, merge PR #60, create an implementation Issue, or write Phase 2 code during this audit.
