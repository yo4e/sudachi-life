# SUDACHI Roadmap

This roadmap is developmental rather than feature-driven. Each phase must establish a measurable invariant before the next layer of assistance or autonomy is introduced.

The normative Phase 1 baseline is Minimal Organism Contract v0.2 plus ADRs 0001–0006.

## Phase 0 — Freeze the seed organism contract

**Status:** Complete when the Contract v0.2 reconciliation pull request is merged and Issue #1 is closed.

**Goal:** Define the smallest trustworthy lifecycle that may be called SUDACHI-0.

Accepted deliverables:

- ADR 0001 — SQLite canonical state and append-only event history
- ADR 0002 — injected real and fake clocks
- ADR 0003 — fail-fast SQLite runtime locking
- ADR 0004 — verified checkpoints and rollback lineage
- ADR 0005 — deterministic two-plot seed garden
- ADR 0006 — concrete budgets with no scalar energy
- Minimal Organism Contract v0.2
- protected and mutable authority boundaries
- 41 fixed Phase 1 evaluations

Exit criteria:

- One complete lifecycle can be described without a caregiver or language model.
- Every mutable effect has one canonical authority and transaction boundary.
- Duplicate wakes, corruption, exhaustion, checkpoint failure, and rollback have explicit outcomes.
- Success cannot be manufactured by weakening the evaluator or budgets.
- No unresolved seed architecture choice remains for implementation code to invent.

## Phase 1 — Build SUDACHI-0 metabolism

**Goal:** Implement Contract v0.2 exactly in local Python.

Canonical lifecycle:

```text
wake
  -> acquire fail-fast SQLite write transaction
  -> validate state and checkpoint readiness
  -> load protected concrete budgets
  -> claim one synthetic:garden_tick
  -> build one full sorted observation
  -> choose water, harvest, or abstention
  -> reserve budgets before mutation
  -> execute recoverable action inside a savepoint
  -> independently evaluate
  -> append events and usage ledger
  -> commit with checkpoint pending
  -> create and validate immutable SQLite checkpoint
  -> register checkpoint stable
  -> sleep or enter maintenance
  -> terminate
```

Deliverables:

- Python 3.12+ package and CLI
- canonical SQLite schema and versioning
- contract and state validators
- injected real and fake clocks
- fail-fast duplicate-wake rejection using competing SQLite connections
- `seed-garden-v1`
- action registry for `water_plot` and `harvest_plot`
- explicit abstention and typed failures
- concrete budget ledger and storage limits
- checkpoint publication, repair, retention, and rollback lineage
- deterministic JSONL export
- all protected Contract v0.2 tests

Exit criteria:

- The canonical three-wake garden run waters, harvests, and abstains reproducibly.
- All 41 fixed evaluations pass.
- No caregiver, network, subprocess, arbitrary code execution, or external mutable write is available.
- A crash before commit preserves prior canonical state.
- Every committed wake becomes checkpoint-stable before another wake.
- Rollback preserves the abandoned future and produces a distinct lineage generation.

Phase 1 does not demonstrate learning, intelligence, personality, or caregiver independence. It demonstrates trustworthy metabolism.

## Phase 2 — Build caregiver-neutral consultation plumbing

**Goal:** Prove the consultation boundary without a live human or model caregiver.

Deliverables:

- source-neutral caregiver request and response schemas
- typed response classes such as demonstration, correction, constraint, explanation, preference, question, defer, and abstain
- deterministic fixture caregiver
- consultation provenance and cost ledger
- proposal parsing and validation
- strict separation between consultation, interpretation, evaluation, and adoption
- protected tests proving that a caregiver cannot execute actions or mutate state directly
- no-caregiver and fixture-caregiver comparison conditions

Exit criteria:

- Every consultation has a declared reason, source, cost, context summary, and outcome.
- Fixture output cannot bypass action schemas, budgets, checkpointing, or evaluation.
- Long consultation work occurs outside the short adoption transaction.
- Phase 1 behavior remains available with caregiver budget zero.

This phase does not require a commercial API or public human participants.

## Phase 3 — Run the first bounded human-caregiver experiment

**Goal:** Test whether finite human scaffolding can become verified local competence.

The leading first condition is a local owner-researcher human chat caregiver, not a mandatory AI model.

Prerequisites:

- relevant Issue #3 prior-work review
- typed caregiver protocol
- privacy and consent boundary
- explicit accounting for human minutes, latency, clarification, and hidden experimenter labor
- a task that the organism initially cannot solve with its protected local repertoire
- fixed withheld-caregiver evaluation

Deliverables:

- bounded human chat interface
- recorded caregiver proposals and confidence
- clarification and rejection behavior
- provenance from advice to candidate artifact
- protected human-free retest
- misleading and inconsistent-advice scenarios
- no-caregiver baseline

Exit criteria:

- At least one capability that required human help becomes a verified local artifact or policy.
- The same individual retains the capability when human access is withheld.
- Reduced consultation is not replaced by hidden retries or unrecorded experimenter repair.
- Human advice can be rejected or deferred when unsafe, ambiguous, or unverifiable.

