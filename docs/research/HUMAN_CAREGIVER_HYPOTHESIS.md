# Human Caregiver Hypothesis

Status: **Preliminary research note — not a novelty claim**

Verified: **2026-07-21**

Tracked by: GitHub Issue #3

## Question

Could SUDACHI begin with a human caregiver rather than an AI model, learn through a bounded chat interface, and gradually require less human intervention?

## Preliminary answer

Yes. A human caregiver is scientifically coherent and may be a better first live source of developmental scaffolding than a commercial model API.

However, the following ideas already have substantial precedents:

- agents learning from human reward, correction, demonstration, preferences, language, and intervention
- robots developing through interaction with a caregiver
- systems that actively decide when to request human help
- algorithms that reduce human annotation or intervention burden
- virtual creatures whose behavior or personality changes according to owner interaction
- artificial-life systems with lifetime learning, social learning, persistence, and reproduction

Therefore, **"an artificial creature raised by a human" is not a defensible novelty claim by itself**.

A stronger SUDACHI hypothesis is:

> Can a bounded artificial organism convert finite human caregiving into verified local competence, measurably reducing its need for caregiver intervention while preserving protected capabilities and without hiding the cost in computation, storage, retries, or unrecorded human work?

The candidate contribution is the longitudinal integration and measurement of caregiver withdrawal, verified skill formation, bounded resources, protected evaluation, rollback, and organism continuity.

## Terminology change

The current phrase `parent model` is too narrow because it presupposes that the parent is a machine-learning model.

Use the following conceptual layers:

- **caregiver**: a human or artificial entity that provides developmental assistance
- **scaffolding channel**: the interface through which assistance is requested and returned
- **caregiver adapter**: an implementation for one assistance source
- **consultation**: one measured use of the scaffolding channel
- **adoption**: the separate process that verifies and incorporates a derived memory, rule, test, or skill

Candidate caregiver adapters include:

- deterministic fixture caregiver
- human chat caregiver
- local open-weight model
- hosted model API
- human-AI team
- no-caregiver baseline

The organism must not treat any caregiver as authoritative over protected policy, permissions, budgets, or evaluation.

## Closest research traditions

### 1. Developmental robotics and caregiver scaffolding

Nagai, Asada, and Hosoda studied joint-attention learning through interaction between a robot and a human caregiver. Their model included both robot development and caregiver development: as learning progressed, the caregiver changed the task from easier to harder situations. This is a direct precedent for caregiver-shaped machine development.

Related bootstrap-learning work studied higher capabilities emerging from interactions based on simpler embedded capabilities, including settings without explicit external evaluation.

Implication for SUDACHI:

- caregiver interaction and staged difficulty are established ideas
- a caregiver should adapt the kind and difficulty of assistance as the organism develops
- SUDACHI should distinguish a caregiver making tasks harder from an organism actually becoming less dependent

Primary sources:

- Yukie Nagai, Minoru Asada, and Koh Hosoda, "Acquisition of Joint Attention by a Developmental Learning Model based on Interactions between a Robot and a Caregiver" (2003): https://doi.org/10.1527/tjsai.18.122
- Yukie Nagai et al., "Emergence of Joint Attention through Bootstrap Learning based on the Mechanisms of Visual Attention and Learning with Self-evaluation" (2004): https://doi.org/10.1527/tjsai.19.10

### 2. Human feedback and socially guided machine learning

Human teachers have been used to supply reward, guidance, correction, demonstration, and ongoing dialog.

Thomaz and Breazeal showed that human teachers do not merely evaluate past actions; they also use reward signals to guide future behavior. COACH later modeled human feedback as dependent on the learner's current policy rather than as a fixed objective label. PEBBLE and related work study feedback-efficient human-in-the-loop reinforcement learning because human time is expensive.

Implication for SUDACHI:

