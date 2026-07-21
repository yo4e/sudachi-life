# Implementation Discipline for SUDACHI

This document records implementation guardrails established before Phase 1 code begins.

Updated: **July 21, 2026**

## Core principle

> Design decisions live in `docs/decisions/` as ADRs, not hidden inside implementation code.

A future collaborator must be able to restart the project without chat history or model memory. Every architectural choice must be recoverable from repository state, accepted ADRs, tests, and current issues.

## 1. Freeze seed architecture before writing code

Issue #1 must resolve six ADRs before `src/` is created:

1. **ADR 0001 — State and event storage**  
   Decide the canonical store, append-only history, export role, and replay boundary.
2. **ADR 0002 — Clock and determinism**  
   Define operational time, injected test time, timestamps, and deterministic ordering.
3. **ADR 0003 — Runtime locking**  
   Define how duplicate simultaneous wakes are rejected and stale locks are handled.
4. **ADR 0004 — Checkpoints and rollback**  
   Define representation, granularity, atomicity, validation, and recovery.
5. **ADR 0005 — Seed environment**  
   Define the first deterministic environment, observations, actions, and objective.
6. **ADR 0006 — Budget metaphor**  
   Decide whether energy is independent state or only a presentation of concrete budgets.

These decisions interact. Later ADRs may expose a contradiction in an earlier one; revise the ADR explicitly rather than compensating silently in code.

### Exit criteria for Issue #1

- [ ] ADRs 0001–0006 exist and are accepted
- [ ] Minimal Organism Contract v0.1 is reviewed for contradictions
- [ ] protected and mutable boundaries are confirmed
- [ ] fixed Phase 1 evaluations are confirmed
- [ ] `docs/HANDOFF.md` is updated
- [ ] no implementation decision remains only in conversation context
- [ ] no Phase 1 implementation code has been written prematurely

Only then create `pyproject.toml`, `src/sudachi_life/`, and `tests/`.

## 2. Keep Issue #3 research separate from Phase 1 mechanics

Phase 1 does not need:

- a live human caregiver
- a live model caregiver
- final caregiver selection
- a completed literature review
- a completed model-provider review
- a chat interface
- learning or skill adoption

Phase 1 does need:

- a deterministic bounded lifecycle
- local network-free execution
- canonical state and append-only event history
- explicit budgets
- registered actions and sandbox boundaries
- evaluation and rollback
- fixed tests

Research may proceed in parallel, but it must not leak unresolved caregiver semantics into Phase 1 code.

## 3. Treat the contract as an executable boundary

`docs/MINIMAL_ORGANISM_CONTRACT.md` is not decorative prose. The contract must eventually map to explicit schemas, validation, tests, and failure behavior.

Do not prescribe a class hierarchy before the ADRs settle the state and event boundaries. The implementation may use functions, dataclasses, protocols, or classes, but it must provide testable validation for:

- organism state
- events and event ordering
- registered actions and parameters
- budget consumption
- protected regions
- lifecycle outcomes
- checkpoints and recovery

A validation path must not be bypassed by a caregiver response, generated artifact, helper function, or error handler.

## 4. Protect the Phase 1 minimalism boundary

The intended lifecycle is:

```text
wake
  -> acquire lock
  -> load and validate state
  -> read a bounded set of events
  -> choose at most one registered action
  -> execute within declared budgets
  -> evaluate
  -> persist atomically
  -> checkpoint or confirm stability
  -> release lock
  -> sleep and exit
```

Phase 1 must not include:

- continuous or unbounded execution
- unrestricted retries
- multiple hidden action loops
- source-code self-modification
- arbitrary generated shell commands or code execution
- caregiver consultation
- unrestricted internet or filesystem access
- complex planning or backtracking
- personality, affection, or virtual-pet presentation as a substitute for mechanics

The hardest discipline is often not adding an attractive feature before its experimental role is defined.

## 5. Protect the fixed Phase 1 evaluations

The authoritative evaluation list is the current contract, not the illustrative function names in this document. Tests should cover at least:

- identical seed, state, event, clock, and configuration produce identical results
- step and timeout limits cannot be exceeded
- actions cannot write outside allowed paths
- failures do not silently corrupt durable state
- event history is append-only
- budgets never become negative
- protected configuration cannot be modified by an action
- rollback restores the latest stable checkpoint
- duplicate simultaneous waking is rejected
- abstention and budget exhaustion are explicitly recorded
- no network or caregiver is required

These evaluations remain protected until the contract is revised through an explicit reviewed change. Do not weaken a test because the implementation cannot satisfy it.

## 6. Keep documents, decisions, and code in their proper roles

### `docs/HANDOFF.md`

Records:

- current state
- active issue map
- accepted decisions and clearly labeled working directions
- one exact next action
- current research boundaries

### `docs/decisions/000N-*.md`

Records:

- context
- decision
- alternatives considered
- consequences and risks
- compatibility with the contract and other ADRs

### Concept documents

`README.md`, `ORIGIN.md`, `ROADMAP.md`, and `ARCHITECTURE.md` explain what SUDACHI is and why it exists. They must not silently override accepted ADRs.

### Code comments

Explain local non-obvious reasoning. Do not duplicate an ADR or use comments to introduce an undocumented architectural decision.

## 7. Keep recommendations distinct from accepted decisions

ADR 0006 has not yet decided the energy model.

The current recommendation is to expose concrete budgets first, such as:

- steps
- wall time
- writes
- subprocess calls
- generated bytes
- consecutive failures
- caregiver consultations, fixed at zero in Phase 1

This is a recommendation, not an accepted schema. Do not copy an illustrative dataclass into code before the ADR is accepted.

Future phases may introduce drives such as curiosity, fatigue, urgency, or homeostatic variables if they add explanatory or experimental value. Do not hide concrete limits behind a mystery energy number during the seed phase.

## 8. Keep caregiver input outside organism authority

A future caregiver may be human, deterministic, model-based, or hybrid. Regardless of source, a response is a proposal.

A caregiver must not directly:

- execute an organism action
- mutate durable organism state
- modify protected files or evaluation
- raise budgets
- erase history
- adopt a skill
- bypass the sandbox
- authorize model training or distillation

Consultation, interpretation, evaluation, and adoption are separate recorded stages.

## 9. Apply the Tamagotchi test structurally

SUDACHI has failed its central research claim if later phases add:

- a cute interface
- simulated hunger, fatigue, affection, or mood
- growing chat history
- personality quirks
- branching developmental presentation

without demonstrating retained caregiver-independent competence.

Before treating a feature as development, identify:

1. the capability that previously required caregiver help
2. the recorded scaffolding supplied
3. the verified local artifact or policy change produced
4. the protected evaluation retained after assistance is reduced
5. the reduction in caregiver burden
6. the added storage, computation, retries, complexity, and experimenter labor

A feature that cannot answer those questions may still be useful presentation, but it is not evidence of maturation.

## 10. Restart checklist

Before ending substantial work:

- [ ] accepted decisions and open questions are recorded in ADRs or issues
- [ ] `docs/HANDOFF.md` reflects the true current state
- [ ] the relevant issue checklist and status are current
- [ ] `AGENTS.md` points to the correct files and active work streams
- [ ] repository content follows the language policy
- [ ] one exact resume point is documented
- [ ] no critical decision exists only in chat, model memory, or an uncommitted note
- [ ] research claims include appropriate sources and verification dates
- [ ] failures, uncertainty, and unfinished work are reported plainly

This is how the project remains restartable after a long gap.

## 11. When research changes design

When Issue #3 surfaces:

- a precedent that weakens a novelty candidate — update the research notes and handoff
- a provider constraint — update `PARENT_MODEL_PROVIDER_REVIEW.md`
- a caregiver-protocol requirement — record it in Issue #3 or a dedicated future ADR
- a Phase 1 design implication — record it in Issue #1 before implementation

Do not silently change architecture because a new paper or product term was found.

## See also

- `AGENTS.md` — cold-start instructions
- `docs/HANDOFF.md` — authoritative current state and restart point
- `docs/MINIMAL_ORGANISM_CONTRACT.md` — draft executable contract
- `docs/RESEARCH_QUESTIONS.md` — active research plan
- `docs/decisions/` — accepted architecture decisions once created

**End state:** A collaborator arriving months later can read the repository, inspect current issues, and continue without access to the conversations that created it.
