# Caregiver Withdrawal and Retained Competence

Status: **Phase 3 research note — evidence pass 1, not a novelty claim**

Verified: **2026-07-29**

Tracked by: GitHub Issues #3 and #129

## Purpose

This note tests one of SUDACHI's strongest preliminary candidate distinctions:

> maturity measured as retained capability under declining or withdrawn caregiver access

The review asks whether adjacent systems already reduce teacher, expert, scaffold, skill, or advice access as the learner improves, and whether they evaluate the learner after that assistance is absent.

This is research-only. It does not authorize any runtime change, live caregiver, model API, network access, memory, skill adoption, action adoption, or modification of frozen Phase 1 or Phase 2 behavior.

## Bottom line

The broad mechanism is established.

Machine-learning systems already:

- ration teacher advice under finite budgets;
- gate intervention by uncertainty, novelty, risk, disagreement, or expected utility;
- reduce expert monitoring as the learner improves;
- train a student under temporary explanations or skills and test later performance without those inputs;
- progressively withdraw inference-time skill context until a policy operates with no skill retrieval;
- adapt a temporary scaffold to current policy competence and discard it at deployment;
- measure reduced human burden, annotation count, prompt tokens, or interaction cost.

Two recent systems are especially close to the broad SUDACHI hypothesis:

- **SKILL0** progressively withdraws skill context through a dynamic curriculum until an LLM agent operates in a zero-shot setting without runtime skill retrieval.
- **PATS** adapts a temporary training scaffold to policy competence, compresses or removes redundant guidance as performance improves, and discards the scaffold at deployment while measuring success and prompt-token cost.

Therefore, SUDACHI must not claim novelty for caregiver fading, competence-gated support, scaffold-free deployment, retained task performance after withdrawal, or lower inference overhead by themselves.

The remaining plausible contribution is narrower and integrative:

> one persistent bounded artificial individual links finite recorded caregiving to provenance-preserving, verified and versioned local artifacts, then demonstrates retained capability under caregiver withdrawal while protected evaluation, rollback lineage, abstention, storage, computation, retries, and human labor remain auditable.

This remains a hypothesis. This pass did not identify a directly equivalent integrated system, but an unsuccessful search is not proof of novelty.

## Evidence matrix

Legend:

- **yes**: explicit in the paper or official abstract;
- **partial**: adjacent mechanism is present, but the exact SUDACHI property is not established;
- **no**: the source does not make the property part of its contribution;
- **unclear**: a full-text protocol review is still required.

