# Routine Clarification Delegation

Status: **Active project-owner instruction from 2026-07-27**

## Delegated decision class

The project owner authorizes the primary AI collaborator to formally adopt a recommended design clarification without a separate human confirmation when all of the following are true:

1. the clarification only closes an implementation-blocking ambiguity inside already accepted SUDACHI contracts, ADRs, matrices, schemas, or roadmap scope;
2. the recommendation is the smallest exact deterministic choice consistent with the repository's existing normative precedence;
3. it does not broaden canonical authority, writer categories, permissions, evaluator authority, external capabilities, or research scope;
4. it does not weaken, reinterpret, delete, skip, or condition a protected test or accepted invariant;
5. it preserves the frozen Phase 1 boundary and all explicit absence requirements;
6. it is recorded in a focused Issue and accepted ADR or equivalent reviewed repository document before implementation;
7. the documentation PR and protected CI pass before the clarification is treated as merged normative state.

Routine delegated clarifications may define exact field sets, typed aliases, digest preimages, event names, closed payload shapes, deterministic ordering, bounded reason mappings, idempotence rules, or failure behavior that the accepted design already requires but did not enumerate.

## Human confirmation remains required

The collaborator must stop and request explicit project-owner confirmation for a clarification that would materially change any of these:

- SUDACHI's central research question, thesis, evaluation criteria, or roadmap scope;
- Minimal Organism Contract semantics or accepted ADR intent rather than merely closing an ambiguity;
- the frozen Phase 1 behavior, tests, actions, selector, executor, evaluators, clocks, checkpoint rules, rollback transformation, or writer categories;
- canonical authority, permissions, budgets, evaluator sets, lineage rules, or security boundary;
- live caregiver, model/API, human chat, network, subprocess, arbitrary code, credentials, external mutable writes, continuous execution, memory, skill learning, action adoption, or generic-agent behavior;
- migration or destructive data transformation with irreversible or compatibility consequences;
- a contradiction between two equally authoritative accepted requirements where no strictly narrower interpretation exists;
- safety, legal, privacy, financial, or external-service obligations;
- deletion, weakening, or reinterpretation of protected evidence;
- a material expansion of cost, resource ceilings, autonomy, or data retention.

When uncertain whether a clarification crosses this boundary, prefer human confirmation.

## Operating rule

Repository and current GitHub state remain authoritative. A delegated clarification is not canonical merely because it appears in chat or an Issue recommendation. It becomes accepted only after the focused ADR/documentation change merges with protected CI.

Every delegated adoption must be reported in the durable handoff and relevant implementation Issue. The project owner may revise or revoke this delegation explicitly at any time.