# SUDACHI Handoff

Updated: **2026-07-26**

This is the operational restart point after Phase 1 SUDACHI-0, Slices 1–35, completion-audit repairs, and the successful final independent audit. Phase 1 is frozen.

Current work is Phase 2 Consultation Boundary design in Issue #59 and PR #60. The design is reviewed through the ordinary repository process. Codex is reserved for one completion audit after the full Phase 2 implementation and protected test matrix are finished.

Read `AGENTS.md`, `docs/AI_COLLABORATION_OPERATIONS.md`, this handoff, Minimal Organism Contract v0.2, accepted ADRs 0001–0007, the Phase 1 matrix, `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`, and current Issues/PRs. For Phase 2 also read ADR 0008, `docs/phase2/CONSULTATION_PROTOCOL_V1.md`, and `docs/PHASE2_CONSULTATION_TEST_MATRIX.md`.

## Project thesis

SUDACHI asks whether a bounded artificial organism can convert finite external cognitive scaffolding into verified local competence and preserve capability while reducing justified caregiver dependence.

```text
parent reasoning -> verified experience -> reusable skill -> cheap local behavior
```

The repository is the organism's auditable body, developmental history, skill base, and lineage record. A language model may later be a caregiver or organ; it is not the organism itself.

> As it becomes smarter, it should become smaller and quieter.

## Frozen Phase 1

Normative precedence:

1. `docs/MINIMAL_ORGANISM_CONTRACT.md` v0.2
2. accepted ADRs 0001–0007
3. protected Phase 1 tests and `docs/PHASE1_TEST_MATRIX.md`

Phase 1 provides one canonical SQLite body, append-only sequence-ordered events, injected clocks, fail-fast write ownership, deterministic seed-garden behavior, concrete budgets, protected evaluation, exact checkpoint boundaries, immutable checkpoint and rollback evidence, exact authority provenance, no organism-writable external workspace, and narrow action-scoped SQL authority.

It has no caregiver, model adapter, chat UI, organism network or subprocess access, arbitrary generated code, learning, memory, skills, continuous loop, or generic agent framework.

The Phase 1 body and trusted kernel are frozen.

## Completed Phase 1 work

### Issue #13

Completed and closed. PR #57 repaired all six defects found by Issue #56 and merged as `c92aa8efd0b9800afd637ce1f1d16d3223bdeb3b`.

### Issue #56

Completed and closed. The final read-only audit checked `main` at `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338` and reported:

- Findings 1–6 resolved
- no new blocker, high, or medium defect
- Python 3.12 protected suite: 152 passed
- the real 8 MiB storage boundary independently reproduced
- retention-reconciliation interruption and retry independently reproduced
- no tracked-file or index modification during audit

Final conclusion:

> Phase 1 is ready to freeze and Phase 2 design may begin.

Future Codex work follows the phase-completion policy rather than per-slice or design-gate review.

## Phase 2 Consultation Boundary

### Issue #59 and PR #60

Issue #59 is the design decision record. PR #60 contains the documentation package:

- ADR 0008
- `docs/phase2/CONSULTATION_PROTOCOL_V1.md`
- `docs/PHASE2_CONSULTATION_TEST_MATRIX.md`
- synchronized continuity instructions

The design begins with newly initialized schema-v2 organisms only. It does not authorize Phase 1 migration, downgrade, or cross-version rollback.

The base contract remains `0.2`. Phase 2 uses protected consultation budget configurations:

- `phase2-zero-caregiver-v1`
- `phase2-fixture-v1`

### Five operational boundaries

1. **Garden request wake**
   - occurs only after the unchanged Phase 1 policy selects `no_applicable_action` for an incomplete objective
   - preserves the same tick, abstention, action, mutation, and failure accounting
   - increments the Phase 1 failure streak exactly once
   - creates no request when that wake enters maintenance
   - commits and checkpoints before dispatch admission
2. **Administrative dispatch admission**
   - uses a fresh fail-fast transaction
   - requires a stable, eligible, current-lineage request
   - records immutable dispatch evidence and conservatively charges work before fixture execution
   - commits and releases the SQLite write lock before external work
3. **External deterministic fixture**
   - receives only the canonical request envelope and declared fixture case
   - receives no DB, path, workspace, executor, evaluator, checkpoint, rollback, network, subprocess, or ambient-randomness capability
   - returns a noncanonical package to the explicit caller or harness
4. **Administrative ingress or terminalization**
   - external data cannot declare canonical writer authority or authoritative cost
   - protected administrative receipt and event record writer provenance, package digest, and measured bytes
   - busy or pending-checkpoint rejection permits explicit same-byte resubmission without fixture recall
   - invalid, expired, or interrupted dispatch terminalizes once and is never automatically retried
5. **Explicit disposition wake**
   - is caller-selected separately from a garden wake
   - uses fail-fast wake ownership
   - claims no garden tick
   - selects at most one queued proposal deterministically
   - increments lifecycle but preserves the garden failure streak
   - creates the ordinary checkpoint
   - has no action or garden effect in the first implementation