| System | Assistance form | Finite or gated assistance | Competence-aware fading | Evaluation with assistance absent | Persistence substrate | Same persistent individual and lineage | Protected evaluation / rollback | Explicit burden or deployment cost | Direct relevance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DAgger (2011) | expert action labels | partial | no | yes, learned stationary policy | policy parameters | no | no | no | Establishes iterative expert-assisted training followed by autonomous policy execution, but not developmental fading. |
| Teaching on a Budget (2013) | teacher action advice | yes, fixed advice budget | partial, advice timing is optimized | partial, budget exhaustion implies later unassisted learning | value/policy learner | no | no | advice count | Establishes finite teacher access as a learning constraint. |
| Interactive Teaching Strategies (2016) | action advice and teacher attention | yes, selective advising | partial | no, teacher remains available | policy learner | no | no | teacher attention | Separates teacher monitoring cost from advice count. |
| SafeDAgger (2017) | reference-policy queries | yes, query-efficient safety gating | partial | yes, trained driving policy | policy parameters | no | no | query count and convergence | Establishes automated query reduction and curriculum-like expert use. |
| HG-DAgger (2019) | human takeover and corrective labels | human-gated | partial | yes, fully trained novice is evaluated | policy plus learned risk threshold | no | no | intervention burden implicit | Establishes human-controlled intervention and prediction of novice competence by state region. |
| ThriftyDAgger (2022) | human interventions | yes, declared intervention budget; novelty/risk gating | partial | partial; the method can still intervene at execution time | policy plus switching/risk model | no | no | intervention count, duration, user burden | Very close on budgeted help requests, but reduced intervention is not equivalent to complete caregiver withdrawal. |
| Can Language Models Teach? (2023) | teacher-LLM explanations | yes, teacher communicates for only a fraction of data | yes, intervention is selected by expected utility | yes, future unexplained data are evaluated | student model behavior/parameters | no | no | explanation budget | Direct precedent for finite explanation budgets and improved later performance without explanations. |
| Agnostic Interactive Imitation Learning (2024) | expert action annotations | yes, query minimization | partial | yes, final learner policy | policy parameters | no | no | annotation count | Establishes performance competitive with an expert under limited annotations. |
| MILES (2025) | one human demonstration | yes, one demonstration and one reset | no adaptive fading; assistance ends immediately | yes, later data collection and execution are autonomous | learned policy | no | no | demonstrations, resets, interventions | Strong precedent for finite scaffolding followed by autonomous retained behavior. |
| AIM / Robot-Gated IIL (2025) | expert takeover demonstrations | yes, agent requests help | yes, request criterion changes with expert-policy alignment | partial | policy plus proxy Q-function | no | no | takeover cost, monitoring effort, data, interactions | Direct precedent for competence-sensitive reduction of expert intervention. |
| CADP (2025) | inter-agent advice during centralized training | yes, communication is progressively constrained | yes | yes, decentralized execution | decentralized policies | no | no | communication overhead implicit | Adjacent precedent for training-time advice followed by independent execution without performance degradation. |
| SkillRL (2026) | retrieved reusable skills | no withdrawal objective; skills persist | partial, library co-evolves | no, retrieval remains part of execution | hierarchical skill library plus policy | no | no | token footprint | Important contrast: competence grows through a persistent external skill bank. |
| SKILL0 (2026) | inference-time skill context during training | yes, linearly decaying budget | yes, policy helpfulness controls retention | yes, fully zero-shot with no runtime skill retrieval | model parameters | no | no | context tokens | Directly weakens novelty claims about progressive scaffold withdrawal and independent deployment. |
| ReSkill (2026) | created and versioned skills | bounded by testing and pruning rather than full withdrawal | partial | no, skills remain part of the agent mechanism | versioned skill set plus policy | partial lifecycle, not organism lineage | no | marginal overhead and skill lifecycle | Strong adjacent precedent for skills being created, tested, refined, selected, and pruned as policy changes. |
| PATS (2026) | temporary textual training scaffold | yes, scaffold has entry/token limits and is removed at deployment | yes, support expands, revises, compresses, or disappears according to policy performance | yes, scaffold-free deployment | model policy parameters; scaffold is discarded | no | task evaluation, but no protected lineage/rollback boundary | success rate and prompt-token reduction | Closest current precedent to temporary, competence-aware scaffolding and “smaller and quieter” deployment. |

## Annotated primary-source bibliography

### Ross, Gordon, and Bagnell — DAgger (2011)

**Source:** “A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning.” AISTATS 2011.  
https://proceedings.mlr.press/v15/ross11a.html

**Implemented/evaluated:** yes.

**Contribution:** trains a stationary deterministic policy through iterative interaction with an expert-labeled state distribution.

**Relevance:** expert assistance is a training mechanism rather than a permanent runtime dependency. It establishes autonomous learned-policy evaluation, but does not define support withdrawal as maturation, track one long-lived individual, preserve caregiving provenance, or use protected evaluation and rollback.

### Torrey and Taylor — Teaching on a Budget (2013)

**Source:** “Teaching on a Budget: Agents Advising Agents in Reinforcement Learning.” AAMAS 2013.  
https://www.ifaamas.org/Proceedings/aamas2013/forms/contents.htm

