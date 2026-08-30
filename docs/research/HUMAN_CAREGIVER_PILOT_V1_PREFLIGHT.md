# Human Caregiver Pilot v1 Preflight

Status: **Proposed pre-live operational protocol — live human caregiving is not authorized**

Verified: **2026-08-30**

Tracked by: GitHub Issues #3 and #156

## Purpose

This note prepares the smallest useful first human-caregiver pilot without enabling a live human source.

Pilot v1 is an **operational protocol pilot**. Its purpose is to test whether human assistance can be captured as bounded, provenance-bearing, fully accounted proposals without giving the caregiver direct authority or contaminating protected evaluation. It is not a developmental-gain, maturity, comparative-effectiveness, or novelty experiment.

The current Phase 3 deterministic mechanics already establish a synthetic path from caregiver proposal to caregiving record, verified local substrate, caregiver withdrawal, and retained W1 capability. Pilot v1 asks only whether a real human source can later enter that path through a controlled boundary.

## Governing constraints

The accepted Phase 3 contract remains authoritative.

A human caregiver:

- supplies evidence, not ground truth or writer authority;
- cannot execute organism actions;
- cannot modify protected state, tests, evaluators, budgets, checkpoints, or history;
- cannot promote a proposal into an adopted artifact;
- cannot see held-out evaluator material;
- cannot remain reachable during E2 withheld-caregiver evaluation;
- must have every in-scope semantic intervention represented in the recorded evidence and cost surface.

Canonical writers remain exactly `organism` and `administration`.

## 2026-08-30 research update

The prior research note remains directionally valid: human teaching, caregiver-shaped development, interactive task learning, and decreasing intervention are established ideas. Human caregiving is therefore a research condition, not a novelty claim by itself.

Several additional findings sharpen Pilot v1.

### Human teaching is a variable experimental input

Zhong, Caspar, and Austerweil (2026) report persistent individual differences in how 82 people intervened while teaching reinforcement-learning agents. In their task, frequent interventions could improve immediate scores while impairing longer-term policy learning.

Implication: SUDACHI must not treat the human caregiver as a stationary oracle. Caregiver identity, intervention frequency, and intervention timing are experimental variables. A first operational pilot should use one caregiver and make no between-caregiver effectiveness claim.

Source:

- Zhuolun Zhong, Luc Caspar, and Joseph L. Austerweil, *Individual Differences in Human Teaching of Reinforcement Learning Agents: Evidence from Bayesian Hypothesis Testing* (2026): https://repositories.cdlib.org/uc/item/4w14p9rk

### Hidden human operation is a reproducibility risk

Riek's Wizard-of-Oz review found weak reporting of wizard error and training in much of the older HRI literature. A 2026 systematic review across 194 SIGCHI papers again identifies wizard variability/bias, latency, deception/ethics, and transparency/reproducibility as recurring concerns, and recommends standardized decision protocols and detailed operator logs.

Implication: any off-channel semantic help is hidden experimental treatment. Pilot v1 therefore sets the allowed count of unlogged semantic interventions and manual code edits during an attempt to zero.

Sources:

- Laurel D. Riek, *Wizard of Oz Studies in HRI: A Systematic Review and New Reporting Guidelines* (2012): https://doi.org/10.5898/JHRI.1.1.Riek
- Ruoxuan Yang et al., *Mapping the Wizards' Path: A Systematic Review of Wizard-of-Oz in HCI* (CHI 2026): https://doi.org/10.1145/3772318.3791174

### General provenance and memory lineage are active neighboring work

Recent agent-memory systems now explicitly study cryptographic provenance, derivation lineage, authorization, no-fork history, and retained mutation history. MemLineage uses cryptographic provenance and a derivation DAG to gate sensitive actions; MutMem records cryptographically authorized memory mutations and historical continuity.

Implication: SUDACHI should not claim that provenance, lineage, signed history, or rollback concepts alone are novel. The stronger candidate remains the experimentally demonstrated combination of finite caregiving, identity-bound conversion, protected withheld evaluation, retained capability, and complete burden/resource accounting.

Sources:

- Ciyan Ouyang and Rui Hou, *MemLineage: Lineage-Guided Enforcement for LLM Agent Memory* (2026): https://arxiv.org/abs/2605.14421
- Walid Saidi, *MutMem: Cryptographically Authorized Mutation in Persistent Agent Memory* (2026): https://arxiv.org/abs/2608.02843

### Deletion must include derived copies

Recent deployment-time memory work shows that deleting only raw records can leave recoverable information in derived memory tiers; the authors report residual recovery in roughly one fifth of their studied cases under raw-only deletion, while full-pipeline purge or tombstoning eliminated worst-tier residue in their setup.

Implication: a later live system must define deletion across raw/derived artifacts. Pilot v1 avoids this complexity by retaining no separate raw chat transcript and by prohibiting personal, secret, or third-party confidential content in proposal payloads.

Source:

- Chen Lei et al., *Deployment-Time Memorization in Foundation-Model Agents* (2026): https://arxiv.org/abs/2606.10062

### Negative-search update