Recruiting additional participants requires a separate review of consent, privacy, and institutional obligations.

## Phase 4 — Compile assistance into reusable skills

**Goal:** Convert repeated successful scaffolding into cheaper inspectable local behavior.

Deliverables:

- skill schema with purpose, inputs, outputs, preconditions, tests, version, provenance, and cost
- proposed, active, deprecated, and quarantined states
- sandboxed skill validation
- adoption and rollback pipeline
- comparison between caregiver-supported reasoning and local execution
- bounded skill-library storage and retirement rules

Exit criteria:

- At least one recurring caregiver-assisted capability becomes a tested local skill.
- The skill reduces caregiver burden while preserving protected performance.
- Failed, obsolete, or harmful skills can be rejected, retired, or rolled back.

A deterministic rule or Python skill is scientifically and legally distinct from model-weight distillation.

## Phase 5 — Begin competence-gated caregiver fading

**Goal:** Reduce external scaffolding deliberately and measure what survives.

Deliverables:

- competence-gated and scheduled withdrawal conditions
- fixed caregiver-available, declining-access, and no-caregiver comparisons
- autonomous-duration and retained-capability measurements
- explicit escalation and abstention behavior
- caregiver burden dashboard
- accounting for storage, compute, retries, and maintenance

Core metrics:

- consultations per retained capability
- caregiver minutes and latency
- successful autonomous duration
- skill reuse and transfer
- protected task success after withdrawal
- regression and recovery rates
- storage and computation per retained capability
- correct abstention

Exit criteria:

- SUDACHI retains one meaningful capability after caregiver access is removed for a defined period.
- Reduced consultation does not create hidden local work or evaluator drift.
- Capability loss is reported honestly rather than masked.

## Phase 6 — Add model-caregiver comparison conditions

**Goal:** Compare human caregiving with local or hosted artificial caregivers when scientifically useful and permitted.

Prerequisites:

- dated provider and product review
- exact transformation permissions
- data-flow, retention, provenance, and cost controls
- local open-weight license review where applicable
- no-caregiver and human-caregiver baselines

Possible conditions:

- deterministic fixture
- small local open-weight model
- stronger local or hosted open-weight model
- commercial API
- human-AI team

Exit criteria:

- Provider identity can change without changing organism authority or protected evaluation.
- Live model capability is not misreported as retained local competence.
- Every call and downstream transformation is permitted, budgeted, and auditable.

Model caregivers are optional comparison conditions, not the definition of SUDACHI.

## Phase 7 — Sleep, consolidation, and forgetting

**Goal:** Keep the organism small by reorganizing experience rather than accumulating it indefinitely.

Deliverables:

- separation of episodic records from consolidated knowledge
- importance and expiry rules
- duplicate detection and semantic merging
- skill consolidation and retirement
- bounded-memory reports
- pre/post-consolidation protected tests

Exit criteria:

- Storage growth is bounded under repeated workload.
- Consolidation preserves selected capabilities.
- Forgetting is distinguishable from corruption and rollback.

## Phase 8 — Developmental experiments

**Goal:** Study how environments, caregivers, and budgets produce different developmental trajectories.

Deliverables:

- reproducible experiment manifests
- multiple isolated organism instances
- fixed and novel environment variants
- cohort comparisons
- lineage and abandoned-branch records
- published experiment reports

Questions:

- Does stricter caregiver access improve compilation or cause brittleness?
- When should the organism ask, abstain, or test locally?
- Which kinds of assistance compile well into rules or skills?
- How do human and artificial caregivers differ in burden and retained competence?
- Does forgetting improve transfer or merely reduce recall?

Exit criteria:

- Controlled instances can be compared from identical seeds or declared variants.
- Results do not depend on hidden conversation or provider context.
- Total human and computational work is reported.

## Phase 9 — Inheritance and branching

**Goal:** Explore reproduction without equating copying with identity.

Possible inherited material:

- tested skills
- constitutional constraints
- consolidation methods
- broad action tendencies

Not inherited by default:

- complete episodic history
- conversation transcripts
- caregiver credentials
- environment-specific state
- the parent organism's current self-description

Deliverables:

- fork protocol
- lineage metadata
- controlled variation
- parent/child capability comparison
- identity and continuity analysis

Exit criteria:

- A child can function from inherited structure while developing a distinct history.
- Parent, child, restored branch, and abandoned branch remain auditable.

## Deferred until justified

Do not add these merely because they sound advanced:

- unrestricted self-modification
- autonomous internet exploration
- continuous always-on execution
- routine model fine-tuning or LoRA updates
- large vector databases
- multi-agent societies
- physical robotics
- self-replication outside controlled experiments
- emotional presentation before life mechanisms

SUDACHI should earn complexity by demonstrating that a simpler body is insufficient.

## Immediate next milestone

After Contract v0.2 and its aligned documentation are merged, create the Python package skeleton and implement protected tests before filling in organism behavior.

The first code milestone is not a caregiver or chat window. It is a deterministic initialization path that creates a validated SQLite organism and stable genesis checkpoint.
