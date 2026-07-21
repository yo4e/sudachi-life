# SUDACHI Project Handoff

Last updated: July 21, 2026

## Cold-start summary

SUDACHI is a developmental artificial-life experiment built around this candidate question:

> Can a bounded artificial organism convert external cognitive scaffolding into verified local competence and retain capability while becoming less dependent on that scaffolding?

The caregiver may be human, deterministic, model-based, hybrid, or absent in a control condition. The architecture does not assume that the caregiver is an AI model or named product.

Successful assistance should settle into verified experience, tested skills, deterministic routines, or other inspectable local artifacts. Maturity is retained capability under declining caregiver access and bounded total cost.

The repository is the organism's body, developmental record, skill substrate, and auditable lineage. A language model may be an organ or caregiver, but it is not the organism.

## Current state

The repository contains:

- founding concept, roadmap, architecture, and Minimal Organism Contract v0.1
- implementation discipline and cold-start continuity documents
- active caregiver-withdrawal, prior-work, and provider research
- preliminary evidence, model-caregiver, and human-caregiver research notes
- accepted ADRs 0001–0006 for the complete seed architecture

No implementation code exists yet. This is intentional.

Active work streams:

1. Issue #1 now moves from seed ADRs to contract reconciliation, protected boundaries, and fixed evaluations before implementation.
2. Issue #3 continues prior-work, caregiver-design, novelty, and model-provider research.

Phase 1 remains deterministic, local, network-free, and caregiver-free.

## Accepted decisions

- Project name: **SUDACHI**
- First organism: provisional name **SUDACHI-0**
- Runtime model: one bounded lifecycle followed by process termination
- Initial environment: local execution with no network access
- Phase 1 caregiver consultation budget: zero
- A deterministic fixture may later verify consultation plumbing
- Repository language: English, except for the two intentional Japanese etymology lines in `README.md`
- SUDACHI-0 will not initially rewrite its own source code
- Model-weight development remains disabled without an explicit provider- and model-specific review
- Candidate novelty claims remain hypotheses
- Architecture decisions must be recorded as ADRs before implementation

### ADR 0001 — state and event storage

- one SQLite database per organism is the sole canonical durable store
- state, budgets, event history, outcomes, provenance, and checkpoint metadata share that authority
- logically related lifecycle changes commit in one SQLite transaction
- canonical event order is a monotonically increasing database sequence, not a timestamp
- canonical event rows are append-only
- JSONL is a reproducible, non-canonical export only
- Phase 1 starts from SQLite's rollback-journal model unless later ADRs justify WAL
- schema evolution is explicit, versioned, validated, transactional, and outside organism authority

See `docs/decisions/0001-state-and-event-storage.md`.

### ADR 0002 — clock and determinism

- every time read goes through an injected clock boundary
- a clock reading contains integer UTC epoch microseconds and monotonic nanoseconds
- operational runs use a real clock; tests and replay use an explicit fake clock
- unexpected extra fake-clock reads fail deterministic tests
- canonical wall timestamps are SQLite integers; ISO 8601 strings are derived presentation
- elapsed-time budgets and deadlines use monotonic time
- event sequence remains authoritative when wall time repeats or moves backward
- current time may not be an implicit seed, identifier, or tie breaker

See `docs/decisions/0002-clock-and-determinism.md`.

### ADR 0003 — runtime locking

- one fresh SQLite connection executes `BEGIN IMMEDIATE` before reading mutable state
- the SQLite write transaction is the authoritative wake lock
- acquisition is fail-fast; a busy attempt is rejected rather than queued
- the same transaction spans the bounded canonical wake and atomic persistence
- no committed lease row, PID file, wall-time expiry, or in-process mutex is a second authority
- a crashed or closed connection releases the file lock and rolls back uncommitted changes
- process identity is non-canonical diagnostic metadata
- nested and reentrant wakes are prohibited
- later interactive caregiver phases must separate long proposal work from a short adoption transaction

See `docs/decisions/0003-runtime-locking.md`.

### ADR 0004 — checkpoints and rollback

