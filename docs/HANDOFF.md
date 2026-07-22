# SUDACHI Project Handoff

Last updated: July 22, 2026

## Cold-start summary

SUDACHI asks whether a bounded artificial organism can convert external cognitive scaffolding into verified local competence and retain capability while becoming less dependent on that scaffolding.

A future caregiver may be human, deterministic, model-based, hybrid, or absent. Phase 1 has no caregiver.

One SQLite database is the canonical runtime body. Git and repository documents record source, protected tests, decisions, and developmental history.

## Normative authority

For Phase 1, use this precedence:

1. Minimal Organism Contract v0.2
2. accepted ADRs 0001–0006
3. protected tests and `docs/PHASE1_TEST_MATRIX.md`
4. this handoff
5. explanatory architecture and roadmap documents

When sources conflict, stop and repair the contract, test, or documentation. Do not choose private semantics in code.

## Current state

Phase 0 is complete. Issue #1 is closed. Issue #13 tracks Phase 1 implementation.

### Slice 1 — foundation and genesis

Merged through PR #14: package, canonical SQLite body, injected clocks, protected garden and budgets, append-only events, verified genesis checkpoint, `init`, and `status`.

### Slice 2 — inbox, wake ownership, and observation

Merged through PR #15: idempotent garden ticks, fail-fast `BEGIN IMMEDIATE`, non-queued competing-wake rejection, oldest input claim, and deterministic full observation.

### Slice 3 — first canonical water wake

Merged through PR #17:

- fixed `water_plot(bed-a)` decision
- action and mutation reservation before change
- savepoint execution and independent evaluation
- exact pending boundary at event sequence 13
- lifecycle checkpoint stabilization at sequence 14
- return to `sleeping`
- checkpoint timeout preserves committed pending state

### Slice 4 — canonical harvest wake

Merged through PR #18:

- the fixed policy reuses the same lifecycle and selects `harvest_plot(bed-b)` when no water target remains
- the executor removes exactly one fruit and increments harvested inventory inside a savepoint
- the evaluator independently proves the transition and changes objective completion from false to true
- the second pending boundary is event sequence 24
- administrative checkpoint stabilization is event sequence 25
- the protected objective becomes complete and the organism sleeps at lifecycle 2

### Slice 5 — objective-complete abstention

Merged through PR #19:

- the third canonical tick observes `objective_complete = true`
- a dedicated abstention decision records `objective_already_complete`
- zero action attempts and zero environment mutations are consumed
- the evaluator independently proves that plots, inventory, objective, and environment step remain unchanged
- lifecycle 3 commits pending boundary 34 and stabilizes at event sequence 35
- the organism returns to `sleeping` with failure streak zero
- the complete canonical water, harvest, abstention run is protected

### Slice 6 — classified no-applicable-action abstention

Merged through PR #20:

- a protected administrative fixture creates an incomplete objective with a dry sprout, no water, and no harvestable fruit
- the fixed policy selects typed `no_applicable_action` before entering any mutating executor
- one input and one observation are consumed; action attempts and environment mutations remain zero
- the independent evaluator proves that the objective remains incomplete, no protected action is executable, unresolved needs remain unchanged, and canonical environment state does not move
- `consecutive_failures` advances exactly once from zero to one
- the protected maintenance threshold remains three and is not entered
- the committed pending boundary is event sequence 16 and administrative stabilization is event sequence 17
- the organism returns to `sleeping`

The fixture is test administration, not a live caregiver. No human, model, or fixture caregiver participates in action selection.

### Slice 7 — resource-aware harvest recovery

Merged through PR #21:

