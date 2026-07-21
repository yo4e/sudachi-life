# Minimal Organism Contract v0.2

Status: **Accepted for Phase 1 implementation**

Accepted: **2026-07-21**

This contract defines the smallest implementation that may be called SUDACHI-0. It consolidates ADRs 0001–0006 into one executable boundary.

Implementation must follow both this contract and the accepted ADRs in `docs/decisions/`. The contract states the required invariants; the ADRs preserve detailed reasoning and consequences. If an implementation discovers a contradiction, work stops until the contract or ADR is deliberately revised. Code must not choose a private interpretation.

Version 0.2 replaces the draft v0.1 contract for Phase 1.

## 1. Individual identity and canonical state

A SUDACHI individual has one durable organism identifier and one active canonical SQLite database.

Identity is not one running process. A process may terminate; continuity is carried by validated canonical state, append-only history, immutable checkpoints, and lineage metadata.

### 1.1 Required protected identity and version fields

Canonical state includes at least:

- `organism_id`
- `contract_version`
- `schema_version`
- `environment_version`
- `budget_config_version`
- `lineage_generation`
- `developmental_stage`
- `created_wall_time_utc_us`

Phase 1 values include:

- `contract_version = "0.2"`
- `environment_version = "seed-garden-v1"`
- `developmental_stage = "seed"`
- `lineage_generation >= 0`

A rollback increments lineage generation according to ADR 0004.

### 1.2 Required mutable lifecycle state

Canonical state includes at least:

- `lifecycle_number`
- `status`
- `checkpoint_pending`
- pending checkpoint lineage and event boundary when applicable
- `latest_stable_checkpoint_id`
- `latest_stable_event_sequence`
- `consecutive_failures`
- `maintenance_reason` when applicable
- `last_wake_wall_time_utc_us`
- `last_sleep_wall_time_utc_us`

A random seed is a declared lifecycle input and audit field, not an implicit source of identity or time-derived state.

### 1.3 Durable status values

Phase 1 durable status is one of:

- `sleeping`
- `checkpoint_pending`
- `maintenance_required`
- `rollback_in_progress`
- `quarantined`

`waking`, `acting`, and `evaluating` are transient runtime phases recorded through lifecycle events or diagnostics. They are not trusted as durable lock state.

A normal wake may begin only from `sleeping` with no pending checkpoint.

### 1.4 Forbidden canonical identity shortcuts

Canonical identity or authorization may not depend on:

- operating-system process ID
- hostname
- thread ID
- current wall time
- a random lock token
- Git working-tree location alone
- an LLM conversation or provider session

Those values may appear only as non-canonical diagnostics when useful.

## 2. Canonical storage and authority

### 2.1 One canonical live store

Each organism has one SQLite database inside its allowed local state directory. It is the sole canonical durable live store for:

- organism state and versions
- protected configuration identifiers
- concrete budget configuration and ledgers
- queued synthetic input state
- seed-garden state and inventory
- append-only lifecycle and action history
- outcomes and evaluations
- provenance
- checkpoint registration metadata
- maintenance and lineage state

JSON, JSONL, YAML, caches, rendered views, Git commits, and in-memory objects are not secondary canonical stores.

### 2.2 JSONL is export only

JSONL may be generated deterministically for inspection, analysis, debugging, or publication.

JSONL:

- is non-canonical
- is not dual-written inside the lifecycle transaction
- may be deleted without changing organism state
- is ordered by canonical event sequence
- identifies organism, lineage, schema, contract, and event boundaries
- is not imported into canonical Phase 1 state

### 2.3 Local single-host boundary

Phase 1 supports one organism database on a validated local filesystem.

Unsupported while the organism may be awake:

- multi-host access
- unvalidated network filesystems
- cloud-sync replacement of the live database
- moving or renaming the active database
- treating a copied database as the same active individual

Forking or copying an organism is an offline administrative operation and requires future identity rules.

## 3. Clock and deterministic inputs

### 3.1 Injected clock

All organism and lifecycle time access goes through an explicit injected clock boundary.

A clock reading contains:

- `wall_time_utc_us`: signed integer microseconds since the Unix epoch in UTC
- `monotonic_ns`: integer nanoseconds from an unspecified monotonic origin