- the caregiver cannot be modeled as a perfect, stationary oracle
- feedback meaning depends on context, the organism's current competence, and the caregiver's teaching strategy
- caregiver time is a real resource budget, not free background labor

Primary sources:

- Andrea L. Thomaz and Cynthia Breazeal, "Reinforcement Learning with Human Teachers: Evidence of Feedback and Guidance with Implications for Learning Performance" (2006): https://aaai.org/papers/00977-reinforcement-learning-with-human-teachers-evidence-of-feedback-and-guidance-with-implications-for-learning-performance/
- James MacGlashan et al., "Interactive Learning from Policy-Dependent Human Feedback" (2017): https://proceedings.mlr.press/v70/macglashan17a.html
- Kimin Lee, Laura M. Smith, and Pieter Abbeel, "PEBBLE: Feedback-Efficient Interactive Reinforcement Learning via Relabeling Experience and Unsupervised Pre-training" (2021): https://proceedings.mlr.press/v139/lee21i.html

### 3. Natural-language teaching and interactive task learning

Interactive Task Learning studies agents that acquire tasks through online natural-language instruction, often combined with demonstration and clarification. Systems have learned task concepts, games, puzzles, low-level skills, and high-level task structure from ongoing human dialog.

Interactive learning from activity description also shows that verbal descriptions can provide richer learning signals than scalar reward without requiring the teacher to demonstrate actions through the learner's embodiment.

Implication for SUDACHI:

- a chat interface for human teaching has direct precedents
- natural language alone is not a contribution
- SUDACHI must operationalize how advice becomes validated local capability and how later consultation is reduced

Primary sources:

- Baris Akgun et al., "Learning Tasks and Skills Together From a Human Teacher" (2011): https://doi.org/10.1609/aaai.v25i1.8002
- Joyce Y. Chai et al., "Language to Action: Towards Interactive Task Learning with Physical Agents" (2018): https://doi.org/10.24963/ijcai.2018/1
- James R. Kirk and John E. Laird, "Learning Hierarchical Symbolic Representations to Support Interactive Task Learning and Knowledge Transfer" (2019): https://doi.org/10.24963/ijcai.2019/844
- Khanh X. Nguyen et al., "Interactive Learning from Activity Description" (2021): https://proceedings.mlr.press/v139/nguyen21e.html

### 4. Assistance requesting and reduction of human burden

Several systems explicitly decide when human help is worth requesting.

ThriftyDAgger requests intervention under novelty or risk while respecting a human-intervention budget. Later robot-gated interactive imitation learning adapts its help-request criterion as alignment with the expert improves. Other work trains agents to request rich, contextual information from humans when autonomous ability is insufficient.

This literature is especially close to SUDACHI because it treats human attention as scarce and attempts to reduce requests as competence improves.

Implication for SUDACHI:

- fewer human requests is not new as an optimization target
- SUDACHI must go beyond intervention efficiency by studying persistent individual development, verified artifact formation, retained competence after withdrawal, rollback, and total resource cost

Primary sources:

- Ryan Hoque et al., "ThriftyDAgger: Budget-Aware Novelty and Risk Gating for Interactive Imitation Learning" (2022): https://proceedings.mlr.press/v164/hoque22a.html
- Khanh X. Nguyen, Yonatan Bisk, and Hal Daume III, "A Framework for Learning to Request Rich and Contextually Useful Information from Humans" (2022): https://proceedings.mlr.press/v162/nguyen22a.html
- Yichen Li and Chicheng Zhang, "Agnostic Interactive Imitation Learning: New Theory and Practical Algorithms" (2024): https://proceedings.mlr.press/v235/li24ck.html
- Haoyuan Cai, Zhenghao Peng, and Bolei Zhou, "Robot-Gated Interactive Imitation Learning with Adaptive Intervention Mechanism" (2025): https://proceedings.mlr.press/v267/cai25e.html

### 5. Imperfect teachers and mismatched understanding

