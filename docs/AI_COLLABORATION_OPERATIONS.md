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

Exact context-window usage is not visible or reliably inferable from character count. Therefore rollover uses structural triggers rather than a guessed token threshold.

At the next clean boundary, recommend starting a new chat when any of these conditions is true:

- two substantial slices or pull requests have been merged in the current chat
- one slice required a long debugging trail or repeated CI repair
- the current chat spans a major decision plus its implementation
- responses begin relying on large summaries instead of direct repository reconstruction
- the user or assistant notices omitted, confused, or stale context

Do not continue beyond three substantial merged slices in one chat unless stopping would leave a branch, pull request, or canonical transition in an unsafe intermediate state. Finish or safely park that unit, update continuity documents, and then roll over.

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
