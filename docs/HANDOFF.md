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

Four bounded implementation slices are merged on `main`:

1. **Deterministic evaluation foundation** — PR #151, merge `6e8aa28c8a620248afd59e3a7f81c37aa7c07cf7`.
   - Implements deterministic E0/E1/E2 fixture evidence, fail-closed validation, W0/W1/W2 classification, W3 evidence, and adversarial tests.
   - Issue #147 is the historical independent audit record for an earlier candidate; its findings were repaired before merge.

2. **Caregiver proposal protocol / source-neutral interface** — PR #153, merge `298d1e3b9e3d5b2c3f553259c0568955fbd7781d`.
   - Adds typed proposal classes, immutable request/proposal binding, proposal-only authority, deterministic fixture adapter, payload/proposal integrity checks, and explicit absence accounting.
   - The active source set remains exactly the deterministic fixture source. Human/model source kinds are representable identifiers only and fail validation.

3. **Integrated caregiver-to-retention rehearsal** — PR #155, merge `596c9e184d1592f350dcc504c03a4dd31556e4ec`.
   - Connects the typed fixture proposal to the existing caregiving record, conversion provenance, caregiver-derived local substrate, withdrawal evidence, and retained W1 capability.
   - This is a mechanics/conformance rehearsal only; the report remains explicitly non-developmental-claiming.

4. **Human Caregiver Pilot v1 preflight** — PR #157, merge `276d28e2205f375439a2e975f28d89f9449a2786`.
   - Adds a disabled preflight model, `HumanProposalDraft`, closed pseudonymous caregiver IDs, visible-reference validation, proposed fixed pilot limits, privacy/data-minimization defaults, hidden-labor controls, failure/stop handling, and the research packet `docs/research/HUMAN_CAREGIVER_PILOT_V1_PREFLIGHT.md`.
   - Pilot v1 is proposed as a one-caregiver, one-attempt **operational protocol pilot**, not a scientific developmental-gain/effectiveness/novelty study.
   - Proposed review defaults: max 3 consultations, max 2 clarifications, max 10 minutes active caregiver time, max 5 minutes response latency, max 30 minutes attempt wall time, max 2,048 UTF-8 bytes per proposal; no separate raw chat transcript; proposed 365-day local proposal-payload retention; no raw proposal publication by default; zero off-channel semantic help and zero in-attempt code edits.
   - `CaregiverSourceKind.HUMAN` remains outside `ACTIVE_SOURCE_KINDS`; no live transport or live draft-to-proposal bridge exists.
   - PR-head Test run 725: **475 passed in 45.54s**; main Test run 726: **475 passed in 149.12s**. Install, compilation, protected-output upload, and schema-v1 genesis smoke passed.

These slices do **not** add live human/model caregiving, network/subprocess access, credentials/provider selection, arbitrary executable caregiver output, direct caregiver-triggered organism actions, memory/skill generation, training/model updates, live action execution, repeated rollback, continuous execution, new writer categories, or material resource expansion.

## Research and live-capability boundary

Issue #3 is the active research/gate record. The pre-live human-caregiver mechanics are prepared, but live activation still requires one consolidated project-owner decision.

Before live human implementation begins, resolve:

- accept/change the proposed Pilot v1 limits;
- select the first caregiver: project owner or another consenting adult;
- declare the actual institutional/research ethics-review context; if uncertain, keep it unresolved;
- accept/change the proposed 365-day proposal-payload retention period;
- accept/change the no-separate-raw-chat and no-public-raw-payload defaults;
- authorize implementation of the bounded live human bridge.

Do not infer whether ethics/IRB review is legally required. That depends on the actual research environment and participant context.

If the live bridge is authorized, create a new explicitly bounded live-integration scope. The exact live candidate must pass protected tests/CI and then receive one independent read-only audit because live human access is a high-risk capability boundary. The independent reviewer need not be Codex specifically, but must not materially implement the exact candidate being certified.

## Review process

PR #150 merged the compact review/audit policy:

- ordinary authorized work uses bounded diff review, relevant protected tests, CI, and durable Issue/PR state;
- same-conversation read-only audit mode is optional for concentrated adversarial checking;
- independent audit is reserved for actual phase freeze or another explicitly high-risk boundary;
- repairs do not automatically trigger a full independent re-audit.

The accepted Phase 3 design still requires an independent implementation audit before **Phase 3 freeze**. The merged slices above do not freeze Phase 3.

## Restart

1. Read `AGENTS.md` and this file.
2. Inspect current `main` and Issue #3.
3. Treat Phase 1 and Phase 2 as frozen controls.
4. Treat merge `276d28e2205f375439a2e975f28d89f9449a2786` as the current Phase 3 **pre-live implementation baseline**; later HANDOFF-only commits do not change that implementation baseline.
5. Read `docs/research/HUMAN_CAREGIVER_PILOT_V1_PREFLIGHT.md` before any live-human design work.
6. The next material gate is the consolidated project-owner Pilot v1 decision above. Do not add more pre-live plumbing unless it resolves a concrete blocker.
7. Do not enable `CaregiverSourceKind.HUMAN`, add a live transport, or create a live draft-to-proposal bridge before that authorization.
8. After authorization, implement the smallest live bridge, run protected tests/CI, and perform one independent audit on the exact live candidate.

## Human confirmation boundary

Request explicit project-owner confirmation before changing the research question or accepted contract intent, frozen behavior, authority/security boundaries, checkpoint/rollback semantics, live external capabilities, destructive migration, protected evidence, writer categories, or material autonomy/resource/data-retention scope.

No critical project decision should exist only in chat.
