# Withdrawal Protocol Extraction

Status: **Phase 3 full-text evidence note — not a novelty claim and not an accepted runtime design**

Verified: **2026-07-29**

Tracked by: GitHub Issues #3 and #130

Companion note: [`CAREGIVER_WITHDRAWAL_AND_RETAINED_COMPETENCE.md`](CAREGIVER_WITHDRAWAL_AND_RETAINED_COMPETENCE.md)

## Purpose

This note extracts the exact assistance unit, withdrawal condition, evaluation condition, retained substrate, identity assumptions, failure controls, and reported cost surface from the closest systems identified in the first Phase 3 caregiver-withdrawal evidence pass.

It resolves one ambiguity that the abstract-level comparison could not close:

> Does evaluation make assistance genuinely unavailable, or does the learner merely choose not to request it while teacher-derived runtime scaffolding remains present?

This is a research-only artifact. It does not authorize a live caregiver, model API, human chat, network access, subprocess, memory, skill adoption, action adoption, training, or any change to frozen Phase 1 or Phase 2 behavior.

## Protocol categories

The reviewed systems separate into four materially different withdrawal classes.

### W0 — assistance remains available

The learner may request less assistance, but the channel remains available during evaluation or deployment.

Reduced request frequency is intervention efficiency, not demonstrated independence.

### W1 — live source unavailable; source-derived runtime artifact remains

The teacher or human is absent, but explanations, demonstrations, prompts, retrieved skills, action suffixes, or another teacher-derived runtime artifact remain available.

This proves independence from the live source, not scaffold-free operation.

### W2 — runtime assistance channel and temporary scaffold unavailable

No teacher call, intervention route, retrieved skill context, or temporary scaffold is available at evaluation. Capability remains in policy or model parameters.

This establishes assistance-independent performance, but not an auditable caregiver-to-local-artifact developmental lineage.

### W3 — identity-bound artifact conversion under protected lineage

One persistent individual records finite assistance events, transforms accepted assistance into provenance-bound and inspectable local artifacts, and passes a fixed withheld-caregiver evaluation under protected evaluator and rollback rules with complete cost accounting.

No reviewed system in this pass establishes the complete W3 package. This is a negative search result, not proof of novelty.

## Extraction matrix