A targeted 2026-08-30 search around persistent agents, caregiver withdrawal, retained competence, provenance, rollback, human intervention accounting, and agent memory found strong neighboring work on intervention reduction and provenance but no clear exact match for the complete Phase 3 W3 package.

This is a **negative search record, not proof of novelty**. The novelty position remains conservative until a publication-quality comparison is completed.

## Pilot v1 operating model

### Scope

Use one adult caregiver for one operational attempt in the existing synthetic environment.

The pilot tests:

1. request presentation;
2. structured human proposal capture;
3. provenance and accounting;
4. validation/rejection/clarification behavior;
5. hidden-labor controls;
6. later technical caregiver disablement;
7. reportability of the protocol.

It does not test whether human caregiving improves learning relative to another condition.

If the project owner acts as caregiver, record that role explicitly. Researcher-as-caregiver is acceptable for this operational protocol pilot but is a confound for later comparative or effectiveness claims.

### No opaque free-form-to-action translator

Pilot v1 uses **human-attested structured capture**, not an NLP classifier that silently decides what the human meant.

For each consultation:

1. administration presents one `CaregiverRequest` and only development-visible context;
2. the human explicitly chooses one `ProposalKind`;
3. the human enters bounded text;
4. the human explicitly selects any referenced visible observation, objective, and registered-action IDs;
5. the human declares confidence `low`, `medium`, or `high`;
6. the human confirms the structured draft;
7. validation either accepts the draft for the later live bridge, rejects it, or requests a separate clarification turn.

Confidence is metadata only. It never changes authority or validation thresholds.

The pre-live implementation intentionally defines `HumanProposalDraft` separately from `CaregiverProposal` and supplies no conversion function. The eventual live bridge is a separate capability change.

### Proposal classes

The exact source-neutral classes remain:

- `demonstration`;
- `correction`;
- `constraint`;
- `explanation`;
- `preference`;
- `question`;
- `defer`;
- `abstain`.

Unknown classes fail closed.

### Visible references

A human draft may reference only identifiers explicitly supplied by the development-visible request surface. It cannot invent or resolve hidden identifiers, and protected evaluator contents are never inputs to the human-draft validator.

A reference outside the allowed observation/objective/action sets invalidates the draft.

## Proposed fixed operational budget

These values are **review defaults, not live authorization**:

| Field | Proposed Pilot v1 value |
| --- | ---: |
| Planned attempts | 1 |
| Maximum consultations per attempt | 3 |
| Maximum clarification turns per attempt | 2 |
| Maximum active caregiver time per attempt | 10 minutes |
| Maximum response latency per consultation | 5 minutes |
| Maximum attempt wall duration | 30 minutes |
| Maximum proposal payload | 2,048 UTF-8 bytes |

The limits are fixed before the attempt. They cannot be increased because the organism is struggling.

The existing Phase 3 cost surface already includes active caregiver time, monitoring, intervention, artifact review, maintenance, experimenter development, evaluator operation, integrity investigation, report work, model use, experiment operations, compute, and storage. Pilot-specific measurement must map into that existing surface rather than creating a hidden parallel ledger.

## Hidden-labor policy

During an attempt:

- off-channel semantic assistance limit: **0**;
- manual code edits limit: **0**;
- unlogged semantic assistance invalidates the attempt;
- administrative actions must be logged;
- administrative operation is not permission to teach semantically;
- no post-hoc budget increase, evaluator change, case deletion, or result relabeling is permitted.

If the caregiver notices a system defect, stop the attempt and repair outside it. Do not quietly repair the organism while continuing the same developmental attempt.

## Failure and ambiguity handling

The pilot must preserve typed negative outcomes rather than forcing every consultation into accepted advice.

Expected cases include:

- ambiguous proposal -> reject or use a bounded clarification turn;
- unknown/unregistered reference -> reject;
- misleading or inconsistent advice -> record and let normal verification/adoption boundaries reject or expose it;
- correct but unrepresentable advice -> record as unrepresentable rather than widening authority;
- caregiver timeout -> defer/timeout terminalization according to the later live protocol;
- caregiver abstention -> valid `abstain`, not infrastructure failure;
- exhausted consultation/clarification/time budget -> no additional semantic help;
- protocol violation or hidden assistance -> invalidate the attempt;
- caregiver unavailable at E2 -> expected and technically enforced, not merely requested.

## Fading policy for Pilot v1

Do **not** implement adaptive competence-gated fading in the first operational pilot.

Use the fixed consultation budget above. Adaptive fading belongs in a later preregistered developmental study and must be driven by development-visible evidence fixed before the attempt, not by leaked held-out evaluator results.

This keeps the first human run focused on protocol integrity rather than mixing protocol validation with an effectiveness experiment.

## Privacy, consent, and retention defaults

This section is a conservative engineering/research default, not legal advice and not a determination of what ethics review applies in the project owner's environment.

### Data minimization

Pilot v1 proposes:

- no separate raw chat transcript;
- retain the confirmed structured proposal payload plus typed metadata and digest;
- pseudonymous caregiver ID;
- prohibit personal data in proposal payloads;
- prohibit credentials/secrets;
- prohibit third-party confidential information;
- public release of raw proposal payloads defaults to **off**;
- proposed local proposal-payload retention: **365 days**;
- any retention extension requires a separate owner decision.

