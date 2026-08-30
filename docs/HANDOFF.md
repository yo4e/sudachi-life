# SUDACHI Handoff

Updated: **2026-08-30**

This file records only the current durable restart state. Historical details remain in merged ADRs, Issues, PRs, and audit records.

## Current project state

- Phase 1 is frozen at audited reference `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338`; the original 152 protected tests remain the schema-v1 control.
- Phase 2 is frozen at merge `b0941a8ba2a178fc891839198cd5dd5bf6e87719`; the accepted Phase 2 package has 213 matrix/evidence IDs and a 395-test protected baseline.
- Canonical writer categories remain exactly `organism` and `administration`.
- The Phase 3 withheld-caregiver evaluation design is accepted through `docs/phase3/WITHHELD_CAREGIVER_ACCEPTANCE.md`.
- The accepted Phase 3 design reference is `c543b429c00b5c0aa2d9aa0ed26f4f7f3218d29c` with canonical 140-row registry SHA-256 `12cd803c821f094b5292eb052c15dc99b8f08019c1950ffe506a6a44f228bab1`, byte length `43179`.
- The first deterministic fixture-only Phase 3 implementation foundation is merged to `main` as `6e8aa28c8a620248afd59e3a7f81c37aa7c07cf7` via PR #151.

Repository and current GitHub state outrank stale prose or conversation memory.

## Phase 3 fixture foundation

Issue #145 authorized the smallest deterministic fixture-only Phase 3 implementation foundation and is now complete.

The merged package remains additive: 12 Phase 3 files implementing ADR 0018, the implementation evidence map, immutable fixture evidence records, fail-closed validation, deterministic E0/E1/E2 fixture flow, W0/W1/W2 classification, W3 evidence, and protected adversarial tests.

Issue #147 independently audited earlier candidate `8c14d6acaa76c5c523ff42e48e7498b6c1b24b2a`, found four material implementation defects, and is now closed as the historical audit record. A partial earlier Codex audit supplied two additional bounded residual checks. The merged foundation contains the corresponding repairs and adversarial regressions.

Final tested implementation head before squash merge:

- head: `cc9c3299060749a9d68aa51706f7bd7795694202`;
- base: `2c455837d0ce27f2d5494cf856600f7304d6550e`;
- Test run 713: **438 passed in 53.32s**;
- replacement-PR Test run 714: success on the same exact head;
- install, source/test compilation, protected-output artifact upload, and schema-v1 genesis CLI smoke: passed;
- compare to the then-current `main`: exactly 12 additive Phase 3 files.

Draft PR #146 contains the full implementation/audit history. It was closed unmerged only because the connected `mark ready for review` operation failed on a GitHub GraphQL schema mismatch. Non-Draft replacement PR #151 used the same branch and exact tested head and was squash-merged.

The foundation does **not** add live human/model caregiving, network/subprocess access, credentials, arbitrary executable caregiver output, memory/skill generation, training/model updates, live action execution, repeated rollback, continuous execution, new writer categories, or material resource expansion.

## Review process

PR #150 merged the compact review/audit policy.

- Ordinary authorized work uses bounded diff review, relevant protected tests, CI, and durable Issue/PR state.
- Same-conversation read-only audit mode is optional for concentrated adversarial checking; it is not independent evidence.
- Independent audit is reserved for actual phase freeze or another explicitly high-risk boundary.
- Repairs do not automatically trigger a full independent re-audit.

The accepted Phase 3 design still requires an independent implementation audit before **Phase 3 freeze**. The fixture-foundation merge is not a Phase 3 freeze.

## Restart

1. Read `AGENTS.md` and this file.
2. Inspect current `main` and open Issues/PRs relevant to the next Phase 3 scope.
3. Treat Phase 1 and Phase 2 as frozen controls.
4. Treat the fixture foundation merged as `6e8aa28c8a620248afd59e3a7f81c37aa7c07cf7` as the current Phase 3 implementation baseline.
5. Continue Phase 3 only through explicitly authorized scope; before any live caregiver/provider capability, revisit the still-required research/authorization boundary.
6. Use ordinary review + relevant protected tests + CI for ordinary implementation work.
7. Reserve an independent implementation audit for the later Phase 3 freeze or another material high-risk boundary.

## Human confirmation boundary

Request explicit project-owner confirmation before changing the research question or accepted contract intent, frozen behavior, authority/security boundaries, checkpoint/rollback semantics, live external capabilities, destructive migration, protected evidence, writer categories, or material autonomy/resource scope.

No critical project decision should exist only in chat.
