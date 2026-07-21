# Provider-Neutral Parent Strategy

Status: **Preliminary strategy — no provider selected**

Verified: **2026-07-21**

Tracked by: GitHub Issue #3

This document is a research and architecture note, not legal advice. Provider terms change. Every provider decision must be re-verified from current first-party terms on the decision date.

## Decision for the current phase

SUDACHI should not define its parent as ChatGPT, Claude, Gemini, or any other named product.

The parent should be defined as a role:

> An external, comparatively expensive source of general reasoning consulted only when verified local capability is insufficient.

Phase 1 remains parent-free. A deterministic mocked parent is sufficient for testing the future interface.

No live provider should be connected until a dated ADR records:

- the exact product and access method
- the governing terms and policy versions
- permitted and prohibited transformations of output
- data retention and training behavior
- credentials, rate limits, cost controls, and failure behavior
- provenance requirements
- a provider-independent fallback
- a no-parent baseline

## Why the distinction matters

"Use the output" is not one operation. SUDACHI may transform parent assistance in several materially different ways:

1. use advice transiently for one action
2. store a verified factual or procedural memory
3. create a deterministic rule, test, or executable skill
4. generate synthetic examples
5. train, fine-tune, or distill another model

Provider terms may permit some of these while restricting others. Output ownership alone does not establish permission for every downstream use.

## Transformation classes

The future parent adapter should classify every proposed downstream use.

### Class A — Transient consultation

The response informs one bounded decision and is not retained beyond the minimum audit record.

Default: potentially eligible after provider review.

### Class B — Verified memory

A limited derived fact or procedure is retained with provenance, verification evidence, and expiry or review rules.

Default: disabled until the provider decision explicitly permits the intended retention and transformation.

### Class C — Deterministic artifact

The response contributes to a rule, test, configuration, or executable skill that is independently reviewed and validated.

Default: disabled until the provider decision addresses generated-code terms, third-party material, provenance, and whether the resulting system could be considered a competing product.

### Class D — Model development

Outputs, hidden representations, synthetic examples, or traces are used to train, fine-tune, imitate, or distill another AI model.

Default: prohibited unless a provider- and model-specific review explicitly authorizes it.

Class D must never be inferred from general output ownership language.

## Preliminary provider findings

### ChatGPT for individuals

The current individual Terms of Use are separate from OpenAI's business and API agreement. They prohibit automatic or programmatic extraction of data or output and prohibit using output to develop models that compete with OpenAI. Individual-service content may be used to improve models unless the user opts out.

Preliminary implication:

- ChatGPT's consumer interface is not an appropriate unattended parent mechanism.
- Human research conversations may help design SUDACHI, but they should not be treated as an approved automated provider channel.
- Model distillation from ChatGPT output is not an available default assumption.

Sources:

- OpenAI Terms of Use, effective 2026-01-01: https://openai.com/policies/terms-of-use/
- OpenAI data-use explanation, updated 2026-03-13: https://openai.com/policies/how-your-data-is-used-to-improve-model-performance/

### OpenAI API

The OpenAI Services Agreement applies to API and developer use. It states that the customer owns output as between the parties and that customer content is not used to improve the services unless the customer explicitly agrees. It also restricts using output to develop AI models that compete with OpenAI except for defined permitted exceptions.

OpenAI's API documentation states that API data is not used to train OpenAI models by default. Abuse-monitoring logs may contain prompts and responses and are retained for up to 30 days by default; approved customers may receive modified or zero-data-retention controls, subject to feature-specific limitations.

Preliminary implication:

- The API is the technically appropriate OpenAI channel for programmatic consultation.
- It may be usable for bounded advice or code proposals after a detailed legal review.
- It must not be selected for student-model distillation merely because output is assigned to the customer.
- Exact endpoint retention must be part of the experiment manifest.

Sources:

- OpenAI Services Agreement, effective 2026-01-01: https://openai.com/policies/services-agreement/
- OpenAI Service Terms, updated 2026-06-12: https://openai.com/policies/service-terms/
- OpenAI API data controls: https://developers.openai.com/api/docs/guides/your-data

### Claude consumer products

Anthropic's consumer terms govern Claude.ai and individual plans. They prohibit using the services to develop products or services that compete with Anthropic, including training AI or machine-learning models.

Preliminary implication:

- Claude consumer products should not be treated as an automated SUDACHI parent.
- Consumer conversations may inform human research, but they are not a substitute for an approved API operating model.

Source:

- Anthropic Consumer Terms, effective 2025-10-08: https://www.anthropic.com/legal/consumer-terms

### Anthropic API

Anthropic's Commercial Terms state that customers own outputs as between the parties and that Anthropic may not train models on customer content from the services. The same terms prohibit accessing the services to build a competing product or service, including training competing AI models.

