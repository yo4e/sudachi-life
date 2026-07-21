# Prior-Work and Literature Research Plan

Status: **Active preliminary review — no strong novelty claim is authorized**

Verified: **2026-07-21**

Tracked by: GitHub Issue #3

This document defines the research required before SUDACHI makes a strong novelty claim or connects a live caregiver. The review informs terminology, experiment design, and positioning without blocking the deterministic caregiver-free Phase 1 organism.

Model-provider permission, terms, privacy, and operational questions are tracked separately in [`PARENT_MODEL_PROVIDER_REVIEW.md`](PARENT_MODEL_PROVIDER_REVIEW.md).

Preliminary findings are recorded in:

- [`research/INITIAL_EVIDENCE_MAP.md`](research/INITIAL_EVIDENCE_MAP.md)
- [`research/PARENT_MODEL_STRATEGY.md`](research/PARENT_MODEL_STRATEGY.md)
- [`research/HUMAN_CAREGIVER_HYPOTHESIS.md`](research/HUMAN_CAREGIVER_HYPOTHESIS.md)

## Core research question

Which parts of SUDACHI already exist in adjacent fields, and which integration or measurement strategy may be genuinely distinctive?

The central candidate distinction to test is:

> A bounded artificial organism converts finite external cognitive scaffolding into verified local competence and is evaluated longitudinally by retained capability under declining caregiver access, with protected evaluation, rollback, provenance, and total resource accounting.

Treat this as a hypothesis, not an established novelty claim.

## Terminology under review

`Parent model` is too narrow as the general term because the caregiver may be human, deterministic, model-based, hybrid, or absent in a control condition.

Working terms:

- **caregiver** — a human or artificial source of developmental assistance
- **scaffolding channel** — the bounded interface through which assistance is requested and returned
- **consultation** — one measured use of that channel
- **adoption** — the separate verified process that incorporates a memory, rule, test, policy, or skill
- **withdrawal or fading** — reduction of caregiver availability according to a declared schedule or competence rule
- **maturity** — retained capability under reduced justified dependence and bounded total cost

## Research traditions to map

### 1. Artificial life and digital evolution

Investigate digital organisms, minimal self-maintaining systems, open-ended evolution, resource constraints, lineage, lifetime learning, social learning, and persistent virtual creatures.

Questions:

- Which SUDACHI mechanisms are standard artificial-life concepts under different names?
- How are organism boundaries, continuity, development, and inheritance operationalized?
- Is reduced dependence on an external teacher ever treated as maturation?

Priority comparisons include Avida, Creatures, autopoiesis research, and open-ended dynamics measurement.

### 2. Developmental AI, developmental robotics, and scaffolding

Investigate caregiver–learner interaction, staged difficulty, intrinsic motivation, educational scaffolding, fading, and autonomy as a developmental process.

Questions:

- Are there systems whose teacher access declines according to schedule or competence?
- Is independence from the teacher used as an explicit maturity metric?
- What happens when support is withdrawn too early or too late?
- Does the caregiver adapt alongside the learner?

### 3. Human feedback, demonstration, and interactive task learning

Investigate reinforcement learning with human teachers, learning from demonstration, correction, preferences, natural-language task teaching, clarification dialog, and socially guided exploration.

Questions:

- How is ambiguous or policy-dependent feedback interpreted?
- How does free-form language become a bounded action proposal?
- How are teacher inconsistency, limited knowledge, and embodiment mismatch handled?
- What human labor is counted or hidden?

### 4. Assistance requesting and intervention efficiency

Investigate systems that decide when to request human help, novelty- and risk-gated intervention, budget-aware imitation learning, and methods that reduce annotation or monitoring burden.

Questions:

- Is reduced intervention evidence of acquired persistent competence or only improved gating?
- Is capability retested after the human is completely removed?
- How are consultation budget, latency, and human minutes measured?

### 5. Knowledge and policy distillation

Investigate teacher–student model distillation, policy distillation, online distillation, model cascades, and selective escalation.

Questions:

- How is competence retained while teacher usage falls?
- Is assistance converted into model weights, a policy, executable code, a rule, or a skill library?
- Which evaluations reveal hidden teacher dependence?

Model-weight distillation is an established neighboring field and must remain distinct from deterministic artifact formation.

### 6. Skill acquisition and compilation of reasoning

Investigate agent skill libraries, program synthesis, procedural memory, reusable action policies, tested tools, DreamCoder, Voyager, and related robot-library learning.

Questions:

- How are generated skills verified, versioned, composed, deprecated, and rolled back?
- How is provenance retained from caregiver advice to adopted capability?
- How are skill libraries bounded rather than allowed to grow forever?

### 7. Continual learning, consolidation, and forgetting

Investigate catastrophic forgetting, complementary learning systems, episodic and procedural memory, sleep-inspired consolidation, pruning, compression, and bounded memory.