Machine-teaching and imitation-learning research shows that a teacher may have incomplete knowledge of the learner, its state representation, its sensors, or its possible actions. Advice that is sensible for the teacher may be impossible, unsafe, or misleading for the learner.

Implication for SUDACHI:

- caregiver advice is evidence, not ground truth
- the organism must be able to ask for clarification, abstain, reject advice, or record unresolved ambiguity
- caregiver reliability should be evaluated by context rather than collapsed into one permanent trust score

Primary sources:

- Rati Devidze et al., "Understanding the Power and Limitations of Teaching with Imperfect Knowledge" (2020): https://doi.org/10.24963/ijcai.2020/367
- Andrew Warrington et al., "Robust Asymmetric Learning in POMDPs" (2021): https://proceedings.mlr.press/v139/warrington21a.html

### 6. Artificial life, social learning, and virtual creatures

Artificial-life research already studies lifetime learning, imitation, social transmission, persistence, reproduction, and the interaction between acquired and inherited behavior.

The 1996 game `Creatures` is an especially important precedent. Its persistent virtual creatures used neural and biochemical systems, interacted with human users and the environment, learned during their lifetimes, and reproduced with mutation.

Implication for SUDACHI:

- persistent virtual organisms that learn from interaction are not new
- SUDACHI must define its body, metabolism, development, learning, and lineage operationally
- its potential distinction lies in deliberate caregiver withdrawal and auditable conversion of assistance into bounded local artifacts, not in life-like vocabulary

Primary sources:

- Dave Cliff and Stephen Grand, "The Creatures Global Digital Ecosystem" (1999): https://doi.org/10.1162/106454699568683
- John A. Bullinaria, "Imitative and Direct Learning as Interacting Factors in Life History Evolution" (2017): https://doi.org/10.1162/ARTL_a_00237

## Tamagotchi comparison

### What Tamagotchi establishes

Bandai describes Tamagotchi as a portable nurturing digital pet. The caregiver feeds it, cleans it, treats illness, disciplines it, and plays games. Its growth path and adult form depend on how it is cared for.

This establishes several precedents:

- a persistent creature with needs
- periodic demands for human attention
- growth shaped by care history
- emotional attachment and responsibility
- multiple developmental outcomes

Official sources:

- Bandai character history: https://www.bandai.co.jp/character/tamagotchi.php
- Original Tamagotchi product description and care mechanics: https://www.bandai.com/original-tamagotchi-tama-garden

### What would make SUDACHI different

| Dimension | Tamagotchi | Candidate SUDACHI design |
| --- | --- | --- |
| Primary relationship | The owner repeatedly provides care | The caregiver provides temporary cognitive scaffolding |
| Developmental goal | Reach a growth form and remain cared for | Preserve competence while requiring less caregiver help |
| Human input | Feed, clean, heal, discipline, play | Explain, correct, demonstrate, constrain, clarify, or abstain |
| Behavioral structure | Primarily predefined state transitions and growth branches | Acquired, tested, versioned local memories, rules, and skills |
| Independence | Reduced owner involvement is generally neglect or end of play | Reduced justified consultation is the central maturity measure |
| Evaluation | Creature state and entertainment outcome | Fixed task success, safety, budget, transfer, recovery, and abstention tests |
| Auditability | Product-internal state | Explicit event history, provenance, checkpoints, and rollback |
| Resource objective | Sustain the care loop | Reduce caregiver burden and total cost per retained capability |

The distinction is not that SUDACHI has more complicated code or a chat box. The distinction must be experimentally demonstrated:

> After receiving finite caregiving, the same individual can handle a fixed class of situations with less caregiver intervention, without reduced protected performance or hidden increases in local work.

### Failure criterion: "Tamagotchi with Git"

If SUDACHI only:

- displays hunger, fatigue, curiosity, or affection meters
- asks a human what to do
- follows free-form instructions
- changes personality or cosmetic state
- accumulates chat history
- branches into predefined developmental stages

