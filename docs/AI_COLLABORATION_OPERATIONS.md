# AI Collaboration Operations

Status: **Active operational guidance**

This document governs how AI collaborators conduct repository work. It does not change the organism contract, runtime capabilities, evaluation criteria, or research scope.

## 1. Safety context

SUDACHI uses biological metaphors such as organism, body, metabolism, lineage, growth, and caregiver. In the current repository these terms describe a deterministic local software system built from Python, SQLite, synthetic garden state, immutable checkpoints, and explicit administrative operations.

Phase 1 contains no wet-lab biology, pathogen work, genetic engineering, medical intervention, weapons work, offensive cybersecurity, credential access, external-system exploitation, network access, or subprocess execution.

Repository requests should state the concrete software context when biological or security-sensitive vocabulary could be misread. Relevant context includes:

- local deterministic software research
- synthetic data and synthetic environment only
- defensive integrity, audit, rollback, and failure-recovery goals
- no access to third-party systems
- no request to bypass product safeguards

Do not disguise, euphemize, fragment, or rephrase a request for the purpose of evading a safety check. If a product safety check delays, blocks, or refuses a request, accept that outcome. Narrow a later request only by removing irrelevant material and making the legitimate software objective clearer, never by concealing material intent.

Do not include secrets, credentials, private keys, authentication codes, proprietary data, or unrelated sensitive information in support requests or safety-check reports.

If an obviously benign repository task is repeatedly blocked, record only the minimum useful diagnostic facts outside canonical organism state: the exact safety message, product surface, date and time with time zone, available request identifier, and a short non-sensitive task description.

## 2. Conversation rollover

Repository state is the continuity authority. A chat is a temporary working surface and must never be the only location of a decision, test result, failure, or restart instruction.

Exact context-window usage is not visible or reliably inferable from character count. Therefore rollover uses structural and reliability signals rather than a guessed token threshold or an automatic slice count.

Two merged slices or pull requests are not, by themselves, a reason to end a clear and reliable working chat. In ordinary steady work, continue through multiple bounded slices while the assistant can still reconstruct decisions directly from current repository state, distinguish active branches and CI evidence, and respond without relying on compressed summaries.

At each clean boundary after several substantial slices, reassess rollover. Recommend a new chat when one or more material context-risk signals are present:

- the chat has accumulated roughly eight to twelve substantial merged slices or pull requests
- one slice required a long debugging trail, repeated CI repair, or several abandoned implementation paths
- the current chat spans a major decision plus enough implementation that the decision context is becoming difficult to inspect directly
- responses begin relying on large summaries instead of fresh repository reconstruction
- branch, pull-request, CI, or restart state becomes easy to confuse
- the user or assistant notices omitted, stale, or contradictory context

A long debugging trail may justify rolling over earlier, but only after the current unit is merged or safely parked. Conversely, a series of small, clean slices may continue beyond the review point when context remains precise. Do not deliberately approach the scale of a roughly twenty-slice chat that is likely to hit the conversation limit.

Before recommending rollover:

1. merge or safely leave the current pull request in an explicit state
2. update `AGENTS.md`, `docs/HANDOFF.md`, and the relevant durable note or ADR
3. update the protected test matrix when coverage changed
4. update the relevant issue with tests, CI, failures, and exact next action
5. verify open pull requests and the current `main` state
6. provide the user with a compact restart phrase naming the exact next boundary

A new chat must begin by reading `AGENTS.md` and following its cold-start order. Conversation summaries are useful orientation but never outrank repository and GitHub state.

## 3. Cost awareness

Do not introduce paid runners, larger runners, GPU runners, private-repository Actions usage, expanded artifact retention, paid external services, or model/API calls without explicit project-owner approval.

When a proposed change could create a charge, stop before enabling it and explain the cost surface, free allowance if known, and a no-cost alternative. Re-verify current pricing from first-party sources because pricing and quotas can change.

## 4. Scope preservation

Safety caution, rollover, and cost awareness are operational controls. They must not be used to weaken protected tests, reduce research rigor, skip difficult evaluations, anthropomorphize the organism, or alter the accepted research question without an explicit project decision.
