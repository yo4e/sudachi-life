# SUDACHI Project Handoff

Last updated: July 21, 2026

## Cold-start summary

SUDACHI is a developmental artificial-life experiment whose central question is whether an artificial organism can become **less dependent on a capable parent model as it becomes more capable**.

A young organism may eventually consult a parent model when local capability is insufficient. Successful assistance should be converted into verified memory, tested skills, and deterministic local behavior so that dependency decreases with development.

The repository is treated as the organism's body, developmental record, skill substrate, and auditable lineage. The language model is an organ or parent, not the whole organism.

## Current state

The repository contains:

- the founding concept and origin record
- a phased roadmap
- a conservative architecture proposal
- Minimal Organism Contract v0.1 as a draft
- continuity instructions for future AI collaborators
- implementation discipline and guardrails
- a deferred prior-work and novelty research plan
- a deferred provider and compliance checklist for any future live parent model

No implementation code exists yet. This is intentional.

The project is paused at the boundary between design and implementation. The next task is to resolve six seed architecture decisions as ADRs, review the contract for contradictions, and only then build the Python package skeleton and first deterministic lifecycle.

## Decisions already made

- Project name: **SUDACHI**
- Repository: `yo4e/sudachi-life`
- First organism: provisional name **SUDACHI-0**
- Primary objective: convert parent-model assistance into memory, tested skills, and deterministic local behavior so that dependency decreases with development
- Initial technical candidates: Python, SQLite, JSONL exports, Git, and pytest
- Runtime model: execute one bounded lifecycle and terminate; do not begin with an unbounded resident loop
- Initial environment: local execution with no network access
- Phase 1 will not call a parent model
- A deterministic mocked parent may later verify the parent-adapter pathway
- The repository is both body and developmental history
- The LLM is an organ or parent, not the whole organism
- Maturity means increasing retained capability and autonomous duration without increasing dependence
- SUDACHI-0 will not initially rewrite its own source code
- Repository language is English, except for the two Japanese etymology lines intentionally preserved in `README.md`
- Prior-work research is recorded but intentionally deferred; it does not block deterministic Phase 1
- **The caregiver/parent concept is provider-neutral:** can be human, model, hybrid, or fixture; human caregiver is the leading candidate for first live experiment
- No live commercial parent may be connected until current provider terms, product boundaries, automation rules, data practices, output-use rules, and operational constraints have been reviewed
- Candidate novelty claims are hypotheses only until the prior-work review is complete

## Reading order when resuming

Read all of these before proposing implementation:

1. `README.md`
2. `docs/ORIGIN.md`
3. `docs/MINIMAL_ORGANISM_CONTRACT.md`
4. `docs/ROADMAP.md`
5. `docs/ARCHITECTURE.md`
6. `docs/RESEARCH_QUESTIONS.md`
7. `docs/PARENT_MODEL_PROVIDER_REVIEW.md`
8. `docs/IMPLEMENTATION_DISCIPLINE.md` ← implementation guardrails and session protocol
9. `AGENTS.md`
10. this file

Then inspect current GitHub issues. Do not rely on remembered issue state.

## Issue map at handoff

- **Issue #1 — open and active:** Phase 0 architecture decisions and ADRs. This is the next work stream.
- **Issue #2 — closed:** Copilot architecture review record. Its accepted recommendations were folded into the plan; it does not create a separate implementation stream.
- **Issue #3 — open but deferred:** literature, novelty, caregiver design, and parent-provider compliance research. Research may proceed in parallel with Phase 1; complete it before live caregiver integration or strong novelty claims.
- **Issue #4 — closed and irrelevant:** accidental placeholder created during repository setup.

If this map differs from current GitHub state, trust current GitHub state and update this file.

## Exact next task

Resume with Issue #1.

Create `docs/decisions/` and record:

1. `0001-state-and-event-storage.md`
   - SQLite only, or SQLite as canonical state plus JSONL exports
2. `0002-clock-and-determinism.md`
   - real time in operation and an injectable clock interface in tests
3. `0003-runtime-locking.md`
   - how to prevent two simultaneous wakes of the same organism
4. `0004-checkpoints.md`
   - checkpoint representation, rollback granularity, and cross-resource atomicity
5. `0005-seed-environment.md`
   - the first synthetic environment and objective
6. `0006-budget-metaphor.md`
   - whether energy is an independent state variable or a readable view of concrete budgets

Current recommendations, not yet accepted ADRs:

- canonical durable state: SQLite
- event history: append-only SQLite table; JSONL only as an observation and experiment export
- clock: real clock in operation, injected fake clock in tests
- locking: begin by evaluating a SQLite transaction plus a runtime lock record
- checkpoint: SQLite backup or state snapshot plus event offset
- seed environment: a tiny deterministic virtual garden with a few objects, events, and measurable action outcomes
- energy: initially present concrete budgets directly instead of introducing a mysterious independent variable

