# SUDACHI Architecture

Status: **Phase 1 baseline aligned with Minimal Organism Contract v0.2**

This document describes the implementation architecture accepted for the first organism. The normative sources are:

1. `docs/MINIMAL_ORGANISM_CONTRACT.md`
2. accepted ADRs in `docs/decisions/`
3. protected Phase 1 tests

This document explains structure. It does not override those sources.

## Architectural thesis

SUDACHI is not a language model wrapped in a loop and is not a virtual pet whose growth is only presentation.

It is a bounded persistent organism composed of:

- one canonical body in SQLite
- an append-only developmental history
- explicit concrete budgets
- a deterministic environment and action repertoire
- protected evaluation
- verified checkpoints and rollback lineage
- a finite wake–act–evaluate–persist–checkpoint–sleep lifecycle

A future caregiver may be human, deterministic, model-based, hybrid, or absent. No caregiver exists in the Phase 1 runtime.

## Phase 1 authority model

### Canonical authority

One SQLite database per organism is the sole canonical live store.

It owns:

- organism identity and lineage generation
- contract, schema, environment, and budget versions
- mutable lifecycle status
- input queue state
- seed-garden state and inventory
- concrete budget ledgers
- append-only events and outcomes
- checkpoint registration and maintenance state

### Non-canonical artifacts

The following may be derived or maintained but are not live organism authority:

- JSONL exports
- rendered status views
- diagnostic logs
- immutable checkpoint copies and manifests
- Git history
- experiment reports

Git records source and developmental decisions. It is not the runtime transaction engine.

## Proposed repository structure

```text
sudachi-life/
├── AGENTS.md
├── README.md
├── pyproject.toml
├── docs/
│   ├── MINIMAL_ORGANISM_CONTRACT.md
│   ├── ARCHITECTURE.md
│   ├── ROADMAP.md
│   ├── HANDOFF.md
│   └── decisions/
│       ├── 0001-state-and-event-storage.md
│       ├── 0002-clock-and-determinism.md
│       ├── 0003-runtime-locking.md
│       ├── 0004-checkpoints.md
│       ├── 0005-seed-environment.md
│       └── 0006-budget-metaphor.md
├── src/sudachi_life/
│   ├── __init__.py
│   ├── cli.py
│   ├── lifecycle.py
│   ├── storage.py
│   ├── schema.py
│   ├── clock.py
│   ├── budgets.py
│   ├── events.py
│   ├── garden.py
│   ├── actions.py
│   ├── evaluation.py
│   ├── checkpoints.py
│   └── errors.py
├── tests/
│   ├── fixtures/
│   ├── test_contract.py
│   ├── test_determinism.py
│   ├── test_storage.py
│   ├── test_locking.py
│   ├── test_garden.py
│   ├── test_budgets.py
│   └── test_checkpoints.py
└── runtime/                     # ignored by Git
    └── <organism-id>/
        ├── organism.sqlite3
        ├── checkpoints/
        │   └── <checkpoint-id>/
        │       ├── organism.sqlite3
        │       └── manifest.json
        ├── exports/
        └── diagnostics/
```

Module names may change without an ADR when the contract boundary is unchanged. Phase 1 does not need memory, skill, model, chat, or caregiver modules.

## Core components

### 1. Schema and contract validation

The schema layer defines and validates:

- protected identity and version fields
- durable status transitions
- garden plots and inventory
- inbox and event schemas
- concrete budget configuration and ledgers
- checkpoint and lineage metadata

Validation occurs before mutable state is used and before commit.

The validator is not optional middleware. Every lifecycle path reaches it.

### 2. Storage boundary

The storage layer:

- opens one organism database path
- enables and verifies foreign keys
- creates and migrates supported schemas administratively
- exposes explicit transaction ownership
- enforces append-only event behavior
- performs parameterized queries
- never exposes arbitrary SQL to organism actions

State, input consumption, budget usage, outcomes, and canonical events commit together.

JSONL is generated only from a declared committed event boundary.

### 3. Injected clock

The clock boundary returns one explicit reading containing:

- integer UTC epoch microseconds
- monotonic nanoseconds

Real operation uses system wall and monotonic clocks. Tests use a fake clock with an explicit reading sequence.

Clock access must not be hidden inside storage, logging, or identifiers.

### 4. Runtime locking

A wake:

1. opens a fresh SQLite connection
2. attempts fail-fast `BEGIN IMMEDIATE`
3. reads mutable state only after acquisition
4. uses that transaction through canonical wake commit
5. rolls back or closes on every failure path

A competing wake receives an explicit busy rejection and is not silently queued.

There is no authoritative PID file, lease row, or wall-time stale-lock rule.

### 5. Lifecycle controller

The accepted Phase 1 lifecycle is:

```text
wake command
  -> open database and acquire fail-fast write transaction
  -> validate state, versions, maintenance, and checkpoint readiness
  -> load protected concrete budgets
  -> claim one synthetic:garden_tick
  -> build one full sorted garden observation
  -> choose one registered action or abstain
  -> validate and reserve budgets
  -> execute recoverable action inside a savepoint
  -> independently evaluate outcome and objective
  -> append outcomes, events, and budget ledger
  -> mark an exact checkpoint boundary pending
  -> validate and commit
  -> create, validate, and publish an immutable SQLite checkpoint
  -> register checkpoint stable in a short transaction
  -> set sleeping or maintenance_required
  -> close and terminate
```

The twelve semantic wake steps are fixed by Contract v0.2. Internal code may be factored differently but may not hide retries or additional actions.

### 6. Seed garden