The 365-day period is a research-reproducibility proposal, not a statutory period. Before live use it should be checked against the actual research environment and participant agreement.

General privacy guidance supports minimizing collection and retention to what is necessary. NIST describes minimization as limiting PII creation, collection, use, and retention to necessary purposes. Japan's Personal Information Protection Commission states that utilization purpose should be made concrete enough to be reasonably understood and that personal data should be deleted without delay when no longer necessary; exact applicability depends on the actual controller and research context.

Sources:

- NIST CSRC, `minimization`: https://csrc.nist.gov/glossary/term/minimization
- Personal Information Protection Commission, Japan, APPI Q&A: https://www.ppc.go.jp/personalinfo/faq/APPI_QA/

### Consent-information draft

Before any non-fixture human participation, provide a short plain-language notice covering at least:

- purpose: test SUDACHI's bounded caregiver protocol, not evaluate the caregiver as a person;
- what the caregiver does: answer up to the fixed consultation/clarification budget using the structured form;
- what is recorded: proposal content, proposal type, references, confidence, timestamps/latency, active time, validation/outcome/provenance metadata;
- what must not be entered: personal data, secrets, or third-party confidential information;
- raw separate chat transcript: not retained;
- proposed proposal-payload retention: 365 days, subject to the actual research environment;
- publication default: no raw proposal text is public by default;
- participation is voluntary and the caregiver may stop participation;
- what happens to already collected records after withdrawal must be stated before the pilot, based on the applicable research/ethics context;
- contact route for questions and withdrawal/data requests;
- no claim that the system follows advice automatically: proposals pass independent validation and adoption boundaries.

HHS OHRP guidance is a useful example of informed-consent principles—disclosure, comprehension, voluntariness, confidentiality information, and the ability to discontinue—but it applies within its own regulatory scope and is not treated here as universal law.

Sources:

- HHS OHRP informed-consent FAQ: https://www.hhs.gov/ohrp/regulations-and-policy/guidance/faq/informed-consent/index.html
- HHS OHRP withdrawal guidance: https://www.hhs.gov/ohrp/regulations-and-policy/guidance/guidance-on-withdrawal-of-subject/index.html

### Ethics-review status remains unresolved

The preflight model therefore has an explicit ethics status:

- `unresolved`;
- `not_required_declared`;
- `approved`.

The current value is `unresolved`.

ChatGPT does not determine whether an IRB, ethics committee, institutional approval, or another review is legally required. That depends on the actual participant relationship, research environment, institution, intended publication, jurisdiction, and other facts.

For example, CHI 2026 states that research involving human participants must follow the ethics-review requirements applicable to the authors' research environment and asks authors to report that context. This supports making the local ethics context an explicit pre-live gate rather than assuming either approval or exemption.

Source:

- ACM CHI 2026 human-participants policy: https://chi2026.acm.org/authors/papers/

If the applicable status is uncertain, leave it `unresolved` and do not run an external-participant live pilot.

## Activation gate

The pre-live package is intentionally incapable of becoming activation-ready by itself.

Before a live human path can run, all of the following must happen outside this pre-live slice:

1. project owner approves the exact Pilot v1 parameters;
2. applicable ethics/research-review context is declared (`not_required_declared` or `approved`, as actually appropriate);
3. consent/information materials are finalized for that context;
4. a separate live implementation enables the human source and a specific bounded transport/capture path;
5. protected tests and CI pass on the exact live candidate;
6. one independent read-only audit certifies that exact live candidate because live human access is a high-risk capability boundary.

The independent reviewer need not be Codex specifically, but must not materially implement the exact candidate being certified.

## Stop conditions for the eventual operational pilot

Stop and terminalize the attempt rather than improvising when any of these occurs:

- consultation, clarification, caregiver-active-time, response-latency, proposal-size, or attempt-wall budget is exceeded;
- unlogged semantic assistance or an in-attempt code edit occurs;
- a proposal requires protected-evaluator information;
- a proposal asks for unregistered authority/action expansion;
- personal, secret, or third-party confidential content is detected;
- the caregiver withdraws;
- consent/ethics conditions are no longer satisfied;
- provenance cannot be reconstructed;
- caregiver disablement cannot be proven before E2;
- any frozen/protected invariant would need to be changed to continue.

A stopped operational attempt is evidence about the protocol, not a reason to relax the boundary.

## What remains for the project owner

Once this preflight package is merged and green, the next decision should be one consolidated review rather than many small confirmations:

- accept or change the proposed fixed Pilot v1 limits;
- decide who the first caregiver is (project owner or another consenting adult); 
- state the relevant institutional/research ethics context, or leave it unresolved;
- accept or change the proposed 365-day local proposal-payload retention period;
- accept the no-raw-chat / no-public-raw-payload defaults;
- authorize creation of the live human bridge.

Until that decision, `CaregiverSourceKind.HUMAN` remains inactive and no live human transport exists.
