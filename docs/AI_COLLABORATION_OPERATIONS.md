# AI Collaboration Operations

Status: **Active operational guidance**

This document governs collaboration mechanics. It does not change SUDACHI's organism contract, runtime capabilities, evaluation criteria, or research scope.

## 1. Repository-first continuity

Repository state and current GitHub state are the continuity authority. Chat is a working surface, not a canonical record.

Do not create a new conversation merely because several slices or pull requests have accumulated. Continue while current state can be reconstructed reliably from the repository and active GitHub work.

Start a new conversation when context is materially confusing, stale, contradictory, or difficult to separate from current repository evidence. A new conversation is a reliability tool, not a mandatory phase boundary.

Before a rollover, only synchronize durable records that have materially changed. Do not update every continuity document as ritual if it would merely repeat already-canonical state.

## 2. Review and audit cost

Use ordinary diff review, relevant protected tests, CI, and Issue/PR tracking for normal work.

A same-conversation audit mode is allowed for concentrated read-only checking. Independent review is reserved for actual phase freeze or another explicitly high-risk gate under `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`.

Do not consume independent-review capacity on every slice, pull request, documentation update, ordinary repair, or intermediate commit.

## 3. Safety context

SUDACHI uses biological metaphors such as organism, body, lineage, growth, and caregiver. In the repository these describe a bounded software research system using Python, SQLite, synthetic environments, checkpoints, and explicit administrative operations.

When a request could be misread, state the concrete software context. Do not disguise intent or attempt to evade safety checks. Do not include secrets, credentials, private keys, authentication codes, proprietary data, or unrelated sensitive information in support requests or diagnostics.

## 4. Cost awareness

Do not introduce paid runners, larger runners, GPU runners, paid external services, model/API calls, expanded artifact retention, or another chargeable surface without explicit project-owner approval.

When a proposed change could create a charge, identify the cost surface and a no-cost alternative before enabling it.

## 5. Scope preservation

Operational caution must not silently change the research question or weaken protected evidence.

Human confirmation remains required for material changes to frozen behavior, accepted contract/ADR intent, authority/security boundaries, live external capabilities, destructive migration, protected evidence, or material autonomy/resource scope.

Routine implementation work inside already accepted scope should stay routine: make the bounded change, test it, run CI, record material state, and merge when green.