- initialization and every committed wake outcome establish an exact pending checkpoint boundary
- another wake cannot advance until that boundary has a verified stable checkpoint
- checkpoint artifacts are immutable directories containing a SQLite backup and deterministic manifest
- Python's SQLite Online Backup interface creates the snapshot; ordinary live-file copying is prohibited
- candidate snapshots require digest, size, integrity, foreign-key, identity, schema, contract, lineage, and event-boundary validation
- temporary artifacts become valid only through atomic same-filesystem publication
- checkpoint registration is a short canonical transaction and does not recursively require another checkpoint
- checkpoint failure preserves committed state but blocks future wakes until repair
- Phase 1 retains a bounded default of four stable lifecycle checkpoints and creates a genesis checkpoint before waking
- rollback is an explicit offline administrative operation with a verified pre-rollback archive
- rollback increments lineage generation and preserves the abandoned future for audit
- Phase 1 checkpoints cover canonical SQLite state only

See `docs/decisions/0004-checkpoints.md`.

### ADR 0005 — seed environment

- Phase 1 uses `seed-garden-v1`, a fully observable two-plot virtual garden stored entirely in SQLite
- initial state contains a dry sprout in `bed-a`, one mature fruit in `bed-b`, and one water unit
- the fixed objective requires watering the sprout and harvesting one fruit
- the only normal external trigger is a uniquely identified `synthetic:garden_tick`
- one wake processes at most one tick and performs at most one mutating action
- registered mutating actions are `water_plot` and `harvest_plot`
- the fixed policy waters the lexicographically first executable dry living plot, otherwise harvests the first executable mature fruit, otherwise abstains
- invalid actions are rejected atomically without incrementing the environment step
- there is no randomness, autonomous ecology, hidden state, mood, or natural-language parsing in Phase 1
- observations, transitions, objectives, and action schemas are protected and versioned
- the canonical run waters, harvests, then records post-completion abstention across three wakes

See `docs/decisions/0005-seed-environment.md`.

### ADR 0006 — budgets and energy

- Phase 1 has no independent scalar energy state
- concrete budgets are separated into per-wake decision budgets, a protected lifecycle safety envelope, and persistent maintenance/storage limits
- per-wake limits allow one input event, one observation, one action attempt, and one successful environment mutation
- caregiver consultations, network calls, subprocess calls, and authoritative external writes are exactly zero
- the normal lifecycle has twelve semantic steps, sixteen canonical record slots, a 2000 ms monotonic work limit, and 250 ms cleanup grace
- checkpoint stabilization has a separate 5000 ms maintenance limit
- active database, checkpoint artifact, checkpoint store, and runtime working-set byte limits are explicit and protected
- per-wake unused budget does not accumulate
- action attempts are charged before execution; successful mutations are reserved after preconditions pass
- recoverable action failures use a savepoint so attempt cost and failure history survive without partial environment mutation
- justified abstention has minimal explicit cost
- three consecutive classified failures enter protected maintenance state
- status exposes the concrete budget vector; no canonical energy percentage exists

See `docs/decisions/0006-budget-metaphor.md`.

## Current research direction

Not yet a final caregiver architecture decision:

- define the parent by function as an external caregiver or cognitive-scaffolding source
- treat a human chat caregiver as the leading candidate for the first live experiment
- keep the interface source-neutral across deterministic, human, local-model, hosted-model, hybrid, and no-caregiver conditions
- treat caregiver messages as proposals rather than direct commands
- measure human time, consultations, clarification, latency, and hidden intervention
- define maturity as retained capability after caregiver access is reduced or withheld
- reject “Tamagotchi with Git”: personality or care presentation without retained caregiver-independent competence

## Reading order

1. `README.md`
2. `docs/CHATGPT_PROJECT_HANDOFF.md`
3. `docs/ORIGIN.md`
4. `docs/MINIMAL_ORGANISM_CONTRACT.md`
5. `docs/ROADMAP.md`
6. `docs/ARCHITECTURE.md`
7. `docs/IMPLEMENTATION_DISCIPLINE.md`
8. `docs/RESEARCH_QUESTIONS.md`
9. `docs/PARENT_MODEL_PROVIDER_REVIEW.md`
10. `docs/research/INITIAL_EVIDENCE_MAP.md`
11. `docs/research/PARENT_MODEL_STRATEGY.md`
12. `docs/research/HUMAN_CAREGIVER_HYPOTHESIS.md`
13. accepted files in `docs/decisions/`, in numeric order
14. `AGENTS.md`
15. this file

Then inspect current GitHub issues and open pull requests.

## Issue map

- **Issue #1 — open and active:** contract reconciliation, protected boundaries, and fixed Phase 1 evaluations; implementation-critical.
- **Issue #2 — closed:** Copilot architecture review record.
- **Issue #3 — open and active:** caregiver withdrawal, prior work, novelty, and provider research.
- **Issue #4 — closed and irrelevant:** accidental placeholder.

