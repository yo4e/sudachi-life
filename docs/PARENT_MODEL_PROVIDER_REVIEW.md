# Model-Caregiver Provider and Compliance Review

Status: **Active preliminary review — no live provider selected**

Verified: **2026-07-21**

Tracked by: GitHub Issue #3

This document records the questions that must be answered before SUDACHI connects to a live commercial model caregiver. It is not legal advice and is not a statement that any particular use is currently permitted.

Preliminary findings and dated first-party sources are recorded in [`research/PARENT_MODEL_STRATEGY.md`](research/PARENT_MODEL_STRATEGY.md).

Provider terms, product capabilities, pricing, and policies change. Every provider decision must be re-verified from current first-party documentation and recorded in a dated ADR.

## Primary question

Can SUDACHI lawfully, ethically, practically, and reproducibly use a particular model product or API as an occasional caregiver, and which transformations of its outputs are permitted?

The architecture must not assume that a model caregiver is canonical. Human, deterministic fixture, local open-weight, hosted model, hybrid, and no-caregiver conditions remain comparison options.

## Product and access boundaries

Investigate each product separately:

- consumer chat interfaces used interactively by a human researcher
- official programmatic APIs
- local open-weight inference
- enterprise or organizational offerings with different controls
- product features such as projects, connectors, tasks, tools, and agent capabilities
- account plan, organization, geography, and data-control differences

Do not treat a consumer chat product and the provider's API as interchangeable.

Do not automate a consumer interface merely because a human can use it manually.

## Transformation classes

“Use the output” is not one operation. Review each intended transformation separately:

1. **Transient consultation** — advice influences one bounded decision.
2. **Verified memory** — a derived fact or procedure is retained with provenance and review rules.
3. **Deterministic artifact** — a response contributes to a tested rule, configuration, program, or skill.
4. **Synthetic data** — outputs become examples or evaluation material.
5. **Model development** — outputs, traces, or synthetic data train, fine-tune, imitate, or distill another model.

Output ownership does not automatically authorize every transformation. Model development remains disabled until the exact provider, product, model, terms, and intended use are explicitly approved.

## Terms and acceptable-use questions

Verify from current official terms and policies:

- whether autonomous or periodically waking software may initiate calls
- whether a human must approve calls, actions, or derived artifacts
- whether delegated credentials or machine-controlled accounts are allowed
- whether the intended agentic behavior is permitted
- whether special restrictions apply to self-improving or long-running systems
- whether outputs may become code, rules, memories, tests, skills, synthetic data, or training data
- whether competing-model or competing-product restrictions apply
- whether publication of prompts, outputs, traces, or experiments requires redaction or permission
- whether attribution, disclosure, branding, or provenance requirements apply

## Data governance and privacy

Determine:

- what prompts, outputs, metadata, tool traces, and abuse-monitoring records are retained
- whether submitted data may improve provider models and which settings affect this
- whether API and consumer-product data practices differ
- which personal, private, copyrighted, confidential, or credential-bearing data must never be sent
- whether data residency or regional processing matters
- how deletion, export, retention periods, and audit logs work
- which experiment records SUDACHI must retain locally

A model-caregiver adapter must minimize transmitted context and must never send secrets merely because they exist in organism memory.

## Output, licensing, and provenance

Investigate:

- ownership and permitted use of outputs
- obligations associated with generated code or text
- treatment of third-party or copyrighted material
- whether derived deterministic artifacts retain provider provenance
- what records link a consultation to a proposed and adopted capability
- whether raw responses may be stored, published, or redistributed
- how to handle non-unique or substantially similar outputs
- whether license conditions attach to local open-weight model derivatives

## Operational feasibility

Record current information about:

- exact product, model, version, or snapshot
- supported interfaces and structured-output features
- rate limits, quotas, context limits, and concurrency limits
- pricing and hard cost controls
- latency, outages, model retirement, and reproducibility risks
- authentication and secret storage
- sandbox, timeout, and tool behavior
- monitoring, auditability, and incident response
- fallback behavior when the caregiver is unavailable or refuses a request

SUDACHI must be able to abstain, defer, or sleep safely when no caregiver is available.

Local inference is not automatically free. Hardware memory, energy, setup, maintenance, latency, and license constraints must be counted.

## Research and publication ethics

Consider:

- whether research or ethics review is required for the experiment or collected data
- how to describe a provider's role without implying endorsement
- how to report product, model, snapshot, date, parameters, prompts, and costs reproducibly
- how to distinguish SUDACHI's retained capability from capability supplied live by a caregiver
- how to disclose human intervention and approval gates
- how to publish examples without exposing private data or prohibited material

## Provider comparison

Compare at least:

- no-caregiver baseline
- deterministic fixture caregiver
- human caregiver
- local open-weight model
- hosted commercial model API
- human-AI team

Dimensions include:

- permission and license clarity
- privacy and retention
- reproducibility
- cost and required hardware
- capability and latency
- reliability and availability
- auditability and provenance
- ease of replacement
- permitted transformation classes

## Required outputs before live model integration

- dated summary of applicable official terms and policies
- exact product, access method, and model identifier
- approved caregiver-adapter operating model
- allowed and prohibited transformation classes
- data-flow and retention description
- credential and secret-handling plan
- output-provenance policy
- hard cost, call, token, and rate-limit budgets
- prohibited inputs and actions
- provider-independent fallback and no-caregiver baseline
- ADR selecting the first live model caregiver and explaining why

## Timing

Complete the relevant review before:

- connecting a live commercial model caregiver
- automating model consultations
- retaining or publishing live model outputs
- creating deterministic artifacts from provider output when terms are unclear
- attempting distillation, fine-tuning, imitation, or synthetic-data training
- making public claims that SUDACHI is permitted to use a named provider

This review does not block Phase 0 ADRs, the deterministic caregiver-free Phase 1 organism, fixture-caregiver plumbing, source-neutral interfaces, or local tests.