Operational runs use a real clock implementation. Tests and replay use an explicit fake clock.

Unexpected fake-clock reads fail deterministic tests.

### 3.2 Time semantics

- Canonical wall timestamps are SQLite integers.
- Human-readable ISO 8601 strings are derived presentation.
- Monotonic values enforce elapsed deadlines.
- Absolute monotonic origins are not persisted as globally comparable timestamps.
- Wall time may repeat or move backward without reordering events.
- Current time may not be an implicit random seed, identifier, or tie breaker.

### 3.3 Complete declared deterministic input

For Phase 1, identical:

- canonical starting database state
- ordered queued event
- protected contract, schema, environment, and budget versions
- declared random seed
- fake-clock reading sequence

must produce identical canonical decisions, state transitions, outcomes, and event content.

`seed-garden-v1` consumes no randomness. Different declared seeds do not change its transition.

## 4. Wake triggers and input queue

### 4.1 Allowed wake sources

Phase 1 wake invocation may originate from:

- direct CLI invocation
- scheduled local invocation
- the experiment harness

A wake can perform environment work only when one valid queued synthetic event is available.

Repository hooks, filesystem watchers, external services, and network webhooks are deferred.

### 4.2 Seed environment event

The only normal Phase 1 environment event type is:

```text
synthetic:garden_tick
```

Each enqueued tick has a caller-supplied external event identifier that is unique within the organism inbox.

Duplicate external identifiers are rejected idempotently and do not cause a second action.

The harness or administrator may enqueue input. The organism may consume an allowed queued input but may not invent or enqueue its own external trigger in Phase 1.

### 4.3 Busy wake attempts

A process that cannot acquire the runtime write transaction returns a typed busy rejection and performs no organism work.

Because it lacks write authority, the busy attempt is not required to appear in canonical history. It may appear in an external diagnostic.

The attempt is not queued to run automatically after the winner finishes.

## 5. Runtime lock and transaction boundary

### 5.1 Authoritative wake lock

Each wake uses one fresh SQLite connection and executes `BEGIN IMMEDIATE` before reading mutable organism state.

The resulting SQLite write transaction is the authoritative runtime lock.

No committed lease row, PID file, wall-time expiry, in-process mutex, or random owner token is a second lock authority.

### 5.2 Fail-fast acquisition

Lock acquisition uses an immediate busy policy.

If acquisition fails, the wake stops with a typed runtime or database-busy result.

### 5.3 No mutable read before acquisition

Before `BEGIN IMMEDIATE` succeeds, wake logic may validate the database path and open the connection but may not:

- load mutable organism state
- inspect the queue for decision making
- select an action
- reserve budgets
- create a checkpoint boundary

### 5.4 One bounded outer transaction

The same transaction covers the canonical wake through commit:

- state and version validation
- checkpoint and maintenance readiness
- one input claim
- one observation
- action or abstention decision
- budget reservation and accounting
- recoverable action savepoint
- environment transition or rejection
- evaluation
- event and outcome append
- failure-streak update
- pending-checkpoint boundary
- final transaction validation

Every path ends in commit, rollback, or connection close.

Nested or reentrant wakes are prohibited. Helper functions receive the existing transaction context and do not open hidden write connections.

## 6. Bounded lifecycle

### 6.1 Lifecycle acceptance

A normal wake is accepted only when:

- the write transaction was acquired
- canonical state validates
- contract, schema, environment, and budget versions are supported
- status is `sleeping`
- no checkpoint is pending
- maintenance is not required
- one valid garden tick can be claimed

If a precondition fails, no environment action occurs.

### 6.2 Twelve semantic wake steps

The normal Phase 1 wake contains at most these twelve counted semantic steps:

1. validate canonical state and checkpoint readiness
2. claim one input event
3. build one sorted observation
4. choose action or abstention
5. validate decision schema
6. reserve decision budgets
7. execute action or abstain
8. evaluate transition and objective
9. persist outcome and usage ledger
10. mark checkpoint pending
11. validate the transaction boundary
12. commit

One internal function may implement multiple steps, but retries or loops may not be hidden inside one step.

### 6.3 Post-commit checkpoint stabilization