then it is not yet demonstrating the central hypothesis. It would be a virtual pet or task agent with additional record keeping.

To avoid this failure, each claimed developmental gain must identify:

1. the capability that previously required help
2. the caregiver interventions that supplied scaffolding
3. the verified local artifact or changed policy produced from experience
4. the fixed evaluation retained after assistance is withdrawn
5. the reduction in caregiver burden
6. any increase in local compute, storage, retries, or complexity

## aibo comparison

Sony describes aibo as an autonomous companion whose behavior and personality change through owner interaction. It learns which actions please its owner, recognizes people, adapts to its environment, and uses both on-device and cloud AI. Earlier AIBO products also learned through praise and scolding.

This is closer to SUDACHI than Tamagotchi because owner interaction genuinely changes behavior rather than only selecting a predefined growth character.

Official sources:

- Sony aibo launch description: https://www.sony.com/en/SonyInfo/News/Press/201711/17-105E/
- Sony aibo FAQ: https://electronics.sony.com/aibo-FAQ
- Original AIBO learning and growth description: https://www.sony.com/ja/SonyInfo/News/Press/199905/99-046/

Potential SUDACHI distinction:

- aibo optimizes an enduring companion relationship and remains dependent on a proprietary body and cloud service
- SUDACHI would explicitly measure decreasing caregiver dependence
- SUDACHI would expose event history, caregiver provenance, skill adoption, protected evaluations, checkpoints, and rollback as research artifacts
- SUDACHI would count storage, computation, and hidden assistance rather than presenting adaptation only as personality or bonding

This distinction must be tested, not assumed.

## Candidate novelty matrix

| Candidate claim | Current assessment | Notes |
| --- | --- | --- |
| A human can teach an artificial agent | Established | Human feedback, imitation learning, interactive task learning, and developmental robotics provide direct precedents. |
| A creature can develop differently according to its owner | Established | Tamagotchi, Creatures, and aibo are major precedents. |
| An agent can ask a human for help only when needed | Established | Assistance-requesting and intervention-gating systems directly address this. |
| Human intervention can decrease as a learner improves | Established neighboring objective | Interactive imitation learning explicitly reduces human monitoring and intervention cost. |
| A persistent artificial individual can convert caregiving into versioned local artifacts | Plausible integration candidate | Skill learning and persistent agents exist, but the exact audit and adoption pipeline needs deeper comparison. |
| Maturity is retained capability after caregiver withdrawal | Strong candidate for deeper novelty testing | Educational fading and intervention efficiency are precedents; an ALife individual using withdrawal as its primary maturity experiment remains less clearly matched. |
| Growth must reduce caregiver burden without hiding cost in storage or local computation | Strong systems-and-measurement candidate | Resource-aware learning exists, but this full longitudinal accounting may be distinctive in combination. |
| The same organism has an auditable developmental lineage with rollback | Plausible engineering-research candidate | Versioning and rollback are established engineering tools; their use as organism continuity and experimental lineage requires comparison. |

No row is yet a public novelty claim.

## Recommended first live-caregiver design

### Human caregiver as the first live parent

Use a human caregiver before a commercial model API because it:

- avoids per-call API cost
- avoids prematurely selecting a provider
- makes explanations and clarification available
- exposes inconsistency, ambiguity, delay, fatigue, and limited attention as real developmental conditions
- allows the researcher to observe the organism's consultation behavior directly

This does not make human labor free. Measure:

- caregiver minutes
- number of consultations
- number of clarification turns
- response latency
- intervention type
- caregiver confidence
- later reuse or rejection of the advice

### Bounded chat protocol

The chat interface should not pass arbitrary human text directly to actions.

Each caregiver response should be recorded as one or more typed proposals:

- `demonstration`
- `correction`
- `constraint`
- `explanation`
- `preference`
- `question`
- `defer`
- `abstain`