**Implemented/evaluated:** yes, in Mountain Car and Pac-Man.

**Contribution:** a teacher suggests actions only a limited number of times; the work studies how advice timing changes student learning.

**Relevance:** finite caregiver access and consultation-count accounting are established. The goal is faster learning under a budget, not an auditable developmental individual or retained capability per total resource cost.

### Amir, Kamar, Kolobov, and Grosz — Interactive Teaching Strategies (2016)

**Source:** “Interactive Teaching Strategies for Agent Training.” IJCAI 2016.  
https://www.ijcai.org/Abstract/16/119

**Implemented/evaluated:** yes.

**Contribution:** teacher and student jointly identify useful advising opportunities so that the teacher need not continuously monitor the student.

**Relevance:** human attention is explicitly separable from the number of advice events. The work reduces monitoring burden but does not require full withdrawal or retained post-withdrawal competence.

### Zhang and Cho — SafeDAgger (2017)

**Source:** “Query-Efficient Imitation Learning for End-to-End Simulated Driving.” AAAI 2017.  
https://ojs.aaai.org/index.php/AAAI/article/view/10857

**Implemented/evaluated:** yes, in a car-racing simulator.

**Contribution:** reduces expensive reference-policy queries through a safety policy and reports faster convergence.

**Relevance:** query-efficient expert use and automated curriculum effects are established. Query reduction alone is not evidence of a maturing persistent organism.

### Kelly et al. — HG-DAgger (2019)

**Source:** “HG-DAgger: Interactive Imitation Learning with Human Experts.” ICRA 2019.  
https://arxiv.org/abs/1810.02890

**Implemented/evaluated:** yes, simulated and real-world autonomous driving.

**Contribution:** lets human experts take control and learns a model-uncertainty safety threshold that predicts the fully trained novice’s performance in different state-space regions.

**Relevance:** human-gated intervention and competence-region modeling are strong precedents for bounded caregiver proposals and selective intervention. The work does not expose event lineage, artifact provenance, protected tests, or rollback.

### Hoque et al. — ThriftyDAgger (2022)

**Source:** “ThriftyDAgger: Budget-Aware Novelty and Risk Gating for Interactive Imitation Learning.” CoRL 2021 proceedings, published 2022.  
https://proceedings.mlr.press/v164/hoque22a.html

**Implemented/evaluated:** yes, simulation, physical cable routing, and a user study.

**Contribution:** a learned switching policy requests human intervention under a declared budget when states are novel or task completion is risky.

**Relevance:** explicit intervention budgets, request gating, and supervisor-burden measurement overlap strongly with SUDACHI. However, the method can retain execution-time intervention, so lower request frequency cannot be treated as equivalent to independence.

### Saha, Hase, and Bansal — Can Language Models Teach? (2023)

**Source:** “Can Language Models Teach? Teacher Explanations Improve Student Performance via Personalization.” NeurIPS 2023.  
https://proceedings.neurips.cc/paper_files/paper/2023/hash/c6afe9a5d1e1068796d32613ddca1ab7-Abstract-Conference.html

**Implemented/evaluated:** yes.

**Contribution:** a teacher LLM intervenes under a communication budget, personalizes explanations, and improves the student’s performance on future unexplained data; misleading teachers can also degrade performance severely.

**Relevance:** finite explanations followed by unassisted evaluation and explicit harmful-teacher controls are direct precedents. The transformed capability is not an inspectable deterministic artifact with organism lineage.

### Li and Zhang — Agnostic Interactive Imitation Learning (2024)

**Source:** “Agnostic Interactive Imitation Learning: New Theory and Practical Algorithms.” ICML 2024.  
https://proceedings.mlr.press/v235/li24ck.html

**Implemented/evaluated:** yes.

**Contribution:** learns a policy competitive with an expert while querying as few expert annotations as possible, including settings where the expert cannot be represented exactly by the learner.