After the outer wake transaction commits:

1. create a candidate SQLite backup
2. validate it and its boundary
3. publish the immutable checkpoint atomically
4. register it stable in a short transaction
5. clear checkpoint pending
6. set final durable status to `sleeping` or `maintenance_required`
7. close connections and terminate

Checkpoint stabilization is bounded maintenance, not an additional organism action.

### 6.4 Finite termination states

One wake command terminates with one of:

- stable `sleeping`
- `checkpoint_pending` requiring repair
- `maintenance_required`
- `quarantined`
- a rolled-back fatal or busy result with the prior canonical state unchanged

No lifecycle contains an unbounded retry, recursive planning loop, caregiver wait, network wait, subprocess wait, or hidden queued second action.

## 7. Seed garden environment

### 7.1 Protected initial state

`seed-garden-v1` contains:

| Plot | Stage | Moisture | Fruit |
| --- | --- | ---: | ---: |
| `bed-a` | `sprout` | `0` | `0` |
| `bed-b` | `mature` | `1` | `1` |

Initial inventory:

- `water_units = 1`
- `harvested_fruit = 0`

Initial counters:

- `environment_step = 0`
- `objective_complete = false`

All mutable authoritative environment state is inside SQLite.

### 7.2 Protected objective

The objective is complete when:

- no living plot has moisture `0`
- no plot has harvestable fruit
- `harvested_fruit >= 1`

Completing this objective is only a lifecycle verification target. It is not evidence of learning or general intelligence.

### 7.3 Full observation

One tick produces one canonical fully observable garden observation containing:

- environment identifier and version
- environment step
- plots sorted by plot identifier
- each plot's stage, moisture, and fruit
- inventory water and harvested fruit
- objective status
- applicable registered actions and preconditions

There is no hidden state, natural-language parsing, noisy sensing, or autonomous change between wakes.

### 7.4 Registered mutating actions

#### `water_plot(plot_id)`

Preconditions:

- plot exists
- stage is `sprout` or `mature`
- moisture is `0`
- at least one water unit remains
- action and mutation budgets remain

Effects:

- moisture becomes `1`
- water units decrease by `1`
- environment step increases by `1`

#### `harvest_plot(plot_id)`

Preconditions:

- plot exists
- stage is `mature`
- fruit is at least `1`
- action and mutation budgets remain

Effects:

- fruit decreases by `1`
- harvested fruit increases by `1`
- environment step increases by `1`

No arbitrary code, shell command, dynamic tool name, or unregistered action may execute.

### 7.5 Deterministic policy

The fixed Phase 1 policy is:

1. among executable dry living plots, water the lexicographically smallest plot identifier
2. otherwise, among executable mature fruit plots, harvest the lexicographically smallest plot identifier
3. otherwise abstain

If a dry plot exists but no water remains, the policy may select a valid harvest candidate. If no executable mutating action remains, it abstains with the most specific reason.

Selection does not depend on row insertion order, current time, process identity, dictionary ordering, or random seed.

### 7.6 No autonomous ecology

Phase 1 has no random growth, weather, moisture decay, death, reproduction, procedural generation, hidden timer, or between-wake environment transition.

Changing initial state, observation schema, action schema, transition effects, objective, or policy priority creates a new environment version or explicit migration.

## 8. Action, abstention, and evaluation contract

### 8.1 Registered action metadata

Every executable mutating action declares:

- stable action identifier and version
- description
- input and output schemas
- preconditions
- required permissions
- concrete budget costs
- deterministic flag
- evaluator identifier
- rollback behavior

### 8.2 Execution preconditions

An action may enter execution only when:

- action and parameter schemas validate
- the action is registered
- target state exists
- all preconditions pass
- permissions are allowlisted
- required concrete budgets were reserved
- the organism is not in maintenance or quarantine

### 8.3 Recoverable action savepoint

Recoverable action execution occurs inside a SQLite savepoint within the outer wake transaction.

On recoverable failure:

- partial environment mutation is rolled back to the savepoint
- the action attempt remains spent
- successful mutation cost remains zero
- typed failure and failure-streak changes remain in the outer transaction

Fatal schema, corruption, or storage failures may roll back the outer transaction.

