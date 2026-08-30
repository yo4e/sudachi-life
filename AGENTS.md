# AGENTS.md

This file is the compact continuity contract for AI collaborators working on SUDACHI.

## Source of truth

Repository state and current GitHub Issues/PRs outrank conversation memory.

At the start of work, read only what is needed to identify the current boundary:

1. `AGENTS.md`;
2. `docs/HANDOFF.md`;
3. the current Issue/PR or explicit task;
4. the directly governing contract, ADR, matrix, or durable note.

Do **not** reread the full project history by default. Escalate to older material only when a concrete ambiguity, conflict, provenance question, or cross-boundary risk requires it.

## Core question

SUDACHI asks whether a bounded artificial organism can convert finite external cognitive scaffolding into verified local competence and retain capability while requiring less justified caregiver assistance.

```text
parent reasoning -> verified experience -> reusable skill -> cheap local behavior
```

The repository is the organism's auditable body and developmental record. A model may later be caregiver or organ; it is not the organism.

> As it becomes smarter, it should become smaller and quieter.

Do not flatten SUDACHI into a generic agent, chatbot, virtual pet, or self-modifying loop.

## Frozen controls

Phase 1 and Phase 2 are frozen controls.

- Phase 1 freeze reference: `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338`, with the original 152 protected tests preserved.
- Phase 2 freeze merge: `b0941a8ba2a178fc891839198cd5dd5bf6e87719`, with the accepted 213-ID design/evidence package and 395-test baseline.
- Canonical writer categories remain exactly `organism` and `administration`.

Do not reinterpret or reopen frozen behavior for convenience. An exact frozen-boundary defect requires explicit project-owner authorization before repair.

## Phase 3 boundary

The withheld-caregiver evaluation design is accepted through `docs/phase3/WITHHELD_CAREGIVER_ACCEPTANCE.md` and its bound 140-row effective matrix.

Implementation requires separately authorized scope. A live human/model caregiver, network/subprocess route, credentials, arbitrary executable caregiver output, memory/skill generation, training/model updates, live action execution, repeated rollback, continuous execution, new writer categories, or material resource expansion is not authorized unless current repository state explicitly says otherwise.

Current implementation status and restart instructions belong in `docs/HANDOFF.md` and current GitHub state; do not duplicate a long implementation history here.

## Normal development workflow

For ordinary authorized work:

1. make the smallest coherent change;
2. add or update relevant tests;
3. run the relevant protected suite and ordinary CI;
4. record material decisions or findings in the relevant Issue/PR;
5. merge when the change is reviewable, in scope, and green.

Independent audit is **not** a routine per-slice or per-PR requirement. Follow `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md` for the compact review/audit policy.

Same-conversation audit mode may be used for a concentrated read-only adversarial review. It is a review technique, not independent evidence.

Reserve independent phase-gate audits for an actual freeze or another explicitly high-risk boundary.

## Human confirmation boundary

Explicit project-owner confirmation is required before materially changing:

- the research question, evaluation criteria, or accepted contract/ADR intent;
- frozen Phase 1 or Phase 2 behavior;
- canonical authority, permissions, writer categories, security boundaries, checkpoint/rollback semantics, or destructive migration;
- protected evidence or protected tests;
- live external capabilities or credentials;
- material autonomy, cost, resource ceilings, or data-retention scope;
- an unresolved contradiction between equally authoritative requirements.

Routine implementation choices inside already accepted scope do not require separate confirmation when they preserve these boundaries.

## Durable record

Keep durable state sufficient for a future collaborator to restart without chat history, but update documents when state changes materially rather than mechanically after every small edit.

At a stable boundary, record as applicable:

- exact merged or active PR/commit;
- tests and CI result;
- unresolved findings or failures;
- the next material action.

No critical decision may exist only in chat.

Repository prose, code, Issues, ADRs, and tests are English. Intentional Japanese README lines remain the standing exception.
