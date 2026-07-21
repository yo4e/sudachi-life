# SUDACHI Project Handoff

Last updated: July 21, 2026

## Cold-start summary

SUDACHI is a developmental artificial-life experiment built around this candidate question:

> Can a bounded artificial organism convert external cognitive scaffolding into verified local competence and retain capability while becoming less dependent on that scaffolding?

A future caregiver may be human, deterministic, model-based, hybrid, or absent. Phase 1 has no caregiver.

Successful assistance should eventually settle into verified local artifacts. Maturity is retained capability under declining caregiver access and bounded total cost, not model size, simulated affection, or uncontrolled complexity.

The repository records source and developmental decisions. One SQLite database is the canonical runtime body of each organism.

## Current state

Phase 0 architecture is frozen in:

- Minimal Organism Contract v0.2
- ADRs 0001–0006
- aligned Architecture and Roadmap documents
- protected and mutable authority rules in Contract §12
- 41 fixed Phase 1 evaluations in Contract §15

No implementation code exists yet.

Active work streams:

1. Issue #1 closes when the Contract v0.2 reconciliation pull request merges.
2. Phase 1 implementation may begin immediately after that merge.
3. Issue #3 research continues in parallel without authorizing a live caregiver.

## Normative authority

For Phase 1, use this precedence:

1. Minimal Organism Contract v0.2
2. accepted ADRs 0001–0006
3. protected tests
4. this handoff
5. explanatory architecture and roadmap documents

When sources conflict, stop and repair the contract or documentation. Do not choose private semantics in code.

## Accepted Phase 1 decisions

### Canonical state and events — ADR 0001

- one SQLite database per organism is the sole canonical live store
- state, budget ledger, inbox state, outcomes, events, provenance, and checkpoint registration share that authority
- logically related wake changes commit in one transaction
- event sequence, not timestamp, defines order
- canonical events are append-only
- JSONL is deterministic non-canonical export only
- local single-host filesystem is the Phase 1 boundary

### Time — ADR 0002

- all time access is injected
- clock readings contain UTC epoch microseconds and monotonic nanoseconds
- real operation uses a real clock; tests use explicit fake readings
- unexpected clock reads fail deterministic tests
- wall time may repeat or regress without reordering events
- current time is not a seed, identifier, or tie breaker

### Runtime locking — ADR 0003

- each wake uses a fresh SQLite connection
- fail-fast `BEGIN IMMEDIATE` occurs before mutable state is read
- the write transaction is the authoritative wake lock
- a competing wake is rejected rather than queued
- no PID file, lease row, or wall-time stale-lock rule is authoritative
- nested and hidden write connections are prohibited

### Checkpoints and rollback — ADR 0004

- initialization and every committed wake create an exact pending checkpoint boundary
- no later wake advances until the boundary is stable
- checkpoints are immutable SQLite backups with deterministic manifests
- validation includes digest, size, integrity, foreign keys, identity, versions, lineage, and event boundary
- publication is atomic on one filesystem
- checkpoint failure leaves committed state pending and blocks later wakes
- Phase 1 retains four stable lifecycle checkpoints by default
- rollback creates a pre-rollback archive and new lineage generation
- the abandoned future remains auditable

### Seed garden — ADR 0005

`seed-garden-v1` begins with:

- `bed-a`: dry sprout
- `bed-b`: mature with one fruit
- one water unit
- zero harvested fruit

The protected objective is to water the dry living plot and harvest one fruit.

One uniquely identified `synthetic:garden_tick` permits at most one mutation.

Registered actions:

- `water_plot`
- `harvest_plot`

The fixed policy waters the lexicographically first executable dry plot, otherwise harvests the first executable fruit, otherwise abstains.

There is no randomness, hidden state, natural-language parsing, autonomous ecology, mood, or caregiver.

### Budgets and energy — ADR 0006

- no scalar energy exists in Phase 1
- one wake permits one input, one observation, one action attempt, and one successful mutation
- caregiver, network, subprocess, and external mutable-write budgets are zero
- twelve semantic wake steps
- sixteen canonical wake records with terminal capacity reserved
- 2000 ms normal work deadline and 250 ms cleanup grace
- 5000 ms checkpoint deadline
- explicit database, checkpoint, working-set, retention, and failure limits
- budget is reserved before mutation
- recoverable action failure uses a savepoint so partial mutation disappears while attempt cost remains
- three classified consecutive failures enter maintenance

