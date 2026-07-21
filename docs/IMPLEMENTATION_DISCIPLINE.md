# Implementation Discipline for SUDACHI

This document records implementation guardrails for Phase 1.

Updated: **July 21, 2026**

## Core principle

> Implement Minimal Organism Contract v0.2 and ADRs 0001–0006. Do not hide a new architecture inside code.

A future collaborator must be able to restart the project without chat history or model memory. Every invariant, exception, and change of direction belongs in repository state.

## 1. Phase 0 is frozen

The seed architecture decisions are accepted:

1. SQLite is the sole canonical live store.
2. Time is injected; event sequence defines order.
3. `BEGIN IMMEDIATE` is the fail-fast wake lock.
4. Every committed wake requires a verified stable checkpoint before another wake.
5. Phase 1 uses `seed-garden-v1`.
6. Concrete budgets replace scalar energy.

Contract v0.2 reconciles those decisions and defines 41 protected evaluations.

Implementation may choose ordinary local structure such as module names, private helpers, and equivalent typed abstractions. It may not privately change canonical authority, time, locking, checkpoint lineage, garden transitions, budget values, protected authority, or fixed evaluations.

When implementation reveals a contradiction, stop and update the contract or ADR through review.

## 2. Start test-first from the protected boundary

Create the package skeleton only after the Contract v0.2 reconciliation pull request is merged.

The first implementation slice should include:

- `pyproject.toml`
- `src/sudachi_life/`
- `tests/`
- contract and schema validation tests
- SQLite initialization tests
- real and fake clock tests
- genesis checkpoint tests
- minimal `init` and `status` commands

Do not begin by filling every future module or by creating a generic framework.

The full test suite must eventually map each of the 41 fixed Contract v0.2 evaluations to one or more protected tests. Maintain a visible mapping so no requirement becomes an untested paragraph.

Do not weaken a protected test because implementation is difficult.

## 3. Keep research separate from Phase 1 mechanics

Phase 1 does not need:

- a live human caregiver
- a deterministic fixture caregiver in action selection
- a model caregiver
- a chat interface
- final novelty claims
- a completed literature review
- memories, skills, learning, consolidation, or fading

Phase 1 does need:

- one canonical SQLite organism
- injected time
- fail-fast wake locking
- explicit budgets
- deterministic garden actions
- protected evaluation
- checkpoints, repair, retention, and rollback
- fixed tests

Issue #3 research may proceed in parallel, but unresolved caregiver semantics must not enter Phase 1 code.

## 4. Treat the contract as executable

`docs/MINIMAL_ORGANISM_CONTRACT.md` is an accepted specification.

Implementation must provide testable validation for:

- identity and version fields
- durable status transitions
- canonical SQLite schema
- inbox and append-only event history
- clock readings and deterministic inputs
- concrete budget configuration and ledgers
- registered actions and garden transitions
- checkpoint manifests, validation, and lineage
- protected, mutable, and administrative authority
- typed outcomes and terminal states

Validation paths cannot be bypassed by helpers, error handlers, administration, future caregiver responses, or generated artifacts.

## 5. Protect the Phase 1 lifecycle

The required lifecycle is:

```text
wake
  -> acquire fail-fast SQLite write transaction
  -> validate state and checkpoint readiness
  -> load protected budgets
  -> claim one garden tick
  -> build one sorted observation
  -> choose water, harvest, or abstention
  -> validate and reserve budgets
  -> execute recoverable action inside a savepoint
  -> independently evaluate
  -> append outcome, events, and usage ledger
  -> mark checkpoint pending and commit
  -> create and validate immutable checkpoint
  -> register checkpoint stable
  -> sleep or enter maintenance
  -> terminate
```

The normal wake has twelve counted semantic steps. Internal code may combine functions but may not hide retries, loops, or additional actions inside one step.

Phase 1 must not include:

- continuous execution
- unrestricted retries
- source-code self-modification
- arbitrary generated code or shell commands
- caregiver consultation
- network or subprocess access
- authoritative mutable files outside SQLite
- complex planning or backtracking
- personality, affection, mood, or virtual-pet presentation

## 6. Keep one canonical body

SQLite is authoritative for state, input claim, garden state, budgets, outcomes, events, maintenance, and checkpoint registration.

JSONL and status views are reproducible exports.

Never introduce a second canonical file because it is easier to inspect. A lifecycle may not dual-write canonical SQLite and canonical JSONL.

