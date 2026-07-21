# AGENTS.md

This file is the continuity contract for AI collaborators working on SUDACHI.

## Cold-start rule

Assume you remember nothing about SUDACHI.

Do not rely on conversation memory, prior model context, an issue title, or a single code fragment. Reconstruct the project from the repository before proposing or changing anything.

## Before doing any work

Read these files in order:

1. `README.md`
2. `docs/CHATGPT_PROJECT_HANDOFF.md`
3. `docs/ORIGIN.md`
4. `docs/MINIMAL_ORGANISM_CONTRACT.md`
5. `docs/ROADMAP.md`
6. `docs/ARCHITECTURE.md`
7. `docs/IMPLEMENTATION_DISCIPLINE.md`
8. `docs/RESEARCH_QUESTIONS.md`
9. `docs/PARENT_MODEL_PROVIDER_REVIEW.md`
10. `docs/research/INITIAL_EVIDENCE_MAP.md`
11. `docs/research/PARENT_MODEL_STRATEGY.md`
12. `docs/research/HUMAN_CAREGIVER_HYPOTHESIS.md`
13. `docs/HANDOFF.md`

Then inspect current open issues and pull requests and confirm which work streams are active.

Current issue roles after the owner authorized research on July 21, 2026:

- **#1** — active Phase 0 architecture decisions and ADR work; implementation-critical
- **#2** — completed Copilot architecture review record; closed
- **#3** — active caregiver-withdrawal, prior-work, novelty, and model-provider research
- **#4** — accidental placeholder; closed and irrelevant

If repository state and this list disagree, trust current GitHub state and update `docs/HANDOFF.md`.

Do not infer the project only from the latest issue or code fragment. SUDACHI is a developmental artificial-life experiment, not a generic autonomous-agent framework or a virtual-pet presentation layer.

## Immediate restart point

For implementation planning, resume at Issue #1:

1. resolve ADRs 0001 through 0006 in `docs/decisions/`
2. review the Minimal Organism Contract for contradictions
3. confirm protected and mutable boundaries
4. confirm fixed Phase 1 evaluations
5. update `docs/HANDOFF.md`
6. only then create the Python package skeleton

Issue #3 research may proceed in parallel. Research findings must be written to the repository with dated primary sources. Research does not authorize connecting a live human or model caregiver.

Do not begin implementation with a live caregiver. Phase 1 must remain deterministic, local, network-free, and caregiver-free.

## Project intent

SUDACHI may eventually receive assistance from an external caregiver or cognitive-scaffolding source. The caregiver may be human, deterministic, model-based, hybrid, or absent in a control condition.

Successful assistance should be converted into verified experience, reusable skills, tests, deterministic routines, or other inspectable local artifacts. The central research question is whether capability can be retained while justified dependence on external scaffolding decreases.

The caregiver is a role behind a source-neutral boundary, not a commitment to ChatGPT, another named product, or even an AI model.

The intended direction is:

`external scaffolding -> verified experience -> reusable skill -> cheap local behavior`

Growth is not the accumulation of text, files, prompts, simulated needs, personality changes, or model calls.

## Language policy

- Write repository content in English, including code, identifiers, documentation, interfaces, tests, decision records, journals, and handoff notes.
- Preserve only the two Japanese name-etymology lines explicitly marked in `README.md`.
- Do not add other Japanese text unless the repository owner changes this policy.

## Non-negotiable design rules

