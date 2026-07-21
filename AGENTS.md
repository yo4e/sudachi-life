# AGENTS.md

This file is the continuity contract for AI collaborators working on SUDACHI.

## Cold-start rule

Assume you remember nothing about SUDACHI.

Do not rely on conversation memory, prior model context, an issue title, or a single code fragment. Reconstruct the project from the repository before proposing or changing anything.

## Before doing any work

Read these files in order:

1. `README.md`
2. `docs/ORIGIN.md`
3. `docs/MINIMAL_ORGANISM_CONTRACT.md`
4. `docs/ROADMAP.md`
5. `docs/ARCHITECTURE.md`
6. `docs/RESEARCH_QUESTIONS.md`
7. `docs/PARENT_MODEL_PROVIDER_REVIEW.md`
8. `docs/HANDOFF.md`

Then inspect the current open issues and confirm which issue is active.

Current issue roles at the end of the seed-documentation session:

- **#1** — active Phase 0 architecture decisions and ADR work
- **#2** — completed Copilot architecture review record; closed
- **#3** — deferred literature, novelty, and parent-provider compliance research; do not begin unless explicitly requested
- **#4** — accidental placeholder; closed and irrelevant

If repository state and this list disagree, trust current GitHub state and update `docs/HANDOFF.md`.

Do not infer the project only from the latest issue or code fragment. SUDACHI is a developmental artificial-life experiment, not a generic autonomous-agent framework.

## Immediate restart point

Unless the owner gives a newer instruction, resume at Issue #1:

1. create `docs/decisions/`
2. resolve ADRs 0001 through 0006
3. review the Minimal Organism Contract for contradictions
4. update `docs/HANDOFF.md`
5. only then create the Python package skeleton

Do not begin with a live language model. Phase 1 must remain deterministic, local, network-free, and parent-free.

## Project intent

SUDACHI begins with access to a capable parent language model and should gradually convert successful assistance into local memory, skills, tests, and routines. The central research question is whether capability can be retained while dependence on the parent model decreases.

The intended direction is:

`parent reasoning -> verified experience -> reusable skill -> cheap local behavior`

Growth is not the accumulation of text, files, prompts, or model calls.

## Language policy

- Write repository content in English, including code, identifiers, documentation, interfaces, tests, decision records, journals, and handoff notes.
- Preserve only the two Japanese name-etymology lines explicitly marked in `README.md`.
- Do not add other Japanese text unless the repository owner changes this policy.

## Non-negotiable design rules

1. **Bound all autonomous activity.** Every run must have explicit limits on steps, time, storage, and external effects.
2. **Keep parent usage measurable.** Parent-model calls must be logged and budgeted. Never hide them inside helper functions.
3. **Separate proposals from adoption.** Self-generated changes must be tested before becoming part of the organism.
4. **Protect evaluation.** The organism must not alter fixed tests, safety boundaries, or success metrics merely to improve its score.
5. **Prefer local deterministic skills.** Once a recurring action is understood, replace repeated language-model reasoning with tested code or a compact rule when practical.
6. **Preserve rollback.** Every developmental step must be reversible through Git or an equivalent state checkpoint.
7. **No unrestricted network or filesystem access.** Use allowlists and a sandbox. Default to no external writes.
8. **Do not equate autonomy with continuous execution.** Event-driven or periodic waking is preferred to an unbounded always-on loop.
9. **Do not anthropomorphize away the mechanics.** Life-like language is welcome, but state, budgets, triggers, and evaluation must remain explicit.
10. **Update the handoff.** After a substantial change, update `docs/HANDOFF.md` with the current state, decisions, issue roles, and next concrete action.
11. **Verify providers before connection.** Do not assume ChatGPT, the OpenAI API, or another commercial model may be used as a live parent. Complete the provider review and record a dated decision first.
12. **Do not claim novelty before research.** Candidate novelty statements remain hypotheses until the deferred prior-work review is completed.

## Definition of a valid developmental improvement

A change counts as growth only when it does at least one of the following without unacceptable regression:

- reduces parent-model calls for an existing capability
- increases successful autonomous duration
- turns a repeated reasoning pattern into a reusable tested skill
- improves transfer using existing skills
- improves recovery from failure
- reduces storage or inference cost while preserving behavior

A change that merely adds complexity is not growth.

## Working method

- Make small, testable changes.
- Use branches and pull requests once implementation begins.
- Record the hypothesis behind an experiment before running it.
- Store raw events separately from consolidated knowledge.
- Keep organism state separate from source code.
- Prefer reproducible experiments with fixed seeds where possible.
- Do not silently resolve an open architectural choice in implementation code; write or update an ADR first.
- Before ending a work session, leave the repository restartable without conversation context.

## Initial boundary

During the seed phase, do not connect a live language model until a deterministic lifecycle cycle, state store, event format, budget mechanism, evaluator, sandbox, checkpoint strategy, and provider review exist. A mocked parent is sufficient for testing later consultation plumbing.

## Commit guidance

Use clear conventional prefixes where practical:

- `docs:` documentation and decisions
- `feat:` new organism capability
- `test:` evaluation or regression tests
- `refactor:` structural change without intended behavior change
- `experiment:` research setup or results
- `fix:` bug or broken invariant

The repository is part of the organism’s developmental record. Commit messages should explain why a change exists, not only what file changed.