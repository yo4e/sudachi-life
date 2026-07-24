# SUDACHI Handoff

Updated: **2026-07-24**

This is the operational restart point for repository state containing Phase 1 Slices 1–35, accepted ADRs 0001–0007, and the independent Phase 1 completion-audit repair work in PR #57. Read `AGENTS.md` first, then the normative contract and ADRs before changing implementation.

## Project thesis

SUDACHI asks whether a bounded artificial organism can convert finite external cognitive scaffolding into verified local competence and preserve capability while reducing justified caregiver dependence.

```text
parent reasoning -> verified experience -> reusable skill -> cheap local behavior
```

The repository is the organism's auditable body, developmental history, skill base, and lineage record. A language model is a possible future caregiver or organ, not the organism itself.

> As it becomes smarter, it should become smaller and quieter.

## Normative Phase 1 baseline

Use this precedence:

1. `docs/MINIMAL_ORGANISM_CONTRACT.md` v0.2
2. ADRs 0001–0007 in `docs/decisions/`
3. protected Phase 1 tests and `docs/PHASE1_TEST_MATRIX.md`

Phase 1 has one canonical SQLite body, append-only sequence-ordered events, injected clocks, fail-fast write ownership, deterministic `seed-garden-v1`, concrete budgets, protected evaluation, exact checkpoint boundaries, immutable checkpoints, bounded retention, rollback lineage rules, explicit authority provenance, no organism-writable external workspace, and action-scoped SQL authority.

Phase 1 has no caregiver, model adapter, chat interface, network access, organism subprocess access, arbitrary generated code, learning, memory, skills, continuous execution, or generic autonomous loop.

## AI collaboration operations

Read `docs/AI_COLLABORATION_OPERATIONS.md`.

Repository and GitHub state outrank conversation memory. Do not introduce a paid runner, larger or GPU runner, private-repository Actions usage, paid external service, or model/API call without explicit owner approval.

## Current work streams

### Issue #13 — Phase 1 SUDACHI-0 metabolism

Issue #13 was reopened only because the independent completion audit in Issue #56 demonstrated six Phase 1 regressions. PR #57 is the bounded repair stream. Do not use the reopened issue to add Phase 2 behavior.

### Issue #56 — independent Phase 1 completion audit

The first read-only audit at baseline commit `54b2be47107cd9fbad3301812d23ab90f7ea9c4e` confirmed the original 142-test baseline and found six cross-boundary failures. After PR #57 is documentation-complete and green, the exact next external task is a read-only Codex re-audit of the latest PR head. Phase 1 is not re-frozen until that re-audit concludes that the specified repairs are sufficient.

### Issue #3 — prior work and provider review

Research continues independently. Preliminary evidence and provider-neutral strategy exist, but no strong novelty claim and no live caregiver selection are authorized.

Do not connect a human or model caregiver merely because Phase 1 is complete. Provider permissions, retention, pricing, limits, and transformation classes must be reverified from current first-party sources before any live integration.

## Implemented Phase 1 summary

### Slices 1–23 — canonical metabolism, storage, maintenance, and rollback

- canonical SQLite body, append-only events, injected clocks, and fail-fast write ownership
- deterministic garden water, harvest, abstention, classified failure, and recovery paths
- concrete budgets, lifecycle deadline, savepoint rollback, maintenance, and checkpoint retention/repair
- deterministic non-canonical JSONL export
- complete bounded rollback path from verified archive through restored wakeability
- one-completed-rollback retention boundary under ADR 0007

### Slices 24–26 — declared determinism

- backward wall time cannot reorder canonical events
- different declared seeds do not change fixed seed-garden behavior
- identical declared inputs produce exact canonical and checkpoint-artifact equivalence

### Slices 27–32 — bounded failure and concurrency closures

- cleanup grace permits only terminalization and overrun rolls back atomically
- lexicographic action selection ignores physical insertion order
- consumed input replay cannot duplicate action
- real process exit rolls back an uncommitted wake and releases ownership
- nested wake and hidden writers fail fast
- a pending checkpoint blocks the next wake until explicit repair

### Slice 33 — no organism-writable external workspace

The action executor receives no path or workspace handle. Guarded filesystem, temporary-file, network, subprocess, and process-launch interfaces are not invoked. A path-like target remains only a rejected SQLite identifier. The probe rolls back and the same tick later completes normally.

See `docs/phase1/SLICE33_NO_EXTERNAL_WORKSPACE.md`.

### Slice 34 — protected organism action authority

One registered action dispatch runs under a narrow SQLite authorizer. Water may update only moisture, water units, and environment step. Harvest may update only fruit, harvested fruit, and environment step. Protected identity, versions, budgets, registry, inbox, history, schema, triggers, source, contract, ADRs, and administrative artifacts remain exact.

See `docs/phase1/SLICE34_PROTECTED_AUTHORITY.md`.

### Slice 35 — authority provenance

