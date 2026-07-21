# ADR 0006: Concrete Budgets Without Independent Energy State

- **Status:** Accepted
- **Date:** 2026-07-21
- **Issue:** #1
- **Scope:** SUDACHI-0 seed architecture

## Context

SUDACHI needs finite resources to make abstention, failure, maintenance, and later caregiver dependence measurable.

A single mutable variable named `energy` would be easy to display but would hide unlike constraints:

- number of events processed
- number of actions attempted
- number of environment mutations
- elapsed time
- database and checkpoint storage
- external effects
- caregiver consultations
- network and subprocess access

Those resources have different units, failure modes, and safety meanings. Combining them into one scalar before their mechanics exist would create an unexplained game meter rather than a useful artificial-life variable.

ADRs 0001–0005 establish a deterministic SQLite lifecycle, injected clocks, fail-fast wake locking, required checkpoints, and a two-action seed garden. ADR 0006 must assign explicit Phase 1 limits and define how exhaustion is recorded without allowing counters to become negative or preventing the system from safely closing and auditing a wake.

## Decision

### 1. Phase 1 has no independent `energy` state

SUDACHI-0 does not store, spend, regenerate, inherit, or optimize a scalar named `energy`.

The canonical state contains concrete budget configuration and usage ledgers only.

User interfaces may present a clearly labeled non-canonical summary of remaining capacity, but they must also expose the underlying budget vector. No derived display may become an action-selection input or research metric without a later ADR.

The term “energy” remains available for future research only if a later phase gives it an operational definition that explains behavior better than the concrete budgets.

### 2. Budgets are divided into three layers

#### A. Per-wake deterministic decision budgets

These reset from protected configuration at the start of each accepted wake and do not carry unused capacity forward.

They constrain what the organism may observe and attempt.

#### B. Protected lifecycle safety envelope

These bound lifecycle phases, wall time, canonical records, cleanup, and storage growth. They are enforced by the runtime and cannot be spent or raised by organism actions.

#### C. Persistent maintenance and storage limits

These apply across wakes to database size, checkpoint storage, retention, and consecutive failures. They do not reset merely because the process sleeps.

This separation prevents an organism action from consuming the capacity needed to record its own exhaustion, roll back safely, or close the database.

### 3. Protected Phase 1 defaults are explicit

The following values are the accepted defaults for `seed-garden-v1`.

#### Per-wake decision budgets

| Budget | Default | Meaning |
| --- | ---: | --- |
| `input_events` | `1` | Maximum queued environment events consumed by one wake |
| `observations` | `1` | Maximum canonical environment observations built by one wake |
| `action_attempts` | `1` | Maximum registered mutating action proposals submitted to the executor |
| `environment_mutations` | `1` | Maximum successful garden state transition |
| `caregiver_consultations` | `0` | Human, model, hybrid, or fixture consultation during Phase 1 |
| `network_calls` | `0` | Network operations initiated by organism or lifecycle logic |
| `subprocess_calls` | `0` | Child-process launches |
| `external_mutable_writes` | `0` | Authoritative writes outside canonical SQLite state |

#### Lifecycle safety envelope

| Limit | Default | Meaning |
| --- | ---: | --- |
| `lifecycle_steps` | `12` | Maximum counted semantic lifecycle phases before terminalization |
| `canonical_records` | `16` | Maximum canonical audit/event records created by one wake transaction |
| `lifecycle_wall_time_ms` | `2000` | Monotonic time allowed for normal wake work through commit |
| `cleanup_grace_ms` | `250` | Runtime-only time reserved for rollback, terminal diagnostics, and connection close after normal work stops |
| `checkpoint_wall_time_ms` | `5000` | Monotonic time allowed for checkpoint creation, validation, publication, and registration |

#### Persistent maintenance and storage limits

| Limit | Default | Meaning |
| --- | ---: | --- |
| `active_database_max_bytes` | `8388608` | 8 MiB maximum canonical database file size |
| `checkpoint_artifact_max_bytes` | `8388608` | 8 MiB maximum database snapshot size per checkpoint |
| `checkpoint_store_max_bytes` | `41943040` | 40 MiB maximum retained checkpoint store, excluding explicitly exported research packages |
| `runtime_working_set_max_bytes` | `67108864` | 64 MiB maximum active database, SQLite sidecars, checkpoint store, and temporary checkpoint working set |
| `checkpoint_retention_limit` | `4` | Stable lifecycle checkpoints retained under ADR 0004 |
| `consecutive_failure_limit` | `3` | Canonically recorded failed wakes allowed before maintenance is required |

The byte values are powers of two and are part of protected experiment configuration.

