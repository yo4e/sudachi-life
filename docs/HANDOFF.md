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

### Slice 10 — maintenance-threshold entry

Implemented and verified in PR #24:

- a protected administrative fixture starts from an incomplete blocked garden with `consecutive_failures = 2`
- two uniquely identified ticks are queued before the threshold wake
- the first tick is claimed, observed, and classified as `no_applicable_action`
- one input and one observation are consumed; action attempts, successful environment mutations, and all external-capability counters remain zero
- the independent evaluator proves the complete environment and unresolved needs remain unchanged
- `consecutive_failures` advances exactly from two to three
- the committed pending boundary is event sequence 17
- checkpoint registration stabilizes event 18, records typed `maintenance_entered` at event 19, and leaves the organism in `maintenance_required`
- the protected maintenance reason is `consecutive_failure_limit_reached`
- a later normal wake is rejected before reading the clock, claiming the second tick, appending an event, or changing canonical state

Maintenance repair and exit are not implemented. The queued second tick remains unclaimed and unconsumed.

### Slice 11 — read-only maintenance inspection

Implemented and verified in PR #25:

- a protected administrative fixture starts in stable `maintenance_required` state with failure streak three and typed reason `consecutive_failure_limit_reached`
- one uniquely identified garden tick remains queued and unclaimed
- `inspect_maintenance` opens the canonical database read-only, validates it, and accepts only exact maintenance state
- `sudachi maintenance inspect <organism_id>` exposes the same explicit administrative boundary
- the result reports status, maintenance reason, failure streak, latest stable checkpoint identity and boundary, inbox accounting, and exact unconsumed rows
- the inspection verifies latest checkpoint registry consistency and exact inbox accounting
- the API has no clock parameter and performs no clock read
- API and CLI inspection leave every organism file byte-for-byte and metadata-for-metadata unchanged
- event, inbox, checkpoint registry, maintenance state, and queued input remain unchanged
- a later normal wake remains rejected with zero clock reads
- inspection requested against a sleeping organism is rejected through a typed error

Maintenance clear, repair, and rollback are not implemented.

### Slice 12 — explicit administrative maintenance clear

Implemented and verified in PR #26:

- a stable protected fixture starts in `maintenance_required` with failure streak three, typed reason `consecutive_failure_limit_reached`, stable checkpoint boundary six, and one queued unclaimed tick
- `clear_maintenance` and `sudachi maintenance clear` expose one explicit administrative recovery boundary
- the caller must provide a bounded recovery-reason token before any clock read or database mutation
- the operation acquires fail-fast `BEGIN IMMEDIATE` ownership and validates exact maintenance and checkpoint-registry consistency
- one injected clock read supplies the administrative audit timestamp
- one transaction resets the failure streak from three to zero, clears `maintenance_reason`, restores `sleeping`, and appends typed `maintenance_cleared` event nine
- plots, inventory, objective state, environment step, lifecycle, lineage, latest checkpoint references, checkpoint registry, and queued input remain unchanged
- forced audit-event failure rolls back the state update and leaves maintenance intact
- busy, invalid-reason, repeated-clear, and non-maintenance attempts reject without partial state
- a later normal wake claims the preserved tick under the unchanged policy, classifies `no_applicable_action`, advances failures from zero to one, stabilizes boundary 18, and returns to sleeping at event 19

Environment repair, checkpoint repair, retention pruning, and rollback are not implemented.

### Slice 13 — successful bounded checkpoint retention pruning

Implemented and verified in PR #27:

- the canonical three-wake history starts with four stable checkpoints at boundaries 2, 13, 24, and 34
- a fourth objective-complete abstention wake commits boundary 44 and registers it as the newest stable checkpoint
- pruning begins only after checkpoint stabilization is recorded at event 45
- the protected retention transaction validates exact latest-stable identity and requires exactly five registered stable checkpoints
- genesis is preserved and the oldest eligible non-genesis checkpoint at boundary 13 is selected
- the selected artifact is staged by same-filesystem atomic rename before canonical registry mutation
- one matching registry row is deleted and typed `checkpoint_pruned` event 46 records identifier, boundary, lineage, provenance, database bytes, total artifact bytes, retained count, and retained store bytes
- the staged artifact is removed only after the canonical pruning transaction commits
- the final retained boundaries are 2, 24, 34, and 44
- every retained checkpoint validates, no staging directory remains, and normal wake ownership can still be acquired
- active environment, objective, inventory, lineage, failure streak, latest-stable references, and inbox history remain unchanged

Checkpoint repair, orphan cleanup, and rollback are not implemented.

### Slice 14 — classified checkpoint-retention pruning failure

Implemented and verified in PR #28:

