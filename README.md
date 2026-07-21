# SUDACHI

**A lightweight artificial life that learns to leave its parent model.**

SUDACHI is an experimental artificial-life project built around a simple reversal of the usual AI scaling story:

> As it grows, it should need *less* help from a large language model.

A young SUDACHI may ask a capable “parent model” how to handle unfamiliar situations. When an approach succeeds, it should convert that help into local memory, tested skills, and embodied routines. Maturity is not defined by a larger model or more tokens. It is defined by preserving useful behavior while reducing dependence on the parent.

The name carries two meanings:

- 巣立ち (sudachi): leaving the nest
- すだち (Sudachi): a small Japanese citrus fruit—green, compact, and alive

## Core hypothesis

Can an artificial organism become lighter as it becomes more capable?

More precisely:

- Can parent-model reasoning be compiled into small, reusable local skills?
- Can the organism preserve competence while parent access is gradually reduced?
- Can memory consolidation, forgetting, and skill reuse lower inference cost over time?
- Can a repository, rather than a model alone, serve as the organism’s body and developmental history?

## What SUDACHI is

SUDACHI is planned as a small local Python system composed of:

- a bounded lifecycle loop
- persistent state and memory
- a registry of tested skills
- a parent-model adapter used only when necessary
- explicit resource and consultation budgets
- evaluation and rollback mechanisms
- Git history as an auditable developmental record

The language model is an organ, not the whole organism.

## What SUDACHI is not

- A smaller imitation of ChatGPT
- An unrestricted self-modifying agent
- A process that must run continuously
- A system whose “growth” is measured by file count, token count, or uncontrolled complexity
- A project that treats autonomy as the absence of boundaries

## Design principles

1. **Small brain, structured body**  
   Intelligence should be distributed across memory, tools, routines, tests, and environment.

2. **Skills are compiled cognition**  
   Repeated successful reasoning should become cheaper, deterministic behavior where possible.

3. **Maturity means reduced dependency**  
   Parent-model calls should decline without unacceptable loss of performance or safety.

4. **Finite resources create meaningful behavior**  
   Time, storage, consultation, and action budgets must be visible and bounded.

5. **Forgetting is a feature**  
   The organism should consolidate experience rather than accumulate everything forever.

6. **Growth must be measurable**  
   Every claimed improvement should survive fixed tests and comparison with an earlier state.

7. **The measuring stick is protected**  
   Core evaluation criteria and safety boundaries must not be rewritten merely to make the organism appear successful.

## Initial maturity metrics

- **Parent calls per successful action**
- **Autonomous survival time** after parent access is removed
- **Skill reuse rate**
- **Transfer to unfamiliar tasks** using existing skills
- **Recovery rate** after failure or corruption
- **Storage and inference cost per retained capability**

## Repository map

- [`AGENTS.md`](AGENTS.md) — cold-start and continuity instructions for future AI collaborators
- [`docs/ORIGIN.md`](docs/ORIGIN.md) — origin, intent, and founding conversation
- [`docs/MINIMAL_ORGANISM_CONTRACT.md`](docs/MINIMAL_ORGANISM_CONTRACT.md) — draft contract for the smallest valid SUDACHI-0
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — proposed system architecture
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — phased development plan
- [`docs/RESEARCH_QUESTIONS.md`](docs/RESEARCH_QUESTIONS.md) — deferred prior-work and novelty research plan
- [`docs/PARENT_MODEL_PROVIDER_REVIEW.md`](docs/PARENT_MODEL_PROVIDER_REVIEW.md) — deferred provider, terms, automation, data, and compliance checklist
- [`docs/HANDOFF.md`](docs/HANDOFF.md) — authoritative current state, issue map, and exact restart point

## Language policy

The repository is written in English. The only intentional Japanese text is the two name-etymology lines near the top of this README.

## Status

**Seed phase — repository established and Minimal Organism Contract v0.1 drafted on July 21, 2026.**

No organism has been implemented yet. The next task is to resolve the contract’s open design decisions as ADRs, review the contract, and then build one deterministic lifecycle cycle before connecting any language model.

The prior-work and provider-compliance reviews are recorded as future tasks. They do not block deterministic Phase 1, but both must be completed before live parent integration or strong novelty and provider-permission claims.

For a cold start, read [`AGENTS.md`](AGENTS.md), then [`docs/HANDOFF.md`](docs/HANDOFF.md).