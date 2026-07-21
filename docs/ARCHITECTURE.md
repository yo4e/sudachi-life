# SUDACHI Architecture

This document describes the intended architecture before implementation. It is deliberately conservative: the first organism should be understandable, bounded, and testable.

## Architectural thesis

SUDACHI is not a language model wrapped in a loop.

It is a small organism composed of state, memory, drives, budgets, skills, evaluators, and a lifecycle. A language model may serve as a parent or cognitive organ, but it should remain optional and explicitly accounted for.

## Proposed top-level structure

```text
sudachi-life/
├── AGENTS.md
├── README.md
├── docs/
├── src/sudachi_life/
│   ├── organism.py
│   ├── lifecycle.py
│   ├── state.py
│   ├── events.py
│   ├── budgets.py
│   ├── actions.py
│   ├── evaluation.py
│   ├── memory.py
│   ├── skills.py
│   ├── parent.py
│   └── sandbox.py
├── tests/
├── experiments/
├── runtime/             # ignored: mutable organism state
│   ├── state.db
│   ├── event-log.jsonl
│   ├── checkpoints/
│   └── workspaces/
└── pyproject.toml
```

The repository contains source, policy, tests, and developmental history. Mutable runtime state should remain separate and ignored by Git unless intentionally captured as an experiment artifact.

## Core components

### 1. Organism state

The smallest durable description of the current individual.

Candidate fields:

- organism ID
- developmental stage
- cycle number
- energy or run budget
- parent-consultation budget
- unresolved goals
- fatigue or failure count
- active skill versions
- current checkpoint
- last wake and sleep times
- random seed

State must be serializable, versioned, and validated before use.

### 2. Event stream

Events are observations, not conclusions.

Examples:

- a file appeared in an allowed directory
- a scheduled wake occurred
- a test passed or failed
- a skill invocation succeeded or failed
- a parent consultation returned advice
- a budget threshold was reached

Use an append-only event log. Consolidated knowledge belongs elsewhere.

### 3. Lifecycle controller

A lifecycle run should be finite.

```text
wake
  -> validate state
  -> collect one or more allowed observations
  -> select one bounded objective
  -> choose local skill, parent consultation, abstention, or sleep
  -> execute one action in a sandbox
  -> evaluate
  -> update state and logs
  -> checkpoint
  -> sleep and terminate
```

The controller enforces limits. No component may silently create an unbounded internal loop.

### 4. Budgets and metabolism

Budgets give actions consequences and prevent “autonomy” from meaning unlimited execution.

Initial budgets should include:

- maximum lifecycle steps
- wall-clock time
- parent-model calls
- tokens or model cost
- filesystem writes
- subprocess executions
- generated storage
- consecutive failures

The first implementation may use simple integer counters. Physical-energy metaphors must map to inspectable mechanics.

### 5. Action registry

Actions are the organism’s available motor repertoire.

Each action should declare:

- name and version
- input schema
- output schema
- preconditions
- permissions required
- budget cost
- deterministic or stochastic behavior
- timeout
- evaluator
- rollback behavior

Unknown free-form tool use should not be the default.

### 6. Skill registry

A skill is reusable, tested behavior acquired or refined through experience.

A proposed skill record should include:

- stable identifier
- purpose
- provenance: how and why it was created
- implementation
- tests
- preconditions and limits
- observed success/failure counts
- parent calls replaced
- last validation time
- status: proposed, active, deprecated, quarantined

Skills should be promoted only after evaluation. The organism may propose a skill, but should not unilaterally weaken the test required to adopt it.

### 7. Parent-model adapter

The parent is an external source of expensive general reasoning.

The adapter must expose usage rather than conceal it.

A consultation record should include:

- consultation ID
- reason for asking
- local attempts already made
- information supplied
- response summary or hash
- cost
- proposed action
- verification result
- whether the interaction later produced a reusable skill

Implement a deterministic mock before any live provider.

### 8. Memory system

Separate at least three layers:

- **episodic memory:** what happened in particular cycles
- **semantic memory:** consolidated facts and learned relations
- **procedural memory:** skills and routines

Do not feed all memory into every decision. Retrieval should be selective, inspectable, and budgeted.

### 9. Evaluator

The evaluator determines whether an action or proposed change improved the organism.

Protected evaluation should include:

- fixed regression tests
- task-specific outcome checks
- budget compliance
- state integrity
- permission compliance
- comparison with an earlier baseline

The organism may propose new tests. It must not delete or relax protected tests merely to pass.

### 10. Sandbox and permissions

Default posture:

- no network access
- no external writes
- repository-scoped read access
- writes only to designated runtime or proposal directories
- subprocess allowlist
- strict timeout
- resource limits where available

Source-code changes should begin as proposals or branches and pass tests before adoption.

## Decision policy

A minimal decision order could be:

1. Can a verified local skill handle this event?
2. Can a safe deterministic action handle it?
3. Is abstention or deferral acceptable?
4. Is the event important and novel enough to justify a parent call?
5. If the parent is unavailable, can the organism preserve itself and report uncertainty?

This order prevents the parent from becoming the invisible default.

## Maturity model

A simple initial maturity score should not collapse everything into one number. Track a vector instead:

- dependency: parent calls per successful action
- competence: success rate on fixed tasks
- autonomy: successful cycles without parent access
- efficiency: compute/storage per retained capability
- adaptability: transfer to controlled novel tasks
- resilience: recovery after injected failure
- honesty: correct abstention under uncertainty

A mature organism is not one that always acts. It is one that knows when local capability is insufficient without immediately becoming helpless.

## Protected versus mutable layers

### Protected

- constitutional safety boundaries
- fixed core evaluations
- permission policy
- budget enforcement
- provenance requirements
- rollback mechanisms

### Mutable through tested proposals

- skills
- retrieval strategies
- memory summaries
- action-selection heuristics
- internal self-description
- non-protected tests

This distinction is necessary to prevent Goodhart-style self-improvement, where the organism edits the measuring system instead of becoming better.

## Scheduling model

Prefer sleeping processes over permanent processes.

Possible wake triggers:

- explicit invocation
- scheduled interval
- queued event
- repository change
- experiment harness

Each wake creates a bounded run, persists state, and exits. Continuity comes from state and history, not from keeping one process alive forever.

## Minimal technical choices

Initial recommendation:

- Python 3.12+
- standard library where practical
- SQLite for state and indexed memory
- JSON Lines for append-only event records
- `pytest` for tests
- Git for source and developmental history
- no vector database in the seed phase
- no model fine-tuning in the seed phase

## First implementation target

The first executable SUDACHI should be deliberately unimpressive:

- wake from a CLI command
- read validated state
- receive one synthetic event
- choose among two or three deterministic actions
- spend a visible budget
- log the result
- checkpoint
- sleep

If that lifecycle is not trustworthy, adding an LLM will only make the failure more articulate.