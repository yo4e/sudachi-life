# SUDACHI Project Handoff

Last updated: July 21, 2026

## Current state

The repository now contains the founding concept, origin record, roadmap, initial architecture, the first draft of the Minimal Organism Contract v0.1, a deferred prior-work research plan, and a provider/compliance review backlog for any future live parent model.

No implementation code exists yet. This is intentional. The next step is to close the remaining architectural decisions with short decision records, then implement the Python skeleton for SUDACHI-0.

## Decisions already made

- Project name: **SUDACHI**
- Repository: `yo4e/sudachi-life`
- First organism: provisional name **SUDACHI-0**
- Primary objective: convert parent-model assistance into memory, tested skills, and deterministic local behavior so that dependency decreases with development
- Initial technical candidates: Python, SQLite, JSONL exports, Git, and pytest
- Runtime model: execute one bounded lifecycle and terminate; do not begin with an unbounded resident loop
- Initial environment: local execution with no network access
- Phase 1 will not call a parent model
- A deterministic mocked parent may later be used to verify the parent-adapter pathway
- The repository is both body and developmental history
- The LLM is an organ or parent, not the whole organism
- Maturity means increasing retained capability and autonomous duration without increasing dependence
- SUDACHI-0 will not initially be allowed to rewrite its own source code
- Repository language: English, except for the two Japanese etymology lines intentionally preserved in `README.md`
- Prior-work research is recorded but intentionally deferred; it does not block deterministic Phase 1
- No live commercial parent may be connected until current provider terms, product boundaries, automation rules, data practices, output-use rules, and operational constraints have been reviewed

## Reading order when resuming

1. `README.md`
2. `docs/ORIGIN.md`
3. `docs/MINIMAL_ORGANISM_CONTRACT.md`
4. `docs/ROADMAP.md`
5. `docs/ARCHITECTURE.md`
6. `docs/RESEARCH_QUESTIONS.md`
7. `docs/PARENT_MODEL_PROVIDER_REVIEW.md`
8. `AGENTS.md`
9. this file

## Next concrete task

**Resolve the open decisions in Minimal Organism Contract v0.1.**

Create `docs/decisions/` and record at least these ADRs:

1. `0001-state-and-event-storage.md`
   - SQLite only, or SQLite as canonical state plus JSONL exports
2. `0002-clock-and-determinism.md`
   - real time in production and an injectable clock interface in tests
3. `0003-runtime-locking.md`
   - how to prevent two simultaneous wakes of the same organism
4. `0004-checkpoints.md`
   - checkpoint representation and rollback granularity
5. `0005-seed-environment.md`
   - the first synthetic environment and objective
6. `0006-budget-metaphor.md`
   - whether energy is an independent state variable or only a readable view of concrete budgets

Current recommendations:

- canonical durable state: SQLite
- event history: append-only SQLite table; JSONL only as an observation and experiment export
- clock: real clock in operation, injected fake clock in tests
- locking: begin by evaluating a SQLite transaction plus a runtime lock record
- checkpoint: SQLite backup or state snapshot plus event offset
- seed environment: a tiny deterministic virtual garden with a few objects, events, and measurable action outcomes
- energy: initially present concrete budgets directly instead of introducing a mysterious independent variable

After the ADRs are accepted, create `pyproject.toml`, `src/sudachi_life/`, and `tests/`.

## Deferred research reviews

The prior-work questions and search plan are recorded in `docs/RESEARCH_QUESTIONS.md` and tracked by Issue #3.

Do not claim novelty yet. The future literature review should map artificial life, developmental AI, teacher-student withdrawal, distillation, agent skill compilation, continual learning, memory consolidation and forgetting, resource-rational intelligence, safe self-improvement, and identity or lineage in digital organisms.

The separate provider and compliance checklist is recorded in `docs/PARENT_MODEL_PROVIDER_REVIEW.md`. Before connecting ChatGPT, an OpenAI API model, or any other live commercial parent, verify:

- the distinction between an interactive product and an official programmatic API
- current terms and usage policies
- automation and unattended-call rules
- whether outputs may be transformed into skills, code, memory, distillation data, or training data
- data retention, privacy, and deletion controls
- credentials, costs, rate limits, reliability, and provider-independent fallback behavior

Begin both reviews before connecting a live parent model or publishing strong originality or provider-permission claims. They do not block the Phase 0 ADRs or deterministic Phase 1 implementation.

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
  -> validate state
  -> read one synthetic event
  -> choose one deterministic action
  -> consume bounded resources
  -> evaluate the outcome
  -> persist state and append the event record
  -> create a checkpoint
  -> sleep and terminate the process
```

Do not call a parent model yet.

## Initial fixed tests

Treat the Phase 1 evaluations in `docs/MINIMAL_ORGANISM_CONTRACT.md` as authoritative. Core checks include:

- identical seed, state, event, and configuration produce identical results
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

## To the next AI collaborator

Do not flatten this project into a generic autonomous-agent framework.

The center is development, not task completion.

Knowledge borrowed from the parent should settle into the body. The organism should gradually do more without asking, consolidate memory and skills, and carry itself into another day within finite resources. Making that process observable is the core of SUDACHI.

The Minimal Organism Contract has a first draft. Close its open decisions with ADRs before implementing the minimal CLI and first lifecycle.

Do not connect a named live provider merely because an adapter can be written. Verify permission and operational constraints first.

Do not make it large merely because expansion is easy.

**As it becomes smarter, it should become smaller and quieter.**