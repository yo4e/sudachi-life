# ChatGPT Project Handoff

This note is for a dedicated ChatGPT Project using project-only memory. It should allow a fresh assistant session to resume SUDACHI without relying on conversation memory.

## Source of truth

Treat current repository state and current GitHub issues and pull requests as authoritative.

Use this precedence for Phase 1:

1. `AGENTS.md`
2. Minimal Organism Contract v0.2
3. accepted ADRs 0001–0006
4. protected tests
5. `docs/HANDOFF.md`
6. current issues and pull requests

At the start of a new session, read `AGENTS.md` and follow its cold-start order before proposing implementation or research changes.

Repository: `https://github.com/yo4e/sudachi-life`

Repository content remains in English except for the two intentional Japanese etymology lines in `README.md`.

## Project center

SUDACHI asks:

> Can a bounded artificial organism convert external cognitive scaffolding into verified local competence and retain capability while becoming less dependent on that scaffolding?

The developmental path is:

`external scaffolding -> verified experience -> reusable skill -> cheap local behavior`

A future caregiver may be human, deterministic, model-based, hybrid, or absent in a control condition. Do not assume the parent is an AI model or named commercial product.

The repository is body design and developmental record. The canonical runtime body is one SQLite database. A language model may later be an organ or caregiver, but it is not the organism.

Maturity is retained capability under declining caregiver access and bounded total cost, not model size, token use, file count, simulated needs, personality, or uncontrolled complexity.

Guiding phrase:

> As it becomes smarter, it should become smaller and quieter.

## Current project state

- ADRs 0001–0006 are accepted on `main`.
- Minimal Organism Contract v0.2 and aligned documentation are in the reconciliation pull request.
- Contract v0.2 defines protected and mutable authority and 41 fixed Phase 1 evaluations.
- No executable organism exists yet.
- No live human or model caregiver is connected.
- Phase 1 is deterministic, local, network-free, and caregiver-free.
- Issue #3 research remains active in parallel.

Current issue roles:

- Issue #1: Phase 0 contract freeze; close after Contract v0.2 reconciliation merges.
- Issue #2: closed Copilot architecture review.
- Issue #3: active caregiver-withdrawal, prior-work, novelty, human-caregiver, and model-provider research.
- Issue #4: closed accidental placeholder.

Always verify current GitHub state.

## Accepted Phase 1 baseline

SUDACHI-0 uses:

- one canonical SQLite database per organism
- integer UTC timestamps and injected monotonic time
- fail-fast `BEGIN IMMEDIATE` wake locking
- immutable append-only event history ordered by database sequence
- `seed-garden-v1`, with one dry sprout, one fruiting plant, and one water unit
- water, harvest, or explicit abstention
- one tick, one observation, one action attempt, and one successful mutation at most per wake
- concrete budgets rather than scalar energy
- zero caregiver, network, subprocess, and external mutable-write capability
- a verified checkpoint after every committed wake
- rollback with a pre-rollback archive and new lineage generation

The canonical three-wake run waters, harvests, and then abstains after objective completion.

This proves metabolism and recovery, not learning or intelligence.

## Exact restart point

After the Contract v0.2 reconciliation PR is merged:

1. close Issue #1
2. create a Phase 1 implementation branch
3. create `pyproject.toml`, `src/sudachi_life/`, and `tests/`
4. encode protected tests before broad behavior
5. implement canonical SQLite initialization and schema validation
6. implement real and fake clocks
7. create and validate a stable genesis checkpoint
8. expose `sudachi init` and `sudachi status`

Do not start with chat, caregivers, models, memory, skills, or a general autonomous loop.

## Human caregiver working direction

The human caregiver remains the leading candidate for the first live developmental experiment because it avoids per-call API cost and premature provider selection.

This is not a novelty claim. Human teaching, language instruction, developmental caregivers, intervention reduction, and owner-shaped virtual creatures have substantial precedents.

The stronger candidate for novelty testing is:

`finite recorded caregiving -> verified local artifact -> retained capability -> competence-gated withdrawal -> measured independence`

The explicit failure mode is **Tamagotchi with Git**: simulated needs, affection, personality, branching growth, or chat history without caregiver-independent competence.

A future caregiver response is a bounded proposal and cannot bypass actions, permissions, budgets, protected evaluation, checkpointing, or adoption review.

Human time, consultations, latency, clarification, confidence, corrections, and hidden experimenter labor are real costs.

## Caregiver and provider boundaries

Before a live human caregiver is connected, define typed responses, provenance, human-time budgets, competence-gated fading, withheld-caregiver trials, controls for inconsistency and hidden labor, and privacy or consent requirements.

Before a live commercial model caregiver is connected, complete the dated provider review covering product and API boundaries, current terms, automation, output transformations, data handling, cost, reliability, provenance, and no-caregiver fallbacks.

Do not infer permission for model-weight distillation from output ownership.

Candidate novelty claims remain hypotheses until the prior-work review is substantially complete.

## Session hygiene

After substantial work:

- update `docs/HANDOFF.md`
- update relevant issues and pull requests
- record decisions or contract changes before implementing them
- keep repository changes in English
- report tests, failures, uncertainty, and unfinished work plainly
- leave one exact next action

The project must remain restartable without personal context or conversation memory.
