# Initial Evidence Map

Status: **Preliminary research note**

Verified: **2026-07-21**

Tracked by: GitHub Issue #3

## Purpose

This note begins the prior-work review authorized by the repository owner. It does not establish novelty. It identifies nearby research traditions, records early design implications, and separates SUDACHI's candidate contribution from mechanisms that clearly have precedents.

The current working hypothesis remains:

> A developmental artificial organism can retain useful capability while deliberately reducing dependence on an expensive parent reasoner, converting successful assistance into verified experience, reusable skills, and cheaper local behavior.

## Preliminary conclusion

The individual ingredients of SUDACHI have substantial precedents:

- digital organisms and controlled artificial-life experiments
- teacher-student knowledge transfer and policy distillation
- human or teacher scaffolding of autonomous learners
- executable skill libraries built from language-model assistance
- wake-sleep program learning and library compression
- model routing and cascades that reduce expensive inference
- protected evaluation, rollback, and bounded execution in agent systems

The likely research contribution is therefore **not one unprecedented component**. A stronger candidate is the integration and measurement strategy:

1. treat parent access as developmental scaffolding that should be withdrawn
2. require successful assistance to settle into auditable local artifacts
3. measure maturity longitudinally as retained capability under declining parent access
4. protect evaluation and rollback so apparent growth cannot be manufactured by changing the measuring stick
5. include storage and inference cost in the definition of retained capability

These remain hypotheses until the literature map is broader and negative searches have been recorded.

## Evidence clusters

### 1. Digital organisms and artificial-life experiment platforms

Avida provides a mature precedent for treating self-replicating programs as digital organisms inside a controlled experimental environment with explicit measurements and reproducible protocols. It supports the general idea that an artificial organism should be studied through an environment, resource conditions, lineage, and measured behavior rather than only through a model benchmark.

The Creatures ecosystem is an earlier example of persistent artificial agents with internal neural and biochemical mechanisms, learning, reproduction, and interaction inside a virtual world.

Work on autopoiesis and minimal persistent individuals shows that artificial-life research also asks where an individual boundary comes from and what mechanisms maintain it. Open-ended evolution research, including the MODES toolbox, emphasizes that claims about ongoing development require explicit metrics rather than impressionistic complexity.

Implication for SUDACHI: the repository and runtime state may function as an experimental organism boundary, but SUDACHI must define operational maintenance, development, and lineage rather than relying on life-like vocabulary.

Primary sources:

- Charles Ofria and Claus O. Wilke, "Avida: A Software Platform for Research in Computational Evolutionary Biology" (2004): https://doi.org/10.1162/106454604773563612
- Dave Cliff and Stephen Grand, "The Creatures Global Digital Ecosystem" (1999): https://doi.org/10.1162/106454699568683
- Randall D. Beer, "An Investigation into the Origin of Autopoiesis" (2020): https://doi.org/10.1162/artl_a_00307
- Emily Dolson et al., "The MODES Toolbox: Measurements of Open-Ended Dynamics in Evolving Systems" (2019): https://doi.org/10.1162/artl_a_00280

### 2. Scaffolding and withdrawal of assistance

Developmental robotics and socially guided exploration provide precedents for an intrinsically motivated learner using human guidance and scaffolding without reducing learning to direct instruction. The educational scaffolding literature treats gradual withdrawal, or fading, as a defining property: support should become unnecessary as the learner internalizes useful structure.

Implication for SUDACHI: "weaning" should not mean merely lowering an API quota. Parent access should be withdrawn according to measured competence, and premature withdrawal should be treated as an experimental failure mode.

Early sources:

- Andrea L. Thomaz and Cynthia Breazeal, "Experiments in Socially Guided Exploration: Lessons Learned in Building Robots that Learn with and without Human Teachers" (2008): https://doi.org/10.1080/09540090802091917
- Janneke van de Pol, Monique Volman, and Jos Beishuizen, "Scaffolding in Teacher-Student Interaction: A Decade of Research" (2010): https://doi.org/10.1007/s10648-010-9127-6

A deeper search is still required for systems that explicitly use declining teacher access as a machine maturity metric.

### 3. Teacher-student compression and policy distillation

Knowledge distillation demonstrates that capability from a large or ensemble teacher can be transferred into a smaller deployable model. Policy distillation extends this idea to reinforcement-learning policies and shows that a smaller student can retain expert-level performance and consolidate multiple task-specific teachers.

Implication for SUDACHI: model-weight distillation is a well-established neighboring field and cannot itself be claimed as novel. It should also be kept distinct from SUDACHI's broader compilation targets: deterministic code, rules, tests, state transitions, and procedural skills.

Primary sources:

- Geoffrey Hinton, Oriol Vinyals, and Jeff Dean, "Distilling the Knowledge in a Neural Network" (2015): https://arxiv.org/abs/1503.02531
- Andrei A. Rusu et al., "Policy Distillation" (2015): https://arxiv.org/abs/1511.06295