## Accepted Contract v0.2 boundary

### Protected from organism and caregiver

Contract, ADRs, validators, canonical schemas, fixed evaluations, permissions, action definitions, evaluator, garden fixture and objective, budget defaults, append-only enforcement, clock boundary, checkpoint and rollback machinery, source code, and migration rules.

### Mutable through bounded runtime

Lifecycle counters and allowed status, queue claim state, event additions, garden moisture and fruit, inventory, objective status, budget ledger, failure streak, maintenance reason, and checkpoint references.

### Administrative only

Initialization, input enqueue, status inspection, checkpoint repair and pruning, maintenance, rollback, quarantine, migration, and export.

Administration is not organism autonomy and must be reported separately.

### Fixed evaluations

Contract §15 defines 41 protected evaluations covering:

- deterministic inputs and clocks
- bounded lifecycle and hard-zero capabilities
- canonical seed-garden behavior
- budget reservation and failure handling
- atomic SQLite storage, append-only events, and locking
- checkpoint publication, repair, retention, rollback, and lineage
- protected authority and administrative separation

A test mapping must show where every numbered evaluation is enforced.

## Exact next implementation task

After the Contract v0.2 reconciliation pull request merges:

1. close Issue #1
2. create a Phase 1 implementation branch
3. create `pyproject.toml`, `src/sudachi_life/`, and `tests/`
4. create a visible mapping from all 41 fixed evaluations to protected tests
5. implement the smallest vertical slice:
   - protected version constants and schema definitions
   - SQLite organism initialization
   - state and schema validation
   - injected real and fake clocks
   - genesis checkpoint creation and validation
   - `sudachi init`
   - `sudachi status`
6. run tests locally and report exact results

Do not implement the full wake, garden, or rollback in the first commit merely to make the repository look complete. Build small verified slices.

## First complete Phase 1 CLI target

```text
sudachi init
sudachi enqueue synthetic:garden_tick --id tick-1
sudachi wake --seed 1
sudachi status
sudachi checkpoint repair
sudachi rollback
```

Complete wake:

```text
wake
  -> acquire fail-fast SQLite write transaction
  -> validate state and checkpoint readiness
  -> load protected concrete budgets
  -> claim one garden tick
  -> build one full sorted observation
  -> choose water, harvest, or abstention
  -> reserve budgets
  -> execute recoverable action inside a savepoint
  -> independently evaluate
  -> append outcomes, events, and ledger
  -> mark checkpoint pending and commit
  -> create and validate immutable checkpoint
  -> register checkpoint stable
  -> sleep or enter maintenance
  -> terminate
```

## Current research direction

The human caregiver remains the leading candidate for the first live developmental experiment because it avoids per-call API cost and premature provider selection.

This is not a novelty claim. Human teaching, developmental caregivers, intervention reduction, interactive task learning, Tamagotchi, Creatures, and aibo are established precedents.

The strongest current candidate for deeper novelty testing is:

> finite recorded caregiving -> verified local artifact -> retained capability -> competence-gated withdrawal -> measured independence

The failure mode is **Tamagotchi with Git**: simulated needs, affection, personality, or chat history without retained caregiver-independent competence.

No live human or model caregiver may be connected merely because an interface can be written.

## Issue map

- **Issue #1 — open until Contract v0.2 reconciliation merges:** Phase 0 contract freeze.
- **Issue #2 — closed:** Copilot architecture review.
- **Issue #3 — open and active:** caregiver withdrawal, prior work, novelty, human-caregiver, and model-provider research.
- **Issue #4 — closed and irrelevant:** accidental placeholder.

Trust current GitHub state when this map becomes stale.

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
9. research and provider documents
10. `AGENTS.md`
11. this file
12. current issues and pull requests

## End-of-session protocol

Before ending substantial work:

1. run relevant protected tests and report results
2. update contract or ADRs before implementing any changed invariant
3. update current issue and pull-request status
4. update this file with true state, failures, and one exact next action
5. ensure `AGENTS.md` points to current work streams
6. leave no required decision only in chat, model memory, or an uncommitted note

The next collaborator must resume without the conversation that created the project.

## To the next AI collaborator

Do not flatten SUDACHI into a generic autonomous-agent framework or virtual-pet presentation layer.

The center is development, not task completion or simulated affection.

Knowledge borrowed from a caregiver should eventually settle into the body. First make the body trustworthy.

**As it becomes smarter, it should become smaller and quieter.**
