# SUDACHI Roadmap

This roadmap is developmental rather than feature-driven. Each phase should establish a new invariant before the next layer of autonomy is introduced.

## Phase 0 — Freeze the organism contract

**Goal:** Define the smallest thing that counts as one living cycle of SUDACHI.

Deliverables:

- lifecycle state machine
- event schema
- organism-state schema
- explicit budgets for steps, time, storage, and parent consultation
- fixed evaluation boundary
- threat model and permission policy
- definitions of growth, maturity, failure, sleep, and recovery
- a deterministic mocked parent

Exit criteria:

- One complete cycle can be described without referring to a language model.
- Every side effect has an explicit permission boundary.
- Success cannot be achieved merely by rewriting the evaluator.

## Phase 1 — Build SUDACHI-0

**Goal:** Implement one bounded, deterministic organism cycle in local Python.

Proposed minimal cycle:

1. wake
2. load state
3. observe one queued event
4. choose one allowed action
5. execute in a sandbox
6. evaluate the result
7. update state and append an event record
8. sleep and terminate

Deliverables:

- Python package and CLI
- SQLite or similarly lightweight state store
- append-only event log
- deterministic action registry
- budget enforcement
- rollback/checkpoint support
- basic unit and invariant tests

Exit criteria:

- Repeated runs are reproducible with a fixed seed.
- The organism cannot exceed its run budget.
- A failed action leaves recoverable state.

## Phase 2 — Add parent-assisted learning

**Goal:** Allow a parent model to help only when local capability is insufficient.

Deliverables:

- parent-model adapter interface
- mocked and live adapters kept interchangeable
- explicit parent-call ledger
- uncertainty or novelty trigger for consultation
- proposal format for memories and skills derived from parent advice
- human- or test-gated adoption path

Exit criteria:

- Every parent call has a reason, cost, input summary, and outcome.
- Parent advice cannot directly modify protected code, tests, or policy.
- The organism can refuse or defer when advice cannot be verified.

## Phase 3 — Compile reasoning into skills

**Goal:** Convert repeated successful assistance into cheap, local behavior.

Deliverables:

- skill schema with purpose, inputs, outputs, preconditions, tests, version, and provenance
- skill registry and retrieval
- skill-generation proposal pipeline
- sandboxed skill tests
- promotion, deprecation, and rollback lifecycle
- comparison between parent reasoning and local skill execution

Exit criteria:

- At least one recurring parent-assisted task becomes a tested local skill.
- The skill reduces parent calls while preserving agreed performance.
- Failed or obsolete skills can be detected and retired.

## Phase 4 — Begin weaning

**Goal:** Reduce parent-model access deliberately and measure what survives.

Deliverables:

- declining parent-call schedules or budgets
- autonomous survival experiments
- graceful abstention and escalation behavior
- performance baselines under different parent quotas
- maturity dashboard

Core metrics:

- parent calls per successful action
- successful actions per parent call
- autonomous survival time
- skill reuse rate
- task success under reduced consultation
- regression and recovery rates

Exit criteria:

- SUDACHI retains one meaningful capability after parent access is removed for a defined period.
- Reduced consultation does not create hidden retries or uncontrolled local work.
- Loss of capability is reported honestly rather than masked.

## Phase 5 — Sleep, consolidation, and forgetting

**Goal:** Keep the organism small by reorganizing experience instead of accumulating it indefinitely.

Deliverables:

- separation of episodic events from consolidated knowledge
- memory importance and expiry rules
- duplicate detection and semantic merging
- skill consolidation
- sleep-cycle reports
- pre/post consolidation regression tests

Exit criteria:

- Storage growth is bounded under a repeated workload.
- Consolidation preserves selected capabilities.
- Forgotten information can be distinguished from corruption.

## Phase 6 — Developmental experiments

**Goal:** Study whether different environments and budgets produce distinct developmental trajectories.

Deliverables:

- reproducible experiment manifests
- multiple isolated organism instances
- fixed environmental tasks
- cohort comparisons
- developmental lineage records
- published experiment reports

Questions:

- Does a stricter parent budget produce better skill formation or premature brittleness?
- When should the organism ask rather than guess?
- Which kinds of knowledge compile well into local skills?
- Does forgetting improve transfer or merely reduce recall?

Exit criteria:

- Two or more instances can be compared from identical seeds or controlled variants.
- Results are reproducible and not dependent on hidden model context.

## Phase 7 — Inheritance and branching

**Goal:** Explore reproduction without equating copying with identity.

Possible inheritance boundary:

Inherited:

- tested skills
- constitutional constraints
- memory-consolidation methods
- broad action tendencies

Not inherited by default:

- complete episodic history
- conversation transcripts
- parent organism’s current self-description
- private credentials or environment-specific state

Deliverables:

- fork protocol
- lineage metadata
- controlled variation mechanism
- parent/child capability comparison
- identity and continuity notes

Exit criteria:

- A child instance can function from inherited structure while developing a distinct history.
- Lineage remains auditable.

## Deferred until justified

The following should not be added merely because they sound advanced:

- unrestricted self-modification
- autonomous internet exploration
- continuous always-on execution
- model fine-tuning after every interaction
- large vector databases
- multi-agent societies
- physical robotics
- self-replication outside a controlled experiment

SUDACHI should earn complexity by demonstrating that a simpler body is insufficient.

## Immediate next milestone

Write the **Minimal Organism Contract v0.1**, then implement a deterministic one-event lifecycle with a mocked parent and no network access.