### 8.4 Invalid action

An invalid or rejected action:

- does not change plot, inventory, objective, or environment step
- consumes one action attempt if a registered mutating proposal reached executor validation
- consumes zero successful environment mutations
- records a typed rejection when canonical storage is healthy

### 8.5 Abstention

Abstention is a lifecycle decision, not a fake mutating action.

Initial reasons include:

- `objective_already_complete`
- `no_applicable_action`
- `insufficient_action_budget`
- `insufficient_write_budget`
- `insufficient_resource`
- `invalid_observation`

Abstention before the executor consumes zero action attempts and zero environment mutations.

`objective_already_complete` is justified and does not increment consecutive failures.

### 8.6 Independent evaluation

After action or abstention, the evaluator recomputes objective and invariant status from canonical state.

The action cannot declare itself successful.

Evaluation records before/after needs, objective status, budget compliance, state integrity, and progress classification.

## 9. Concrete budget contract

Phase 1 has no independent scalar `energy` field.

### 9.1 Per-wake decision defaults

| Budget | Value |
| --- | ---: |
| input events | 1 |
| observations | 1 |
| action attempts | 1 |
| successful environment mutations | 1 |
| caregiver consultations | 0 |
| network calls | 0 |
| subprocess calls | 0 |
| authoritative external mutable writes | 0 |

Unused per-wake budget does not accumulate.

### 9.2 Lifecycle safety defaults

| Limit | Value |
| --- | ---: |
| semantic lifecycle steps | 12 |
| canonical records per wake | 16 |
| lifecycle monotonic work time | 2000 ms |
| protected cleanup grace | 250 ms |
| checkpoint stabilization time | 5000 ms |

At least two canonical record slots are reserved for terminal outcome and budget ledger records.

Cleanup grace is not additional organism action time.

### 9.3 Persistent maintenance and storage defaults

| Limit | Value |
| --- | ---: |
| active database | 8 MiB |
| one checkpoint database artifact | 8 MiB |
| retained checkpoint store | 40 MiB |
| runtime working set | 64 MiB |
| stable lifecycle checkpoint retention | 4 |
| consecutive failures before maintenance | 3 |

Budget configuration is protected, versioned, and included in deterministic inputs.

### 9.4 Reservation and nonnegative invariant

- Counters are checked before decrement.
- No counter may become negative, including transient canonical state.
- One mutating proposal spends one action attempt.
- One successful garden transition spends one environment mutation.
- A rejected proposal spends zero mutations.
- Checkpoint work consumes time and storage accounting, not decision-action counters.

### 9.5 Hard-zero interfaces

Phase 1 caregiver, network, subprocess, and external mutable-write capabilities are absent or fail before effect.

A helper may not perform those effects and label them infrastructure.

### 9.6 Exhaustion

Budget exhaustion is a typed outcome recorded before the forbidden operation when canonical storage is healthy.

Exhaustion never triggers:

- automatic refill
- hidden retry
- second action
- fallback caregiver call
- configuration increase

### 9.7 Failure streak

Consecutive failures increment for committed invalid observations, failed or rejected actions, incomplete states with no executable action, or budget exhaustion.

The counter resets after a successful action or justified objective-complete abstention.

At three failures, checkpoint registration leaves the organism in `maintenance_required` rather than `sleeping`.

Busy lock rejection and checkpoint-required rejection do not alter the counter.

## 10. Canonical event and inbox contract

### 10.1 Event order and identity

Committed canonical event rows are append-only and receive a unique monotonically increasing integer `event_sequence` inside the active database.

Event sequence, not timestamp, defines order.

Cross-lineage event identity is the tuple:

```text
(organism_id, lineage_generation, event_sequence)
```

A rendered `event_id` may be derived from that tuple. It need not be a random identifier.

### 10.2 Minimum event fields

Canonical event records include at least:

- `event_sequence`
- `organism_id`
- `lineage_generation`
- `lifecycle_number`
- `wall_time_utc_us`
- `event_type`
- `source`
- structured payload or controlled payload reference
- `schema_version`
- relevant environment and budget configuration versions

Source-provided timestamps or external event identifiers are recorded separately from SUDACHI's own wall timestamp.

