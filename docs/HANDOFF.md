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

Merged through PR #14.

- Python package and primary CLI
- canonical SQLite schema and protected versions
- injected real and fake clocks
- protected `seed-garden-v1` genesis state
- exact budget configuration
- append-only event enforcement
- immutable verified genesis checkpoint
- `sudachi init` and `sudachi status`

### Slice 2 — inbox, wake ownership, and observation

Merged through PR #15.

- idempotent `synthetic:garden_tick` enqueueing
- no duplicate event or hidden clock read on replay
- fail-fast `BEGIN IMMEDIATE` wake ownership
- non-queued competing-wake rejection
- oldest-tick claim inside the transaction
- deterministic sorted garden observation

### Slice 3 — first canonical water wake

Implemented and verified in PR #17.

- primary CLI enqueue and wake commands
- protected per-wake budget ledger
- fixed selection of `water_plot(bed-a)`
- action-attempt and mutation reservation before state change
- SQLite savepoint execution
- independent transition and objective evaluation
- tick consumption and bounded append-only lifecycle records
- exact checkpoint-pending commit at event sequence 13
- verified lifecycle checkpoint and administrative stabilization at event sequence 14
- return to sleeping state
- checkpoint timeout leaves committed pending state

No live human, fixture, or model caregiver is connected.

## Verified implementation results

GitHub Actions passed on PR #17 with Python 3.12:

- clean editable installation
- `python -m compileall -q src tests`
- **25 protected tests**
- the installed genesis CLI smoke test
- exact first-water state, budget, event, checkpoint, and sleep assertions through protected tests

A broader local development suite also passed before the branch was reduced to its final protected test set.

## Integration repair record

PR #15 was accidentally merged before its required foundation in PR #14. PR #16 repaired the order, introduced clean-checkout CI, and verified the combined baseline with 23 tests. This was an integration defect, not a contract change.

## Accepted Phase 1 baseline

- one canonical SQLite database per organism
- event sequence, not timestamp, defines canonical order
- injected wall and monotonic time
- fail-fast SQLite write ownership
- one input, observation, action attempt, and successful mutation at most per wake
- zero caregiver, network, subprocess, and authoritative external-write capability
- no scalar energy
- immutable checkpoint after every committed wake before another wake
- rollback will preserve the abandoned future and create a new lineage generation

The first canonical wake changes only:

- `bed-a.moisture`: `0 -> 1`
- `water_units`: `1 -> 0`
- `environment_step`: `0 -> 1`
- `lifecycle_number`: `0 -> 1`

`bed-b` retains one fruit and the objective remains incomplete.

## Exact next implementation task

After PR #17 is merged, create a new branch from current `main` and implement **Slice 4: the canonical harvest wake**.

The slice must:

1. reuse the existing enqueue, lock, observation, budget, event, and checkpoint boundaries
2. select `harvest_plot(bed-b)` through the fixed policy
3. reserve attempt and mutation budgets before change
4. execute the exact harvest transition inside a savepoint
5. independently verify fruit, inventory, environment step, and objective completion
6. consume one new tick
7. commit a bounded pending boundary
8. create and register a stable checkpoint
9. return to sleep
10. prove the second wake in protected tests and CI

Do not add objective-complete abstention, rollback, caregiver consultation, learning, or generic planning in Slice 4.

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