- a protected administrative fixture starts with an incomplete objective, a dry sprout, zero water, one harvestable fruit, and `consecutive_failures = 1`
- deterministic observation exposes no executable water target and one executable harvest target
- the fixed policy skips impossible watering and selects `harvest_plot(bed-b)`
- one input, observation, action attempt, and environment mutation are consumed; all external-capability counters remain zero
- the independent evaluator proves the exact harvest transition, positive progress, and an objective that correctly remains incomplete
- unresolved needs decrease from two to one
- `consecutive_failures` resets exactly once from one to zero
- the committed pending boundary is event sequence 17 and administrative stabilization is event sequence 18
- the organism returns to `sleeping`

The recovery fixture is also test administration and does not participate in action selection.

### Slice 8 — classified action failure and savepoint cost preservation

Merged through PR #22:

- a protected administrative fixture exposes exactly one executable `water_plot(bed-a)` action
- test administration requests one typed failure after the plot row is partially written inside the existing SQLite savepoint
- the executor rolls the savepoint back and releases the successful-mutation budget reservation while preserving the charged action attempt
- the lifecycle records `action_failed`, never records false `action_completed`, and consumes the claimed input
- the independent evaluator proves plots, inventory, objective, unresolved needs, and environment step are unchanged
- `consecutive_failures` advances exactly once from zero to one below maintenance threshold three
- the committed pending boundary is event sequence 17 and administrative stabilization is event sequence 18
- the organism returns to `sleeping`

The failure injection is a test-only keyword argument. It is not available through the CLI, inbox, fixed policy, or organism state.

### Slice 9 — classified lifecycle budget exhaustion before mutation

Implemented and verified in PR #23:

- every wake now performs one explicit injected monotonic-time reading after fixed-policy selection and before any action executor is entered
- a protected administrative fixture exposes exactly one executable `water_plot(bed-a)` action while leaving the protected budget configuration unchanged
- the fake clock reports 2,001 ms elapsed against the protected 2,000 ms lifecycle work limit
- the runtime records typed `lifecycle_wall_time_exhausted_before_action` before action proposal, action attempt, mutation reservation, or environment write
- one input and one observation are consumed; action attempts and successful environment mutations remain zero; all external-capability counters remain zero
- the independent evaluator re-reads the protected budget configuration and proves plots, inventory, objective, unresolved needs, and environment step are unchanged
- `consecutive_failures` advances exactly once from zero to one below maintenance threshold three
- the committed pending boundary is event sequence 16 and administrative stabilization is event sequence 17
- the organism returns to `sleeping`

The fake clock is a declared deterministic test input. The operational deadline check is part of the normal lifecycle and is not exposed as an organism-controlled switch.

## Verified implementation results

GitHub Actions passed on PR #23 with Python 3.12:

- clean editable installation
- `python -m compileall -q src tests`
- **33 protected tests**
- installed genesis CLI smoke test
- all earlier canonical water, harvest, abstention, blocked-state, recovery, and action-failure behavior remains protected
- the budget-exhaustion fixture proves deadline detection before action attempt or mutation, exact nonnegative accounting, one failure increment, checkpoint stabilization, and sleep

The exact local source-tree run also passed **33 tests**, compileall, and the canonical three-wake CLI sequence with unchanged boundaries 13, 24, and 34 and final event count 35. A separate local clean editable install could not resolve `hatchling>=1.25` from the execution environment's package mirror; GitHub Actions independently completed the clean install, so that mirror failure is not treated as success.

Canonical three-wake values remain:

- `lifecycle_number = 3`
- `environment_step = 2`
- `bed-a.moisture = 1`
- `bed-b.fruit = 0`
- `water_units = 0`
- `harvested_fruit = 1`
- `objective_complete = true`
- `latest_stable_event_sequence = 34`
- `event_count = 35`
- `status = sleeping`

The isolated Slice 6 blocked fixture finishes with:

- `lifecycle_number = 1`
- `environment_step = 0`
- `bed-a.moisture = 0`
- `bed-b.fruit = 0`
- `water_units = 0`
- `harvested_fruit = 0`
- `objective_complete = false`
- `consecutive_failures = 1`
- `latest_stable_event_sequence = 16`
- `event_count = 17`
- `status = sleeping`