Changing a default creates a new configuration version and must be recorded in experiment metadata. The organism cannot change these values.

### 4. Budget configuration is a declared deterministic input

At accepted wake start, the runtime loads a versioned protected budget configuration from canonical SQLite state.

The configuration identifier and initial counters are included in the lifecycle record.

Identical state, event, clock readings, seed, environment version, and budget configuration must produce identical decisions and usage ledgers.

A budget value may not come from an environment variable, local machine heuristic, hidden global default, or current account balance without being normalized into the declared protected configuration first.

### 5. Unused per-wake budget does not accumulate

Per-wake counters reset for each accepted wake.

Unused action attempts, mutations, time, or records are not banked as future power. There is no rechargeable energy pool in Phase 1.

Persistent resources such as stored bytes and failure streak remain across wakes because they describe continuing organism condition or maintenance burden.

### 6. Counted lifecycle steps are semantic, not Python statements

The normal Phase 1 wake has at most twelve counted semantic steps:

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

Lock acquisition and connection opening occur before these counted steps but remain inside the monotonic wall-time envelope.

Checkpoint stabilization is a protected post-commit maintenance phase with its own wall-time and storage limits.

An implementation may combine internal functions, but it must preserve these semantic accounting points. It may not hide retries or loops inside one “step.”

### 7. Terminalization capacity is protected from organism spending

The runtime reserves enough control-plane capacity to:

- record abstention or budget exhaustion when canonical storage is healthy
- roll back a recoverable action savepoint
- validate the outer transaction
- close cursors and connections
- report an external diagnostic when canonical recording is impossible

The organism cannot use the last canonical record slot or cleanup grace for additional action work.

Of the sixteen canonical record slots, at least two are reserved for terminal outcome and budget ledger records.

If normal logic would consume the protected reserve, it stops and terminalizes with `budget_exhausted` or an equivalent typed result.

### 8. Budget checks and reservation occur before mutation

The sequence for a mutating action is:

1. consume one `action_attempts` unit when a registered proposal enters executor validation
2. validate schema, target, preconditions, protected boundaries, and remaining budgets
3. reserve one `environment_mutations` unit only after preconditions pass
4. execute within a SQLite savepoint inside ADR 0003's outer wake transaction
5. evaluate the actual transition
6. release the savepoint on valid completion or roll it back on recoverable action failure
7. persist the attempt, mutation usage, outcome, and remaining counters in the outer transaction

Counters are checked before decrement. A counter is never allowed below zero, even transiently in canonical state.

A rejected action spends its action attempt but not an environment mutation.

A successful `water_plot` or `harvest_plot` spends one action attempt and one environment mutation.

### 9. Recoverable action failure preserves the cost without preserving partial mutation

Recoverable executor failures use a SQLite savepoint.

The environment mutation is rolled back to the savepoint, while the outer wake transaction retains:

- the consumed action attempt
- zero successful environment mutations
- the typed failure outcome
- the updated failure streak
- the checkpoint-pending boundary for the committed audit history

Fatal state, schema, corruption, or storage failures may require rolling back the entire wake transaction. When canonical storage is still writable, a separate short administrative transaction may record the fatal attempt. Otherwise the failure exists only in an external diagnostic and is reported honestly as unrecorded canonically.

### 10. Abstention has explicit and minimal cost

An abstention consumes:

- one input event if a tick was claimed
- one observation if an observation was built
- the semantic steps already performed
- canonical terminal records

It consumes:

- zero action attempts when no mutating proposal enters the executor
- zero environment mutations
- zero caregiver consultations
- zero network, subprocess, and external-write units

Budget-exhaustion abstention occurs before the forbidden operation.

`objective_already_complete` is a justified abstention and does not increment the failure streak.

### 11. Wall-time limits use ADR 0002 monotonic time

The normal lifecycle deadline is calculated from injected monotonic readings.

The organism must stop normal work when `lifecycle_wall_time_ms` is exhausted.

The `cleanup_grace_ms` is not additional organism thinking time. It exists only for bounded rollback, terminal reporting, and resource closure.

Tests use a fake clock and do not sleep. Operational SQLite lock waiting is fail-fast under ADR 0003 and is not charged as hidden queued computation.

Checkpoint time is measured separately because checkpointing occurs after the canonical wake commit.

### 12. Storage budgets are measured at declared boundaries

Before and after a lifecycle and checkpoint operation, the runtime measures relevant local files without following symlinks.

At minimum it accounts for:

- active SQLite database
- SQLite journal or other approved sidecars
- retained stable checkpoints
- temporary checkpoint directory
- pre-rollback archive when protected by ADR 0004

If a predicted operation cannot fit within the applicable artifact or working-set limit, it does not begin.

