# SUDACHI Project Handoff

Last updated: July 21, 2026

## Cold-start summary

SUDACHI is a developmental artificial-life experiment built around this candidate question:

> Can a bounded artificial organism convert external cognitive scaffolding into verified local competence and retain capability while becoming less dependent on that scaffolding?

A future caregiver may be human, deterministic, model-based, hybrid, or absent. Phase 1 has no caregiver.

One SQLite database is the canonical runtime body of each organism. The repository records source, contract, decisions, tests, and developmental history.

## Normative authority

For Phase 1, use this precedence:

1. Minimal Organism Contract v0.2
2. accepted ADRs 0001–0006
3. protected tests and `docs/PHASE1_TEST_MATRIX.md`
4. this handoff
5. explanatory architecture and roadmap documents

When sources conflict, stop and repair the contract or documentation. Do not choose private semantics in code.

## Current state

Phase 0 is complete. Issue #1 is closed.

Issue #13 tracks Phase 1 implementation. The first implementation slice exists on the `agent/phase1-genesis` branch and includes:

- Python package configuration and CLI entry point
- protected contract, schema, environment, and budget constants
- injected real and deterministic fake clocks
- validated runtime paths and organism identifiers
- canonical SQLite schema initialization
- protected `seed-garden-v1` genesis state
- exact protected budget configuration in canonical state
- append-only event triggers
- immutable genesis checkpoint creation through SQLite backup
- checkpoint manifest, digest, integrity, foreign-key, identity, version, lineage, and event-boundary validation
- checkpoint publication and registration
- `sudachi init`
- `sudachi status`
- an explicit mapping from Contract v0.2 §15 evaluations to implemented or planned tests

The slice does **not** yet implement:

- enqueueing garden ticks
- the normal wake transaction
- duplicate-wake tests
- water, harvest, or abstention behavior
- per-wake action budget ledgers and savepoint failure handling
- post-wake checkpoint stabilization
- checkpoint repair or retention pruning
- rollback
- JSONL export
- all 41 protected evaluations

No live human, fixture, or model caregiver is connected.

## Verified implementation results

The final local equivalent of the branch was validated with:

- `16 passed` under pytest
- successful `python -m compileall` for `src` and `tests`
- successful editable package installation in a clean virtual environment with no project dependencies
- successful real CLI smoke run for `init` and `status`

No GitHub Actions workflow exists yet, so these results are local validation rather than remote CI.

Two implementation defects were caught before handoff:

1. refusing duplicate initialization originally consumed an unnecessary fake-clock reading; initialization now checks existence before reading time
2. read-only SQLite URI construction originally risked misinterpreting `?` or `#` in filesystem paths; it now uses `Path.as_uri()` and has a regression test

Checkpoint validation was also strengthened to verify budget configuration, snapshot method, database filename, manifest status, directory name, pending lineage, and protected byte limits.

## Accepted Phase 1 baseline

### Canonical body

- one SQLite database per organism
- canonical events are append-only and ordered by integer sequence
- JSONL is non-canonical export only
- local single-host filesystem boundary

### Time

- all time access is injected
- real clock in operation, fake clock in deterministic tests
- UTC epoch microseconds and monotonic nanoseconds
- current time is not a seed, identifier, or tie breaker

### Locking

- each normal wake will use a fresh connection
- fail-fast `BEGIN IMMEDIATE` occurs before mutable state is read
- a competing wake is rejected rather than queued
- no PID file, lease row, or stale wall-time lock

### Checkpoints

- genesis and every committed wake establish an exact pending boundary
- no later wake advances until the boundary is stable
- checkpoints are immutable SQLite backups with deterministic manifests
- invalid or incomplete artifacts are never registered stable
- rollback will preserve the abandoned future and create a new lineage generation

### Seed garden

Genesis state:

- `bed-a`: dry sprout
- `bed-b`: mature with one fruit
- one water unit
- zero harvested fruit

The protected policy will water the lexicographically first executable dry plot, otherwise harvest the first executable fruit, otherwise abstain.

### Concrete budgets

- no scalar energy
- one input, one observation, one action attempt, and one successful mutation per accepted wake
- zero caregiver, network, subprocess, and authoritative external-write capability
- twelve semantic wake steps
- bounded canonical records, monotonic time, database bytes, checkpoint bytes, working set, retention, and consecutive failures

## Current issue map

- **Issue #1 — closed:** Phase 0 contract freeze.
- **Issue #2 — closed:** Copilot architecture review.
- **Issue #3 — open and active:** caregiver withdrawal, prior work, novelty, human-caregiver, and model-provider research.
- **Issue #13 — open and active:** Phase 1 SUDACHI-0 metabolism implementation.

Always verify current GitHub state.

## Exact next implementation task

After the genesis slice is merged:

1. create a new branch from current `main`
2. implement idempotent enqueueing of uniquely identified `synthetic:garden_tick` events
3. implement fail-fast `BEGIN IMMEDIATE` wake acquisition before any mutable read
4. add real competing-connection tests proving one winner and one non-queued busy rejection
5. build one stable sorted garden observation inside the acquired transaction
6. update `docs/PHASE1_TEST_MATRIX.md` and Issue #13

Do not add water or harvest mutation until enqueue, acquisition, and observation boundaries are protected by tests.

## First complete Phase 1 CLI target

```text
sudachi init
sudachi enqueue synthetic:garden_tick --id tick-1
sudachi wake --seed 1
sudachi status
sudachi checkpoint repair
sudachi rollback
```

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
10. research and provider documents
11. `AGENTS.md`
12. this file
13. current issues and pull requests

## End-of-session protocol

Before ending substantial work:

1. run relevant protected tests and report exact results
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