Questions:

- Can forgetting improve adaptability or only reduce recall?
- Which consolidation methods preserve capability while reducing storage and inference cost?
- How can one distinguish compact growth from accumulating an unbounded archive?

### 8. Long-lived agents and repository-based identity

Investigate persistent and event-driven agents, periodic wake-and-sleep systems, long-term memory, repository-based agents, software identity, forks, copies, backups, and restored instances.

Questions:

- Which systems already use a repository as body, memory, or developmental history?
- What makes a restored or forked organism the same individual or a different one?
- Can lineage and identity be defined by an auditable protocol rather than metaphor?

### 9. Safe self-improvement and protected evaluation

Investigate bounded self-modification, evaluator protection, Goodhart effects, corrigibility, rollback, sandboxing, immutable tests, and capability gating.

Questions:

- What prevents a system or caregiver from improving the score by weakening the test?
- How are proposals separated from adoption?
- Which invariants must remain outside organism and caregiver authority?

### 10. Resource-rational and bounded intelligence

Investigate bounded rationality, resource-rational cognition, metareasoning, adaptive computation, and cost-aware inference.

Questions:

- How should intelligence be measured when lower compute and lower caregiver burden are objectives?
- Are there established metrics resembling retained capability per consultation, human minute, stored byte, or compute unit?
- How should abstention be valued under resource constraints?

### 11. Homeostasis, motivation, and energy metaphors

Investigate active inference, homeostatic reinforcement learning, intrinsic motivation, curiosity, fatigue, and self-maintenance.

Questions:

- Which biological metaphors have rigorous computational definitions?
- Which variables add explanatory value, and which merely rename concrete budgets?
- Should SUDACHI ever use an explicit energy variable?

ADR 0006 decides only the seed architecture; it does not settle the broader research question permanently.

### 12. Virtual pets, companion agents, and owner-shaped creatures

Investigate Tamagotchi, Creatures, aibo, companion robots, and systems whose personality or behavior changes through owner interaction.

Questions:

- Does reduced owner involvement count as success, neglect, or the end of the product loop?
- Are learned behaviors exposed, tested, versioned, and retained after owner withdrawal?
- Is adaptation substantive competence, predefined branching, or relational presentation?

The explicit failure mode is **Tamagotchi with Git**: simulated needs, affection, personality, branching growth, or chat history without retained caregiver-independent competence.

## Candidate novelty claims to test

Do not publish these as facts until the review is substantially complete.

| Candidate claim | Current preliminary status |
| --- | --- |
| A human can teach an artificial agent | Established |
| A creature can change through owner interaction | Established |
| An agent can request help only when needed | Established |
| Teacher reasoning can become a smaller model or policy | Established |
| External assistance can become executable skills | Established neighboring idea |
| Parent or caregiver access can deliberately fade during machine development | Requires deeper comparison |
| Maturity can be measured as retained capability after caregiver withdrawal | Strong candidate for deeper novelty testing |
| One persistent artificial individual can link recorded caregiving to verified, versioned local artifacts and later independence | Plausible integration candidate |
| Growth can require lower caregiver burden without hiding cost in compute, storage, retries, or experimenter labor | Strong measurement candidate |
| Repository state, tests, checkpoints, and Git lineage together form an experimental organism body | Conceptual and engineering candidate requiring comparison |

The likely contribution may be a specific integration and experimental framing rather than a wholly unprecedented component.

## Research method

1. Prefer primary papers, official repositories, and first-party product documentation.
2. Record publication date, implementation availability, evaluation design, and direct relevance.
3. Search terminology variants across fields.
4. Follow citation graphs backward and forward.
5. Separate conceptual resemblance from implemented and measured precedent.
6. Record negative searches without treating failure to find a result as proof of novelty.
7. Record time-sensitive provider or product claims with a verification date.
8. Keep legal and contractual conclusions separate from scientific similarity.
9. Check patents only if commercialization, funding, or a concrete product path makes that necessary.

## Planned outputs

- annotated bibliography
- map of adjacent research traditions
- product and system comparison matrix
- negative-search record
- terminology and positioning note
- novelty assessment with confidence levels
- list of claims supported, weakened, or ruled out
- design changes suggested by prior work
- Related Work section for future public documentation or papers

## Timing

The relevant review must be substantially complete before:

- connecting a live human caregiver to organism actions
- connecting a live model caregiver
- publishing a strong novelty or originality claim
- presenting SUDACHI as a research contribution
- designing formal caregiver-withdrawal experiments

It does **not** block:

- resolving the Phase 0 ADRs
- implementing the deterministic caregiver-free Phase 1 lifecycle
- building state, events, budgets, sandboxing, checkpoints, and tests
- testing consultation plumbing with a deterministic fixture