Trust current GitHub state if this map becomes stale.

## Exact next implementation task

Review `docs/MINIMAL_ORGANISM_CONTRACT.md` against ADRs 0001–0006.

The review must resolve at least:

- parent-model wording versus caregiver-neutral Phase 1
- event fields and timestamp semantics versus ADRs 0001 and 0002
- one-transaction lifecycle semantics versus pending/stable checkpoint staging
- duplicate-wake rejection versus any durable lock-record assumptions
- checkpoint representation, rollback lineage, and abandoned-history preservation
- the exact seed-garden observation, action, outcome, and abstention contracts
- concrete budget names, defaults, reset rules, maintenance thresholds, and zero-capability interfaces
- whether every fixed evaluation maps to one accepted invariant without contradiction
- protected versus mutable state and administrative authority

After contract reconciliation:

1. update affected architecture and roadmap language
2. confirm protected and mutable boundaries in one authoritative section
3. confirm the normalized Phase 1 evaluation list
4. update Issue #1 and this handoff
5. only then create `pyproject.toml`, `src/sudachi_life/`, and `tests/`

Do not create implementation code before this review is accepted.

## First implementation target

Possible minimal CLI:

```text
sudachi init
sudachi enqueue synthetic:garden_tick --id tick-1
sudachi wake --seed 1
sudachi status
sudachi checkpoint repair
sudachi rollback
```

Lifecycle:

```text
wake
  -> acquire fail-fast SQLite write transaction
  -> validate state, maintenance, and checkpoint readiness
  -> load protected concrete budgets
  -> claim one garden tick
  -> produce one full sorted observation
  -> choose at most one registered action or abstain
  -> reserve budgets before mutation
  -> execute inside a savepoint and evaluate
  -> persist outcome, usage ledger, failure streak, and checkpoint pending
  -> commit
  -> create, validate, and publish checkpoint
  -> register checkpoint stable
  -> close connection
  -> sleep and exit
```

Do not call a caregiver yet.

## Initial fixed evaluation themes

The contract remains authoritative until reconciliation. The accepted ADRs require tests for at least:

- deterministic garden results for identical state, event, clock, seed, environment, and budget configuration
- injected time and monotonic deadline behavior
- one tick and at most one mutating action per wake
- stable observation and tie-break ordering
- action precondition and budget reservation before mutation
- invalid-action savepoint rollback with attempt cost preserved
- duplicate external-event idempotency
- fail-fast duplicate-wake rejection with competing SQLite connections
- state/event atomicity and append-only history
- no negative counters
- explicit exhaustion, abstention, checkpoint-required, and maintenance outcomes
- verified checkpoint publication, retention, repair, and rollback lineage
- protected configuration and evaluation
- zero network, subprocess, external mutable write, and caregiver interfaces
- no independent energy field

## Active research status

Established neighboring ideas include digital organisms, human feedback, language teaching, developmental caregivers, intervention gating, distillation, executable skill libraries, model routing, Tamagotchi, Creatures, and aibo.

Therefore, “an artificial creature raised by a human” is not a novelty claim.

The strongest current candidate for deeper testing is:

> finite recorded caregiving -> verified local artifact -> retained capability -> competence-gated withdrawal -> measured independence

No live human or model caregiver may be connected merely because an interface can be written.

## Do not implement yet

- unrestricted internet exploration
- continuous always-on execution
- unrestricted self-modification
- model training or routine LoRA updates
- a large vector database
- a multi-agent society
- a physical robot body
- replication outside the repository
- personality performance before life mechanisms
- a live named model caregiver
- a free-form human chat channel that bypasses registered actions or protected policy

## End-of-session protocol

Before ending substantial work:

1. update accepted ADRs and affected documentation
2. update relevant issue checklists and status
3. update this file with the true state and one exact next action
4. ensure `AGENTS.md` points to current files and work streams
5. leave no required decision only in chat, model memory, or an uncommitted note
6. record failures, uncertainty, and deferred questions plainly

The next collaborator must be able to resume without access to the conversation that created the project.

## To the next AI collaborator

Do not flatten SUDACHI into a generic autonomous-agent framework or virtual-pet presentation layer.

The center is development, not task completion or simulated affection.

Knowledge borrowed from a caregiver should settle into the body. The organism should gradually do more without asking and carry itself into another day within finite resources.

**As it becomes smarter, it should become smaller and quieter.**
