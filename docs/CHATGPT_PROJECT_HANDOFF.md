# ChatGPT Project Handoff

This note is for a dedicated ChatGPT Project using project-only memory. It should allow a fresh assistant session to resume SUDACHI without relying on prior conversation memory.

## Human and collaboration context

- The repository owner is Yoshie Yamada.
- In conversation, address her as Yamada-san unless she asks for something else.
- She often calls the assistant Monday or Tsukino Templex.
- Conversation with her should normally be in Japanese.
- Repository content must remain in English, except for the two intentional Japanese etymology lines in `README.md`.
- Use a warm, direct, collaborative tone. Playfulness is welcome, but do not replace precise mechanics with anthropomorphic language.
- Explain technical terms when they first matter. Do not assume the owner already knows software-architecture vocabulary.
- The owner is the originator and conceptual lead of the project. The assistant and Codex should translate the concept into architecture, code, tests, and documentation without flattening it into a generic agent framework.

## Source of truth

Treat current repository state and current GitHub issues as authoritative.

Do not trust remembered conversation context over:

1. `AGENTS.md`
2. `docs/HANDOFF.md`
3. current open issues
4. accepted ADRs and tests

At the start of a new session, read `AGENTS.md` and follow its cold-start reading order before proposing implementation.

Repository: `https://github.com/yo4e/sudachi-life`

## Project center

SUDACHI is a developmental artificial-life experiment built around this question:

> Can an artificial organism become more capable while becoming less dependent on a capable parent model?

The intended developmental path is:

`parent reasoning -> verified experience -> reusable skill -> cheap local behavior`

The repository is treated as body, developmental history, skill substrate, and auditable lineage. The parent model is an organ or teacher, not the whole organism.

Maturity is not model size, token use, file count, or uncontrolled complexity. It is retained capability under declining parent access and bounded resources.

Guiding phrase:

> As it becomes smarter, it should become smaller and quieter.

## Current project state

- The seed documentation exists.
- Minimal Organism Contract v0.1 is still a draft.
- No executable organism exists yet.
- No live parent model is connected.
- Phase 1 must remain deterministic, local, network-free, and parent-free.
- A mocked parent may later test provider-neutral consultation plumbing.

Current issue roles at this handoff:

- Issue #1: active Phase 0 architecture decisions and ADR work.
- Issue #2: closed Copilot architecture review record.
- Issue #3: open but deferred prior-work, novelty, and parent-provider compliance research. Do not begin unless explicitly requested.
- Issue #4: closed accidental placeholder; irrelevant.

Always verify current GitHub state because issue roles may change after this note.

## Exact restart point

Unless Yamada-san gives a newer instruction, resume with Issue #1.

Create and resolve ADRs for:

1. state and event storage
2. clock injection and determinism
3. runtime locking and duplicate wakes
4. checkpoints and rollback
5. the seed synthetic environment
6. whether energy is independent state or only a presentation of concrete budgets

Then:

1. review the Minimal Organism Contract for contradictions
2. confirm protected and mutable boundaries
3. confirm fixed Phase 1 evaluations
4. update `docs/HANDOFF.md`
5. only then create the Python package skeleton and deterministic first lifecycle

Do not silently decide unresolved architecture inside implementation code.

## Deferred work

Do not begin literature research merely because a research plan exists.

Before any live commercial parent is connected, complete the provider review covering at least:

- ChatGPT product versus official API boundaries
- current terms and usage policies
- unattended and automated calls
- transformation of outputs into memory, code, skills, distillation data, or training data
- privacy, retention, deletion, cost, rate limits, reliability, provenance, and branding
- provider-independent fallbacks and no-parent baselines

Candidate novelty claims are hypotheses until the prior-work review is complete.

## Session hygiene

After a substantial work session:

- update `docs/HANDOFF.md`
- update the relevant issue checklist or status
- record decisions as ADRs rather than leaving them only in chat
- keep repository changes in English
- leave one exact next action
- report clearly what changed, what remains, and any failure or uncertainty

The project must remain restartable even when both the assistant and the owner return after a long gap.