- the canonical fourth wake first publishes and registers boundary 44 and records checkpoint stabilization at event 45
- a protected test-only failure is injected after boundary-13 artifact staging and before any registry mutation
- the retention transaction rolls back and restores the staged boundary-13 artifact to its original immutable directory
- all five checkpoint registry rows and artifacts remain at boundaries 2, 13, 24, 34, and 44
- the newest checkpoint and exact latest-stable references remain boundary 44
- every retained checkpoint validates, byte accounting matches, and no pruning staging directory remains
- no false `checkpoint_pruned` event is recorded
- one typed `checkpoint_retention_failed` administrative event is recorded at event 46
- status becomes `maintenance_required` with reason `checkpoint_retention_pruning_failed`
- active environment, objective, inventory, lineage, failure streak, and inbox history remain unchanged
- read-only maintenance inspection reports the new reason and exact latest checkpoint
- a later ordinary wake rejects before reading the clock or changing state

Checkpoint repair, orphan cleanup, maintenance clear for the new reason, and rollback are not implemented.

### Slice 15 — explicit pending-checkpoint registration repair

Implemented and verified in PR #29:

- the protected first-water fixture commits boundary 13 and publishes its immutable lifecycle checkpoint artifact
- the checkpoint deadline expires one nanosecond beyond the protected 5,000 ms limit before registry insertion, leaving canonical status `checkpoint_pending`, event count 13, and latest stable boundary 2
- `repair_pending_checkpoint_registration` and `sudachi checkpoint repair-pending` expose one explicit administrative repair boundary
- the operation acquires fail-fast `BEGIN IMMEDIATE` ownership without claiming input or advancing the environment
- before any clock read, it requires exact pending identity and boundary, validates the previous stable checkpoint, rejects hidden or unsafe entries, requires exactly one visible unregistered artifact, and validates its identifier, lineage, lifecycle, versions, provenance, digests, protected configuration, and complete committed snapshot contents
- zero, multiple, foreign-organism, corrupted, repeated, and busy repair attempts reject without clearing pending state or reading the clock
- one injected administrative clock read supplies the successful registration and audit timestamp
- one transaction inserts the registry row, advances latest stable to boundary 13, clears pending fields, restores `sleeping`, and appends typed `checkpoint_registration_repaired` event 14
- no checkpoint artifact is copied, renamed, modified, or deleted; committed lifecycle state, environment, inbox history, genesis, and checkpoint-store bytes remain unchanged
- a later second tick runs under the unchanged fixed policy, harvests `bed-b`, completes the objective, stabilizes boundary 24 at event 25, and returns to `sleeping`

Ambiguous-orphan cleanup, checkpoint deletion, retention-failure maintenance clear, broad repair, and rollback are not implemented.

## Verified implementation results

GitHub Actions passed on PR #29 with Python 3.12:

- clean editable installation
- `python -m compileall -q src tests`
- **50 protected tests**
- installed genesis CLI smoke test
- all earlier canonical water, harvest, abstention, blocked-state, recovery, action-failure, and budget-exhaustion behavior remains protected
- the maintenance-threshold fixture proves exact failure transition, unchanged environment, checkpoint stabilization, typed maintenance entry, and later normal-wake rejection
- the maintenance-inspection fixture proves exact reporting, read-only files and canonical rows, typed non-maintenance rejection, and continued normal-wake blocking
- the maintenance-clear fixture proves bounded reason validation, fail-fast ownership, atomic state and audit commit, exact preservation, rollback on audit failure, and later processing of the preserved tick
- the checkpoint-retention fixture proves no pruning at four, fifth-checkpoint stability before pruning, genesis and latest preservation, oldest-eligible selection, exact artifact and registry removal, explicit byte-accounted audit history, and continued normal wakeability
- the retention-failure fixture proves fifth-checkpoint stability before failure, staged-artifact restoration, five-row/five-artifact preservation, exact latest references, no false pruning success, typed maintenance warning, read-only inspection, and later zero-clock wake rejection
- the pending-checkpoint-repair fixture proves exact one-orphan matching, full snapshot validation, zero-clock rejection for missing, ambiguous, foreign, invalid, repeated, and busy cases, atomic registry/pending/audit repair, artifact preservation, and later normal wakeability

The exact local source-tree run also passed **50 tests** and compileall. A separate local clean editable install could not resolve `hatchling>=1.25` from the execution environment's package mirror; GitHub Actions independently completed the clean install, so that mirror failure is not treated as success.

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

The isolated Slice 10 maintenance-threshold fixture finishes with:

- `lifecycle_number = 1`
- `environment_step = 0`
- `bed-a.moisture = 0`
- `bed-b.fruit = 0`
- `water_units = 0`
- `harvested_fruit = 0`
- `objective_complete = false`
- `consecutive_failures = 3`
- `maintenance_reason = consecutive_failure_limit_reached`
- `latest_stable_event_sequence = 17`
- `event_count = 19`
- `status = maintenance_required`
- the second queued tick remains unclaimed and unconsumed

The isolated Slice 11 maintenance-inspection fixture finishes with:

- `lifecycle_number = 0`
- `environment_step = 0`
- `bed-a.moisture = 0`
- `bed-b.fruit = 0`
- `water_units = 0`
- `harvested_fruit = 0`
- `objective_complete = false`
- `consecutive_failures = 3`
- `maintenance_reason = consecutive_failure_limit_reached`
- `latest_stable_event_sequence = 6`
- `event_count = 8`
- `status = maintenance_required`
- one tick remains queued, unclaimed, and unconsumed
- API and CLI inspection change no organism file or canonical row

The isolated Slice 12 maintenance-clear fixture immediately after clear has:

- `lifecycle_number = 0`
- `environment_step = 0`
- `bed-a.moisture = 0`
- `bed-b.fruit = 0`
- `water_units = 0`
- `harvested_fruit = 0`
- `objective_complete = false`
- `consecutive_failures = 0`
- `maintenance_reason = NULL`
- `latest_stable_event_sequence = 6`
- `event_count = 9`
- `status = sleeping`
- event nine is typed administrative `maintenance_cleared`
- the queued tick remains unclaimed and unconsumed

After the preserved tick runs normally, the same fixture finishes with lifecycle one, failure streak one, stable boundary 18, event count 19, status `sleeping`, and the tick consumed. The environment remains blocked and unchanged.

The isolated Slice 13 checkpoint-retention fixture finishes with:

- `lifecycle_number = 4`
- `environment_step = 2`
- `bed-a.moisture = 1`
- `bed-b.fruit = 0`
- `water_units = 0`
- `harvested_fruit = 1`
- `objective_complete = true`
- `consecutive_failures = 0`
- `latest_stable_event_sequence = 44`
- `event_count = 46`
- `status = sleeping`
- retained checkpoint boundaries 2, 24, 34, and 44
- genesis retained and lifecycle boundary 13 pruned
- event 46 typed administrative `checkpoint_pruned`
- no retention staging directory remains
- normal wake ownership remains available

The isolated Slice 14 checkpoint-retention-failure fixture finishes with:

- `lifecycle_number = 4`
- `environment_step = 2`
- `bed-a.moisture = 1`
- `bed-b.fruit = 0`
- `water_units = 0`
- `harvested_fruit = 1`
- `objective_complete = true`
- `consecutive_failures = 0`
- `latest_stable_event_sequence = 44`
- `event_count = 46`
- `status = maintenance_required`
- `maintenance_reason = checkpoint_retention_pruning_failed`
- retained checkpoint boundaries 2, 13, 24, 34, and 44
- the staged lifecycle boundary 13 artifact is restored and validates
- event 46 typed administrative `checkpoint_retention_failed`
- no false `checkpoint_pruned` event exists
- no retention staging directory remains
- later ordinary wake rejection consumes zero clock readings

The isolated Slice 15 pending-checkpoint-repair fixture immediately after repair has:

- `lifecycle_number = 1`
- `environment_step = 1`
- `bed-a.moisture = 1`
- `bed-b.fruit = 1`
- `water_units = 0`
- `harvested_fruit = 0`
- `objective_complete = false`
- `consecutive_failures = 0`
- `latest_stable_event_sequence = 13`
- `event_count = 14`
- `status = sleeping`
- registered checkpoint boundaries 2 and 13
- event 14 typed administrative `checkpoint_registration_repaired`
- checkpoint artifacts and exact checkpoint-store bytes unchanged

Before repair, the same fixture is committed at boundary 13 with event count 13, status `checkpoint_pending`, latest stable boundary 2, and exactly one valid published but unregistered boundary-13 artifact. Missing, ambiguous, foreign, invalid, repeated, and busy attempts leave that state unchanged with zero clock reads.

After a later second tick, the repaired fixture finishes with lifecycle two, environment step two, harvested fruit one, completed objective, stable boundary 24, event count 25, status `sleeping`, and both ticks consumed.

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

After PR #29 is merged, create a new branch from current `main` and implement **Slice 16: deterministic non-canonical JSONL event export**.

The slice must:

1. start from one declared stable committed organism boundary with no pending checkpoint
2. expose an explicit administrative read-only export API and narrow CLI command, not an organism action
3. open canonical SQLite read-only and declare the exact source lineage and event boundary
4. emit deterministic JSONL ordered by canonical event sequence
5. identify export format, organism, lineage, schema, contract, and first and last event boundaries
6. use canonical JSON serialization with no wall-clock-dependent output
7. write to a bounded temporary file and publish atomically only after complete validation
8. produce byte-identical output when canonical state is unchanged
9. prove export creation, deletion, modification, and injected write failure cannot alter canonical SQLite state, checkpoint state, inbox state, or wakeability
10. pass protected tests and CI

Do not add JSONL import, lifecycle dual-writing, organism-controlled export, rollback, orphan deletion, caregiver consultation, learning, or generic planning in Slice 16.

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