| System | Assistance unit | Withdrawal schedule or gate | Evaluation condition | Withdrawal class | Retained substrate | Identity and lineage | Failure controls | Reported cost surface | Missing for SUDACHI comparison |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SKILL0 | Skill descriptions injected into the agent context | Starts with full skill context; a linearly decaying budget and per-skill helpfulness tests progressively remove context | Final evaluation is zero-shot with no runtime skill retrieval | W2 | Updated model parameters | Training checkpoint identity only; no persistent organism lineage | Measures skill helpfulness by comparing rollouts with and without each skill | Prompt/context-token use and task performance | No assistance-event provenance, inspectable local artifact lineage, protected evaluator, rollback, human labor, storage, or maintenance accounting |
| PATS | Temporary textual entries in a policy-aware training scaffold | Scaffold edits expand, revise, compress, or remove entries according to frozen-policy evaluation evidence and entry/token limits | The complete scaffold block is removed for unsupported evaluation and deployment | W2 | Updated model policy parameters; scaffold is discarded | Frozen policy snapshots and scaffold edit history, but no persistent organism identity | Proposed scaffold edits are validated against frozen policy snapshots before acceptance | Success rate and prompt-token reduction | No caregiver-event identity, retained local artifact, protected evaluator authority, rollback lineage, or complete human/model/compute/storage ledger |
| AIM | Expert takeover demonstrations requested by a robot gate | Request criterion adapts as policy and expert actions align; initial human-gated trajectories seed learning | Held-out tests run the learned agent without expert involvement | W2 for reported evaluation; W0 during training | Learned policy and proxy value/gating model | Policy checkpoint only; no organism lineage | Evaluates adaptive intervention against baselines; paper assumes a correct expert and reports no real-human experiment | Expert-involved steps, expert data, total data, environment interactions, takeover/monitoring burden | No misleading-expert evaluation, persistent identity, artifact provenance, protected evaluator, rollback, or full time/compute/storage accounting |
| ThriftyDAgger | Human intervention segments and corrective demonstrations | Novelty and risk gate operate under a declared intervention budget | Reports both autonomous success with interventions forbidden and intervention-aided success | W2 for autonomous-success trials; W0 for aided execution | Robot policy; switching model for aided mode | Policy checkpoint only | Risk/novelty gating, physical evaluation, and a user study | Intervention count and duration, human/robot actions, mental load, frustration, idle time | No persistent lineage, artifact conversion, protected evaluator, rollback, model/token/compute/storage/maintenance ledger |
| MILES | One human demonstration and one reset | No adaptive fading; human assistance ends after the initial demonstration/reset | Autonomous data collection and policy execution occur without further live human input | W1 in tasks that retain a demonstrated action suffix; otherwise approaches W2 | Behavior-cloned recurrent policy; pose-estimation mechanism; a demonstrated action suffix may remain available after disturbances | One trained policy instance, not an auditable individual lineage | Validates augmented trajectories and returns to the demonstration trajectory after perturbations | One demonstration, one reset, reset duration, autonomous collection time, augmentation trajectories | Demonstration-derived runtime residue can remain; no protected evaluator, rollback, event provenance, compute/storage/maintenance accounting |
| Can Language Models Teach? | Personalized teacher-LLM explanations for selected examples | Teacher intervenes only within a fixed communication budget chosen by expected utility | Future test examples prohibit live teacher intervention, but prior teacher explanations remain in the student prompt | W1 | In-context explanation examples and student behavior; not a verified deterministic artifact | Prompt/session state only | Includes misleading-teacher conditions that can reduce performance toward chance | Intervention percentage/count | No scaffold-free test, persistent individual, artifact adoption, protected evaluator, rollback, token/latency/compute/storage/human-time ledger |
| ReSkill | Assertion-driven skills proposed from failures and supplied to policy rollouts | New and prior skill versions are tested; versions are accepted, rejected, refined, selected, or pruned as the policy changes | The skill bank remains part of the agent mechanism; some internalized skills may be pruned | W1 | Evolving policy plus external versioned skill bank/reservoir | Skill proposal history and versions, but no organism lineage | Within-group old/new skill testing, reward-based accept/reject, trigger validation, proposal history | Claimed marginal additional overhead; no complete ledger | No full scaffold removal, protected evaluator authority, rollback preserving abandoned futures, identity-bound caregiving provenance, or full cost accounting |

## Source-by-source extraction

## 1. SKILL0

**Source:** Lu et al., “SKILL0: In-Context Agentic Reinforcement Learning for Skill Internalization,” arXiv:2604.02268, 2026.

**Implementation availability:** the paper links an implementation repository.

### Assistance unit

The assistance unit is a retrieved skill description placed in the model context during reinforcement-learning rollouts. Skills are not executable repository artifacts; they are inference-time textual context during training.

### Withdrawal protocol

The training curriculum begins with full skill context. A global skill budget decays linearly, while a local helpfulness test compares the current policy with and without each skill. Only currently helpful skills survive inside the shrinking budget.

The curriculum terminates at a zero-skill condition.

### Evaluation condition

The final agent is evaluated without runtime skill retrieval. The skill channel is not merely ignored: the evaluation context does not contain the skill scaffold.

This is an explicit W2 condition.

### Retained substrate

Capability is retained in updated model parameters.

The paper does not establish a separate inspectable local memory, code artifact, rule, test, or skill file that preserves event-level provenance from assistance to capability.

### Identity, validation, and rollback

The relevant identity is a training checkpoint or policy state. The paper does not define a persistent organism, lineage generation, checkpoint authority boundary, protected evaluator, or rollback that preserves an abandoned developmental future.

### Cost surface

The paper reports task performance and context or prompt-token behavior. It does not provide complete accounting for human labor, model-call cost, training compute, storage growth, retries, maintenance, or artifact review.

### SUDACHI implication

Progressive skill withdrawal, competence-aware support removal, skill internalization, and zero-skill deployment are established. None can be a standalone SUDACHI novelty claim.

## 2. PATS

**Source:** Shi et al., “PATS: Policy-Aware Training Scaffolding for Agentic Reinforcement Learning,” arXiv:2607.21419 v1, 2026-07-23.