A proposal may reference only registered observations, objectives, actions, and permissions. It must pass normal validation, budget, sandbox, evaluation, and adoption boundaries.

The caregiver cannot directly:

- execute an action
- modify protected state or source code
- weaken a fixed evaluation
- increase a budget
- erase event history
- promote a proposed skill

### Developmental sequence

1. **Parent-free seed**
   - deterministic lifecycle
   - synthetic environment
   - fixed action registry
   - no human assistance

2. **Caregiver protocol test**
   - deterministic fixture caregiver
   - verify request, response, provenance, and abstention plumbing

3. **Human-assisted acquisition**
   - human answers bounded requests
   - advice is evaluated through environment outcomes
   - successful patterns become proposed local artifacts

4. **Competence-gated fading**
   - consultation budget decreases only after fixed evaluations pass
   - withheld-caregiver trials test retained capability

5. **Transfer and recovery**
   - test related unfamiliar tasks
   - inject failures or misleading advice
   - measure abstention, correction, and rollback

## Core experiment proposal

### Research question

Can one SUDACHI individual learn a small set of environment-management behaviors from a human caregiver and later preserve those behaviors when caregiver access is reduced or removed?

### Conditions

- no-caregiver baseline
- fixed scripted caregiver
- human caregiver with constant access
- human caregiver with competence-gated fading
- human caregiver removed after a fixed number of interventions

### Measures

- task success on a protected fixed suite
- caregiver consultations per successful action
- caregiver minutes per retained capability
- successful cycles without caregiver access
- skill reuse rate
- correction and clarification rate
- safe abstention under novelty
- recovery after misleading or contradictory advice
- storage and computation per retained capability
- total retries and hidden local work

### Strong success criterion

A developmental gain requires all of the following:

1. a capability initially fails or requires caregiver help
2. bounded caregiver assistance contributes to successful experience
3. the organism creates or updates a local, inspectable capability
4. fixed tests pass after caregiver access is reduced
5. the result reproduces from recorded state, seed, and event history
6. caregiver burden decreases without unacceptable regression
7. local cost growth remains within the declared bound

## Risks and controls

### Anthropomorphic false positives

A creature may appear attached, grateful, curious, or independent without gaining measurable competence.

Control: keep relational presentation separate from fixed capability evaluation.

### Hidden human labor

A researcher may repair files, tune prompts, select favorable events, or interpret outputs outside the recorded interface.

Control: record all interventions and distinguish experiment administration from caregiving.

### Caregiver overfitting

The organism may learn one person's vocabulary and preferences rather than transferable skills.

Control: paraphrase tests, delayed tests, second-caregiver tests, and no-caregiver transfer tasks.

### Unsafe obedience

The organism may treat a trusted caregiver instruction as permission.

Control: caregiver advice never bypasses permissions, protected evaluation, budgets, or sandboxing.

### Caregiver inconsistency

Human advice may conflict across time or be wrong.

Control: preserve provenance, request clarification, compare advice with outcomes, and support rejection or rollback.

### Research ethics and privacy

A single owner-researcher interacting with a local system is operationally simpler than a public human-subject study. If later experiments recruit participants or analyze their behavior, consent, privacy, and institutional research requirements must be reviewed before data collection.

## Current recommendation

Adopt the **human caregiver hypothesis** as the leading candidate for the first live developmental experiment, while keeping the architecture caregiver-neutral.

Do not yet redefine the entire project around a human-only parent. Preserve artificial caregivers as comparison conditions and future tools.

The immediate implementation order remains unchanged:

1. resolve ADRs 0001 through 0006
2. implement the deterministic, parent-free Phase 1 organism
3. test a deterministic caregiver adapter
4. design a separate reviewed human-chat caregiver protocol
5. begin human-assisted experiments only after fixed evaluations and provenance are operational

The clearest current distinction from virtual pets is not appearance, affection, or branching growth. It is the measurable conversion of finite caregiving into retained, auditable independence.