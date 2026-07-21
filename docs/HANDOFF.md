# SUDACHI Project Handoff

Last updated: July 21, 2026

## Cold-start summary

SUDACHI is a developmental artificial-life experiment built around this candidate question:

> Can a bounded artificial organism convert external cognitive scaffolding into verified local competence and retain capability while becoming less dependent on that scaffolding?

A future caregiver may be human, deterministic, model-based, hybrid, or absent. Phase 1 has no caregiver.

One SQLite database is the canonical runtime body of each organism. The repository records source, contract, decisions, protected tests, and developmental history.

## Normative authority

For Phase 1, use this precedence:

1. Minimal Organism Contract v0.2
2. accepted ADRs 0001–0006
3. protected tests and `docs/PHASE1_TEST_MATRIX.md`
4. this handoff
5. explanatory architecture and roadmap documents

When sources conflict, stop and repair the contract, test, or documentation. Do not choose private semantics in code.

## Current state

Phase 0 is complete. Issue #1 is closed.

Issue #13 tracks Phase 1 implementation.

The following implementation slices are on `main`:

### Slice 1 — foundation and genesis

Merged through PR #14.

- Python 3.12+ package and `sudachi` CLI entry point
- protected contract, schema, environment, checkpoint, and budget constants
- injected real and deterministic fake clocks
- validated organism identifiers and runtime paths
- canonical SQLite schema initialization
- protected `seed-garden-v1` genesis state
- exact protected budget configuration in canonical state
- database-level append-only event triggers
- immutable genesis checkpoint creation through SQLite backup
- checkpoint manifest, digest, integrity, foreign-key, identity, version, lineage, boundary, and byte-limit validation
- checkpoint publication and registration
- `sudachi init`
- `sudachi status`
- initial Contract v0.2 evaluation-to-test mapping

### Slice 2 — inbox, wake acquisition, and observation

Merged through PR #15.

- idempotent enqueueing of uniquely identified `synthetic:garden_tick` inputs through the administrative Python API
- one canonical enqueue event for first receipt only
- no hidden clock read on duplicate input replay
- fail-fast wake ownership through a fresh SQLite connection and `BEGIN IMMEDIATE`
- mutable-state validation only after lock acquisition
- immediate non-queued rejection of a competing wake
- one oldest eligible tick claimed inside the transaction
- rollback of incomplete claim state
- one fully deterministic sorted garden observation

`WakeTransaction` remains deliberately rollback-only. No normal wake can commit yet.

No live human, fixture, or model caregiver is connected.

## Integration repair record

PR #15 was accidentally merged before its required foundation in PR #14. The repository temporarily contained Slice 2 modules without the Slice 1 package body.

The repair was:

1. merge PR #14 into the then-current `main`, preserving the already merged Slice 2 files
2. add a clean-checkout GitHub Actions workflow in PR #16
3. run installation, compilation, all protected tests, and real CLI smoke checks against the combined tree
4. repair one stale checkpoint-corruption test fixture so it isolates digest corruption instead of failing earlier on the intentionally protected directory-name invariant
5. correct the CI smoke expectation from two genesis events to the canonical three events after stable checkpoint registration

This was an integration-order defect, not an accepted contract change.

## Verified implementation results

GitHub Actions now provides the clean-checkout source of truth for each push to `main` and each pull request.

The repaired combined foundation passed:

- package installation on Python 3.12
- `python -m compileall -q src tests`
- **23 protected tests**
- real `sudachi init` CLI execution
- real `sudachi status` CLI execution
- stable genesis checkpoint identity checks
- protected initial garden-state checks

Earlier local checks also caught and repaired:

- an unnecessary fake-clock read during duplicate initialization rejection
- unsafe manual construction of read-only SQLite URIs when paths contain `?` or `#`
- incomplete checkpoint manifest and byte-limit validation

## Accepted Phase 1 baseline

### Canonical body

- one SQLite database per organism
- canonical events are append-only and ordered by integer sequence
- JSONL is non-canonical export only
- local single-host filesystem boundary

### Time

- all time access is injected
- real clock in operation and explicit fake readings in deterministic tests
- UTC epoch microseconds and monotonic nanoseconds
- current time is not a seed, identifier, or tie breaker

### Locking

- each normal wake uses a fresh connection
- fail-fast `BEGIN IMMEDIATE` occurs before mutable state is read
- a competing wake is rejected rather than queued
- no PID file, lease row, or wall-time stale-lock authority

### Checkpoints

- genesis and every committed wake establish an exact pending boundary
- no later wake advances until that boundary is stable
- checkpoints are immutable SQLite backups with deterministic manifests
- invalid or incomplete artifacts are never registered stable
- rollback will preserve the abandoned future and create a new lineage generation

