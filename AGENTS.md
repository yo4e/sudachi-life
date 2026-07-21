# AGENTS.md

This file is the continuity contract for AI collaborators working on SUDACHI.

## Cold-start rule

Assume you remember nothing about SUDACHI.

Do not rely on conversation memory, prior model context, an issue title, or one code fragment. Reconstruct the project from repository state before proposing or changing anything.

## Before doing any work

Read these files in order:

1. `README.md`
2. `docs/CHATGPT_PROJECT_HANDOFF.md`
3. `docs/ORIGIN.md`
4. `docs/MINIMAL_ORGANISM_CONTRACT.md`
5. accepted files in `docs/decisions/`, in numeric order
6. `docs/ARCHITECTURE.md`
7. `docs/ROADMAP.md`
8. `docs/IMPLEMENTATION_DISCIPLINE.md`
9. `docs/RESEARCH_QUESTIONS.md`
10. `docs/PARENT_MODEL_PROVIDER_REVIEW.md`
11. `docs/research/INITIAL_EVIDENCE_MAP.md`
12. `docs/research/PARENT_MODEL_STRATEGY.md`
13. `docs/research/HUMAN_CAREGIVER_HYPOTHESIS.md`
14. `docs/HANDOFF.md`

Then inspect current open issues and pull requests and confirm which work streams are active.

Current issue roles after Contract v0.2 reconciliation:

- **#1** — Phase 0 seed architecture and contract freeze; close when the reconciliation PR is merged
- **#2** — completed Copilot architecture review record; closed
- **#3** — active caregiver-withdrawal, prior-work, novelty, human-caregiver, and model-provider research
- **#4** — accidental placeholder; closed and irrelevant

If repository state and this list disagree, trust current GitHub state and update `docs/HANDOFF.md`.

Do not infer the project only from the latest issue or code fragment. SUDACHI is a developmental artificial-life experiment, not a generic autonomous-agent framework or virtual-pet presentation layer.

## Immediate restart point

After the Contract v0.2 reconciliation PR is merged, begin Phase 1 implementation from the contract rather than redesigning it.

The first implementation slice is:

1. create `pyproject.toml`, `src/sudachi_life/`, and `tests/`
2. encode protected Contract v0.2 tests before broad organism behavior
3. implement canonical SQLite initialization and schema validation
4. implement injected real and fake clocks
5. create a stable genesis checkpoint
6. expose the minimal `sudachi init` and `sudachi status` commands

Do not begin with a caregiver, chat interface, model adapter, memory system, skill system, or general agent loop.

Issue #3 research may continue in parallel. Research findings must be written to the repository with dated primary sources. Research does not authorize connecting a live human or model caregiver.

Phase 1 remains deterministic, local, network-free, and caregiver-free.

## Normative implementation authority

For Phase 1, use this precedence:

1. Minimal Organism Contract v0.2
2. accepted ADRs 0001–0006
3. protected tests
4. `docs/HANDOFF.md`
5. explanatory architecture and roadmap documents

When sources conflict, stop and repair the documentation or contract. Do not choose a private interpretation in code.

Ordinary module names and private helpers do not require an ADR when they preserve every contract invariant.

## Project intent

SUDACHI may eventually receive assistance from an external caregiver or cognitive-scaffolding source. The caregiver may be human, deterministic, model-based, hybrid, or absent in a control condition.

Successful assistance should become verified experience, reusable skills, tests, deterministic routines, or other inspectable local artifacts. The central research question is whether capability can be retained while justified dependence on external scaffolding decreases.

The caregiver is a role behind a source-neutral boundary, not a commitment to ChatGPT, another named product, or even an AI model.

The intended direction is:

`external scaffolding -> verified experience -> reusable skill -> cheap local behavior`

Growth is not the accumulation of text, files, prompts, simulated needs, personality changes, or model calls.

## Language policy

- Write repository content in English, including code, identifiers, documentation, interfaces, tests, decision records, journals, and handoff notes.
- Preserve only the two Japanese name-etymology lines explicitly marked in `README.md`.
- Do not add other Japanese text unless the repository owner changes this policy.

## Non-negotiable design rules