### 4. Program libraries and executable skill acquisition

DreamCoder grows reusable symbolic abstractions through a wake-sleep program-learning process. It is a strong precedent for the idea that repeated problem solving can become a more compact language of reusable concepts.

Voyager uses a large language model to create and improve executable skills in Minecraft, stores them in a growing skill library, and reuses them compositionally in new situations. Lifelong Robot Library Learning similarly transfers experience into composable robot skills through language-model assistance.

Implication for SUDACHI: converting language-model assistance into executable skills already exists. SUDACHI's possible distinction must be narrower and experimentally explicit: verified provenance, protected adoption tests, rollback, finite resources, declining parent access, and bounded total storage.

Primary sources:

- Kevin Ellis et al., "DreamCoder: Growing Generalizable, Interpretable Knowledge with Wake-Sleep Bayesian Program Learning" (2020): https://arxiv.org/abs/2006.08381
- Guanzhi Wang et al., "Voyager: An Open-Ended Embodied Agent with Large Language Models" (2023): https://arxiv.org/abs/2305.16291
- Georgios Tziafas and Hamidreza Kasaei, "Lifelong Robot Library Learning" (2024): https://arxiv.org/abs/2406.18746

### 5. Routing, cascades, and expensive-model reduction

FrugalGPT and later routing or cascade work show that systems can route easy requests to cheaper models and escalate difficult requests to stronger models while preserving quality. This is an important systems precedent for reducing expensive-model calls.

However, routing is not equivalent to development. A static router may reduce cost without changing the organism's local capability.

Implication for SUDACHI: parent-call reduction counts as growth only when the same organism has acquired or consolidated local capability, not merely when a better external router chooses a cheaper provider.

Primary sources:

- Lingjiao Chen, Matei Zaharia, and James Zou, "FrugalGPT" (2023): https://arxiv.org/abs/2305.05176
- Jasper Dekoninck, Maximilian Baader, and Martin Vechev, "A Unified Approach to Routing and Cascading for LLMs" (2024): https://arxiv.org/abs/2410.10347

## Candidate claims and current status

| Candidate claim | Preliminary status | Reason |
| --- | --- | --- |
| Teacher reasoning can be converted into smaller local behavior | Established neighboring idea | Knowledge and policy distillation, program libraries, and executable skill systems provide direct precedents. |
| Executable skills can replace repeated LLM reasoning | Established neighboring idea | Voyager and related library-learning systems already demonstrate this pattern. |
| Parent access should deliberately decline during development | Plausible candidate distinction | Scaffolding fading is established, but an artificial organism using declining model access as an explicit developmental pressure needs deeper search. |
| Maturity can be measured as retained capability under declining parent access | Strong candidate for further novelty testing | No direct equivalent was identified in this initial pass. This is not evidence of absence. |
| Repository, state, tests, and Git lineage together constitute the organism's body | Conceptual candidate | Nearby precedents exist for persistent digital organisms and repository-based agents; the exact combination requires a dedicated search. |
| Growth should reduce total storage or inference cost per retained capability | Related to compression and resource-rational work | The longitudinal organism framing may be distinctive, but the efficiency objective is not new by itself. |

## Immediate design implications

1. **Define the parent by role, not brand.** The parent is an external, expensive, general reasoning source behind a provider-neutral interface.
2. **Separate artifact compilation from model distillation.** A tested rule or Python skill is not the same legal or scientific operation as training student weights on provider output.
3. **Require longitudinal baselines.** Each developmental claim should compare the same fixed task suite before and after parent access is reduced.
4. **Measure hidden work.** Local retries, storage growth, and increased computation must not disguise reduced parent calls.
5. **Bound the skill library.** An ever-growing library conflicts with the project's "smaller and quieter" objective; later phases need consolidation, deprecation, and forgetting.
6. **Preserve no-parent and mocked-parent controls.** They are necessary to distinguish actual acquired capability from invisible provider dependence.
7. **Record provenance by transformation class.** Parent advice, retained memory, deterministic code, and trained weights should have different permission and audit requirements.

## Next research passes

- developmental AI systems with scheduled or competence-gated teacher withdrawal
- continual-learning systems that measure decreasing teacher dependence
- repository-based persistent agents and software identity or lineage
- skill-library compression, retirement, and bounded-memory agents
- resource-rational cognition and retained capability per unit cost
- safe self-improvement with protected evaluators and rollback
- legal and contractual treatment of generated code, deterministic skills, synthetic data, and model distillation for each candidate provider

## Research discipline

- Prefer primary papers and official project documentation.
- Record publication date, implementation availability, experimental design, and direct relevance.
- Separate conceptual similarity from an implemented and measured precedent.
- Record negative searches without treating them as proof of novelty.
- Do not write public novelty claims until the comparison matrix and bibliography are substantially complete.