### Seed garden

Genesis state:

- `bed-a`: dry sprout
- `bed-b`: mature with one fruit
- one water unit
- zero harvested fruit

The protected policy waters the lexicographically first executable dry plot, otherwise harvests the first executable fruit, otherwise abstains.

### Concrete budgets

- no scalar energy
- one input, one observation, one action attempt, and one successful mutation per accepted wake
- zero caregiver, network, subprocess, and authoritative external-write capability
- twelve semantic wake steps
- bounded canonical records, monotonic time, database bytes, checkpoint bytes, working set, retention, and consecutive failures

## Exact next implementation task

Create a new branch from current `main` and implement **Slice 3: the first canonical water wake**.

The slice must:

1. wire garden-tick enqueueing into the primary CLI
2. load protected per-wake budget counters
3. claim one oldest tick under the existing fail-fast wake transaction
4. produce the deterministic full observation
5. select `water_plot(bed-a)` through the fixed protected policy
6. reserve action-attempt and mutation budgets before state change
7. execute the transition inside a SQLite savepoint
8. independently evaluate the observed result
9. consume the claimed tick
10. append the bounded lifecycle event and usage records
11. commit one exact checkpoint-pending boundary
12. create, validate, publish, and register the stable post-wake checkpoint
13. return the organism to sleeping state and terminate
14. prove the complete wake with protected tests and CI

Do not implement harvest, objective-complete abstention, rollback, caregiver consultation, learning, or generic planning in Slice 3.

## First complete Phase 1 CLI target

```text
sudachi init
sudachi enqueue synthetic:garden_tick --id tick-1
sudachi wake --seed 1
sudachi status
sudachi checkpoint repair
sudachi rollback
```

Only `init` and `status` are currently wired to the primary CLI. Slice 2 enqueueing exists as a protected Python administrative API.

## Current issue map

- **Issue #1 — closed:** Phase 0 contract freeze.
- **Issue #2 — closed:** Copilot architecture review.
- **Issue #3 — open and active:** caregiver withdrawal, prior work, novelty, human-caregiver, and model-provider research.
- **Issue #13 — open and active:** Phase 1 SUDACHI-0 metabolism implementation.

Always verify current GitHub state.

## Current research direction

The human caregiver remains the leading candidate for the first live developmental experiment because it avoids per-call API cost and premature provider selection.

This is not a novelty claim. Human teaching, developmental caregivers, intervention reduction, interactive task learning, Tamagotchi, Creatures, and aibo are established precedents.

The strongest current candidate for deeper novelty testing remains:

> finite recorded caregiving -> verified local artifact -> retained capability -> competence-gated withdrawal -> measured independence

The failure mode is **Tamagotchi with Git**: simulated needs, affection, personality, or chat history without retained caregiver-independent competence.

No live caregiver may be connected merely because an interface can be written.

## Do not add during Phase 1

- a human or model caregiver
- chat or natural-language action selection
- network or subprocess access
- organism-writable external files
- arbitrary code or shell execution
- continuous operation
- learning, memory, skills, consolidation, or fading
- scalar energy, mood, affection, or personality
- large vector databases or multi-agent systems
- unrestricted self-modification

## Reading order

1. `README.md`
2. `docs/CHATGPT_PROJECT_HANDOFF.md`
3. `docs/ORIGIN.md`
4. `docs/MINIMAL_ORGANISM_CONTRACT.md`
5. `docs/decisions/` in numeric order
6. `docs/ARCHITECTURE.md`
7. `docs/ROADMAP.md`
8. `docs/IMPLEMENTATION_DISCIPLINE.md`
9. `docs/PHASE1_TEST_MATRIX.md`
10. `docs/phase1/SLICE2_INBOX_WAKE.md`
11. research and provider documents
12. `AGENTS.md`
13. this file
14. current issues, pull requests, and CI state

## End-of-session protocol

Before ending substantial work:

1. run relevant protected tests in CI and report exact results
2. update contract or ADRs before implementing changed invariants
3. update the test matrix, issue, and pull-request status
4. update this file with true state, failures, and one exact next action
5. ensure `AGENTS.md` points to current work streams
6. leave no required decision only in chat, model memory, or an uncommitted note

The next collaborator must resume without the conversation that created the project.

## To the next AI collaborator

Do not flatten SUDACHI into a generic autonomous-agent framework or virtual-pet presentation layer.

The center is development, not task completion or simulated affection.

Knowledge borrowed from a caregiver should eventually settle into the body. First make the body trustworthy.

**As it becomes smarter, it should become smaller and quieter.**
