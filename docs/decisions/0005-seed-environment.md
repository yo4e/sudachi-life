# ADR 0005: Deterministic Seed Garden

- **Status:** Accepted
- **Date:** 2026-07-21
- **Issue:** #1
- **Scope:** SUDACHI-0 seed architecture

## Context

Phase 1 needs an environment small enough to implement and exhaustively test, but rich enough to exercise the organism contract:

- persistent observation and environment state
- a queued external trigger
- deterministic action selection
- one registered action per wake
- measurable action outcomes
- invalid-action rejection
- abstention
- budget enforcement
- atomic state and event persistence
- checkpoint and rollback

The environment is not intended to demonstrate intelligence, learning, open-ended evolution, personality, or caregiver withdrawal. It is a mechanical test body for SUDACHI-0.

ADR 0001 makes SQLite the sole canonical durable store. ADR 0004 checkpoints only canonical SQLite state. Therefore, authoritative mutable environment state must also live inside the organism database or be deterministically reconstructable from it.

A filesystem-change task would overemphasize software automation and introduce external mutable state before cross-resource recovery exists. A larger grid world would add navigation, pathfinding, hidden state, and arbitrary content without improving the seed contract test.

## Decision

### 1. Phase 1 uses a tiny deterministic virtual garden

The seed environment is named `seed-garden-v1`.

It contains exactly two named plots and a small inventory:

| Plot | Initial stage | Initial moisture | Initial fruit |
| --- | --- | ---: | ---: |
| `bed-a` | `sprout` | `0` | `0` |
| `bed-b` | `mature` | `1` | `1` |

Initial inventory:

- `water_units = 1`
- `harvested_fruit = 0`

Initial environment counters:

- `environment_step = 0`
- `objective_complete = false`

All values are canonical SQLite state.

### 2. The seed objective is to resolve two care opportunities

The fixed seed objective is complete when:

- no living plot has `moisture = 0`, and
- no plot has harvestable fruit, and
- `harvested_fruit >= 1`

From the canonical initial state, this requires two successful actions:

1. water `bed-a`
2. harvest `bed-b`

The objective is a test harness, not the organism's ultimate purpose. Task completion alone is not SUDACHI's research contribution.

### 3. Environment state is fully observable in Phase 1

When a garden tick is processed, the organism receives a deterministic observation containing:

- environment identifier and version
- current environment step
- plots sorted by plot identifier
- stage, moisture, and fruit for each plot
- inventory water and harvested fruit
- objective status
- applicable registered actions with their declared preconditions

There is no hidden state, partial observability, noisy sensing, or natural-language description in Phase 1.

The canonical serialized observation uses stable field names and stable ordering. Presentation text is derived and non-canonical.

### 4. One synthetic event advances one wake

The only normal external environment trigger is:

```text
synthetic:garden_tick
```

Each enqueued tick has a unique caller-supplied external event identifier.

A wake processes at most one oldest unconsumed tick by canonical event order.

Duplicate external event identifiers are rejected idempotently and do not cause another action.

A tick does not mutate the garden by itself. It requests one observe–decide–act–evaluate cycle against the current persistent state.

### 5. Phase 1 has two mutating environment actions

#### `water_plot`

Parameters:

- `plot_id`

Preconditions:

- plot exists
- plot stage is `sprout` or `mature`
- plot moisture is `0`
- inventory has at least one water unit
- the action and write budgets permit execution

Effects:

- plot moisture becomes `1`
- `water_units` decreases by `1`
- environment step increases by `1`

#### `harvest_plot`

Parameters:

- `plot_id`

Preconditions:

- plot exists
- plot stage is `mature`
- plot fruit is at least `1`
- the action and write budgets permit execution

Effects:

- plot fruit decreases by `1`
- `harvested_fruit` increases by `1`
- environment step increases by `1`

Both actions produce an explicit structured outcome containing the action, parameters, precondition result, before/after environment revision, objective progress, consumed budgets, and success or rejection reason.

### 6. Abstention is an explicit lifecycle decision

If no valid mutating action can be selected, the organism records an abstention rather than inventing an action.

Phase 1 abstention reasons include:

- `objective_already_complete`
- `no_applicable_action`
- `insufficient_action_budget`
- `insufficient_write_budget`
- `insufficient_resource`
- `invalid_observation`

Abstention does not mutate plot or inventory state. It consumes only the minimum lifecycle bookkeeping budget decided by ADR 0006 and is recorded in append-only history.

There is no separate `wait`, `rest`, or mood action in Phase 1.

### 7. The seed policy is a fixed deterministic rule

Phase 1 does not learn an action policy.