**Implementation and evaluation:** evaluated on ALFWorld, WebShop, and seven search-augmented question-answering benchmarks.

### Assistance unit

The assistance unit is a temporary textual scaffold composed of compact entries derived from policy experience. It is inserted into the training prompt as a bounded experience block.

### Withdrawal protocol

A frozen policy snapshot produces evidence used to propose scaffold edits. Entries can be added, revised, compressed, or removed. Proposed changes are evaluated before acceptance. Entry and token limits bound the scaffold.

Support therefore changes according to measured policy competence rather than only a fixed time schedule.

### Evaluation condition

Unsupported evaluation removes the complete scaffold block. Deployment receives an empty scaffold rather than a persistent skill bank.

This is an explicit W2 condition.

The ordinary task renderer, interaction history, tool interface, and action format remain part of the environment. “Scaffold-free” therefore means removal of the learned temporary experience block, not removal of the task interface itself.

### Retained substrate

The retained capability is in model policy parameters. The scaffold is intentionally disposable and is not the deployed memory.

### Identity, validation, and rollback

PATS records frozen policy snapshots and a trace of scaffold edits. This is a meaningful precedent for evidence-backed, versioned scaffold operations.

However, the trace does not define one persistent organism, caregiver-event lineage, protected evaluator authority, checkpoint publication, or rollback preserving rejected developmental futures.

### Cost surface

The paper reports success and prompt-token reduction relative to persistent-skill baselines. It does not provide complete human labor, model-call, latency, retry, training-compute, storage, or maintenance accounting.

### SUDACHI implication

Temporary competence-aware scaffolding, evidence-backed scaffold revision, compression, removal, and smaller deployment are established. SUDACHI must distinguish itself through the identity-bound and protected conversion protocol, not the disappearance of the scaffold alone.

## 3. AIM / Robot-Gated Interactive Imitation Learning

**Source:** Cai, Peng, and Zhou, “Robot-Gated Interactive Imitation Learning with Adaptive Intervention Mechanism,” ICML 2025.

**Implementation availability:** the official proceedings and project page link code.

### Assistance unit

The expert supplies takeover demonstrations when the robot gate requests intervention.

### Withdrawal protocol

One or two human-gated demonstration trajectories initialize learning. The robot then requests assistance according to a proxy value function and expert-policy alignment. As the policy approaches expert behavior, intervention pressure decreases.

### Evaluation condition

Held-out evaluations run the learned agent without expert involvement. Reported evaluation includes repeated rollouts in which the agent acts alone.

This is W2 for the reported held-out condition. The intervention channel remains part of the training process, so training-time request reduction is not itself full withdrawal.

### Retained substrate

Capability is retained in the learned policy. A proxy value or gating model determines when assistance should be requested during training.

### Identity, validation, and rollback

The paper evaluates policy checkpoints, not a persistent individual with explicit lineage. It does not define an assistance-event-to-artifact provenance graph, protected evaluator, rollback, or immutable abandoned future.

### Failure controls

The paper compares adaptive intervention with several imitation-learning baselines. Its limitations state that experiments do not use real humans and assume a correct expert. It therefore does not close misleading-caregiver or human inconsistency failure modes.

### Cost surface

Reported measures include expert-involved steps, expert data, total data, environment interactions, takeover cost, and monitoring effort. Human minutes, latency, model calls, tokens, compute, storage, retries, and maintenance are not jointly accounted.

### SUDACHI implication

Competence-sensitive intervention decline and no-expert held-out evaluation are established. SUDACHI cannot equate a falling request rate with acquired local capability.

## 4. ThriftyDAgger

**Source:** Hoque et al., “ThriftyDAgger: Budget-Aware Novelty and Risk Gating for Interactive Imitation Learning,” Proceedings of Machine Learning Research 164, 2022.

**Implementation and evaluation:** simulation, physical cable-routing experiments, and a user study.

### Assistance unit

The human supplies intervention segments and corrective actions while controlling the robot.

### Withdrawal protocol

A switching policy requests intervention when the state is novel or the probability of task failure is high, subject to a declared intervention budget.

### Evaluation condition

The paper distinguishes:

- autonomous success, where interventions are not allowed; and
- intervention-aided execution, where the gate may still request human help.

The autonomous-success condition is W2. The aided condition is W0.