### 10.3 Initial event families

The implementation may use more specific versioned names, but Phase 1 must represent:

- wake accepted
- input claimed
- observation created
- action proposed
- action completed, rejected, or failed
- action abstained
- evaluation completed
- budget exhausted
- checkpoint pending
- checkpoint stabilized
- maintenance entered
- rollback started and completed
- sleep ready or stable lifecycle completion

Administrative checkpoint and rollback records are not required to fit inside the sixteen-record wake cap when they occur in separate transactions, but they remain bounded and auditable.

### 10.4 Append-only enforcement

Normal runtime exposes no event update or delete operation.

Database-level constraints or triggers reject event mutation where practical.

Migration or repair is outside organism authority and leaves an administrative audit record.

### 10.5 Queue versus history

The mutable input inbox and append-only canonical history are distinct schemas.

Queue claim or consumption state may change transactionally. Historical records describing receipt and consumption never change.

### 10.6 Payload safety

Canonical records never contain credentials.

Large or sensitive artifacts are referenced by controlled path and digest rather than embedded without limit.

## 11. Checkpoint and rollback contract

### 11.1 Required checkpoint cadence

A verified genesis checkpoint is required before the organism becomes wakeable.

Every committed wake outcome, including action success, rejection, failure, abstention, or budget exhaustion, establishes one exact pending checkpoint boundary.

No later wake advances until that boundary is stable.

### 11.2 Checkpoint artifact

A checkpoint is an immutable directory containing:

- `organism.sqlite3`
- `manifest.json`

The manifest identifies organism, lineage, schema, contract, environment, budget configuration, event boundary, creation time, size, digest, method, and implementation version.

Snapshots use SQLite's Online Backup API through Python's connection backup interface. Naive live-file copy is prohibited.

### 11.3 Validation and publication

Before stability, a checkpoint must pass:

- SHA-256 and size validation
- read-only SQLite open
- full integrity check
- foreign-key check
- organism and lineage match
- schema, contract, environment, and budget version match
- exact event-boundary validation
- protected configuration presence

Creation occurs in a same-filesystem temporary directory. Only an atomically published final directory is valid.

### 11.4 Pending failure and repair

If creation, validation, publication, or registration fails:

- committed canonical state remains
- checkpoint pending remains true
- normal wakes reject
- an explicit administrative repair may retry or register a valid orphan artifact

The system does not clear pending silently.

### 11.5 Retention

Phase 1 retains at most four stable lifecycle checkpoints under protected policy, while preserving the latest stable checkpoint and the rollback guarantees in ADR 0004.

Pruning occurs only after a newer checkpoint is stable.

### 11.6 Rollback

Rollback is an explicit offline administrative operation.

It:

- enters protected maintenance
- validates the target stable checkpoint
- creates a verified pre-rollback archive of the active database
- restores into a temporary candidate
- validates and updates the candidate administratively
- atomically replaces the active database
- increments lineage generation from the abandoned active generation
- records target and abandoned boundaries
- preserves the abandoned future in the pre-rollback archive
- clears maintenance only after the restored active database validates

Default recovery selects the latest valid stable checkpoint. Choosing an older one requires an explicit identifier and reason.

The source checkpoint remains immutable.

### 11.7 Database-only Phase 1 recovery

Phase 1 checkpoints cover canonical SQLite state only.

The organism has no authoritative mutable external files. Rendered views and exports are reproducible and not restored as organism state.

## 12. Protected, mutable, and administrative authority

### 12.1 Protected from organism and caregiver

The organism and any future caregiver cannot modify:

- this contract and accepted ADRs
- contract validator and canonical schemas
- fixed Phase 1 evaluations
- permission and sandbox policy
- action registry definitions and versions
- seed-garden initial fixture, observation schema, transition rules, policy priority, and objective
- budget defaults and enforcement
- event append-only enforcement
- clock and randomness boundaries
- checkpoint, maintenance, and rollback mechanisms
- schema migration rules
- secret-handling rules
- source code
- model-provider transformation permissions

### 12.2 Mutable through the bounded runtime

The bounded Phase 1 runtime may modify only through validated schemas and transactions:

- lifecycle number and timestamps
- status transitions allowed by this contract
- checkpoint-pending and latest-stable references
- consecutive failures and maintenance reason
- input queue claim or consumption state
- append-only event additions
- plot moisture and fruit
- water and harvested-fruit inventory
- environment step and objective-complete state
- per-wake budget ledger

The organism cannot modify the queue by inventing external ticks.

### 12.3 External reviewed code change

The following require a reviewed repository change and, where applicable, a new version or ADR:

- source code
- registered action implementation or schema
- evaluator implementation
- protected configuration defaults
- environment version
- contract or schema migration
- new capability interface

### 12.4 Administrative operations

The administrator or experiment harness may perform explicit validated operations including:

- initialize an organism
- enqueue a synthetic tick
- inspect status
- create or repair checkpoints
- prune eligible checkpoints
- enter or clear maintenance with recorded reason
- roll back or quarantine
- migrate a supported schema
- export non-canonical experiment data

Administrative authority is not organism autonomy. It is recorded separately in experiment reports.

### 12.5 No organism-writable external workspace

Because `external_mutable_writes = 0`, Phase 1 exposes no organism-writable filesystem workspace.

Checkpoint temporary directories are runtime maintenance, not organism action space.

## 13. Outcome and integrity definitions

### 13.1 Successful action outcome

A registered action is successful when:

- schemas and preconditions pass
- concrete budgets were reserved
- the exact declared environment transition occurs
- independent evaluation passes
- protected invariants remain valid
- the outer wake transaction commits

Checkpoint stabilization is required before another wake, but checkpoint failure does not falsely erase the already committed outcome.

### 13.2 Rejected or failed action

A rejected or recoverably failed action:

- leaves environment state unchanged
- preserves action-attempt cost
- records a typed outcome and failure streak when canonical storage is healthy
- may still commit a lifecycle history boundary requiring checkpoint

### 13.3 Abstention

Abstention explicitly chooses no mutating action.

Honest abstention is not automatically failure. Classification depends on the reason.

### 13.4 Stable sleep

Stable sleep means:

- the wake transaction committed
- the pending boundary has a verified registered checkpoint
- status is `sleeping`
- connections close and the process terminates

Sleep does not imply that the garden objective is complete.

### 13.5 Checkpoint pending

`checkpoint_pending` is a durable safe stop after a committed wake when recovery protection is not yet stable.

It is neither sleeping nor corruption. It blocks normal wakes until repair.

### 13.6 Maintenance required

Maintenance is a protected stop entered after the failure threshold or an explicit administrative condition.

Status reporting and repair are allowed. Ordinary environment actions are not.

### 13.7 Quarantine

Quarantine is a stronger protected stop used when integrity, permission, identity, or recovery cannot be trusted.

A quarantined organism may report controlled status but may not perform ordinary actions.

### 13.8 Fatal failure

A fatal failure rolls back the outer transaction when possible and leaves the previous committed state authoritative.

If canonical recording is impossible, the implementation reports that limitation instead of claiming a canonical failure event exists.

## 14. Caregiver boundary

Phase 1 is caregiver-free.

The caregiver consultation budget is exactly zero, and no human, fixture, local model, hosted model, or hybrid caregiver may participate in action selection.

A deterministic fixture may be introduced only in later dedicated consultation-plumbing work after Phase 1 invariants exist.

Any future caregiver response is a proposal and may not directly:

- execute an action
- mutate durable state
- alter protected policy or evaluation
- raise budgets
- erase history
- adopt a skill
- bypass permissions or sandboxing
- authorize model training or distillation

No live human or model interface is part of Minimal Organism Contract v0.2.

## 15. Fixed Phase 1 evaluations

The implementation must prove all of the following with protected tests.

### Determinism and declared inputs

1. Identical canonical state, queued tick, versions, seed, and fake-clock readings produce identical canonical results.
2. Unexpected clock reads fail deterministic tests.
3. Wall time repeating or moving backward does not reorder events.
4. Different declared seeds do not change `seed-garden-v1` behavior.

### Bounded lifecycle and capability

