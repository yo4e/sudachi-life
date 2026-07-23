# SUDACHI Handoff

Updated: **2026-07-24**

This is the operational restart point for repository state containing Phase 1 Slices 1–35 and accepted ADRs 0001–0007. Read `AGENTS.md` first, then the normative contract and ADRs before changing implementation.

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

Slices 1–35 implement all 41 fixed Minimal Organism Contract v0.2 evaluations. After PR #54 is merged and current `main` is reverified, Issue #13 is complete and should remain closed unless a Phase 1 regression is found.

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

## Accepted ADR 0007 retention boundary

Phase 1 permits at most one completed rollback per organism. The complete pre-rollback archive and candidate evidence set remains immutable and retained. There is no rollback-artifact deletion or pruning in Phase 1.

## Phase 1 completion review

The roadmap exit criteria are satisfied:

- the canonical three-wake garden run waters, harvests, and abstains reproducibly
- all 41 fixed evaluations have complete protected coverage
- caregiver, network, subprocess, arbitrary-code, and authoritative external-write capability remain absent
- crashes before commit preserve prior canonical state
- every committed wake becomes checkpoint-stable before another wake
- rollback preserves the abandoned future and creates a distinct lineage generation

This establishes trustworthy metabolism only. It does not demonstrate learning, intelligence, personality, memory formation, skill acquisition, or caregiver independence.

## Validation state

PR #54 closes evaluation 41 and the fixed Phase 1 matrix.

GitHub Actions run 313 failed four existing exact CLI JSON assertions because Slice 35 intentionally added authority provenance fields. All other protected tests passed. The four assertions were strengthened rather than weakened.

GitHub Actions run 317 then passed on Python 3.12:

- clean editable installation
- source and test compilation
- genesis CLI smoke
- **142 protected tests in 7.25 seconds**

A final synchronized documentation head must also pass before merge.

## Exact next gate — no automatic Phase 2 implementation

There is no authorized Slice 36.

After reconstructing current `main`, Issue #13, and open pull requests:

1. verify PR #54 is merged and Issue #13 is closed as completed
2. verify `docs/PHASE1_TEST_MATRIX.md` still reports all 41 evaluations complete
3. preserve the 142-test Phase 1 baseline as a regression suite
4. review Issue #3 and current research documents
5. decide through an explicit reviewed issue or ADR whether Phase 2 caregiver-neutral consultation plumbing should begin
6. define Phase 2 schemas, budgets, provenance, adoption boundaries, and comparison conditions before implementation
7. keep the Phase 1 caregiver budget at zero and preserve the no-caregiver baseline

Do not begin a human caregiver, model caregiver, live API integration, learning, memory, skill adoption, or generic agent framework without that reviewed Phase 2 scope decision.

## Restart protocol

At the next session or clean reconstruction point:

1. read `AGENTS.md`
2. read `docs/AI_COLLABORATION_OPERATIONS.md`
3. read this handoff and normative documents in order
4. inspect current open issues and pull requests
5. verify PR #54 merge, Issue #13 closure, and the final Phase 1 CI evidence
6. stop at the Phase 2 decision gate unless a newer reviewed repository decision authorizes implementation

No critical decision may remain only in chat history.