After a transaction but before commit, the runtime verifies the resulting active database size where the platform and SQLite state allow. If the hard active-database limit would be exceeded, the transaction rolls back and terminalizes as storage exhaustion when possible.

Checkpoint publication refuses an oversized artifact. The pending-checkpoint flag remains set and later wakes remain blocked until repair, pruning, or an explicit protected configuration change.

### 13. Checkpoint work is maintenance cost, not an organism action

Checkpoint creation consumes:

- checkpoint wall time
- checkpoint artifact bytes
- checkpoint store bytes
- runtime working-set bytes

It does not consume:

- action attempts
- environment mutations
- caregiver consultations

Checkpoint cost is still part of the total cost of maintaining the organism and must be included in experiment reports. Calling it “maintenance” does not make it free.

### 14. Consecutive failures create maintenance state, not death or fatigue

The canonical organism state contains a nonnegative `consecutive_failures` counter.

It increments after a committed wake outcome classified as:

- invalid observation
- rejected or failed action
- incomplete objective with no executable action
- action or lifecycle budget exhaustion
- recoverable lifecycle validation failure

It does not increment for:

- successful action
- justified `objective_already_complete` abstention
- duplicate-wake busy rejection that never acquired the runtime transaction
- checkpoint-required rejection while a prior boundary is pending

A successful action or justified objective-complete abstention resets the counter to zero.

When the counter reaches three, the organism enters protected `maintenance_required` state after the outcome is checkpointed. Later normal wakes reject until an administrative inspection, rollback, or explicit recovery clears maintenance.

This is a safety threshold, not simulated illness, death, morale, or energy depletion.

### 15. Zero-capability budgets are hard prohibitions

The Phase 1 values for caregiver consultations, network calls, subprocess calls, and external mutable writes are exactly zero.

The corresponding interfaces are absent or return a protected prohibition before any external effect.

A helper function may not perform one of these operations and claim it was “infrastructure” or “not an organism action.”

Administrative GitHub work, source development, and test orchestration occur outside the running organism and must not be confused with Phase 1 runtime capability.

### 16. Budget exhaustion is a normal typed outcome

Exhaustion is not represented as a generic exception when the runtime can classify it safely.

The canonical outcome identifies:

- exhausted budget name
- configured initial value
- consumed amount
- attempted forbidden operation
- environment and event boundary
- whether state mutation occurred
- remaining counters

Exhaustion never grants an automatic refill, retry, fallback caregiver call, hidden second action, or larger limit.

A caller may initiate a later wake with the same protected configuration only if maintenance and checkpoint state permit it.

### 17. Budget changes are administrative experiment changes

Changing protected limits requires:

- an explicit administrative command or configuration migration
- a new budget configuration version
- validation against hard safety minima and maxima
- an audit event
- a stable checkpoint before another normal wake
- experiment reporting that prevents comparison as if configuration were unchanged

The organism and caregiver cannot negotiate higher budgets during a wake.

### 18. No single energy percentage is canonical

Status output should show the concrete vector, for example:

```text
input_events: 0 / 1 remaining
action_attempts: 1 / 1 remaining
environment_mutations: 1 / 1 remaining
caregiver_consultations: 0 / 0
network_calls: 0 / 0
lifecycle_steps: 4 / 12 used
wall_time_ms: 31 / 2000 used
checkpoint_store_bytes: 1245184 / 41943040 used
```

A UI may derive labels such as `capacity_ok` or `maintenance_required`, but it must not imply that ten milliseconds equals one database write or one caregiver consultation.

Any future scalar energy function must document its units, update rule, behavioral role, and validation evidence in a new ADR.

## Phase 1 operation costs

| Operation | Decision-budget cost | Other accounting |
| --- | --- | --- |
| Claim garden tick | `input_events -1` | semantic step, canonical record |
| Build full observation | `observations -1` | semantic step, canonical record or hash reference |
| Submit valid or invalid mutating proposal | `action_attempts -1` | semantic step, proposal record |
| Successful water or harvest | `environment_mutations -1` | state transition, outcome record |
| Rejected mutating proposal | no mutation cost | attempt remains spent, failure outcome |
| Abstain before executor | no action or mutation cost | terminal record, possible failure-streak effect |
| Caregiver request | prohibited at `0` | protected violation if attempted |
| Network access | prohibited at `0` | protected violation if attempted |
| Subprocess launch | prohibited at `0` | protected violation if attempted |
| External mutable file write | prohibited at `0` | protected violation if attempted |
| Checkpoint stabilization | no decision-budget cost | checkpoint time and byte accounting |
| Duplicate-wake rejection | no canonical decision budget | caller diagnostic; no runtime lock acquired |