This distinction is methodologically important: a single system can report both assistance-independent capability and better assisted reliability, and those outcomes must not be conflated.

### Retained substrate

The autonomous substrate is the learned robot policy. Assisted execution additionally depends on the switching or risk model and an available human.

### Identity, validation, and rollback

The paper evaluates learned policies, not one persistent organism with lineage. It does not define protected evaluator authority, assistance-event provenance, checkpoint publication, or rollback.

### Failure and burden controls

The gate explicitly models risk and novelty. The user study reports subjective and operational burden, including intervention actions, robot actions, mental load, frustration, and idle time.

### Cost surface

The cost surface is broader than simple intervention count: intervention duration, human/robot actions, idle time, and user burden are visible. It still omits a complete model-call, token, latency, compute, storage, retry, and maintenance ledger.

### SUDACHI implication

Withheld-caregiver trials must make the channel unavailable and must be reported separately from assisted reliability trials. Intervention efficiency and independence are different dependent variables.

## 5. MILES

**Source:** Papagiannis and Johns, “MILES: Making Imitation Learning Easy with Self-Supervision,” Proceedings of Machine Learning Research 270, 2025.

**Implementation availability:** code and videos are linked from the official paper page.

### Assistance unit

The human provides one demonstration and one reset. The system then gathers self-supervised data autonomously around the demonstration trajectory.

### Withdrawal protocol

There is no competence-gated fading. Live human assistance ends immediately after the finite initial input.

### Evaluation condition

Data collection and policy execution proceed without further live human intervention.

However, after some disturbances the runtime can return to a demonstrated state and replay the remaining demonstrated action suffix. The live caregiver is absent, but a caregiver-derived runtime artifact can remain.

MILES is therefore W1 for tasks that depend on the retained action suffix and approaches W2 where the learned policy alone suffices.

### Retained substrate

The primary substrate is a behavior-cloned recurrent policy. The runtime also uses pose estimation and may preserve a demonstrated action segment for recovery.

### Identity, validation, and rollback

The paper evaluates a trained policy, not an individual with explicit lineage. It validates augmented trajectories before using them, but does not define a protected evaluator, checkpoint authority, rollback, or abandoned-future archive.

### Cost surface

Reported costs include one demonstration, one reset, reset duration, the number of augmentation trajectories, and approximately thirty minutes of autonomous data collection. Training compute, inference compute, storage, retries, maintenance, and hidden experimenter labor are not jointly accounted.

### SUDACHI implication

“No further human intervention” is weaker than “no caregiver-derived runtime scaffold.” A Phase 3 protocol must inventory retained demonstrations, prompt examples, action traces, skill banks, and recovery scripts before declaring caregiver independence.

## 6. Can Language Models Teach?

**Source:** Saha, Hase, and Bansal, “Can Language Models Teach? Teacher Explanations Improve Student Performance via Personalization,” NeurIPS 2023.

**Implementation and evaluation:** multi-round and single-round teaching experiments with declared communication budgets.

### Assistance unit

A teacher language model supplies personalized natural-language explanations for selected examples.

### Withdrawal protocol

The teacher selects interventions under a uniform explanation budget using expected utility. The teacher cannot intervene on future test points.

### Evaluation condition

The live teacher is unavailable during future test evaluation. Previously supplied explanations remain in the student’s in-context prompt.

This is W1, not W2: the live source is absent, but teacher-derived runtime scaffolding remains.

### Retained substrate

The retained substrate is a set of teacher explanations in context and the resulting student behavior. The protocol does not convert explanations into a separately verified deterministic artifact or permanently trained student weights.

### Identity, validation, and rollback

The relevant state is a prompt/session. There is no persistent individual lineage, protected evaluator, checkpoint authority, or rollback.

### Failure controls

The paper includes misleading-teacher conditions. Incorrect explanations can severely degrade student performance, approaching random chance in some settings.

This is a direct precedent for testing harmful assistance rather than assuming teacher benevolence.

### Cost surface

The primary cost is explanation count or percentage. The protocol does not jointly account prompt/output tokens, teacher latency, model cost, compute, storage, retries, or human review.

### SUDACHI implication

Phase 3 must distinguish live-caregiver absence from teacher-artifact absence and must include deliberately misleading, inconsistent, or low-quality caregiving controls.