5. One accepted wake processes at most one tick, one observation, one action attempt, and one successful environment mutation.
6. The lifecycle terminates within twelve semantic steps and the declared monotonic deadline.
7. Cleanup grace cannot be used for additional organism work.
8. Network, subprocess, caregiver, and authoritative external-write interfaces cannot produce effects.
9. No independent energy field exists in canonical state.

### Seed garden behavior

10. The canonical first wake waters `bed-a`.
11. The canonical second wake harvests `bed-b` and completes the objective.
12. The canonical third wake records `objective_already_complete` abstention without environment mutation.
13. Lexicographic tie breaking is independent of insertion order.
14. Resource-aware fallback selects a valid harvest when watering is impossible.
15. Invalid actions leave environment and step unchanged.
16. Duplicate external tick identifiers never produce duplicate action.

### Budgets and failure handling

17. No canonical counter becomes negative.
18. Action attempt is charged before execution; rejected action spends zero mutation units.
19. Recoverable action savepoint rollback removes partial mutation while preserving attempt cost and failure history.
20. Budget exhaustion is recorded before the forbidden operation and never creates a hidden retry or caregiver call.
21. Three classified consecutive failures enter maintenance; success or justified completion abstention resets the streak.

### Storage, events, and locking

22. State, budget ledger, input consumption, outcomes, and events commit atomically or not at all.
23. Canonical event sequence is unique, increasing, and authoritative over timestamps.
24. Event update and deletion are rejected.
25. JSONL export is deterministic for a fixed boundary and cannot change canonical state.
26. Two competing connections cannot both acquire a wake; the loser is rejected and not queued.
27. Crash or connection close rolls back uncommitted wake state and releases the SQLite lock.
28. Nested wake and hidden write connections are rejected.

### Checkpoints, recovery, and lineage

29. Initialization cannot become wakeable before a stable genesis checkpoint.
30. Every committed wake leaves an exact pending checkpoint boundary until stabilization.
31. Pending checkpoint state blocks later normal wakes.
32. Incomplete or invalid checkpoint artifacts are never registered stable.
33. Checkpoint digest, size, integrity, foreign keys, identity, versions, lineage, and event boundary are validated.
34. Checkpoint failure preserves committed state and remains explicitly pending.
35. Retention never removes the latest stable checkpoint before a newer one is stable.
36. Rollback creates a valid pre-rollback archive before replacing active state.
37. Rollback restores the selected checkpoint, increments lineage generation, and preserves abandoned events outside the active branch.
38. Failure during rollback leaves either the old or restored database in explicit recoverable maintenance, never silently ambiguous.

### Protected authority

39. Organism actions cannot modify protected files, schema, configuration, evaluator, action definitions, contract, ADRs, or checkpoint machinery.
40. Phase 1 exposes no organism-writable external workspace.
41. Administrative actions are distinguishable from organism actions in records and reports.

These evaluations are fixed for Contract v0.2. A change requires a deliberate contract version and reviewed test update.

## 16. Minimal success condition for SUDACHI-0

SUDACHI-0 exists when local commands can:

1. initialize one `seed-garden-v1` individual
2. publish and register a stable genesis checkpoint
3. enqueue uniquely identified garden ticks
4. perform the canonical deterministic water, harvest, and abstention wakes
5. persist each wake atomically in SQLite
6. enforce concrete budgets and hard-zero external capabilities
7. reject duplicate wakes and duplicate external ticks
8. create and validate stable checkpoints after every committed wake
9. restore a checkpoint with lineage-preserving rollback
10. terminate every command within declared bounds
11. pass all fixed Phase 1 evaluations

It does not need to converse, learn, self-modify, consult a caregiver, appear emotional, or claim intelligence.

A trustworthy metabolism precedes a clever brain.

## 17. Change control

The six seed architecture questions are resolved by ADRs 0001–0006.

Implementation may now choose ordinary local code structure only where it does not alter a contract invariant. Examples include module names, private helper functions, and equivalent validated data-access abstractions.

Any change to canonical authority, clock semantics, locking, checkpoint lineage, seed environment behavior, protected budgets, or fixed evaluations requires an ADR amendment and contract version review.

The next step is to align `ARCHITECTURE.md`, `ROADMAP.md`, handoff documents, and Issue #1 with Contract v0.2. Only after that alignment may the Python package skeleton and tests be created.