- exact Phase 1 authority namespaces are `organism:` and `administration:`
- empty, unknown, malformed, or cross-category sources fail closed
- caller-supplied enqueue provenance validates before database ownership or clock use
- canonical lifecycle and administrative records remain operation-specific and classifiable
- every CLI report carries non-spoofable `authority_category` and `authority_source`
- read-only and intentionally event-free administration remains event-free while its public report identifies administrative provenance
- all fourteen current CLI paths have one protected source mapping

See `docs/phase1/SLICE35_AUTHORITY_PROVENANCE.md`.

## Independent completion-audit repairs — PR #57

PR #57 repairs the six findings from Issue #56 without changing Contract v0.2 or adding Phase 2 capability:

1. required protected table and trigger definitions, singleton cardinality, seed layout, action registry, and budget configuration are validated before active-state or checkpoint acceptance; unexpected mutating schema objects fail closed
2. one valid published pending checkpoint can be registered for genesis, ordinary lifecycle, or maintenance-bound failure-threshold state
3. normal registration and repaired registration share one retention policy that restores the protected limit even from an already-over-limit registry
4. administrative enqueue checks the active SQLite allocation before and after its writes and rolls the transaction back before crossing the protected limit
5. post-commit retention artifact cleanup failure records explicit maintenance and is recoverable through bounded reconciliation
6. ordinary checkpoint creation and repair use one no-symlink working-set accountant covering the active database, SQLite sidecars, checkpoint store and staging, rollback archives, and restore candidates

Eight adversarial tests protect these intersections. See `docs/phase1/PHASE1_INDEPENDENT_AUDIT_REPAIRS.md`.

## Accepted ADR 0007 retention boundary

Phase 1 permits at most one completed rollback per organism. The complete pre-rollback archive and candidate evidence set remains immutable and retained. There is no rollback-artifact deletion or pruning in Phase 1.

## Phase 1 completion review

The roadmap exit criteria remain satisfied:

- the canonical three-wake garden run waters, harvests, and abstains reproducibly
- all 41 fixed evaluations have complete protected coverage
- caregiver, network, subprocess, arbitrary-code, and authoritative external-write capability remain absent
- crashes before commit preserve prior canonical state
- every committed wake becomes checkpoint-stable before another wake
- rollback preserves the abandoned future and creates a distinct lineage generation

This establishes trustworthy metabolism only. It does not demonstrate learning, intelligence, personality, memory formation, skill acquisition, or caregiver independence.

## Validation state

The original completion baseline remains:

- PR #54 squash-merged as `1f46ea5817414dbaa11b5ac65039477bcaf10a42`
- GitHub Actions run 317: **142 protected tests in 7.25 seconds**
- GitHub Actions run 323: **142 protected tests in 7.95 seconds**

Independent audit repair validation on PR #57:

- run 332 compiled successfully and produced **144 passed / 5 failed**, exposing integration mismatches without weakening existing tests
- run 333 passed **149 tests in 9.97 seconds**
- run 334 passed 149 and failed one safe abort-guard classification test
- run 335 passed clean editable installation, source/test compilation, genesis CLI smoke, and **150 tests in 8.74 seconds** at head `4bb632a226dd8891fbd71aec345b1298777e3614`

PR #57 remains a draft until documentation is synchronized and Codex performs the requested read-only re-audit. Issue #13 remains open for this repair only.

## Exact next gate — independent re-audit before Phase 2

There is no authorized Slice 36 and no authorized Phase 2 implementation.

1. keep PR #57 green and documentation-complete
2. ask Codex to re-audit the latest PR #57 head against all six Issue #56 findings
3. require finding-by-finding evidence and a final conclusion in Issue #56
4. repair any verified remaining Phase 1 defect without changing the contract or adding Phase 2 behavior
5. merge PR #57 only after the re-audit is satisfactory
6. close Issue #13 and re-freeze the 150-test Phase 1 baseline
7. only then review Issue #3 and decide through an explicit reviewed issue or ADR whether Phase 2 caregiver-neutral consultation plumbing should begin
8. keep the Phase 1 caregiver budget at zero and preserve the no-caregiver baseline

Do not begin a human caregiver, model caregiver, live API integration, learning, memory, skill adoption, or generic agent framework without that reviewed Phase 2 scope decision.

## Restart protocol

At the next session or clean reconstruction point:

1. read `AGENTS.md`
2. read `docs/AI_COLLABORATION_OPERATIONS.md`
3. read this handoff and normative documents in order
4. inspect Issues #13 and #56 and PR #57
5. verify the latest PR #57 head and CI evidence rather than relying on chat history
6. stop at the independent re-audit gate until Issue #56 contains the new conclusion
7. after merge, verify the final `main` commit and CI before closing Issue #13
8. stop at the Phase 2 decision gate unless a newer reviewed repository decision authorizes implementation

No critical decision may remain only in chat history.