### Proposal and authority boundaries

Protocol v1 proposal types:

- `action_candidate`
- `abstain`
- `defer`

Final dispositions:

- `accepted`
- `rejected`
- `deferred`
- `clarification_requested`

Clarification rounds are zero. An accepted proposal does not enter the existing action selector or execute an action.

Canonical writer categories remain exactly:

- `organism`
- `administration`

Caregiver and adapter identity are immutable provenance only.

### Acyclic identifier graph

Derivation order is:

1. request
2. dispatch
3. proposal content and proposal ID
4. response ID
5. final package digest
6. disposition

Proposal ID excludes response ID. Pre-insert identifiers exclude later-assigned event sequences only where explicitly declared.

### Lineage budget epoch

Consultation budget epoch is the current `lineage_generation`:

- at most four requests and four charged fixture invocations per lineage
- one current-lineage outstanding request
- 64 KiB logical consultation payload per lineage
- old-lineage rows remain immutable historical evidence and inactive
- rollback starts a fresh bounded epoch
- ADR 0007 permits one completed rollback, bounding one physical organism to at most eight charged fixture invocations

A global four-call counter across rollback lineages is not claimed because enforcing it would alter frozen rollback transformation or introduce another authority.

### Finite limits

- request: at most 16 KiB
- response plus proposal: at most 16 KiB
- external provenance: at most 8 KiB
- fixture human minutes, model units, money, and declared latency: zero
- exact record and semantic-step caps are fixed by ADR 0008 and protocol v1
- inherited active database: 8 MiB
- inherited checkpoint store: 40 MiB
- inherited runtime working set: 64 MiB
- every Phase 2 administrative write preserves the existing 1 MiB next-wake reserve before and after mutation

Request expiry is lifecycle-based: a request created in lifecycle `N` is eligible through `N+2`.

### Zero-caregiver control

`phase2-zero-caregiver-v1` creates no consultation row, event, source, adapter invocation, cost, disposition, or caregiver-derived effect.

The protected Phase 1-relevant projection:

1. normalizes only existing schema and budget configuration values
2. compares every original Phase 1 row, column, event payload, and original-table sequence exactly
3. requires operational consultation tables and sequences to remain empty
4. requires no consultation event, source, cost, or effect
5. preserves behavior, status, lifecycle, checkpoint, rollback, and authority semantics

## Audit cadence and implementation gate

There is no separate Codex audit for Phase 2 design acceptance.

The correct sequence is:

1. finish ordinary review of Issue #59 and PR #60
2. accept ADR 0008 and merge the design package
3. open a separate test-first Phase 2 implementation Issue
4. implement bounded slices mapped to `docs/PHASE2_CONSULTATION_TEST_MATRIX.md`
5. keep all 152 Phase 1 tests unchanged and passing
6. complete the Phase 2 matrix and CI evidence
7. run one independent read-only Codex audit of the complete implemented Phase 2 candidate
8. repair accepted findings and freeze Phase 2 only after a satisfactory conclusion

Do not run Codex for each slice, PR, intermediate fix, or design draft.

## Issue #3 research

Research continues independently. Deterministic fixture plumbing is not blocked.

Live human or model experiments, provider automation, retained provider output, and strong novelty claims remain blocked pending current first-party review of privacy, consent, terms, retention, pricing, limits, and transformation rules.

## Validation state

Phase 1 evidence includes PR #54, runs 317 and 323, repair runs 335, 336, 340, and 343, PR #57 merge, and the final independent 152-pass audit.

PR #60 is documentation-only. No Phase 2 executable behavior is claimed until the separate implementation stream begins.

## Explicit exclusions

Do not add:

- live API or model caregiver
- live human chat or unattended consumer automation
- long-term memory or skill generation
- caregiver source or test generation
- model training, fine-tuning, imitation, distillation, or synthetic-data training
- arbitrary Python, shell, SQL, tools, paths, URLs, credentials, or executable payloads
- organism network or subprocess access
- continuous or always-on execution
- autonomous internet use
- personality, emotion, affection, mood, or virtual-pet presentation
- caregiver-controlled budgets, permissions, evaluation, checkpoints, migration, or rollback
- a generic agent framework

## Exact next gate

Complete ordinary design review and merge ADR 0008 through PR #60. Then open the separate test-first Phase 2 implementation Issue. Do not request Codex review until the complete Phase 2 implementation is a candidate for freezing.

## Restart

1. read `AGENTS.md` and collaboration operations
2. read this handoff, Contract v0.2, ADRs 0001–0007, and the Phase 1 matrix
3. verify Issues #13 and #56 are closed and PR #57 is merged
4. inspect Issues #3 and #59 and PR #60
5. read ADR 0008, protocol v1, and the Phase 2 matrix
6. complete normal design acceptance and merge
7. create the test-first implementation Issue
8. map every implementation slice to matrix IDs
9. run one Codex completion audit only after implementation is complete

No critical decision may remain only in chat.