1. **Bound all autonomous activity.** Every run must have explicit limits on steps, time, storage, and external effects.
2. **Keep caregiver usage measurable.** Human minutes, consultations, model calls, clarification turns, latency, and hidden intervention must not disappear inside helper functions or experiment administration.
3. **Separate proposals from adoption.** Caregiver responses and self-generated changes are proposals. They must be validated and tested before becoming part of the organism.
4. **Protect evaluation.** The organism and caregiver must not alter fixed tests, safety boundaries, or success metrics merely to improve the score.
5. **Prefer local deterministic skills.** Once a recurring action is understood, replace repeated external reasoning with tested code, a compact rule, or another inspectable local capability when practical.
6. **Preserve rollback.** Every developmental step must be reversible through Git or an equivalent state checkpoint.
7. **No unrestricted network or filesystem access.** Use allowlists and a sandbox. Default to no external writes.
8. **Do not equate autonomy with continuous execution.** Event-driven or periodic waking is preferred to an unbounded always-on loop.
9. **Do not anthropomorphize away the mechanics.** Life-like language is welcome, but state, budgets, triggers, learning evidence, and evaluation must remain explicit.
10. **Update the handoff.** After a substantial change, update `docs/HANDOFF.md` with the current state, decisions, issue roles, and next concrete action.
11. **Verify model providers before connection.** Do not assume ChatGPT, an API, or another commercial model may be used as a live caregiver. Complete the provider review and record a dated decision first.
12. **Review human-study boundaries before recruitment.** A local owner-researcher experiment is not automatically equivalent to a public participant study. Review consent, privacy, and institutional requirements before recruiting or analyzing additional people.
13. **Do not claim novelty before research.** Candidate novelty statements remain hypotheses until the active prior-work review is substantially complete.
14. **Separate transformation classes.** Transient advice, retained memory, deterministic artifacts, synthetic data, and model-weight development require separate permissions and provenance.
15. **Do not infer distillation permission from output ownership.** Weight-level learning remains disabled until the exact provider, product, model, and intended transformation are explicitly approved.
16. **Do not build Tamagotchi with Git.** Simulated needs, affection, branching growth, or chat history do not count as development without retained caregiver-independent competence on protected evaluations.

## Definition of a valid developmental improvement

A change counts as growth only when it does at least one of the following without unacceptable regression:

- reduces caregiver consultations for an existing capability
- reduces caregiver time required per retained capability
- increases successful autonomous duration
- turns a repeated reasoning pattern into a reusable tested skill
- improves transfer using existing skills
- improves recovery from failure or misleading advice
- reduces storage or inference cost while preserving behavior
- improves correct abstention under uncertainty

A change that merely adds complexity or emotional presentation is not growth.

Every claimed caregiver-derived gain should identify:

1. the capability that previously required help
2. the recorded scaffolding supplied
3. the verified local artifact or policy change produced
4. the fixed evaluation retained after help is reduced
5. the reduction in caregiver burden
6. any increase in storage, computation, retries, or complexity

## Working method

- Make small, testable changes.
- Use branches and pull requests for implementation and for substantial research or decision changes.
- Record the hypothesis behind an experiment before running it.
- Store raw events separately from consolidated knowledge.
- Keep organism state separate from source code.
- Prefer reproducible experiments with fixed seeds where possible.
- Do not silently resolve an open architectural choice in implementation code; write or update an ADR first.
- Prefer primary papers, official repositories, and current first-party provider or product documentation for research.
- Record verification dates for provider terms and time-sensitive claims.
- Distinguish caregiving from experiment administration and record both.
- Before ending substantial work, follow the restart checklist in `docs/IMPLEMENTATION_DISCIPLINE.md` and leave the repository restartable without conversation context.

## Initial boundary

During the seed phase, do not connect a live human or model caregiver until a deterministic lifecycle, state store, event format, budget mechanism, evaluator, sandbox, checkpoint strategy, and consultation-provenance design exist.

A deterministic fixture caregiver is sufficient for testing later consultation plumbing. Free-form caregiver text must never bypass registered actions, permissions, budgets, or protected evaluation.

## Commit guidance

Use clear conventional prefixes where practical:

- `docs:` documentation and decisions
- `feat:` new organism capability
- `test:` evaluation or regression tests
- `refactor:` structural change without intended behavior change
- `experiment:` research setup or results
- `fix:` bug or broken invariant

The repository is part of the organism's developmental record. Commit messages should explain why a change exists, not only what file changed.