The isolated Slice 7 recovery fixture finishes with:

- `lifecycle_number = 1`
- `environment_step = 1`
- `bed-a.moisture = 0`
- `bed-b.fruit = 0`
- `water_units = 0`
- `harvested_fruit = 1`
- `objective_complete = false`
- `consecutive_failures = 0`
- `latest_stable_event_sequence = 17`
- `event_count = 18`
- `status = sleeping`

The isolated Slice 8 action-failure fixture finishes with:

- `lifecycle_number = 1`
- `environment_step = 0`
- `bed-a.moisture = 0`
- `bed-b.fruit = 0`
- `water_units = 1`
- `harvested_fruit = 0`
- `objective_complete = false`
- `consecutive_failures = 1`
- `latest_stable_event_sequence = 17`
- `event_count = 18`
- `status = sleeping`

The isolated Slice 9 budget-exhaustion fixture finishes with:

- `lifecycle_number = 1`
- `environment_step = 0`
- `bed-a.moisture = 0`
- `bed-b.fruit = 0`
- `water_units = 1`
- `harvested_fruit = 0`
- `objective_complete = false`
- `consecutive_failures = 1`
- `latest_stable_event_sequence = 16`
- `event_count = 17`
- `status = sleeping`

## Integration repair record

PR #15 was accidentally merged before its required foundation in PR #14. PR #16 repaired the order, introduced clean-checkout CI, and verified the combined baseline. This was an integration defect, not a contract change.

## Accepted Phase 1 baseline

- one canonical SQLite database per organism
- event sequence, not timestamp, defines canonical order
- injected wall and monotonic time
- fail-fast SQLite write ownership
- one input, observation, action attempt, and successful mutation at most per mutating wake
- zero caregiver, network, subprocess, and authoritative external-write capability
- no scalar energy
- immutable checkpoint after every committed wake before another wake
- rollback will preserve the abandoned future and create a new lineage generation

## Exact next implementation task

After PR #23 is merged, create a new branch from current `main` and implement **Slice 10: maintenance-threshold entry after the third consecutive classified failure**.

The slice must:

1. use an explicit protected fixture with `consecutive_failures = 2`, an incomplete objective, and no executable protected mutation
2. claim one tick, build one complete observation, and classify `no_applicable_action`
3. consume one input and one observation while action attempts and environment mutations remain zero
4. independently prove the environment remains unchanged
5. advance `consecutive_failures` exactly from two to three
6. commit and stabilize an exact checkpoint boundary
7. leave the organism in `maintenance_required`, with a typed maintenance reason, rather than `sleeping`
8. reject a later normal wake without consuming another input or changing the failure counter
9. prove the result in protected tests and CI

Do not add maintenance repair, failure-counter clearing, checkpoint repair, lineage rollback, caregiver consultation, learning, or generic planning in Slice 10.

## Current issue map

- **Issue #1 — closed:** Phase 0 contract freeze.
- **Issue #2 — closed:** Copilot architecture review.
- **Issue #3 — open:** caregiver withdrawal, prior work, novelty, human-caregiver, and provider research.
- **Issue #13 — open:** Phase 1 metabolism implementation.

Always verify current GitHub state.

## Do not add during Phase 1

- a human or model caregiver
- chat or natural-language action selection
- network or subprocess access
- organism-writable external files
- arbitrary code or shell execution
- continuous operation
- learning, memories, skills, consolidation, or fading
- scalar energy, mood, affection, or personality
- a generic agent framework

## End-of-session protocol

Before ending substantial work:

1. run relevant protected tests in CI and report exact results
2. update contract or ADRs before implementing changed invariants
3. update the test matrix, issue, and pull-request status
4. update this file with true state, failures, and one exact next action
5. leave no required decision only in chat or model memory

**As it becomes smarter, it should become smaller and quieter.**
