# ChatGPT Project Handoff

This note is for a dedicated ChatGPT Project using project-only memory. It should allow a fresh assistant session to resume SUDACHI without relying on prior conversation memory.

## Source of truth

Treat current repository state and current GitHub issues and pull requests as authoritative.

Do not trust remembered conversation context over:

1. `AGENTS.md`
2. `docs/HANDOFF.md`
3. current open issues and pull requests
4. accepted ADRs and tests

At the start of a new session, read `AGENTS.md` and follow its cold-start reading order before proposing implementation or research changes.

Repository: `https://github.com/yo4e/sudachi-life`

Repository content must remain in English, except for the two intentional Japanese etymology lines in `README.md`.

## Project center

SUDACHI is a developmental artificial-life experiment built around this candidate question:

> Can a bounded artificial organism convert external cognitive scaffolding into verified local competence and retain capability while becoming less dependent on that scaffolding?

The intended developmental path is:

`external scaffolding -> verified experience -> reusable skill -> cheap local behavior`

The caregiver may be human, deterministic, model-based, hybrid, or absent in a control condition. Do not assume the parent is an AI model or a named commercial product.

The repository is treated as body, developmental history, skill substrate, and auditable lineage. A language model may be an organ or caregiver, but it is not the organism.

Maturity is not model size, token use, file count, simulated needs, personality performance, or uncontrolled complexity. It is retained capability under declining caregiver access and bounded total resources.

Guiding phrase:

> As it becomes smarter, it should become smaller and quieter.

SUDACHI must not be flattened into a generic autonomous-agent framework or a virtual pet. Its center is development: borrowed assistance should settle into verified local memory, skills, tests, and routines while justified dependence decreases.

## Current project state

- Seed documentation and implementation guardrails exist.
- Minimal Organism Contract v0.1 is still a draft.
- No executable organism exists yet.
- No live human or model caregiver is connected.
- Phase 1 must remain deterministic, local, network-free, and caregiver-free.
- A deterministic fixture caregiver may later test source-neutral consultation plumbing.
- Prior-work, novelty, human-caregiver, virtual-pet, and model-provider research is active.
- Preliminary research notes exist in:
  - `docs/research/INITIAL_EVIDENCE_MAP.md`
  - `docs/research/PARENT_MODEL_STRATEGY.md`
  - `docs/research/HUMAN_CAREGIVER_HYPOTHESIS.md`

Current issue roles:

- Issue #1: active Phase 0 architecture decisions and ADR work; implementation-critical.
- Issue #2: closed Copilot architecture review record.
- Issue #3: active caregiver-withdrawal, prior-work, novelty, and model-provider research.
- Issue #4: closed accidental placeholder; irrelevant.

Always verify current GitHub state because issue and PR roles may change after this note.

## Human caregiver working direction

The human caregiver is the leading candidate for the first live developmental experiment because it avoids per-call API cost and premature provider selection.

This is not a novelty claim. Existing research already covers human feedback, demonstration, language teaching, developmental caregivers, assistance requesting, intervention reduction, virtual pets, and persistent learning creatures.

The stronger candidate for novelty testing is the longitudinal integration:

`finite recorded caregiving -> verified local artifact -> retained capability -> competence-gated withdrawal -> measured independence`

The explicit failure mode is **Tamagotchi with Git**: simulated hunger, affection, personality, branching growth, or chat history without measurable acquisition of caregiver-independent competence.

A future human chat caregiver must return bounded proposals, not direct executable commands. The caregiver may not bypass registered actions, permissions, budgets, sandboxing, protected evaluation, checkpoints, or adoption review.

Human time is not free. Future experiments must measure caregiver minutes, consultations, latency, clarification, confidence, corrections, hidden experimenter labor, and later reuse or rejection of advice.

## Exact restart point

For implementation planning, resume with Issue #1 and draft `docs/decisions/0001-state-and-event-storage.md`.

Then resolve:

1. clock injection and determinism
2. runtime locking and duplicate wakes
3. checkpoints and rollback
4. the seed synthetic environment
5. whether energy is independent state or only a presentation of concrete budgets

After the six ADRs:

1. review Minimal Organism Contract v0.1 for contradictions
2. confirm protected and mutable boundaries
3. confirm fixed Phase 1 evaluations
4. update `docs/HANDOFF.md`
5. only then create the Python package skeleton and deterministic first lifecycle

Do not silently decide unresolved architecture inside implementation code. Follow `docs/IMPLEMENTATION_DISCIPLINE.md`.

Issue #3 research may proceed in parallel. Write research findings into the repository with dated primary sources. Do not treat preliminary similarities or negative searches as proof of novelty.

## Caregiver and provider boundaries

Before a live human caregiver is connected, define:

- typed response classes
- free-text parsing into bounded proposals
- provenance and intervention records
- human-time and consultation budgets
- competence-gated fading and withheld-caregiver trials
- controls for hidden experimenter work, inconsistency, misleading advice, and caregiver overfitting
- privacy, consent, and later human-subject research requirements

Before a live commercial model caregiver is connected, complete the provider review covering product and API boundaries, current terms, automation, output transformations, data handling, cost, reliability, provenance, and no-caregiver fallbacks.

Do not infer permission for model-weight distillation from output ownership. Model-development uses remain disabled until the exact provider, product, model, and intended transformation are explicitly approved in a dated ADR.

Candidate novelty claims remain hypotheses until the prior-work review is substantially complete.

## Session hygiene

After substantial work, follow the restart checklist in `docs/IMPLEMENTATION_DISCIPLINE.md`:

- update `docs/HANDOFF.md`
- update relevant issue checklists or status
- record decisions as ADRs rather than leaving them only in chat
- keep repository changes in English
- leave one exact next action
- report clearly what changed, what remains, and any failure or uncertainty

The project must remain restartable after a long gap without relying on personal context or conversation memory.