Given a valid full observation, the policy is:

1. find living plots with moisture `0`; choose the lexicographically smallest plot identifier and propose `water_plot`
2. otherwise find mature plots with fruit; choose the lexicographically smallest plot identifier and propose `harvest_plot`
3. otherwise abstain

A water candidate that lacks inventory water is not executable. The policy then considers harvest candidates. If no executable mutating action remains, it abstains with the most specific applicable reason.

Lexicographic plot identifiers are the declared tie breaker. Current time, database row order, process identity, and incidental dictionary ordering may not affect selection.

### 8. Environment transitions contain no randomness or autonomous ecology

Phase 1 does not include:

- random growth
- weather
- moisture decay
- plant death
- reproduction
- procedural generation
- hidden timers
- autonomous changes between wakes

The lifecycle seed is still a declared and recorded input for contract consistency, but `seed-garden-v1` does not consume random numbers. Different random seeds must not change the environment transition in Phase 1.

Future environmental stochasticity requires an injected random-source decision and explicit transition versioning.

### 9. The environment is persistent, not episodically reset by wake

The garden remains in SQLite across process termination.

A wake never resets the environment. Initialization is the only normal creation of the canonical seed state.

The standard fixed run is:

```text
init
  -> genesis checkpoint

tick-1
  -> water bed-a
  -> checkpoint

tick-2
  -> harvest bed-b
  -> objective complete
  -> checkpoint

tick-3
  -> abstain: objective_already_complete
  -> checkpoint
```

Tests may create separate fixture organisms with altered initial state. Test fixtures do not mutate the protected canonical seed configuration of another organism.

### 10. Objective evaluation is deterministic and protected

After a successful action, the evaluator recomputes objective status from canonical environment state.

It does not accept an action's claim that progress occurred.

The objective definition, action schemas, transition rules, tie breaker, and canonical initial fixture are protected Phase 1 configuration. The organism cannot modify them.

Evaluation records:

- needs before action
- needs after action
- objective completion before and after
- whether progress was positive, neutral, or negative

For the two registered Phase 1 mutating actions, a successful valid transition must not increase unresolved needs.

### 11. Invalid actions are rejected atomically

The executor validates the action name, schema, target, preconditions, protected configuration, and budgets before mutation.

Examples of invalid actions:

- watering a missing plot
- watering a plot whose moisture is already `1`
- watering without water inventory
- harvesting a sprout
- harvesting a plot with zero fruit
- supplying unknown parameters
- attempting an unregistered action

A rejected action:

- leaves environment and inventory unchanged
- records a typed rejection outcome
- consumes only the evaluation or attempted-action budget specified by ADR 0006
- does not increment environment step

No partial transition is allowed.

### 12. Authoritative environment state stays inside SQLite

The following are canonical database state:

- environment version
- protected initial-configuration identifier
- plots and their mutable values
- inventory
- environment step
- objective status
- external tick identifiers and consumption state
- observations, proposals, actions, outcomes, and evaluation facts required by the contract

The garden does not read or write arbitrary files. Rendered garden views and JSONL experiment exports are non-canonical and reproducible.

ADR 0004 checkpoints therefore restore the complete Phase 1 environment.

### 13. Environment versioning is explicit

The environment identifier `seed-garden-v1` is stored in protected configuration and checkpoint manifests.

Any change to:

- initial plots
- action schemas
- policy priority
- transition effects
- objective definition
- observation schema

creates a new environment version or an explicit migration and requires fixed-test review.

Existing experiment results must not silently change meaning.

### 14. The seed environment is not presented as learning

Completing the garden objective with the fixed policy demonstrates only that the organism can:

- wake
- observe
- select a registered action deterministically
- enforce preconditions and budgets
- persist an outcome
- checkpoint
- sleep

It does not demonstrate acquired competence, intelligence, autonomy from a caregiver, or artificial life by itself.

Later caregiver experiments must introduce capabilities that the organism initially lacks and then test retained competence after assistance is withdrawn.

## Fixed Phase 1 environment scenarios

The implementation test suite must include at least:

### Scenario A — canonical two-action completion

From the canonical initial state:

- first tick selects and completes `water_plot(bed-a)`
- second tick selects and completes `harvest_plot(bed-b)`
- objective becomes complete
- third tick records `objective_already_complete` abstention

### Scenario B — deterministic tie breaking

Given two dry living plots and sufficient water, the lexicographically smallest plot identifier is selected independent of insertion order.

### Scenario C — resource-aware fallback

Given a dry living plot, no water, and harvestable fruit, the policy selects the valid harvest action rather than proposing impossible watering.