**Relevance:** expert annotation efficiency and imperfect embodiment are established. The evaluation target is policy competitiveness, not longitudinal maturity or artifact provenance.

### Papagiannis and Johns — MILES (2025)

**Source:** “MILES: Making Imitation Learning Easy with Self-Supervision.” CoRL 2024 proceedings, published 2025.  
https://proceedings.mlr.press/v270/papagiannis25a.html

**Implemented/evaluated:** yes, several real-world manipulation tasks; code and videos are linked from the paper page.

**Contribution:** learns from a single demonstration and a single reset, then autonomously gathers self-supervised data without additional human interventions.

**Relevance:** this is a clear finite-scaffolding-to-autonomous-capability precedent. It does not use adaptive fading, persistent organism identity, protected evaluation, or rollback.

### Cai, Peng, and Zhou — AIM (2025)

**Source:** “Robot-Gated Interactive Imitation Learning with Adaptive Intervention Mechanism.” ICML 2025.  
https://proceedings.mlr.press/v267/cai25e.html

**Implemented/evaluated:** yes; official code is linked from the paper page.

**Contribution:** learns an adaptive criterion for requesting expert demonstrations; intervention pressure decreases as the learner’s actions align with the expert. The paper reports lower takeover cost, monitoring effort, expert data, and environment interaction.

**Relevance:** competence-sensitive assistance reduction and explicit human burden are established. SUDACHI must distinguish persistent retained competence after complete withholding from better intervention gating during training.

### Zhou et al. — CADP (2025)

**Source:** “CADP: Towards Better Centralized Learning for Decentralized Execution in MARL.” IJCAI 2025.  
https://www.ijcai.org/proceedings/2025/803

**Implemented/evaluated:** yes; code is linked by the official proceedings page.

**Contribution:** enables advice exchange during centralized multi-agent training and progressively constrains communication into a closed form while preserving decentralized execution performance.

**Relevance:** progressive removal of an external information channel before independent execution is an adjacent direct precedent, although the setting is multi-agent coordination rather than caregiver development.

### Xia et al. — SkillRL (2026)

**Source:** “SkillRL: Evolving Agents via Recursive Skill-Augmented Reinforcement Learning.” arXiv 2026.  
https://arxiv.org/abs/2602.08234

**Implemented/evaluated:** yes; code is linked from the paper.

**Contribution:** distills experience into a hierarchical skill library that co-evolves with an LLM-agent policy and reduces token footprint.

**Relevance:** strong precedent for experience-to-reusable-skill conversion, but the skill library remains an inference-time dependency. It is a useful control against which genuine caregiver withdrawal should be compared.

### Lu et al. — SKILL0 (2026)

**Source:** “SKILL0: In-Context Agentic Reinforcement Learning for Skill Internalization.” arXiv 2026.  
https://arxiv.org/abs/2604.02268

**Implemented/evaluated:** yes; code is linked from the paper.

**Contribution:** begins training with full skill context, uses a dynamic curriculum to retain only currently helpful skills within a linearly decaying budget, and ends in a fully zero-shot setting without runtime skill retrieval.

**Relevance:** this directly rules out novelty claims based only on progressive support withdrawal, skill internalization, or autonomous operation after runtime scaffolding is removed. Its persistent substrate is model parameters rather than a repository-defined organism with auditable artifact lineage.

### He et al. — ReSkill (2026)

**Source:** “ReSkill: Reconciling Skill Creation with Policy Optimization in Agentic RL.” arXiv 2026.  
https://arxiv.org/abs/2606.01619

**Implemented/evaluated:** yes.

**Contribution:** creates assertion-driven skills from failures, compares skill versions during policy rollouts, selects versions adaptively, and reports skill creation, testing, refinement, and pruning as the policy evolves.

**Relevance:** versioned skill lifecycle and pruning are no longer safe novelty candidates. SUDACHI’s remaining distinction would require stronger provenance, protected adoption, rollback lineage, bounded total storage, and caregiver-withdrawal evaluation.

