# SUDACHI Project Handoff

Last updated: July 21, 2026

## Cold-start summary

SUDACHI is a developmental artificial-life experiment whose central question is currently stated as:

> Can a bounded artificial organism convert external cognitive scaffolding into verified local competence and retain capability while becoming less dependent on that scaffolding?

The caregiver may be a human, a deterministic fixture, a local model, a hosted model API, a human-AI team, or absent in a control condition. The architecture must not assume that the caregiver is an AI model or a named commercial product.

Successful assistance should settle into verified experience, tested skills, deterministic routines, or other inspectable local artifacts. Maturity is retained capability under declining caregiver access, not model size, token usage, file count, personality performance, or uncontrolled complexity.

The repository is the organism's body, developmental record, skill substrate, and auditable lineage. A language model may be an organ or caregiver, but it is not the organism.

## Current state

The repository contains:

- the founding concept and origin record
- a phased roadmap
- a conservative architecture proposal
- Minimal Organism Contract v0.1 as a draft
- implementation discipline and restart guardrails
- continuity instructions for future AI collaborators
- an active prior-work and novelty research plan
- an active provider and compliance review for future model caregivers
- `docs/research/INITIAL_EVIDENCE_MAP.md`
- `docs/research/PARENT_MODEL_STRATEGY.md`
- `docs/research/HUMAN_CAREGIVER_HYPOTHESIS.md`

No implementation code exists yet. This is intentional.

The project has two active work streams:

1. Issue #1 resolves the six seed architecture decisions before implementation.
2. Issue #3 maps prior work, caregiver designs, novelty candidates, and model-provider constraints.

Phase 1 remains deterministic, local, network-free, and caregiver-free. Research does not authorize connecting a live model or human chat interface to organism actions.

## Accepted decisions and current working directions

Accepted project decisions:

- Project name: **SUDACHI**
- Repository: `yo4e/sudachi-life`
- First organism: provisional name **SUDACHI-0**
- Runtime model: execute one bounded lifecycle and terminate; do not begin with an unbounded resident loop
- Initial environment: local execution with no network access
- Phase 1 has zero caregiver consultations
- A deterministic fixture may later verify consultation plumbing
- The repository is both body and developmental history
- SUDACHI-0 will not initially rewrite its own source code
- Repository language is English, except for the two Japanese etymology lines intentionally preserved in `README.md`
- Prior-work and provider research was explicitly authorized by the owner on July 21, 2026
- No live commercial model may be connected until current terms, product boundaries, automation rules, data practices, output-use rules, and operational constraints have been reviewed
- Model-weight distillation remains disabled unless a provider- and model-specific review explicitly permits it
- Candidate novelty claims remain hypotheses until comparison work is substantially complete
- Architecture decisions must be written as ADRs before they are hidden in implementation code

Current research direction, not yet a final architecture decision:

- define the parent by function as an external caregiver or cognitive-scaffolding source
- treat a human chat caregiver as the leading candidate for the first live developmental experiment
- keep the interface source-neutral so deterministic, human, local-model, hosted-model, hybrid, and no-caregiver conditions can be compared
- treat caregiver messages as typed proposals rather than direct executable commands
- measure human time, consultations, clarification turns, latency, and hidden intervention as real resource costs
- define maturity as retained capability after caregiver access is reduced or withheld
- distinguish SUDACHI from virtual pets through verified skill acquisition and decreasing justified dependence, not simulated needs or cosmetic development

## Reading order when resuming

Read all of these before proposing implementation:

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
13. `AGENTS.md`
14. this file

Then inspect current GitHub issues and open pull requests. Do not rely on remembered issue state.

## Issue map at handoff

- **Issue #1 — open and active:** Phase 0 architecture decisions and ADRs; implementation-critical.
- **Issue #2 — closed:** Copilot architecture review record; its accepted recommendations were folded into the plan.
- **Issue #3 — open and active:** caregiver withdrawal, prior work, novelty, human-caregiver design, virtual-pet comparison, and model-provider research.
- **Issue #4 — closed and irrelevant:** accidental placeholder.

If this map differs from current GitHub state, trust current GitHub state and update this file.

## Exact next implementation task

Resume with Issue #1 and draft:

`docs/decisions/0001-state-and-event-storage.md`

The ADR must decide whether SQLite is the sole canonical store or whether JSONL has any canonical role. It must account for:

- authoritative state versus observations and exports
- deterministic replay
- append-only event guarantees
- atomic lifecycle commits
- event identity and ordering
- checkpoint boundaries
- export reproducibility
- future provenance records without designing live-caregiver integration

Then resolve:

1. `0002-clock-and-determinism.md`
2. `0003-runtime-locking.md`
3. `0004-checkpoints.md`
4. `0005-seed-environment.md`
5. `0006-budget-metaphor.md`

Current recommendations, not yet accepted ADRs:

- canonical durable state: SQLite
- event history: append-only SQLite table; JSONL only as a reproducible observation and experiment export
- clock: real clock in operation, injected fake clock in tests
- locking: evaluate a SQLite transaction plus a runtime lock record
- checkpoint: SQLite backup or state snapshot plus event offset
- seed environment: a tiny deterministic virtual garden with a few objects, events, and measurable action outcomes
- energy: initially expose concrete budgets rather than introducing an independent mystery variable

After the ADRs are accepted:

1. review Minimal Organism Contract v0.1 for contradictions
2. confirm protected and mutable boundaries
3. confirm fixed Phase 1 evaluations
4. update this handoff
5. create `pyproject.toml`, `src/sudachi_life/`, and `tests/`

Do not resolve these choices silently inside implementation code. Follow `docs/IMPLEMENTATION_DISCIPLINE.md`.