### Scenario D — no applicable action

Given incomplete objective state with no executable registered action, the lifecycle records a specific abstention and does not mutate environment state.

### Scenario E — invalid direct action

Direct executor tests for invalid plot, failed precondition, unknown parameter, and unregistered action leave canonical state unchanged and record rejection.

### Scenario F — duplicate external tick

Enqueuing the same external event identifier twice produces one consumable tick and never two environment actions.

### Scenario G — budget exhaustion

Insufficient action or write budget causes explicit abstention before environment mutation.

### Scenario H — rollback

After canonical objective completion, rollback to the checkpoint after the first action restores the watered sprout, unharvested fruit, inventory, objective status, event boundary, and lineage rules accepted by ADR 0004.

### Scenario I — seed independence

Different declared random seeds produce the same Phase 1 garden decisions and transitions because the environment consumes no randomness.

## Consequences

### Positive

- The first environment is small enough for exhaustive deterministic tests.
- All mutable authoritative state is covered by SQLite transactions and checkpoints.
- Two actions exercise preconditions, inventory, state transitions, evaluation, and persistence.
- Abstention and invalid-action behavior are first-class.
- The fixed policy makes hidden nondeterminism easy to detect.
- The environment avoids network, arbitrary filesystem, language-model, and human dependencies.
- The persistent objective provides a visible multi-wake lifecycle without an always-on loop.

### Negative

- The garden is intentionally not lifelike or open-ended.
- There is no learning, uncertainty, exploration, natural decay, or stochasticity.
- The fixed rule can solve the canonical objective trivially.
- A two-plot world cannot support strong claims about intelligence or adaptation.
- The word “garden” may invite biological interpretation beyond what the mechanics justify.

### Neutral or deferred

- ADR 0006 must assign concrete budget costs to observation, action attempts, writes, abstention, and checkpoint maintenance.
- Contract review must align event and outcome names with this environment.
- Later phases may add unfamiliar garden variants for caregiver-assisted learning, but they must preserve protected evaluation and explicit versioning.
- Natural dynamics, partial observability, new objects, and stochastic transitions require later decisions.

## Alternatives rejected

### Filesystem-change environment

Rejected because it introduces authoritative external mutable files and biases the organism toward generic software-agent tasks before database-only rollback is proven.

### Grid navigation world

Rejected because coordinates, movement, pathfinding, collisions, and larger action spaces add complexity unrelated to the first lifecycle contract.

### Text adventure

Rejected because natural-language parsing and semantic ambiguity would dominate the experiment before state mechanics are validated.

### Random ecological simulation

Rejected because stochastic dynamics would make failures harder to localize before clock, storage, locking, checkpoint, and budget invariants have implementation coverage.

### Single one-shot flag toggle

Rejected because it would not exercise action priority, inventory, multiple wakes, objective completion, and post-completion abstention.

### Tamagotchi-style needs and mood meters

Rejected because simulated needs or affection would add presentation without demonstrating caregiver-independent competence.

## Required implementation invariants

The later implementation and fixed tests must demonstrate:

1. initialization creates exactly the protected `seed-garden-v1` state
2. mutable environment state exists only in canonical SQLite storage
3. observations have stable field order and plot order
4. one tick permits at most one mutating environment action
5. duplicate external event identifiers do not cause duplicate action
6. policy selection is independent of database insertion order
7. current time, process identity, and random seed do not affect Phase 1 selection
8. action preconditions are checked before mutation
9. rejected actions leave environment state and step unchanged
10. successful actions produce the exact declared transition
11. objective status is recomputed independently by the evaluator
12. canonical two-action completion and post-completion abstention match the fixed scenario
13. budget exhaustion prevents mutation
14. transaction failure leaves both environment and event history at the prior committed boundary
15. checkpoint and rollback restore all authoritative garden state
16. environment version mismatch is rejected
17. no environment operation accesses network or arbitrary filesystem paths
18. rendered views and exports can be deleted without changing canonical state

## Operational notes for later implementation

- use explicit enums or validated strings for stages and outcomes
- use integer counters only; no floating-point moisture or score
- sort observations explicitly by plot identifier
- keep protected environment configuration separate from mutable plot rows
- represent external event identifiers with a uniqueness constraint
- do not rely on SQLite row order without `ORDER BY`
- implement action transitions as small pure decision logic plus one transactional persistence boundary
- keep objective evaluation separate from action execution
- expose fixture creation only to tests and administration, not organism actions

## Follow-up

Proceed to ADR 0006. It must define concrete Phase 1 budgets and decide whether “energy” exists as independent mutable state or only as a derived presentation of those budgets.