### Shi et al. — PATS (2026)

**Source:** “PATS: Policy-Aware Training Scaffolding for Agentic Reinforcement Learning.” arXiv v1, 2026-07-23.  
https://arxiv.org/abs/2607.21419

**Implemented/evaluated:** yes, on ALFWorld, WebShop, and seven search-augmented QA benchmarks.

**Contribution:** treats skills as a temporary dynamic training scaffold. Evidence from the current policy updates the scaffold; guidance is expanded, revised, compressed, or removed as competence changes. The scaffold is discarded at deployment. The authors report performance gains and lower prompt-token use than persistent-skill baselines.

**Relevance:** this is the closest current precedent to competence-aware temporary scaffolding and reduced deployment overhead. It substantially weakens any claim that SUDACHI is distinctive merely because external reasoning becomes unnecessary or because deployment gets smaller and quieter. PATS does not, from this pass, establish one auditable persistent organism whose individual caregiving events become verified deterministic artifacts under protected evaluation, checkpoint lineage, rollback, and total resource accounting.

## Claim assessment after this pass

| Candidate claim | Assessment | Confidence | Reason |
| --- | --- | --- | --- |
| Teacher or caregiver access can deliberately fade during machine development. | **Established; ruled out as a novelty claim.** | high | Advice budgets, intervention gating, SKILL0, and PATS directly cover scheduled or adaptive reduction. |
| Assistance can be reduced according to learner competence. | **Established; ruled out as a novelty claim.** | high | AIM, SKILL0, and PATS explicitly adapt support to alignment, helpfulness, or policy performance. |
| A learner can retain task capability after assistance is fully removed. | **Established as an evaluation pattern.** | high | DAgger-family deployment, finite-explanation teaching, MILES, SKILL0, CADP, and PATS evaluate autonomous or scaffold-free policies. |
| Lower caregiver use plus lower inference overhead demonstrates development. | **Established neighboring objective; insufficient alone.** | high | PATS and SKILL0 explicitly combine scaffold removal with reduced prompt/context cost. |
| Teacher independence is commonly named “maturity” of an artificial individual. | **Still plausible as a framing distinction, not yet a technical novelty.** | medium-low | This pass found autonomy, zero-shot behavior, decentralized execution, and burden reduction, but not the exact organism-maturity framing. Terminology alone is weak. |
| The same persistent individual links finite recorded caregiving to verified, versioned local artifacts and later independence. | **Plausible integration candidate.** | medium | Skill lifecycle, provenance, persistence, and withdrawal all have separate precedents; this pass found no exact integrated system. |
| Protected evaluation, rollback lineage, and total resource accounting are jointly required for caregiver-withdrawal claims. | **Plausible measurement and systems contribution.** | medium | Adjacent work measures selected burdens, but this pass found no complete protected-evaluator, lineage, rollback, and hidden-cost package. |
| Repository state, tests, checkpoints, and Git lineage constitute the experimental organism body. | **Unresolved conceptual and engineering candidate.** | low-medium | This research slice did not perform the dedicated repository-identity search required to assess it. |

## Terminology and positioning

The literature uses several neighboring terms that must be searched separately:

- advice budget;
- intervention budget;
- query-efficient imitation learning;
- human-gated or robot-gated intervention;
- adaptive intervention;
- teacher attention or monitoring burden;
- student-initiated advising;
- skill internalization;
- curriculum withdrawal;
- scaffold fading;
- temporary training scaffold;
- scaffold-free or zero-shot deployment;
- centralized training with decentralized execution;
- expert-free execution;
- autonomous self-supervision.

Recommended positioning:

- Use **caregiver withdrawal** for the SUDACHI-level experimental variable.
- Use **support schedule** for a declared exogenous reduction rule.
- Use **competence-gated fading** when support changes according to protected evaluation.
- Use **withheld-caregiver evaluation** for trials where the assistance channel is unavailable rather than merely unused.
- Use **retained competence** only when the same fixed capability suite remains satisfied after withdrawal.
- Use **intervention efficiency** only for fewer requests or monitoring events; do not treat it as independence.
- Use **scaffold-free deployment** only when no runtime scaffold, skill retrieval, or advice channel remains available.

## Negative-search record

Searches were performed on 2026-07-29 across primary proceedings, arXiv, official repositories, and citation-oriented web search using combinations of:

- `maturity retained capability caregiver withdrawal artificial agent`;
- `teacher independence machine learning maturity metric`;
- `developmental robotics competence-gated teacher withdrawal`;
- `same learner longitudinal caregiver withdrawal retained competence`;
- `repository organism body caregiver provenance rollback protected evaluation`;
- `human minutes per retained capability artificial agent`;
- `scaffold-free deployment skill internalization agent`;
- `temporary training scaffold policy competence withdrawal`.

No direct system was identified that jointly requires all of the following:

1. one persistent artificial individual with explicit lineage;
2. finite recorded caregiver episodes;
3. transformation into provenance-preserving, versioned, locally inspectable artifacts;
4. protected adoption and evaluation outside caregiver authority;
5. complete caregiver withholding;
6. retained fixed capability after withholding;
7. rollback that preserves abandoned developmental futures;
8. full accounting of human labor, model calls, latency, retries, compute, and storage.

This is a **negative search record, not evidence of absence**. The result is sensitive to terminology, indexing, unpublished systems, non-English literature, and conceptual work that may use different organism or software-evolution vocabulary.

## Design implications for a later Phase 3 gate

1. **Do not define Phase 3 novelty as fading alone.** SKILL0 and PATS are direct counterexamples.
2. **Require an unavailable-caregiver condition.** A system that merely chooses not to ask while the channel remains available has not passed withdrawal.
3. **Separate assistance gating from competence acquisition.** Lower interventions can result from a better gate without any new local capability.
4. **Classify the retained substrate.** Record whether assistance became model weights, a policy, retrieved memory, a skill file, deterministic code, a rule, a test, or an unchanged external router.
5. **Compare against persistent-skill and internalized-weight baselines.** SkillRL, ReSkill, SKILL0, and PATS represent materially different developmental mechanisms.
6. **Measure the same individual longitudinally.** Before/after comparisons must bind organism identity, lineage, environment, task suite, and evaluator version.
7. **Protect the measuring stick.** Caregiver and organism must not be able to weaken withdrawal tests, alter evaluator authority, or erase failed developmental paths.
8. **Count hidden burden.** At minimum: consultations, human monitoring time, intervention duration, clarification rounds, model calls, prompt and output tokens, latency, retries, environment resets, training compute, inference compute, storage growth, and maintenance labor.
9. **Test misleading assistance and premature withdrawal.** Teacher explanations can harm performance; withdrawal schedules can create dependency or collapse.
10. **Preserve no-caregiver and deterministic-fixture controls.** They remain necessary to distinguish acquired competence from invisible external support.

## Evidence limits and exact next action

This first pass primarily uses official abstracts, proceedings pages, and author-provided preprints. It is sufficient to rule out broad novelty claims about fading and scaffold-free deployment, but not sufficient for a final Related Work section or a strong novelty assessment.

The next exact research action is a full-text protocol extraction for the closest systems:

1. SKILL0;
2. PATS;
3. AIM;
4. ThriftyDAgger;
5. MILES;
6. Can Language Models Teach?;
7. ReSkill.

For each, extract the exact unit of assistance, withdrawal schedule, evaluation timing, whether the channel is unavailable or merely unused, persistence substrate, identity assumptions, failure controls, and complete reported cost metrics. Then update the comparison matrix with page-level evidence and determine the minimum defensible Phase 3 experiment-design distinction.