# SUDACHI

**A lightweight artificial life that learns to leave the nest.**

SUDACHI is an experimental artificial-life project built around a reversal of the usual AI scaling story:

> As it develops, it should retain more capability while requiring less external cognitive scaffolding.

A young SUDACHI may eventually ask a caregiver how to handle unfamiliar situations. The caregiver may be a human, a deterministic fixture, a local or hosted model, a human-AI team, or absent in a control condition. When assistance succeeds, the organism should convert the experience into verified memory, tested skills, and inspectable local routines.

Maturity is not defined by a larger model, more tokens, more files, simulated affection, or permanent access to a helper. It is defined by preserving useful behavior while justified dependence decreases.

The name carries two meanings:

- 巣立ち (sudachi): leaving the nest
- すだち (Sudachi): a small Japanese citrus fruit—green, compact, and alive

## Core hypothesis

Can a bounded artificial organism convert finite external scaffolding into verified local competence and retain that competence while caregiver access is reduced?

More precisely:

- Can caregiver assistance become small, reusable local skills or rules?
- Can the same individual preserve competence after assistance is reduced or withheld?
- Can memory consolidation, forgetting, and skill reuse lower total cost over time?
- Can caregiver burden fall without hiding the cost in storage, computation, retries, or unrecorded human work?
- Can a repository, rather than a model alone, serve as the organism's body and developmental history?

## What SUDACHI is

SUDACHI is planned as a small local Python system composed of:

- a bounded wake–act–evaluate–persist–checkpoint–sleep lifecycle
- one canonical SQLite body with append-only event history
- explicit concrete resource budgets
- protected evaluation and rollback lineage
- a deterministic seed environment
- later, a source-neutral caregiver boundary used only when justified
- Git history as an auditable source and decision record

A language model may be an organ or caregiver. It is not the whole organism.

## What SUDACHI is not

- A smaller imitation of ChatGPT
- A commercial-model wrapper
- An unrestricted self-modifying agent
- A process that must run continuously
- A virtual pet whose apparent growth is only mood, personality, or branching presentation
- A system whose growth is measured by file count, token count, or uncontrolled complexity
- A project that treats autonomy as the absence of boundaries

## Design principles

1. **Small brain, structured body**  
   Intelligence should be distributed across memory, tools, routines, tests, and environment.

2. **Skills are compiled cognition**  
   Repeated successful assistance should become cheaper, inspectable local behavior where possible.

3. **Maturity means reduced justified dependency**  
   Caregiver consultations should decline without unacceptable loss of performance or safety.

4. **Finite resources create meaningful behavior**  
   Time, storage, computation, human labor, consultation, and action budgets must be visible and bounded.

5. **Forgetting is a feature**  
   The organism should consolidate experience rather than accumulate everything forever.

6. **Growth must be measurable**  
   Every claimed improvement should survive fixed tests and comparison with an earlier state.

7. **The measuring stick is protected**  
   Core evaluation criteria and safety boundaries must not be rewritten merely to make the organism appear successful.

8. **Caregiver advice is a proposal**  
   Human or model guidance must not bypass permissions, budgets, sandboxing, evaluation, or skill-adoption review.

## Phase 1 organism

Minimal Organism Contract v0.2 and ADRs 0001–0006 define the first executable organism.

SUDACHI-0 begins as a deliberately small deterministic garden metabolism:

- one SQLite database per organism
- one queued `synthetic:garden_tick` per wake
- two plots: a dry sprout and a mature fruiting plant
- one water unit
- two mutating actions: `water_plot` and `harvest_plot`
- explicit abstention
- one action attempt and one successful mutation at most per wake
- zero caregiver, network, subprocess, and external mutable-write capability
- a verified immutable checkpoint after every committed wake
- rollback that preserves the abandoned future and creates a new lineage generation
- no scalar energy variable

The canonical run waters, harvests, then abstains after objective completion. This proves metabolism and recovery, not learning or intelligence.

## Initial maturity metrics

Later caregiver experiments should track:

- caregiver consultations per successful action
- caregiver minutes per retained capability
- successful autonomous duration after caregiver access is removed
- reusable behaviors acquired per consultation
- skill reuse rate
- transfer to unfamiliar tasks using existing skills
- recovery after failure, corruption, or misleading advice
- storage and computation cost per retained capability
- correct abstention under uncertainty

## Tamagotchi test

SUDACHI has not demonstrated its central claim if it only adds simulated needs, affection, personality, chat history, or branching growth.

A developmental gain must connect:

`finite recorded caregiving -> verified local artifact -> retained capability -> reduced caregiver burden`

The closest precedents include developmental robotics, human-in-the-loop learning, interactive task learning, Tamagotchi, Creatures, and aibo. The project's possible contribution is a specific longitudinal integration and measurement strategy, not the unprecedented invention of human-taught artificial creatures.

## Repository map

- [`AGENTS.md`](AGENTS.md) — cold-start and continuity instructions for AI collaborators
- [`docs/CHATGPT_PROJECT_HANDOFF.md`](docs/CHATGPT_PROJECT_HANDOFF.md) — startup context for a dedicated ChatGPT Project
- [`docs/ORIGIN.md`](docs/ORIGIN.md) — origin, intent, and founding conversation
- [`docs/MINIMAL_ORGANISM_CONTRACT.md`](docs/MINIMAL_ORGANISM_CONTRACT.md) — accepted Contract v0.2 for SUDACHI-0
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — Phase 1 architecture aligned with the contract
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — developmental roadmap from metabolism to caregiver withdrawal
- [`docs/IMPLEMENTATION_DISCIPLINE.md`](docs/IMPLEMENTATION_DISCIPLINE.md) — implementation guardrails and restart checklist
- [`docs/decisions/`](docs/decisions/) — accepted ADRs 0001–0006
- [`docs/RESEARCH_QUESTIONS.md`](docs/RESEARCH_QUESTIONS.md) — active prior-work and novelty research plan
- [`docs/PARENT_MODEL_PROVIDER_REVIEW.md`](docs/PARENT_MODEL_PROVIDER_REVIEW.md) — model-provider, terms, data, and compliance checklist
- [`docs/research/INITIAL_EVIDENCE_MAP.md`](docs/research/INITIAL_EVIDENCE_MAP.md) — preliminary related-work map
- [`docs/research/PARENT_MODEL_STRATEGY.md`](docs/research/PARENT_MODEL_STRATEGY.md) — provider-neutral model-caregiver strategy
- [`docs/research/HUMAN_CAREGIVER_HYPOTHESIS.md`](docs/research/HUMAN_CAREGIVER_HYPOTHESIS.md) — human-caregiver hypothesis and virtual-pet comparison
- [`docs/HANDOFF.md`](docs/HANDOFF.md) — authoritative current state, issue map, and exact restart point

## Language policy

The repository is written in English. The only intentional Japanese text is the two name-etymology lines near the top of this README.

## Status

**Phase 1 SUDACHI-0 metabolism is implemented and all 41 fixed Contract v0.2 evaluations have protected coverage.**

The final Slice 35 implementation head passes 142 protected tests, clean editable installation, compilation, and the genesis CLI smoke test on Python 3.12. This establishes trustworthy deterministic metabolism and recovery, not learning or intelligence.

Issue #3 research proceeds in parallel. No live human or model caregiver is connected. Phase 2 requires an explicit reviewed scope decision; there is no automatic next implementation slice.

For a cold start, read [`AGENTS.md`](AGENTS.md), follow its reading order, and then inspect current issues and pull requests.
