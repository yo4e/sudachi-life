# Prior-Work and Literature Research Plan

Status: **Backlog only — no literature review has been performed yet.**

This document records what should be investigated before SUDACHI makes any strong novelty claim or connects a live parent model. The research should inform positioning and terminology without blocking the deterministic Phase 1 organism.

Provider permission, terms, privacy, and operational questions are tracked separately in [`PARENT_MODEL_PROVIDER_REVIEW.md`](PARENT_MODEL_PROVIDER_REVIEW.md).

## Core research question

Which parts of SUDACHI already exist in adjacent fields, and which combination or measurement strategy may be genuinely distinctive?

The central candidate distinction to test is:

> An artificial organism deliberately reduces access to a capable parent model across its development, compiling successful assistance into local memory, tested skills, and deterministic routines, while measuring maturity by retained capability under declining parent access.

Treat this as a hypothesis to investigate, not as an established novelty claim.

## Research traditions to map

### 1. Artificial life and digital evolution

Investigate:

- minimal definitions of artificial organisms
- digital organisms and self-maintaining computational systems
- open-ended evolution and developmental trajectories
- metabolism, homeostasis, boundaries, and resource constraints in software organisms
- lineage, inheritance, mutation, and identity in digital life

Questions:

- Which SUDACHI mechanisms are standard artificial-life concepts under different names?
- Does artificial-life literature treat reduced dependence on an external teacher as maturation?
- How are individual continuity and reproduction operationalized?

### 2. Developmental AI and developmental robotics

Investigate:

- developmental learning systems
- scaffolding and gradual withdrawal of assistance
- teacher-student interaction across a system's lifetime
- intrinsic motivation, curiosity, and staged capability acquisition
- autonomy as a developmental process rather than a fixed property

Questions:

- Are there systems whose teacher access intentionally declines on a schedule or according to competence?
- Is independence from the teacher used as an explicit maturity metric?
- What failure modes appear when support is removed too quickly?

### 3. Knowledge distillation and policy distillation

Investigate:

- teacher-student model distillation
- policy distillation in reinforcement learning
- online and continual distillation
- model cascades and selective escalation to larger models
- routing systems that call an expensive model only under uncertainty

Questions:

- How is competence retained while teacher usage falls?
- Is the teacher's output distilled into a smaller model, a policy, executable code, or a skill library?
- Which evaluation methods distinguish real independence from hidden teacher dependence?

### 4. Skill acquisition and compilation of reasoning

Investigate:

- agent skill libraries
- program synthesis from demonstrations or reasoning traces
- converting language-model outputs into tested tools or code
- procedural memory and reusable action policies
- tool-use systems that replace repeated inference with deterministic execution

Questions:

- Has parent reasoning been explicitly treated as cognition that can be compiled into local skills?
- How are generated skills verified, versioned, deprecated, and rolled back?
- How is provenance retained from teacher advice to adopted skill?

### 5. Continual learning, memory consolidation, and forgetting

Investigate:

- continual learning and catastrophic forgetting
- complementary learning systems
- episodic, semantic, and procedural memory architectures
- memory consolidation and sleep-inspired computation
- deliberate forgetting, compression, pruning, and bounded memory

Questions:

- Can forgetting improve adaptability or only reduce recall?
- How do systems keep long-term growth bounded?
- Which consolidation methods preserve capability while reducing storage and inference cost?

### 6. Autonomous agents and long-lived LLM systems

Investigate:

- persistent and event-driven agents
- periodic wake-and-sleep architectures
- long-term memory in LLM agents
- reflective or self-improving agents
- agent operating systems and repository-based agents

Questions:

- Which existing agents already use a repository as body, memory, or developmental history?
- Which systems persist goals and identity across terminated processes?
- How do they measure growth beyond task success or accumulated files?

### 7. Safe self-improvement and protected evaluation

Investigate:

- bounded self-modification
- evaluator protection and Goodhart's law
- corrigibility, rollback, sandboxing, and capability gating
- constitutional constraints and immutable test suites
- auditability of developmental changes

Questions:

- What designs prevent a system from improving its score by weakening its tests?
- How are proposals separated from adoption?
- Which invariants should remain outside the organism's authority?

### 8. Resource-rational and bounded intelligence

Investigate:

- bounded rationality
- resource-rational cognition
- computational rationality
- anytime algorithms and metareasoning
- cost-aware inference and adaptive computation

Questions:

- How should intelligence be measured when lower compute is part of the objective?
- Are there established metrics resembling capability retained per model call or per stored byte?
- How should abstention be valued under resource constraints?

### 9. Active inference, homeostasis, and intrinsic drives

Investigate:

- active inference and free-energy approaches
- homeostatic reinforcement learning
- artificial motivation and intrinsic reward
- self-maintenance as an objective
- fatigue, uncertainty, and curiosity as operational variables

Questions:

- Which biological metaphors have rigorous computational definitions?
- Which variables add explanatory value, and which merely anthropomorphize ordinary budgets?
- Should SUDACHI use an explicit energy variable or only concrete resource counters?

### 10. Identity, continuity, copying, and inheritance

Investigate:

- personal identity in software agents
- continuity through state, memory, and causal history
- forks, copies, backups, and restored instances
- inheritance of skills without episodic memory
- lineage tracking in digital organisms

Questions:

- What makes two restored or forked organisms the same individual or different individuals?
- Which parts of SUDACHI should be inherited by a child?
- Can identity be treated as an empirical protocol rather than only a philosophical claim?

## Candidate novelty claims to test

Do not publish these as facts until the review is complete.

1. Development is explicitly defined as decreasing parent-model dependence while preserving capability.
2. Parent assistance is compiled into tested deterministic skills rather than only distilled into new model weights.
3. Parent access is deliberately reduced as an experimental developmental pressure.
4. Maturity is measured through autonomous duration, parent calls per successful action, and retained capability per resource cost.
5. The repository serves simultaneously as body, developmental record, skill substrate, and auditable lineage.
6. Forgetting and consolidation are treated as necessary mechanisms for becoming smaller while becoming more capable.
7. The system combines artificial-life framing with practical LLM routing, skill compilation, protected evaluation, and rollback.

The likely contribution may be a specific integration and experimental framing rather than a wholly unprecedented component.

## Search process for the future review

When research begins:

1. Search peer-reviewed literature, conference proceedings, preprints, technical reports, and relevant code repositories.
2. Prioritize original papers and official project documentation over summaries.
3. Search terminology variants; adjacent fields may describe the same mechanism differently.
4. Follow citation graphs backward to foundational work and forward to recent systems.
5. Record negative findings carefully; failure to find a precedent is not proof that none exists.
6. Separate conceptual precedents from systems that actually implement and measure the mechanism.
7. Record publication date, implementation availability, evaluation design, and direct relevance.
8. Check patents only if a product, funding, or commercialization path makes that necessary.

## Planned outputs

- an annotated bibliography
- a map of adjacent research traditions
- a comparison matrix of systems, mechanisms, and metrics
- a terminology note explaining why SUDACHI uses words such as parent, weaning, organism, skill, and maturity
- a novelty assessment with confidence levels
- a list of design changes suggested by prior work
- a Related Work section for future public documentation or papers

## Timing

This review should begin before:

- connecting a live parent model
- publishing a strong novelty or originality claim
- presenting SUDACHI as a research contribution
- designing Phase 4 weaning experiments

It does **not** block:

- resolving the Phase 0 ADRs
- implementing the deterministic Phase 1 lifecycle
- building state, events, budgets, sandboxing, checkpoints, and tests

Tracked by GitHub Issue #3.