All state-changing lifecycle operations use the existing outer transaction context. Helpers do not open hidden write connections.

## 7. Use explicit time and concurrency

Runtime code reads time only through the injected clock adapter.

Tests use explicit fake-clock readings and fail on unexpected reads. Do not patch global clocks as the primary design.

Locking tests use real competing SQLite connections or subprocesses. Do not replace database locking with mocks.

A busy wake is rejected and not queued. Do not add automatic wait-and-run behavior.

## 8. Use concrete budgets and preserve terminal capacity

Phase 1 has no scalar energy.

Keep distinct:

- per-wake decision counters
- lifecycle time and record limits
- persistent storage and failure thresholds
- checkpoint maintenance cost

Check and reserve budgets before mutation. Use a savepoint for recoverable action execution so partial mutation disappears while attempt cost and failure history remain.

Never use protected cleanup grace or terminal record slots for more organism work.

Hard-zero caregiver, network, subprocess, and external mutable-write capabilities must be absent or fail before effect. Do not perform those effects inside “infrastructure.”

## 9. Checkpoint every committed wake

Initialization and every committed wake create one exact pending checkpoint boundary.

No later wake may advance until the boundary is stable.

Checkpoint implementation must:

- use SQLite's backup interface
- create a unique temporary same-filesystem artifact
- close before hashing
- validate integrity, foreign keys, identity, versions, lineage, and event boundary
- publish atomically
- register stability in a short transaction
- preserve pending state on failure

Rollback is offline administration. It creates a pre-rollback archive and a new lineage generation. Never overwrite the immutable source checkpoint or silently discard the abandoned future.

## 10. Keep authority categories distinct

### Organism runtime

May change only the mutable fields listed in Contract v0.2 through validated transactions.

### Administration

May initialize, enqueue input, inspect, repair checkpoints, prune eligible artifacts, enter maintenance, roll back, quarantine, migrate, and export.

Administrative work is not organism autonomy and must be distinguishable in records and reports.

### Repository change

Required for source, action definitions, evaluators, protected defaults, environment version, contract, schema migrations, and new capabilities.

### Future caregiver

Provides proposals only. It cannot execute actions, mutate state, weaken tests, raise budgets, erase history, or adopt skills directly.

## 11. Apply the Tamagotchi test structurally

SUDACHI fails its central claim if later phases add simulated needs, affection, personality, chat history, or branching presentation without retained caregiver-independent competence.

Before treating a feature as development, identify:

1. the capability that previously required caregiver help
2. recorded scaffolding
3. the verified local artifact or policy change
4. protected evaluation after assistance is reduced
5. reduced caregiver burden
6. added storage, compute, retries, complexity, and human labor

A feature may be useful presentation without being evidence of maturation. Label it honestly.

## 12. Keep documentation roles clear

### Contract

Defines normative Phase 1 invariants and fixed evaluations.

### ADRs

Preserve context, decisions, alternatives, consequences, and follow-up constraints.

### `docs/HANDOFF.md`

Records true current state, issue roles, accepted decisions, failures, and one exact next action.

### Architecture and roadmap

Explain structure and developmental sequence. They do not override the contract.

### Code comments

Explain local non-obvious reasoning. They do not introduce architecture.

## 13. Restart checklist

Before ending substantial work:

- [ ] contract and ADR assumptions still match implementation
- [ ] protected test mapping is current
- [ ] relevant tests were run and results reported
- [ ] failures and skipped checks are reported plainly
- [ ] `docs/HANDOFF.md` reflects the true state and exact next action
- [ ] issue and pull-request status is current
- [ ] `AGENTS.md` points to the correct work streams
- [ ] repository content follows the language policy
- [ ] no critical decision exists only in chat, model memory, or an uncommitted note
- [ ] research claims include sources and verification dates

This is how the project remains restartable after a long gap.

## 14. When research or implementation changes design

- A precedent that weakens novelty updates the research notes and handoff.
- A provider constraint updates the provider review.
- A caregiver-protocol requirement belongs in Issue #3 or a future ADR.
- A Phase 1 contradiction requires a contract or ADR change before code proceeds.
- A measured performance limitation may justify a versioned budget or checkpoint amendment, not silent drift.

## See also

- `AGENTS.md`
- `docs/MINIMAL_ORGANISM_CONTRACT.md`
- `docs/decisions/`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/HANDOFF.md`

**End state:** A collaborator arriving months later can read the repository, run protected tests, inspect current issues, and continue without the conversations that created it.