## 7. ReSkill

**Source:** He et al., “ReSkill: Reconciling Skill Creation with Policy Optimization in Agentic RL,” arXiv:2606.01619, 2026.

**Implementation and evaluation:** evaluated with an evolving policy and skill mechanism.

### Assistance unit

The system creates assertion-driven textual skills from failure evidence. Skills are supplied to later policy rollouts.

### Lifecycle and selection protocol

ReSkill records proposal history, validates triggers, compares old and new skill versions within controlled groups, and accepts or rejects versions using rollout reward. Skills can be refined, selected, or pruned as the policy changes.

### Evaluation condition

The skill bank remains part of the agent mechanism. Some skills can be pruned after the policy internalizes their effect, but the system does not require a final no-skill deployment condition.

This is W1.

### Retained substrate

Capability is distributed between updated model policy parameters and an evolving external skill bank or reservoir.

### Identity, validation, and rollback

Version history and accept/reject testing are important precedents for skill lifecycle management. The paper does not define a protected evaluator outside policy and skill-author authority, one persistent organism lineage, or rollback preserving an abandoned developmental future.

No explicit rollback mechanism was identified in the full-text search.

### Cost surface

The paper characterizes the mechanism as adding marginal overhead but does not provide a complete human, model-call, token, latency, retry, compute, storage, or maintenance ledger.

### SUDACHI implication

Created, tested, versioned, accepted, rejected, refined, selected, and pruned skills are established mechanisms. SUDACHI’s candidate distinction must be the complete protected lineage and withdrawal experiment, not the existence of a skill lifecycle.

## Cross-system conclusions

### Full assistance unavailability is established

SKILL0, PATS, ThriftyDAgger autonomous-success trials, and AIM held-out evaluation demonstrate conditions in which the runtime assistance channel is unavailable.

SUDACHI therefore cannot claim novelty for no-helper evaluation or scaffold-free deployment alone.

### Finite human input followed by autonomous behavior is established

MILES demonstrates a one-demonstration and one-reset workflow followed by autonomous data collection and execution.

The runtime may still retain a demonstration-derived recovery trace, showing why finite live assistance is not sufficient evidence of scaffold-free competence.

### Live-source absence with retained teacher artifacts is established

“Can Language Models Teach?” prohibits future live teacher intervention while retaining explanations in the student prompt. ReSkill keeps an external skill bank during execution.

The phrase “caregiver absent” is therefore underspecified unless all caregiver-derived runtime substrates are enumerated.

### Versioned and tested skills are established

ReSkill records skill proposals, versions, validation, accept/reject decisions, refinement, selection, and pruning. PATS records evidence-backed scaffold edits against frozen policy snapshots.

SUDACHI cannot claim novelty for auditable skill edits or pruning alone.

### Complete cost accounting is not established by these systems

The reviewed systems expose different slices of burden:

- prompt or context tokens;
- explanation or annotation counts;
- intervention count and duration;
- expert-involved steps;
- user mental load and frustration;
- demonstrations, resets, and autonomous collection time;
- total environment data.

No reviewed protocol jointly accounts human minutes, consultations, model calls, input/output tokens, latency, retries, training compute, inference compute, storage growth, environment resets, artifact review, and maintenance labor.

## Minimum defensible Phase 3 experiment-design distinction

The literature rules out each of the following as a standalone contribution:

- caregiver fading;
- competence-gated assistance;
- a finite intervention budget;
- no-helper evaluation;
- scaffold-free deployment;
- finite demonstrations followed by autonomy;
- skill internalization into weights;
- created, tested, versioned, refined, or pruned skills;
- lower prompt or intervention cost.

A defensible SUDACHI experiment must instead bind these properties into one protocol:

1. **Identity-bound organism.** One persistent individual, lineage generation, environment, evaluator version, and capability suite are bound before and after development.
2. **Finite recorded caregiving.** Every assistance request, response, clarification, rejection, deferment, and cost is recorded as an event with exact provenance.
3. **Typed retained substrate.** Every caregiver-derived runtime dependency is classified as weights, prompt examples, retrieved memory, skill bank, code, rule, test, action trace, router, or other artifact.
4. **Verified local conversion.** Accepted assistance must become an inspectable, versioned local artifact or an explicitly declared weight update; silent teacher-derived residue is forbidden.
5. **Protected adoption and evaluation.** Caregiver and organism cannot weaken evaluators, alter authority, erase failures, or promote an artifact without the declared gate.
6. **Unavailable-caregiver trial.** The consultation channel is disabled, and no undeclared caregiver-derived prompt, skill retrieval, demonstration suffix, or external router remains available.
7. **Same-suite retained competence.** The same fixed capability, safety, abstention, transfer, and recovery suite is run before development, after adoption, and after withdrawal.
8. **Rollback lineage.** Rejected or harmful developmental futures remain auditable, and rollback creates a new lineage without rewriting the abandoned history.
9. **Failure controls.** Experiments include misleading advice, inconsistent advice, premature withdrawal, dependency collapse, and assistance that cannot be represented by the organism.
10. **Complete cost ledger.** Human minutes, monitoring, consultations, clarification, model calls, input/output tokens, latency, retries, resets, training compute, inference compute, storage growth, artifact review, and maintenance labor are visible.
11. **Substrate baselines.** Compare at least persistent prompt/skill-bank support, internalized-weight support, finite-demonstration policy learning, deterministic-fixture support, and no-caregiver control.
12. **No hidden redefinition.** Reduced caregiver burden counts as development only if protected performance is retained without shifting cost into unrecorded local work.

This package is a plausible integration and measurement contribution. It is not yet established as novel.

## Claim updates

| Candidate claim | Full-text assessment | Confidence | Evidence boundary |
| --- | --- | --- | --- |
| Assistance can deliberately fade according to competence. | Established; ruled out as novelty. | high | AIM, SKILL0, and PATS directly implement adaptive support reduction. |
| Evaluation can disable the assistance channel completely. | Established; ruled out as novelty. | high | SKILL0, PATS, ThriftyDAgger autonomous trials, and AIM held-out trials provide W2 conditions. |
| Finite live caregiving can be followed by autonomous behavior. | Established; ruled out as novelty. | high | MILES and imitation-learning systems provide direct precedents. |
| Teacher-derived runtime scaffolding can remain after the live teacher is gone. | Established and methodologically important. | high | Personalized explanation prompts, retained demonstrations, and skill banks show distinct W1 mechanisms. |
| Skills can be versioned, tested, accepted, rejected, refined, and pruned. | Established neighboring mechanism. | high | ReSkill and PATS provide direct precedents. |
| The same persistent organism can convert event-level caregiving into protected local artifacts and later pass a fully unavailable-caregiver trial under rollback lineage and complete cost accounting. | Plausible integration candidate; not proven novel. | medium | No exact equivalent was identified in this bounded search, but terminology and coverage remain incomplete. |
| Repository state, tests, checkpoints, and Git lineage form the organism body. | Unresolved. | low-medium | Requires a separate repository-identity and long-lived-software-agent research pass. |

## Evidence limitations

- Full paper PDFs were reviewed for SKILL0, PATS, ThriftyDAgger, MILES, “Can Language Models Teach?”, and ReSkill.
- AIM was extracted from the official proceedings abstract, official project materials, and indexed full-paper sections; a page-number-complete local PDF extraction remains desirable.
- The review does not cover every citation descendant, non-English publication, unpublished system, patent, or proprietary product.
- Absence of an exact match is not evidence of novelty.
- Provider permission, output transformation rights, privacy, and terms remain separate questions under `docs/PARENT_MODEL_PROVIDER_REVIEW.md`.

## Exact next action

Create a Phase 3 design-only Issue for a **Withheld-Caregiver Evaluation Contract**. The contract must define:

1. W0–W3 assistance-availability classes;
2. exact identity and lineage binding;
3. an exhaustive caregiver-derived runtime-substrate declaration;
4. the hidden-scaffold prohibition;
5. pre-development, post-adoption, and post-withdrawal evaluation points;
6. protected evaluator and artifact-adoption authority;
7. rollback and harmful-assistance evidence retention;
8. the complete cost ledger;
9. mandatory substrate baselines and failure controls;
10. an explicit gate separating research design from any later runtime implementation.

No Phase 3 implementation should begin until that design contract is reviewed and accepted.