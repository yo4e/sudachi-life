# SUDACHI Handoff

Updated: **2026-08-30**

This file records only the current durable restart state. Historical details remain in merged ADRs, Issues, PRs, and audit records.

## Current project state

- Phase 1 is frozen at audited reference `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338`; the original 152 protected tests remain the schema-v1 control.
- Phase 2 is frozen at merge `b0941a8ba2a178fc891839198cd5dd5bf6e87719`; the accepted Phase 2 package has 213 matrix/evidence IDs and a 395-test protected baseline.
- Canonical writer categories remain exactly `organism` and `administration`.
- The Phase 3 withheld-caregiver design is accepted through `docs/phase3/WITHHELD_CAREGIVER_ACCEPTANCE.md`, bound to design reference `c543b429c00b5c0aa2d9aa0ed26f4f7f3218d29c` and the canonical 140-row registry SHA-256 `12cd803c821f094b5292eb052c15dc99b8f08019c1950ffe506a6a44f228bab1` / byte length `43179`.

Repository and current GitHub state outrank stale prose or conversation memory.

## Current Phase 3 implementation baseline

Three bounded fixture-only implementation slices are merged on `main`:

1. **Deterministic evaluation foundation** — PR #151, merge `6e8aa28c8a620248afd59e3a7f81c37aa7c07cf7`.
   - Implements deterministic E0/E1/E2 fixture evidence, fail-closed validation, W0/W1/W2 classification, W3 evidence, and adversarial tests.
   - Issue #147 is the historical independent audit record for an earlier candidate; its findings were repaired before merge.

2. **Caregiver proposal protocol / source-neutral interface** — PR #153, merge `298d1e3b9e3d5b2c3f553259c0568955fbd7781d`.
   - Adds typed proposal classes, immutable request/proposal binding, proposal-only authority, deterministic fixture adapter, payload/proposal integrity checks, and explicit absence accounting.
   - The active source set remains exactly the deterministic fixture source. Human/model source kinds are representable identifiers only and fail validation.

3. **Integrated caregiver-to-retention rehearsal** — PR #155, merge `596c9e184d1592f350dcc504c03a4dd31556e4ec`.
   - Connects the typed fixture proposal to the existing caregiving record, conversion provenance, caregiver-derived local substrate, withdrawal evidence, and retained W1 capability.
   - This is a mechanics/conformance rehearsal only; the report remains explicitly non-developmental-claiming.
   - PR-head Test run 720: **461 passed in 56.31s**; main Test run 721: success. Install, compilation, protected-output upload, and schema-v1 genesis smoke passed.

These slices do **not** add live human/model caregiving, network/subprocess access, credentials/provider selection, arbitrary executable caregiver output, direct caregiver-triggered organism actions, memory/skill generation, training/model updates, live action execution, repeated rollback, continuous execution, new writer categories, or material resource expansion.

## Research and live-capability boundary

Issue #3 remains open for work required before a live caregiver, named provider, automated external consultation, or strong public novelty/provider claim. This includes human-caregiver protocol details, privacy/consent, hidden-labor controls, live cost/latency/reliability accounting, provider/compliance and transformation-rights review, and remaining novelty/positioning work.

Do not connect a live human/model caregiver or external provider without a new explicitly authorized scope.

## Review process

PR #150 merged the compact review/audit policy:

- ordinary authorized work uses bounded diff review, relevant protected tests, CI, and durable Issue/PR state;
- same-conversation read-only audit mode is optional for concentrated adversarial checking;
- independent audit is reserved for actual phase freeze or another explicitly high-risk boundary;
- repairs do not automatically trigger a full independent re-audit.

The accepted Phase 3 design still requires an independent implementation audit before **Phase 3 freeze**. The merged slices above do not freeze Phase 3.

## Restart

1. Read `AGENTS.md` and this file.
2. Inspect current `main` and open Issues/PRs relevant to the next Phase 3 scope.
3. Treat Phase 1 and Phase 2 as frozen controls.
4. Treat merge `596c9e184d1592f350dcc504c03a4dd31556e4ec` as the current Phase 3 implementation baseline.
5. The deterministic proposal-to-retention mechanics now run end to end; choose the next research/implementation scope before adding more plumbing.
6. Do not drift directly into live caregiver/provider capability. Use Issue #3 and explicit project-owner authorization before crossing that boundary.
7. Use ordinary review + relevant protected tests + CI for ordinary work; reserve independent audit for freeze/high-risk gates.

## Human confirmation boundary

Request explicit project-owner confirmation before changing the research question or accepted contract intent, frozen behavior, authority/security boundaries, checkpoint/rollback semantics, live external capabilities, destructive migration, protected evidence, writer categories, or material autonomy/resource scope.

No critical project decision should exist only in chat.
