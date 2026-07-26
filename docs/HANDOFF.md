# SUDACHI Handoff

Updated: **2026-07-26**

Phase 1 is frozen. ADRs 0008 and 0009 are accepted. Issue #61 owns Phase 2 implementation and Slice 36 is authorized to resume test-first from updated `main`.

A focused read-only re-audit confirmed the contradiction and concluded that ADR 0009 was ready after specified documentation or matrix corrections. Those corrections passed CI and were accepted. PR #64 and Issue #63 close the design correction gate. No live caregiver integration is authorized.

Read `AGENTS.md`, `docs/AI_COLLABORATION_OPERATIONS.md`, Minimal Organism Contract v0.2, accepted ADRs 0001–0009, the Phase 1 matrix, `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`, this handoff, the accepted Consultation Protocol v1, the accepted Phase 2 matrix, and current Issues/PRs.

## Thesis

SUDACHI asks whether a bounded artificial organism can convert finite external cognitive scaffolding into verified local competence and preserve capability while reducing justified caregiver dependence.

```text
parent reasoning -> verified experience -> reusable skill -> cheap local behavior
```

Repository is auditable body, developmental history, skill base, and lineage record. A model may later be caregiver or organ; it is not the organism.

> As it becomes smarter, it should become smaller and quieter.

## Frozen Phase 1

Issues #13 and #56 are closed. PR #57 merged as `c92aa8efd0b9800afd637ce1f1d16d3223bdeb3b`.

The final Phase 1 audit checked `main` at `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338` and found all six findings resolved, no new blocker/high/medium defect, and 152 tests passing. Phase 1 remains the unchanged schema-v1 control.

Do not alter Phase 1 garden actions, selector, executor, evaluators, injected clocks, checkpoint rules, rollback transformation, authority categories, or protected tests for Phase 2 convenience.

## Accepted Phase 2 design

ADRs 0008 and 0009, Consultation Protocol v1, and `docs/PHASE2_CONSULTATION_TEST_MATRIX.md` form one accepted design package.

The design audit reviewed PR #60 head `8cfd65d6e6b153a9dd028333ddf898e7dd4b0647` and concluded:

> Phase 2.0 Consultation Boundary is ready after specified documentation or test-matrix corrections.

Required corrections were incorporated:

- exact zero-caregiver semantic artifact projection under accepted ADR 0009
- exact proposal schemas, evaluator sets, and inherited expiry
- exact digest preimages and package graph
- exact 64 KiB lineage accounting without double counting
- optional request savepoint and real request-wake storage-boundary evidence

Corrected design CI remained green with the unchanged 152-test suite. A later focused re-audit of ADR 0009 found additional exact-location propagation requirements across checkpoint events, repair, retention, rollback, and export; those corrections are accepted.

## Accepted zero-caregiver correction

ADR 0009 requires:

- original `budget_config` and every original budget-version location remain exactly `phase1-v1`
- one protected immutable `consultation_configuration` singleton stores Phase 2 policy
- exact semantic `CP`/`RA`/`RC`/`TC`/retention-staging mappings at enumerated canonical locations
- per-side recomputation and linkage checks for every projected-away digest, size, aggregate byte count, and directory name
- no wildcard/recursive/suffix/prefix/global-key normalization
- bounded schema-v2 structural overhead and separate real absolute-limit tests

Slice 36 may resume under Issue #61.

## Five operational boundaries

1. **Garden request wake**
   - preserves exact Phase 1 `no_applicable_action` outcome and failure increment
   - creates no request on maintenance entry
   - treats request metadata as an optional savepoint extension
   - commits the Phase 1 core wake/checkpoint when extension-only storage does not fit
2. **Administrative dispatch admission**
   - fresh fail-fast transaction
   - stable eligible current-lineage request required
   - conservative fixture charge before external work
   - releases SQLite ownership before fixture execution
3. **External deterministic fixture**
   - receives only final request envelope and declared case
   - no DB, path, workspace, repository, executor, evaluator, checkpoint, migration, rollback, network, subprocess, credential, tool, or randomness capability
