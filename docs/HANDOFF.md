# SUDACHI Handoff

Updated: **2026-08-30**

This file records only the current durable restart state. Historical details remain in merged ADRs, Issues, PRs, and audit records.

## Current project state

- Phase 1 is frozen at audited reference `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338`; the original 152 protected tests remain the schema-v1 control.
- Phase 2 is frozen at merge `b0941a8ba2a178fc891839198cd5dd5bf6e87719`; the accepted Phase 2 package has 213 matrix/evidence IDs and a 395-test protected baseline.
- Canonical writer categories remain exactly `organism` and `administration`.
- The Phase 3 withheld-caregiver evaluation design is accepted through `docs/phase3/WITHHELD_CAREGIVER_ACCEPTANCE.md`.
- The accepted Phase 3 design reference is `c543b429c00b5c0aa2d9aa0ed26f4f7f3218d29c` with the canonical 140-row registry SHA-256 `12cd803c821f094b5292eb052c15dc99b8f08019c1950ffe506a6a44f228bab1`, byte length `43179`.

Repository and current GitHub state outrank stale prose or conversation memory.

## Active Phase 3 implementation foundation

Issue #145 authorizes the smallest deterministic fixture-only Phase 3 implementation foundation. PR #146 implements that scope without introducing a live caregiver or changing frozen Phase 1/2 runtime files.

Current PR #146 head at this handoff update:

- head: `02c4cdc00c7b73feabd68dc70f98cafb6137d55e`;
- base at that head: `7215905f4c04a24a1bd23027527606e4a00fe0c1`;
- changed range: 12 additive Phase 3 files;
- final exact-head CI before the review-policy update: Test run 710 / workflow run `33288637022`;
- protected suite: **438 passed**;
- install, source/test compilation, protected-output upload, and schema-v1 genesis CLI smoke: passed.

Issue #147 independently audited the earlier candidate `8c14d6acaa76c5c523ff42e48e7498b6c1b24b2a` and found four implementation defects. A bounded review of an earlier incomplete Codex audit added two residual repair targets. PR #146 now contains the corresponding repair pass and adversarial regressions.

The repaired foundation does not add live human/model caregiving, network/subprocess access, credentials, arbitrary executable caregiver output, memory/skill generation, training/model updates, live action execution, repeated rollback, continuous execution, new writer categories, or material resource expansion.

## Review process

The compact policy in `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md` distinguishes:

- ordinary review for normal pull requests and repairs;
- optional same-conversation read-only audit mode for concentrated adversarial checking;
- independent phase-gate audit for an actual phase freeze or another explicitly high-risk boundary.

Do not require a fresh independent audit for every repaired pull request. The accepted Phase 3 design still requires an independent implementation audit before **Phase 3 freeze**; that requirement is not a per-foundation-PR merge gate.

## Restart

1. Read `AGENTS.md` and this file.
2. Inspect current PR #146, Issues #145/#147/#148, and current CI/main state.
3. Treat Phase 1 and Phase 2 as frozen controls.
4. Continue Phase 3 only inside explicitly authorized scope.
5. Use ordinary review + relevant protected tests + CI for ordinary development.
6. Reserve an independent audit for the later Phase 3 freeze or another material high-risk boundary.

## Human confirmation boundary

Request explicit project-owner confirmation before changing the research question or accepted contract intent, frozen behavior, authority/security boundaries, checkpoint/rollback semantics, live external capabilities, destructive migration, protected evidence, writer categories, or material autonomy/resource scope.

No critical project decision should exist only in chat.