## Consequences

### Positive

- Every finite resource has a unit and explicit failure behavior.
- Phase 1 cannot hide model calls, network access, subprocesses, or filesystem writes.
- Unused capacity cannot accumulate into an unexplained power reserve.
- Audit and cleanup capacity remains available after organism budget exhaustion.
- Action attempts and successful mutations are distinguishable.
- Checkpoint cost remains visible without pretending it is an organism decision.
- Storage, wall time, and failure streak persist meaningfully across wakes.
- The design avoids adding a cosmetic life meter before homeostatic mechanics exist.

### Negative

- The budget vector is less visually simple than one energy number.
- Several counters and protected limits must be validated and recorded.
- Exact byte and time limits may need revision after measured implementation results.
- Savepoint-based recoverable failures add transaction complexity.
- A two-second lifecycle and per-wake checkpoint may be conservative on slow hardware.
- Maintenance can stop the organism even when its garden state is otherwise valid.

### Neutral or deferred

- Contract review must align its existing budget names with this decision.
- Implementation benchmarks may justify a later configuration version, but not silent default drift.
- Later caregiver phases must add human minutes, latency, tokens, money, and transformation classes without collapsing them into energy.
- Future homeostasis, fatigue, curiosity, urgency, or survival variables require separate hypotheses and evaluations.
- Replication and inherited resource allocation are outside Phase 1.

## Alternatives rejected

### One scalar energy variable

Rejected because it conceals unlike resources, has no justified conversion function, and invites virtual-pet presentation without explanatory value.

### Token budget as the main resource

Rejected because Phase 1 has no language-model calls and tokens do not represent SQLite work, human labor, storage, or action effects.

### Wall time only

Rejected because fast hardware could perform unbounded logical work inside the same duration and test behavior would become machine-dependent.

### Step count only

Rejected because one step could hide network calls, subprocesses, large writes, or long blocking operations.

### Reset every resource on every wake

Rejected because persistent storage and repeated failure are continuing organism conditions, not temporary call-local counters.

### Carry unused budget between wakes

Rejected because it creates an implicit battery and new strategic behavior without a research hypothesis or safety analysis.

### Do not count checkpoint maintenance

Rejected because backup time and storage are real costs of retained capability.

### Automatically increase a budget after exhaustion

Rejected because it weakens protected experiment conditions and makes apparent growth incomparable.

## Required implementation invariants

The later implementation and fixed tests must demonstrate:

1. Phase 1 stores no independent energy field
2. protected budget configuration is versioned and included in deterministic inputs
3. per-wake decision counters reset and unused values do not accumulate
4. persistent storage and failure limits survive process termination
5. no counter becomes negative
6. budget checks occur before prohibited mutation or effect
7. invalid action spends one attempt and zero mutations
8. successful garden action spends one attempt and one mutation
9. abstention before executor spends zero attempts and zero mutations
10. terminalization records remain possible after decision-budget exhaustion when canonical storage is healthy
11. hidden retries do not fit inside one semantic step
12. fake monotonic time deterministically triggers lifecycle and checkpoint timeout scenarios
13. cleanup grace cannot be used for additional action work
14. zero caregiver, network, subprocess, and external-write budgets prevent interface use
15. active database, checkpoint artifact, checkpoint store, and working set limits are enforced
16. checkpoint failure remains visible and blocks later wakes under ADR 0004
17. recoverable action savepoint rollback preserves attempt cost and removes partial environment mutation
18. failure streak classification and maintenance threshold match this ADR
19. budget changes create a new protected configuration version and checkpoint
20. status exposes concrete budgets rather than a canonical scalar percentage
21. experiment output includes checkpoint maintenance cost and human/model costs when those phases exist

## Operational notes for later implementation

- use integer counters and integer milliseconds or nanoseconds; do not use floating-point budget state
- centralize reservation and reconciliation in one budget ledger component
- distinguish decision budgets, runtime safety envelope, and persistent quotas in types and schema
- use SQLite constraints to reject negative canonical counters
- use savepoints for recoverable action execution inside the outer wake transaction
- measure file sizes without following symlinks
- reserve terminal record capacity before ordinary event creation
- keep external diagnostics separate from canonical history and report when canonical recording failed
- include initial, consumed, and remaining values in lifecycle results
- benchmark defaults before Phase 1 release and change them only through an explicit configuration revision

## Follow-up

All six seed ADRs are now specified. Next, review `docs/MINIMAL_ORGANISM_CONTRACT.md` against ADRs 0001–0006, resolve contradictions, confirm protected and mutable boundaries, and normalize the fixed Phase 1 evaluations before creating any Python package skeleton.