`seed-garden-v1` is fully observable and stored in SQLite.

Initial state:

- `bed-a`: dry sprout
- `bed-b`: mature with one fruit
- one water unit
- zero harvested fruit

Registered mutating actions:

- `water_plot(plot_id)`
- `harvest_plot(plot_id)`

Policy:

1. water the lexicographically first executable dry living plot
2. otherwise harvest the lexicographically first executable mature fruit
3. otherwise abstain

There is no randomness, hidden state, natural-language interpretation, autonomous ecology, personality, mood, or caregiver.

### 7. Action registry and executor

An action definition includes:

- identifier and version
- parameter and outcome schemas
- preconditions
- permissions
- concrete budget costs
- deterministic behavior declaration
- evaluator
- rollback behavior

The executor:

1. charges the action attempt
2. validates schema, target, preconditions, permissions, and remaining budgets
3. reserves a mutation only after preconditions pass
4. opens a SQLite savepoint
5. performs the exact transition
6. rolls back partial mutation on recoverable failure
7. preserves attempt cost and typed failure in the outer transaction

No arbitrary generated code, shell command, dynamic tool name, network call, subprocess, or external mutable write exists in Phase 1.

### 8. Evaluation

The evaluator independently recomputes:

- action transition validity
- garden objective status
- protected invariants
- budget compliance
- before/after unresolved needs
- progress classification

An action cannot declare itself successful.

Fixed tests protect the evaluator and measuring conditions from organism or caregiver modification.

### 9. Concrete budgets

Phase 1 has no canonical scalar energy.

Budget layers:

- per-wake decision counters
- protected lifecycle safety envelope
- persistent storage and maintenance limits

Core per-wake limits:

- one input event
- one observation
- one action attempt
- one successful environment mutation
- zero caregiver consultations
- zero network calls
- zero subprocess calls
- zero authoritative external writes

Core runtime limits:

- twelve semantic steps
- sixteen canonical records, with terminal capacity reserved
- 2000 ms normal monotonic deadline
- 250 ms cleanup grace
- 5000 ms checkpoint deadline

Storage and failure defaults are defined in ADR 0006 and Contract v0.2.

Status must expose the budget vector rather than a misleading energy percentage.

### 10. Event history and inbox

The mutable input inbox and immutable event history are separate schemas.

Inbox state may change transactionally when a tick is claimed. Historical receipt, claim, decision, outcome, and evaluation facts are append-only.

Canonical event order uses an increasing integer sequence. Timestamps are audit metadata and do not define order.

Cross-lineage identity is:

```text
(organism_id, lineage_generation, event_sequence)
```

### 11. Checkpoints and rollback

Every initialization and committed wake establishes a pending checkpoint boundary. Another wake cannot advance until it becomes stable.

Checkpoint creation uses SQLite's backup interface and publishes an immutable directory only after:

- database close
- digest and size calculation
- integrity and foreign-key checks
- identity and version checks
- lineage and event-boundary verification
- atomic same-filesystem publication

Rollback is offline administration. It creates a verified pre-rollback archive, restores a selected checkpoint through a temporary candidate, increments lineage generation, and preserves the abandoned future for audit.

### 12. Administrative boundary

Administration may:

- initialize an organism
- enqueue a uniquely identified garden tick
- inspect status
- create or repair checkpoints
- prune eligible checkpoints
- enter or clear maintenance with a reason
- roll back or quarantine
- perform supported migrations
- export non-canonical records

Administration is not organism autonomy and must be reported separately in experiments.

## Protected, mutable, and future layers

### Protected from organism and caregiver

- contract and ADRs
- validators and canonical schemas
- fixed evaluations
- permissions and hard-zero capabilities
- action definitions and evaluators
- seed-garden fixture, policy, and objective
- budget defaults and enforcement
- append-only enforcement
- clock boundary
- checkpoint and rollback machinery
- source code and migration rules

### Mutable through bounded Phase 1 runtime

- lifecycle counters and allowed status transitions
- queue claim state
- append-only event additions
- garden moisture, fruit, and inventory
- objective and environment step
- per-wake budget ledger
- failure streak and maintenance reason
- checkpoint-pending and stable references

### Future caregiver and learning layers

Not implemented in Phase 1:

- caregiver request and response protocol
- human chat interface
- model adapter
- memories and skills
- proposal and adoption pipeline
- caregiver fading experiments
- consolidation and forgetting

A future caregiver response is always a proposal and cannot directly mutate protected or canonical state.

## Maturity model

Phase 1 does not claim maturity. It proves metabolism and recovery.

Later development should track a vector including:

- caregiver consultations per retained capability
- caregiver minutes and latency
- autonomous duration after withdrawal
- fixed-task competence and transfer
- skill reuse
- recovery after failure or misleading advice
- storage and computation cost
- correct abstention
- hidden retries and experimenter intervention

No single score should hide those dimensions.

## Minimal technical choices

Phase 1 baseline:

- Python 3.12+
- standard library where practical
- `sqlite3` for canonical storage and backup
- integer timestamps and counters
- `pytest` for protected tests
- Git for source and decision history
- local single-host filesystem
- no vector database
- no network
- no live or fixture caregiver in action selection
- no model fine-tuning
- no scalar energy

## First implementation target

The first executable SUDACHI is deliberately unimpressive:

```text
sudachi init
sudachi enqueue synthetic:garden_tick --id tick-1
sudachi wake --seed 1
sudachi status
sudachi checkpoint repair
sudachi rollback
```

It must pass every fixed evaluation in Contract v0.2 before any caregiver or learning layer is added.

A trustworthy metabolism precedes a clever brain.