After the ADRs are accepted:

1. review Minimal Organism Contract v0.1 for contradictions
2. confirm protected and mutable boundaries
3. confirm fixed Phase 1 evaluations
4. update this handoff
5. create `pyproject.toml`, `src/sudachi_life/`, and `tests/`

Do not resolve these choices silently inside implementation code.

## First implementation target

Possible minimal CLI:

```text
sudachi init
sudachi enqueue synthetic:file_changed
sudachi wake --seed 1
sudachi status
```

First lifecycle:

```text
wake
  -> acquire the organism lock
  -> validate state
  -> read one synthetic event
  -> choose one deterministic action
  -> consume bounded resources
  -> evaluate the outcome
  -> persist state and append event history atomically
  -> create or confirm a checkpoint
  -> sleep, release the lock, and terminate
```

Do not call a parent model yet.

## Initial fixed tests

Treat the Phase 1 evaluations in `docs/MINIMAL_ORGANISM_CONTRACT.md` as authoritative. Core checks include:

- identical seed, state, event, clock, and configuration produce identical results
- step and timeout limits cannot be exceeded
- actions cannot write outside allowed paths
- failures do not corrupt durable state
- event history is append-only
- budgets never become negative
- protected configuration cannot be modified by an action
- rollback restores the latest stable checkpoint
- duplicate simultaneous waking is rejected
- abstention and budget exhaustion are explicitly recorded
- no network or parent model is required

## Deferred reviews

### Caregiver design and prior work

`docs/RESEARCH_QUESTIONS.md`, tracked by Issue #3, records future research across artificial life, developmental AI, caregiver-supported learning, distillation, skill compilation, continual learning, and related systems.

Issue #3 research may proceed in parallel with Phase 1 implementation. It does not block the deterministic, caregiver-free Phase 1 organism.

Do not claim that SUDACHI is unprecedented until this review is complete. Its likely contribution may be a distinctive integration and experimental framing rather than wholly unprecedented components.

The caregiver concept has been broadened to include human, model, hybrid, and fixture caregivers. The human caregiver is the leading candidate for the first live developmental experiment.

### Parent-model provider and compliance

`docs/PARENT_MODEL_PROVIDER_REVIEW.md`, also tracked by Issue #3, must be completed before connecting ChatGPT, an OpenAI API model, or another live commercial parent.

The review must distinguish an interactive product from an official programmatic API and verify:

- current terms and usage policies
- automation and unattended-call rules
- whether outputs may become skills, code, memory, distillation data, or training data
- data retention, privacy, deletion, and publication controls
- credentials, costs, rate limits, quotas, reliability, and fallback behavior
- attribution, disclosure, provenance, and branding requirements
- provider-independent and no-parent baselines

A dated ADR must select the first live provider. Do not treat ChatGPT and the OpenAI API as interchangeable.

Neither deferred review blocks Phase 0 ADRs, the deterministic Phase 1 lifecycle, mocked-parent plumbing, provider-neutral interfaces, or local invariant tests.

## Do not implement yet

- unrestricted internet exploration
- continuous always-on execution
- unrestricted self-modification
- LoRA training after every experience
- a large vector database
- a multi-agent society
- a physical robot body
- replication outside the repository
- personality performance before the life mechanisms exist
- a live named parent provider

## Central research metrics

Do not reduce the project to one intelligence score. Observe changes in:

- parent calls per successful action
- reusable behaviors acquired per parent call
- successful autonomous duration without parent access
- skill reuse rate
- transfer to unfamiliar tasks through composition of existing skills
- recovery rate after failure
- storage and inference cost per retained capability
- correct abstention under uncertainty

## End-of-session protocol

Before ending any substantial future work session, follow the restart checklist in `docs/IMPLEMENTATION_DISCIPLINE.md § 8`:

1. update accepted ADRs and affected documentation
2. update the relevant issue checklist and status
3. update this file with the true current state and one exact next action
4. ensure `AGENTS.md` still points to the correct files and issue roles
5. leave no required decision only in chat, model memory, or an uncommitted local note
6. record any newly deferred research or compliance question in the repository

The next collaborator should be able to resume from a cold start without access to the conversation that created the project.

## To the next AI collaborator

Do not flatten this project into a generic autonomous-agent framework.

The center is development, not task completion.

Knowledge borrowed from the parent should settle into the body. The organism should gradually do more without asking, consolidate memory and skills, and carry itself into another day within finite resources.

Do not connect a named live provider merely because an adapter can be written. Verify permission and operational constraints first.

Do not make it large merely because expansion is easy.

**As it becomes smarter, it should become smaller and quieter.**
