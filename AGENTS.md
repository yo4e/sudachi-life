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
9. `docs/PHASE1_TEST_MATRIX.md`
10. implemented notes in `docs/phase1/`
11. `docs/RESEARCH_QUESTIONS.md`
12. `docs/PARENT_MODEL_PROVIDER_REVIEW.md`
13. research notes in `docs/research/`
14. `docs/HANDOFF.md`
15. current issues, pull requests, and CI state

Current GitHub state outranks this file when they disagree. Repair stale continuity documents before broad implementation.

Do not infer the project only from the latest issue or code fragment. SUDACHI is a developmental artificial-life experiment, not a generic autonomous-agent framework or virtual-pet presentation layer.

## Current work streams

- **Issue #1 — closed:** Phase 0 contract and ADR freeze.
- **Issue #3 — open:** caregiver withdrawal, prior work, novelty, human-caregiver, and provider research.
- **Issue #13 — open:** deterministic Phase 1 metabolism implementation.

No research result authorizes a live caregiver during Phase 1.

## Immediate restart point

Slices 1–15 establish:

- a canonical SQLite organism body
- injected time and protected concrete budgets
- stable genesis, water, harvest, justified-abstention, blocked-abstention, recovery, action-failure, and budget-exhaustion checkpoints
- idempotent synthetic garden ticks
- fail-fast wake ownership and deterministic observation
- fixed-policy `water_plot(bed-a)` and `harvest_plot(bed-b)` wakes
- justified `objective_already_complete` abstention with zero action and mutation cost
- classified `no_applicable_action` abstention when the objective is incomplete but no protected mutation is executable
- independent transition, abstention, rolled-back failure, and budget-exhaustion evaluation
- explicit failure-streak accounting below the maintenance threshold
- resource-aware harvest fallback when watering is impossible
- verified failure-streak reset after positive progress
- classified injected action failure after a partial savepoint write
- removal of partial environment change while preserving charged action-attempt cost
- an explicit pre-action monotonic deadline check for every wake
- classified lifecycle wall-time exhaustion before action attempt or environment mutation
- exact maintenance-threshold entry after the third consecutive classified failure
- typed `consecutive_failure_limit_reached` maintenance state after checkpoint stabilization
- later normal-wake rejection without clock reads, event writes, input consumption, or state advancement
- explicit administrative `maintenance inspect` API and CLI boundaries
- canonical maintenance reason, failure streak, latest checkpoint, and queued-input reporting
- read-only inspection with no clocks, claims, events, canonical writes, file changes, or maintenance clearing
- typed rejection when inspection is requested outside `maintenance_required`
- explicit administrative `maintenance clear` API and CLI boundaries
- bounded recovery-reason validation before clock use or canonical mutation
- fail-fast maintenance-clear ownership and exact protected-state validation
- atomic `maintenance_required -> sleeping` recovery with failure streak `3 -> 0`
- typed `maintenance_cleared` audit history with rollback if the audit write fails
- preservation of environment, checkpoint references, and queued input through maintenance clear
- later normal-wake processing of the preserved tick under the unchanged fixed policy
- bounded stable-checkpoint retention under protected limit four
- fifth-checkpoint stabilization before any pruning
- genesis preservation and oldest-eligible non-genesis pruning
- matching artifact and registry removal with typed `checkpoint_pruned` audit history
- exact retained-checkpoint and byte accounting with normal wakeability preserved
- classified retention-pruning failure after artifact staging and before registry mutation
- exact staged-artifact restoration with all five stable checkpoints retained and validated
- typed `checkpoint_retention_pruning_failed` maintenance warning without false pruning success
- later normal-wake rejection without clock reads after retention failure
- explicit administrative `checkpoint repair-pending` API and CLI boundaries
- fail-fast pending-checkpoint repair ownership without input claim or environment advancement
- exact one-candidate validation against canonical identity, lineage, lifecycle, pending boundary, versions, protected configuration, database digest, manifest digest, and committed snapshot contents
- typed zero-candidate, ambiguous-candidate, foreign-organism, invalid-artifact, repeated-repair, and busy rejection without clock reads or pending-state changes
- atomic orphan registration, latest-stable advancement, pending-state clearing, return to `sleeping`, and typed `checkpoint_registration_repaired` audit history
- preservation of committed lifecycle state, inbox history, previous checkpoint, immutable artifacts, and checkpoint-store bytes through repair
- later canonical harvest processing at boundary 24 after the repaired boundary 13 becomes stable
- the complete canonical four-wake run plus protected blocked-state, recovery, action-failure, budget-exhaustion, maintenance-threshold, maintenance-inspection, maintenance-clear, checkpoint-retention, retention-failure, and pending-checkpoint-repair fixtures

After PR #29 is merged, the exact next implementation slice is **Slice 16: deterministic non-canonical JSONL event export**.

It must export one declared stable committed boundary through an explicit administrative read-only API and narrow CLI command, order records by canonical event sequence, identify organism, lineage, schema, contract, and event boundaries, produce byte-identical output for unchanged canonical state, write through a temporary file and atomic publication, and prove that export creation, deletion, modification, or failure cannot alter canonical SQLite state.

Do not add JSONL import, lifecycle dual-writing, organism-controlled export, rollback, orphan deletion, a caregiver, chat, learning, memories, skills, or a general agent loop in Slice 16.

Phase 1 remains deterministic, local, network-free, and caregiver-free.

## Normative implementation authority

For Phase 1, use this precedence:

1. Minimal Organism Contract v0.2
2. accepted ADRs 0001–0006
3. protected tests and `docs/PHASE1_TEST_MATRIX.md`
4. `docs/HANDOFF.md`
5. explanatory architecture and roadmap documents

When sources conflict, stop and repair the documentation, test, or contract. Do not choose a private interpretation in code.

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