Anthropic states that API inputs and outputs are normally deleted from backend systems within 30 days, with exceptions for agreed retention, policy enforcement, or law. Approved enterprise API customers may have zero-data-retention arrangements with feature-specific exclusions.

Preliminary implication:

- The Anthropic API is technically suitable for bounded programmatic consultation.
- The competing-product restriction is broader than a narrow ban on weight distillation and requires careful interpretation before using Claude output to build persistent SUDACHI capabilities.
- No Class C or D transformation should be enabled without an explicit dated decision.

Sources:

- Anthropic Commercial Terms, effective 2025-06-17: https://www.anthropic.com/legal/commercial-terms
- Anthropic commercial retention summary: https://privacy.anthropic.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data
- Anthropic zero-data-retention summary: https://privacy.anthropic.com/en/articles/8956058-i-have-a-zero-data-retention-agreement-with-anthropic-what-products-does-it-apply-to

### Gemini API and Google AI Studio

The current Gemini API Additional Terms prohibit using the services to develop models that compete with Gemini API or Google AI Studio.

For unpaid services, Google states that submitted content and generated responses may be used to improve Google products and machine-learning technologies, and human reviewers may process inputs and outputs. For paid services attached to an active billing account, Google states that prompts and responses are not used to improve its products and are processed under the applicable data-processing terms. Google also documents a path toward zero data retention with feature-specific conditions.

Preliminary implication:

- Unpaid Gemini services are unsuitable for confidential organism state or unpublished research material.
- Paid API use is operationally more appropriate but does not remove the competing-model restriction.
- Search-grounded results carry additional storage and downstream-use restrictions and should not be used as skill-training material by default.

Sources:

- Gemini API Additional Terms, effective 2026-03-23: https://ai.google.dev/gemini-api/terms
- Gemini API zero-data-retention documentation, updated 2026-05-28: https://ai.google.dev/gemini-api/docs/zdr

### Local open-weight models

A local open-weight model changes the dependency boundary. It can remove provider availability, prompt-retention, and per-call billing from an experiment, while introducing hardware, energy, maintenance, and model-license costs.

Licenses remain model-specific:

- Qwen3.6's official repository states that its open-weight models are licensed under Apache 2.0.
- Gemma's terms explicitly define model derivatives, including models created through distillation or synthetic outputs, and permit use and distribution subject to the Gemma terms and prohibited-use policy.
- Llama uses a community license with attribution and model-development conditions rather than a standard open-source license.

Preliminary implication:

- A local open-weight parent is the strongest candidate for experiments that may eventually include actual weight-level learning or distillation.
- The exact model artifact and license must still be pinned; family-level labels are insufficient.
- Local inference is not automatically "cheap." Hardware memory, power, latency, and maintenance must be measured as parent cost.

Sources:

- Qwen3.6 official repository and license statement: https://github.com/QwenLM/Qwen3.6
- Gemma Terms of Use, updated 2026-04-01: https://ai.google.dev/gemma/terms
- Llama 4 Community License: https://github.com/meta-llama/llama-models/blob/main/models/llama4/LICENSE

## Recommended architecture

### 1. Parent capability, not parent identity

The organism should depend on a narrow interface such as:

```text
consult(request, budget, policy_context) -> recommendation
```

The adapter configuration should declare:

- provider and product identifier
- exact model or snapshot identifier
- access method
- verification date and terms snapshot
- maximum calls, tokens, money, and latency
- data-retention class
- permitted transformation classes
- required provenance fields
- fallback behavior

### 2. Keep consultation separate from adoption

A parent response may propose an action or artifact. It must not directly:

- execute an organism action
- mutate durable state
- write an active skill
- change tests or policy
- train a student model

Adoption requires an independent evaluator and a recorded provenance chain.

### 3. Use a parent ladder

A future experiment may compare several explicitly metered levels:

1. deterministic local rules and existing skills
2. a small local open-weight model
3. a stronger local or hosted open-weight model
4. a commercial API model
5. human escalation outside the organism

The ladder should not silently route around the parent budget. Every escalation is a distinct measured consultation.

### 4. Separate scientific controls

Every parent-assisted experiment should include:

- no-parent baseline
- deterministic mocked-parent baseline
- fixed-parent-budget condition
- declining-parent-budget condition
- a record of human intervention

This is necessary to show that reduced calls result from acquired local capability rather than task selection, hidden retries, or unrecorded human help.

## Current recommendation

Do not select ChatGPT or any other commercial service as the canonical parent.

Build the deterministic lifecycle and provider-neutral adapter first. For the first live-parent experiment, prefer a model and access method whose license clearly supports the intended transformation class. If the experiment includes weight-level distillation or synthetic-data training, a pinned local open-weight model is currently a more promising research path than assuming permission from a closed commercial API.

This recommendation is provisional. It must be revisited after:

- a fuller provider comparison
- exact model capability and hardware tests
- legal review of the intended transformation
- a dated ADR selecting the first live parent