## First implementation target

Possible minimal CLI:

```text
sudachi init
sudachi enqueue synthetic:file_changed
sudachi wake --seed 1
sudachi status
```

First lifecycle:

```text
wake
  -> acquire the organism lock
  -> validate state
  -> read one synthetic event
  -> choose one deterministic action
  -> consume bounded resources
  -> evaluate the outcome
  -> persist state and append event history atomically
  -> create or confirm a checkpoint
  -> sleep, release the lock, and terminate
```

Do not call a caregiver yet.

## Initial fixed evaluations

Treat the Phase 1 evaluations in `docs/MINIMAL_ORGANISM_CONTRACT.md` as authoritative. Core checks include:

- identical seed, state, event, clock, and configuration produce identical results
- step and timeout limits cannot be exceeded
- actions cannot write outside allowed paths
- failures do not silently corrupt durable state
- event history is append-only
- budgets never become negative
- protected configuration cannot be modified by an action
- rollback restores the latest stable checkpoint
- duplicate simultaneous waking is rejected
- abstention and budget exhaustion are explicitly recorded
- no network, human caregiver, or model caregiver is required

## Active research status

### Human caregiver hypothesis

`docs/research/HUMAN_CAREGIVER_HYPOTHESIS.md` records the current comparison.

Established neighboring ideas include human feedback, demonstrations, natural-language teaching, caregiver-shaped robot development, assistance requesting, intervention reduction, Tamagotchi, Creatures, and aibo. Therefore, “an artificial creature raised by a human” is not a novelty claim.

The strongest current candidate for deeper novelty testing is:

> finite recorded caregiving -> verified local artifact -> retained capability -> competence-gated withdrawal -> measured independence

The central failure mode is **Tamagotchi with Git**: simulated needs, branching growth, chat history, and personality changes without measurable caregiver-independent competence.

### Candidate first live-caregiver experiment

After deterministic Phase 1 and a fixture-caregiver protocol test:

1. expose a bounded human chat interface
2. classify input as demonstration, correction, constraint, explanation, preference, question, defer, or abstain
3. treat every response as a proposal subject to permissions, budgets, sandboxing, evaluation, and adoption rules
4. record human minutes, consultations, latency, confidence, clarification, and later reuse
5. reduce access only after protected competence tests pass
6. run withheld-caregiver and transfer trials

The human caregiver may not directly execute actions, modify protected state, weaken tests, raise budgets, erase history, or promote skills.

### Prior work and novelty

`docs/research/INITIAL_EVIDENCE_MAP.md` finds clear precedents for digital organisms, teacher-student distillation, executable skill libraries, wake-sleep program learning, model routing, human feedback, and caregiver scaffolding.

The strongest remaining candidate is the integration and longitudinal measurement of retained capability under deliberately declining external scaffolding, with protected evaluation, rollback, provenance, and full resource accounting. This is still a hypothesis.

Next research outputs include:

- annotated bibliography
- broader related-work and product comparison matrix
- negative-search record
- terminology and positioning note
- explicit comparison with Creatures, aibo, Tamagotchi, interactive task learning, and intervention-efficient imitation learning

### Model-provider and compliance research

`docs/PARENT_MODEL_PROVIDER_REVIEW.md` and `docs/research/PARENT_MODEL_STRATEGY.md` remain relevant for later artificial-caregiver conditions.

Current direction:

- distinguish consumer chat products from official programmatic APIs
- separate transient advice, retained memory, deterministic artifacts, synthetic data, and model-weight development
- default model-weight development to prohibited until explicitly authorized for the exact provider and model
- preserve local open-weight, deterministic fixture, human, hybrid, and no-caregiver conditions
- do not select ChatGPT or another named model as the canonical parent

A human-first experiment reduces API cost and provider dependence, but it does not remove the need to measure labor, privacy, consent, experimenter intervention, or bias.

## Do not implement yet

- unrestricted internet exploration
- continuous always-on execution
- unrestricted self-modification
- LoRA training after every experience
- a large vector database
- a multi-agent society
- a physical robot body
- replication outside the repository
- personality performance before the life mechanisms exist
- a live named model caregiver
- a free-form human chat channel that can bypass registered actions or protected policy

## Central research metrics

Observe changes in:

- caregiver consultations per successful action
- caregiver minutes per retained capability
- reusable behaviors acquired per consultation
- successful autonomous duration without caregiver access
- skill reuse rate
- transfer to unfamiliar tasks through composition of existing skills
- recovery after failure or misleading advice
- storage and computation cost per retained capability
- clarification and correction rate
- correct abstention under uncertainty
- hidden retries and unrecorded human intervention

## End-of-session protocol

Before ending substantial work, follow the restart checklist in `docs/IMPLEMENTATION_DISCIPLINE.md`:

1. update accepted ADRs and affected documentation
2. update relevant issue checklists and status
3. update this file with the true current state and one exact next action
4. ensure `AGENTS.md` points to the correct files and issue roles
5. leave no required decision only in chat, model memory, or an uncommitted note
6. record newly deferred research or compliance questions

The next collaborator should be able to resume from a cold start without access to the conversation that created the project.

## To the next AI collaborator

Do not flatten this project into a generic autonomous-agent framework or a virtual-pet presentation layer.

The center is development, not task completion or simulated affection.

Knowledge borrowed from a caregiver should settle into the body. The organism should gradually do more without asking, consolidate memory and skills, and carry itself into another day within finite resources. Making that process observable is the core of SUDACHI.

Do not make it large merely because expansion is easy.

**As it becomes smarter, it should become smaller and quieter.**
