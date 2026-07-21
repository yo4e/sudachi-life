# Parent-Model Provider and Compliance Review

Status: **Backlog only — no provider or policy review has been performed yet.**

This document records the questions that must be answered before SUDACHI connects to a live commercial parent model. It is not a statement that any particular use is currently permitted or prohibited.

Provider terms, product capabilities, pricing, and policies change over time. The review must use current first-party documentation and record the date on which each conclusion was verified.

## Primary question

Can SUDACHI lawfully and practically use ChatGPT or an OpenAI model as a parent that supplies occasional reasoning which may later be converted into local memories, tested skills, rules, or code?

## Product boundary: ChatGPT versus API

Investigate separately:

- interactive use of the ChatGPT product by a human researcher
- programmatic use through the official OpenAI API
- whether automated access to the ChatGPT user interface is permitted
- whether an API-based implementation is required for unattended or scheduled parent consultations
- whether ChatGPT features such as Projects, custom GPTs, connectors, tasks, or agent capabilities are relevant and permitted for this experiment
- whether account type, plan, organization, or geographic region changes the available terms or controls

Do not treat “ChatGPT” and “an OpenAI API model” as interchangeable products in design documents.

## Terms and acceptable-use questions

Verify from current official terms and policies:

- whether an autonomous or periodically waking software organism may initiate model calls
- whether humans must approve each call, action, or derived skill
- whether account sharing, delegated credentials, or machine-controlled accounts are allowed
- whether SUDACHI's intended behavior falls within applicable usage policies
- whether special restrictions apply to self-modifying, self-improving, agentic, or long-running systems
- whether provider outputs may be transformed into executable code, rules, memories, or a reusable skill library
- whether outputs may be used for evaluation, fine-tuning, distillation, imitation, or training of another model
- whether any restriction applies to building systems that reduce dependence on the provider model
- whether publication of prompts, outputs, traces, or experiments requires redaction or permission
- whether attribution, disclosure, or branding requirements apply

## Data governance and privacy

Determine:

- what prompts, outputs, metadata, and tool traces are retained by the provider
- whether submitted data may be used to improve provider models, and which controls or account settings affect this
- whether API and ChatGPT data practices differ
- which personal, private, copyrighted, confidential, or credential-bearing data must never be sent
- whether data residency, regional processing, or organizational controls matter
- how deletion, export, retention periods, and audit logs work
- what must be documented in SUDACHI's own privacy and data-handling policy

The parent adapter must minimize transmitted context and must never send secrets merely because they exist in organism memory.

## Output, licensing, and provenance

Investigate:

- ownership and permitted use of model outputs
- obligations associated with generated code or text
- treatment of potentially copyrighted or third-party material in outputs
- whether derived deterministic skills retain provider provenance
- what records should link a parent response to a proposed and adopted skill
- whether raw responses may be stored, published, or redistributed
- how to handle substantially similar or non-unique outputs

## Operational feasibility

Record current information about:

- supported models and relevant API interfaces
- rate limits, quotas, context limits, and concurrency limits
- pricing and methods for enforcing a hard consultation budget
- service availability, version changes, model retirement, and reproducibility risks
- structured outputs, tool calling, sandbox boundaries, and timeout behavior
- authentication and secret storage
- monitoring, auditability, and incident response
- fallback behavior when the provider is unavailable or refuses a request

SUDACHI must remain able to sleep, abstain, or defer safely when no parent is available.

## Research and publication ethics

Consider:

- whether research review, ethics review, or additional consent is needed for particular experiments or data
- how to describe the provider's role without implying endorsement
- how to report model name, version or snapshot, date, parameters, prompts, and costs reproducibly
- how to distinguish claims about SUDACHI from capabilities supplied by the parent
- how to disclose human intervention and approval gates

## Provider comparison

The architecture should not assume OpenAI is the only possible parent. Compare at least:

- OpenAI API models
- other hosted commercial model APIs
- a local open-weight model
- a deterministic mocked parent
- no-parent baselines

Comparison dimensions should include permission, privacy, reproducibility, cost, capability, latency, reliability, auditability, and ease of replacement.

## Required outputs before live integration

- a dated summary of applicable official terms and policies
- a clear decision on ChatGPT product use versus official API use
- an approved parent-adapter operating model
- a data-flow and retention diagram
- a credential and secret-handling plan
- an output-provenance policy
- a hard cost and rate-limit budget
- a list of prohibited inputs and actions
- a provider-independent fallback plan
- an ADR selecting the first live parent provider and explaining why

## Timing

Complete this review before:

- connecting any live commercial parent model
- automating parent consultations
- storing or publishing live parent outputs
- attempting distillation, fine-tuning, or systematic imitation from provider outputs
- making public claims that SUDACHI is permitted to operate with a named provider

This review does not block the deterministic Phase 1 organism, mocked-parent plumbing, provider-neutral interfaces, or local tests.

Tracked with the broader research backlog in GitHub Issue #3.