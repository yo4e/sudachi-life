# SUDACHI Project Handoff

Last updated: July 21, 2026

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

Implemented and verified in PR #18:

- the fixed policy reuses the same lifecycle and selects `harvest_plot(bed-b)` when no water target remains
- the executor removes exactly one fruit and increments harvested inventory inside a savepoint
- the evaluator independently proves the transition and changes objective completion from false to true
- the second pending boundary is event sequence 24
- administrative checkpoint stabilization is event sequence 25
- the organism returns to `sleeping` at lifecycle 2
- a third mutating wake is rejected and fully rolled back because objective-complete abstention is not implemented yet

No live human, fixture, or model caregiver is connected.

## Verified implementation results

GitHub Actions passed on PR #18 with Python 3.12:

- clean editable installation
- `python -m compileall -q src tests`
- **28 protected tests**
- installed genesis CLI smoke test
- protected two-wake CLI path: water, harvest, completed objective, checkpoint, and sleep

A separate clean local virtual environment also completed:

```text
init -> enqueue tick-1 -> wake -> enqueue tick-2 -> wake -> status
```

Final canonical values were:

- `lifecycle_number = 2`
- `environment_step = 2`
- `bed-a.moisture = 1`
- `bed-b.fruit = 0`
- `water_units = 0`
- `harvested_fruit = 1`
- `objective_complete = true`
- `latest_stable_event_sequence = 24`
- `event_count = 25`
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

After PR #18 is merged, create a new branch from current `main` and implement **Slice 5: the canonical objective-complete abstention**.

The slice must:

1. enqueue and claim the third canonical garden tick
2. build the complete observation showing `objective_complete = true`
3. select a typed `objective_already_complete` abstention
4. consume one input and one observation
5. consume zero action attempts and zero environment mutations
6. leave plots, inventory, environment step, and objective unchanged
7. append bounded abstention, evaluation, and budget records
8. consume the tick and commit an exact pending boundary
9. create and register a stable checkpoint
10. reset the justified failure streak to zero
11. return to sleep and terminate
12. prove the canonical three-wake run in protected tests and CI

Do not add other failure classes, checkpoint repair, rollback, caregiver consultation, learning, or generic planning in Slice 5.

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