4. **Administrative ingress or terminalization**
   - exact independent verification of schemas, preimages, IDs, proposal constraints, expiry, sizes, lineage, and physical budgets
   - writer authority/cost authority remain protected administration
   - identical-byte resubmission after busy/pending rejection without fixture recall
   - no automatic fixture retry
5. **Explicit disposition wake**
   - separate caller-selected work class
   - no garden claim
   - at most one proposal
   - preserves garden failure streak and checkpoints
   - no selector, action, memory, skill, or garden effect in first implementation

Proposal types: `action_candidate`, `abstain`, `defer`.

Dispositions: `accepted`, `rejected`, `deferred`, `clarification_requested`.

Clarification rounds: zero.

Canonical writer categories remain exactly `organism` and `administration`. Caregiver identity is provenance only.

## Accepted budgets and lifecycle rules

- schema-v2 new organisms only; no migration/downgrade
- base contract `0.2`
- request envelope ≤16 KiB
- complete external package ≤16 KiB
- provenance ≤8 KiB inside package limit
- four requests/four charged fixture calls per current lineage
- one current-lineage outstanding request
- 64 KiB exact logical payload per current lineage
- zero human/model/money/declared latency
- active DB 8 MiB
- checkpoints 40 MiB
- working set 64 MiB
- next-wake reserve 1 MiB

Logical payload is exactly final request-envelope bytes plus successfully ingressed complete-package bytes. Response/proposal/provenance are not double-counted. Duplicate ingress adds zero.

Request lifecycle `N` is eligible through `N+2`; every proposal inherits that expiry exactly. Considering lifecycle `N+3` or later rejects as expired.

Rollback starts a fresh lineage epoch. Old-lineage consultation rows remain immutable history and inactive. ADR 0007 bounds one physical organism to at most two epochs/eight charged fixture invocations.

## Implementation plan boundary

The separate implementation Issue must map bounded slices to accepted matrix IDs. A recommended grouping is:

1. schema-v2 initialization and zero-caregiver projection — A/B/C
2. request envelope and optional storage-safe extension — D/E
3. exact digests and typed response/proposal schemas — H/I
4. dispatch, precharge, and fixture capability boundary — F/G
5. ingress, logical payload, and terminalization — J/K
6. explicit disposition wake — L
7. lineage, authority, physical budgets, checkpoint/rollback, and absence closure — M/N/O/P

The exact issue may split these further, but no slice may weaken or condition the 152-test Phase 1 baseline.

## Audit cadence

The Phase 2 design audit and focused ADR 0009 correction re-audit are complete. The next Codex audit occurs once only after the full accepted Phase 2 implementation, every matrix item has protected evidence, the unchanged Phase 1 suite passes, and one exact CI-green candidate is ready to freeze.

Do not use Codex for each slice, PR, ordinary bug, or documentation edit. Avoid audit-repair-reaudit ping-pong unless evidence is insufficient, a gate remains blocked, or a repair materially replaces the same certified boundary.

## Explicit exclusions

No:

- live model/API/human caregiver or consumer chat automation
- memory or skill generation/promotion
- caregiver source/test generation
- model training/fine-tuning/imitation/distillation
- arbitrary Python, SQL, shell, tool, path, URL, credential, or executable payload
- organism network or subprocess
- continuous/always-on execution or autonomous internet
- personality, emotion, affection, mood, or virtual-pet state
- caregiver-controlled budgets, permissions, evaluation, checkpoints, migration, rollback, or execution
- generic agent framework

## Exact restart

1. verify Issue #63 is closed completed and PR #64 is merged
2. inspect Issue #61, accepted ADRs 0008–0009, protocol, and matrix
3. create a new Slice 36 implementation branch from updated `main`
4. write failing protected tests for the exact configuration singleton and semantic artifact oracle
5. implement only the declared Slice 36 matrix scope
6. keep all 152 Phase 1 tests unchanged and passing
7. run the implementation audit only when the complete Phase 2 candidate is ready to freeze

No critical decision may remain only in chat.
