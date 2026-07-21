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
- ADR 0001 for canonical state and event storage

No implementation code exists yet. This is intentional.

Active work streams:

1. Issue #1 resolves six seed ADRs and the contract review before implementation.
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

Accepted decision:

- one SQLite database per organism is the sole canonical durable store
- current state, budgets, event history, outcomes, provenance, and checkpoint metadata share that authority
- logically related lifecycle changes commit in one SQLite transaction
- canonical event order is a monotonically increasing database sequence, not a timestamp
- canonical event rows are append-only
- JSONL is a reproducible, non-canonical export only
- Phase 1 uses a local filesystem and begins from the rollback-journal model unless later ADRs justify WAL
- schema evolution is explicit, versioned, validated, transactional, and outside organism authority

See `docs/decisions/0001-state-and-event-storage.md`.

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

- **Issue #1 — open and active:** Phase 0 ADRs and contract review; implementation-critical.
- **Issue #2 — closed:** Copilot architecture review record.
- **Issue #3 — open and active:** caregiver withdrawal, prior work, novelty, and provider research.
- **Issue #4 — closed and irrelevant:** accidental placeholder.

Trust current GitHub state if this map becomes stale.

## Exact next implementation task

Proceed to ADR 0002:

`docs/decisions/0002-clock-and-determinism.md`

ADR 0002 must define:

- the clock interface
- real operational time versus injected test time
- timestamp representation and precision
- deterministic timestamp behavior
- handling of wall-clock movement and equal timestamps
- which recorded times are authoritative facts and which are presentation metadata
- compatibility with ADR 0001's rule that event sequence, not timestamp, defines canonical order

Then resolve:

1. ADR 0003 — runtime locking and duplicate wakes
2. ADR 0004 — checkpoints and rollback
3. ADR 0005 — seed environment
4. ADR 0006 — budget metaphor and energy

After all six ADRs:

1. review Minimal Organism Contract v0.1 for contradictions
2. confirm protected and mutable boundaries
3. confirm fixed Phase 1 evaluations
4. update this handoff
5. create `pyproject.toml`, `src/sudachi_life/`, and `tests/`

Do not implement unresolved semantics. Follow `docs/IMPLEMENTATION_DISCIPLINE.md`.

## First implementation target

Possible minimal CLI:

```text
sudachi init
sudachi enqueue synthetic:file_changed
sudachi wake --seed 1
sudachi status
```

Lifecycle:

```text
wake
  -> acquire lock
  -> validate state
  -> read bounded input
  -> choose at most one registered action
  -> consume budgets
  -> evaluate
  -> persist state and append events atomically
  -> create or confirm checkpoint
  -> release lock
  -> sleep and exit
```

Do not call a caregiver yet.

## Initial fixed evaluation themes

The contract remains authoritative. Tests must cover at least:

- deterministic results for identical declared inputs
- bounded steps and time
- sandboxed effects
- no silent state corruption
- append-only event history
- nonnegative budgets
- protected configuration
- rollback
- duplicate-wake rejection
- explicit abstention and budget exhaustion
- no network or caregiver requirement

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
