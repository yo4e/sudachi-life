# AGENTS.md

This file is the continuity contract for AI collaborators working on SUDACHI.

## Before doing any work

Read these files in order:

1. `README.md`
2. `docs/ORIGIN_JA.md`
3. `docs/ROADMAP.md`
4. `docs/ARCHITECTURE.md`
5. `docs/HANDOFF_JA.md`

Do not infer the project only from the latest issue or code fragment. SUDACHI is a developmental artificial-life experiment, not a generic autonomous-agent framework.

## Project intent

SUDACHI begins with access to a capable parent language model and should gradually convert successful assistance into local memory, skills, tests, and routines. The central research question is whether capability can be retained while dependence on the parent model decreases.

The intended direction is:

`parent reasoning -> verified experience -> reusable skill -> cheap local behavior`

Growth is not the accumulation of text, files, prompts, or model calls.

## Language policy

- Write code, identifiers, public technical documentation, interfaces, and tests in English.
- Use Japanese for origin records, conceptual nuance, handoff notes, and journals when it preserves the meaning better.
- Bilingual documents are acceptable when they improve continuity.

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
10. **Update the handoff.** After a substantial change, update `docs/HANDOFF_JA.md` with the current state, decisions, and next concrete action.

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

## Initial boundary

During the seed phase, do not connect a live language model until a deterministic lifecycle cycle, state store, event format, budget mechanism, and evaluator exist. A mocked parent is sufficient for the first implementation.

## Commit guidance

Use clear conventional prefixes where practical:

- `docs:` documentation and decisions
- `feat:` new organism capability
- `test:` evaluation or regression tests
- `refactor:` structural change without intended behavior change
- `experiment:` research setup or results
- `fix:` bug or broken invariant

The repository is part of the organism’s developmental record. Commit messages should explain why a change exists, not only what file changed.