1. **Implement the accepted contract.** Do not reopen ADRs through accidental code choices.
2. **Bound all runtime activity.** Every wake has explicit limits on semantic steps, monotonic time, records, storage, and effects.
3. **Keep caregiver usage measurable.** Future human minutes, consultations, model calls, clarification, latency, and hidden intervention must not disappear inside helpers or experiment administration.
4. **Separate proposals from adoption.** Future caregiver responses and self-generated changes are proposals; they never mutate canonical state directly.
5. **Protect evaluation.** The organism and caregiver cannot alter fixed tests, safety boundaries, or success metrics to improve a score.
6. **Use one canonical body.** SQLite is the sole live authority; JSONL and rendered views are exports.
7. **Preserve atomicity and lineage.** State, outcomes, events, checkpoints, and rollback behavior must match ADRs 0001, 0003, and 0004.
8. **Use injected time.** Runtime code does not call system clocks outside the clock adapter.
9. **Use concrete budgets.** Phase 1 has no scalar energy and no hidden retries or effects.
10. **Keep hard-zero capabilities absent.** No caregiver, network, subprocess, or authoritative external-write effect exists in Phase 1.
11. **Do not equate autonomy with continuous execution.** One bounded wake terminates.
12. **Do not anthropomorphize away mechanics.** Life-like language is welcome; state, budgets, triggers, evidence, and evaluation remain explicit.
13. **Verify model providers before connection.** Complete the provider review and dated decision before any live model caregiver.
14. **Review human-study boundaries before recruitment.** Consent, privacy, and institutional requirements must be considered before involving additional people.
15. **Do not claim novelty before research.** Candidate novelty statements remain hypotheses until the active review is substantially complete.
16. **Do not infer distillation permission from output ownership.** Model development remains disabled without exact permission.
17. **Do not build Tamagotchi with Git.** Presentation is not development without retained caregiver-independent competence.
18. **Update the handoff.** After substantial work, record the true state, issue roles, failures, and one exact next action.

## Definition of a valid developmental improvement

A later change counts as growth only when it does at least one of the following without unacceptable regression:

- reduces caregiver consultations or time for an existing capability
- increases successful autonomous duration
- turns repeated reasoning into a reusable tested skill
- improves transfer using existing skills
- improves recovery from failure or misleading advice
- reduces storage or inference cost while preserving behavior
- improves correct abstention under uncertainty

Every claimed caregiver-derived gain identifies:

1. the capability that previously required help
2. the recorded scaffolding supplied
3. the verified local artifact or policy change produced
4. the protected evaluation retained after help is reduced
5. the reduction in caregiver burden
6. added storage, computation, retries, complexity, and human labor

A change that merely adds complexity or emotional presentation is not growth.

## Working method

- Make small, testable changes.
- Use branches and pull requests for implementation and substantial research or decisions.
- Write or select protected tests before broad implementation.
- Keep organism state separate from source code.
- Store raw events separately from later consolidated knowledge.
- Use fixed seeds and fake clocks where declared by the contract.
- Use real competing SQLite connections for lock tests.
- Do not weaken a protected test because implementation is difficult.
- Record implementation discoveries that require contract changes before proceeding.
- Prefer primary papers, official repositories, and first-party provider documentation for research.
- Distinguish caregiving, administration, and organism action in records and reports.
- Follow `docs/IMPLEMENTATION_DISCIPLINE.md` at the end of substantial work.

## Phase 1 boundary

Phase 1 implements only the deterministic seed garden metabolism in Contract v0.2.

It has:

- one SQLite organism body
- injected time
- fail-fast wake locking
- concrete budgets
- one garden tick and at most one mutation per wake
- water, harvest, or abstention
- protected evaluation
- a verified checkpoint after every committed wake
- lineage-preserving rollback

It does not have:

- a caregiver of any kind in action selection
- network or subprocess access
- an organism-writable external workspace
- arbitrary code or shell execution
- learning, memories, skills, personality, mood, or scalar energy
- continuous execution

## Commit guidance

Use clear conventional prefixes where practical:

- `docs:` documentation and decisions
- `feat:` new organism capability
- `test:` evaluation or regression tests
- `refactor:` structural change without intended behavior change
- `experiment:` research setup or results
- `fix:` bug or broken invariant

The repository is part of the organism's developmental record. Commit messages should explain why a change exists, not only what file changed.
