# SUDACHI Handoff

Updated: **2026-07-26**

Phase 1 is frozen. ADR 0008 is accepted and Issue #61 owns Phase 2 implementation, but Slice 36 is temporarily blocked by the zero-caregiver semantic artifact contradiction tracked in Issue #63 and draft PR #64.

A focused read-only re-audit confirmed the contradiction and concluded that proposed ADR 0009 is ready after specified documentation or matrix corrections. Those corrections now cover the full checkpoint, repair, retention, rollback, and export byte-provenance graph. The immediate gate is green CI, ADR 0009 acceptance, PR #64 merge, Issue #63 closure, and Slice 36 resumption. No live caregiver integration is authorized.

Read `AGENTS.md`, `docs/AI_COLLABORATION_OPERATIONS.md`, Minimal Organism Contract v0.2, accepted ADRs 0001–0008, proposed ADR 0009, the Phase 1 matrix, `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`, this handoff, the Consultation Protocol v1, the Phase 2 matrix, and current Issues/PRs.

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

## Phase 2 base design and correction

ADR 0008, Consultation Protocol v1, and `docs/PHASE2_CONSULTATION_TEST_MATRIX.md` form the accepted base design.

The design audit reviewed PR #60 head `8cfd65d6e6b153a9dd028333ddf898e7dd4b0647` and concluded:

> Phase 2.0 Consultation Boundary is ready after specified documentation or test-matrix corrections.

The accepted base design includes exact proposal schemas/evaluator sets/inherited expiry, exact digest preimages and package graph, exact 64 KiB lineage accounting, and the optional request savepoint with real storage-boundary evidence.

Implementation preparation exposed an additional contradiction: schema-v2 protected objects alter checkpoint bytes and every identity/digest/size derived from those bytes, while the original zero-caregiver oracle required those original Phase 1 locations to compare exactly.

A focused re-audit of proposed ADR 0009 at PR #64 head `e4f3527518cbc4e4ff8ab239a90f48bfa47fdbb8` confirmed the contradiction and concluded:

> ADR 0009 is ready after specified documentation or matrix corrections.

The correction package now defines the required exhaustive exact-location oracle.

## Zero-caregiver correction

Proposed ADR 0009 requires:

- original `budget_config`, organism/event `budget_config_version`, and values remain exactly `phase1-v1`
- one protected immutable `consultation_configuration` singleton stores Phase 2 policy
- exact semantic `CP`/`RA`/`RC`/`TC`/`STAGE` mappings at enumerated table/column and event-type/JSON locations
- explicit treatment of normal/maintenance checkpoint events, registration repair, retention prune/failure/reconciliation, rollback archive/source candidate/transformed candidate/completion, and semantic event export
- per-side recomputation and bijective linkage for every projected-away digest, size, aggregate-byte count, and directory identity
- no wildcard, recursive walk, suffix/prefix match, regex-by-key, or global key normalization
- active/artifact structural overhead ≤256 KiB per paired database and aggregate additional manifest/directory metadata ≤1 MiB
- separate real absolute-limit tests for 8 MiB active/artifact, 40 MiB checkpoints, 64 MiB working set, and 1 MiB reserve

Slice 36 must not resume before ADR 0009 is accepted and PR #64 merges.

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
- frozen Phase 1 budget `phase1-v1`
- consultation config `phase2-zero-caregiver-v1` or `phase2-fixture-v1`
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

Issue #61 maps bounded slices to accepted matrix IDs. After ADR 0009 acceptance, Slice 36 begins with:

- P2-A01–P2-A05
- P2-B01–P2-B12
- P2-C01–P2-C18
- the Slice-36-relevant P2-O15–P2-O22 physical and integrity controls

Later grouping remains:

1. request envelope and optional storage-safe extension — D/E
2. exact digests and typed response/proposal schemas — H/I
3. dispatch, precharge, and fixture capability boundary — F/G
4. ingress, logical payload, and terminalization — J/K
5. explicit disposition wake — L
6. lineage, authority, physical budgets, checkpoint/rollback, and absence closure — M/N/O/P

Slices may be split into smaller PRs, but requirements may not move silently and no test may weaken or condition the 152-test Phase 1 baseline.

## Audit cadence

The Phase 2 design audit and one focused zero-caregiver correction re-audit are complete. The focused conclusion permits acceptance after specified documentation/matrix corrections, so no automatic third design audit is required after green CI and ordinary review.

The next planned Codex audit occurs once only after the full accepted Phase 2 implementation, every matrix item has protected evidence, the unchanged Phase 1 suite passes, and one exact CI-green candidate is ready to freeze.

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

1. verify Issue #61 is open and Slice 36 has no runtime implementation
2. inspect Issue #63, focused re-audit comment `5082883885`, proposed ADR 0009, and PR #64
3. verify synchronized ADR/protocol/matrix/continuity corrections and green CI
4. accept ADR 0009, merge PR #64, and close Issue #63
5. resume Slice 36 test-first with the exact configuration singleton and semantic artifact oracle
6. keep all 152 Phase 1 tests unchanged and passing
7. run the implementation audit only when the complete Phase 2 candidate is ready to freeze

No critical decision may remain only in chat.
