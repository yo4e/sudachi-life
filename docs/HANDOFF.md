# SUDACHI Handoff

Updated: **2026-08-30**

This file records the current restart state only. Repository and current GitHub state outrank stale prose or conversation memory.

## Frozen controls

- Phase 1 remains frozen at audited reference `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338`; the original 152 protected tests remain the schema-v1 control.
- Phase 2 remains frozen at merge `b0941a8ba2a178fc891839198cd5dd5bf6e87719`; the accepted Phase 2 package has 213 matrix/evidence IDs and a 395-test protected baseline.
- Canonical writer categories remain exactly `organism` and `administration`.
- The accepted Phase 3 withheld-caregiver design remains bound through `docs/phase3/WITHHELD_CAREGIVER_ACCEPTANCE.md` to design reference `c543b429c00b5c0aa2d9aa0ed26f4f7f3218d29c` and the canonical 140-row registry SHA-256 `12cd803c821f094b5292eb052c15dc99b8f08019c1950ffe506a6a44f228bab1`, byte length `43179`.

## Current Phase 3 implementation baseline

The implemented Phase 3 path now includes:

1. PR #151 — deterministic withheld-caregiver evaluation foundation;
2. PR #153 — typed caregiver proposal protocol and source-neutral interface;
3. PR #155 — deterministic caregiver-proposal-to-retention rehearsal;
4. PR #157 — Human Caregiver Pilot v1 preflight;
5. PR #160 — bounded self-only local/manual live-human bridge, merged as `056f9e4dad4b8a5f85e6b64abef18ce37951f7fb`.

PR #160 was independently audited at prior head `bb0639796...`, repaired as one coherent batch, then received a focused independent closure audit at exact head `74966468a8672b123c3440dbebb6cc008ed08c9f`. Closure comment `5468053185` records Finding 1 and Finding 2 as resolved, non-regression PASS, and the conclusion **ready to merge as the bounded self-only live-human bridge**.

Exact repaired candidate CI before merge: Test run 733 / workflow `33305237822`, **495 passed in 57.64s**, with install, compilation, protected-output upload, and schema-v1 genesis smoke passing.

The merged live bridge is intentionally narrow:

- exactly one authorized attempt: `attempt:self-human-pilot-v1-001`;
- exactly one closed pseudonymous caregiver identity;
- project owner is the sole caregiver/participant;
- local/manual structured input only;
- caregiver authority remains proposal-only;
- one-way process-authoritative attempt state with replay/fork resistance and terminal disablement;
- fixed Pilot v1 limits and privacy/data-minimization rules from #158;
- no model/provider, network, subprocess, browser automation, credentials, third-party participant, external mutable writer, new writer category, or direct caregiver-triggered organism action.

No actual human pilot attempt has been executed merely by merging PR #160.

## Review process

PR #150 is the active compact review/audit policy:

- ordinary authorized work uses bounded diff review, relevant protected tests, CI, and durable Issue/PR state;
- same-conversation read-only audit mode is optional;
- independent audit is reserved for actual freeze or another explicitly high-risk boundary;
- repairs do not automatically trigger a full independent re-audit.

PR #160 completed the independent gate required for introducing this first live human source. Phase 3 itself is **not frozen**; the accepted Phase 3 design still requires an independent implementation audit before a later Phase 3 freeze.

## Exact next action

The next material step is **not more bridge plumbing**. It is to prepare and execute the one already-authorized self-only Human Caregiver Pilot v1 operational attempt using the merged local/manual bridge.

At the next session:

1. read `AGENTS.md`, this file, Issue #3, Issue #158, and `docs/research/HUMAN_CAREGIVER_PILOT_V1_PREFLIGHT.md`;
2. inspect current `main` and confirm PR #160 remains the live-human baseline;
3. define the concrete local/manual run procedure for the single authorized attempt without broadening the scope;
4. run the attempt only under the fixed #158 limits, with no off-channel semantic help and no in-attempt code edits;
5. preserve proposal, timing, provenance, disablement, validation, and negative-outcome evidence;
6. after the attempt, evaluate the protocol evidence before deciding whether the next step is protocol repair, a later preregistered developmental study, prior-work/novelty work, or another caregiver condition.

Do **not** silently add another human participant, another authorized attempt, adaptive fading, a model/provider route, networked transport, or scientific developmental/effectiveness claims while running this operational pilot.

## Human confirmation boundary

Request explicit project-owner confirmation before changing the research question or accepted contract intent, frozen behavior, authority/security boundaries, checkpoint/rollback semantics, protected evidence, writer categories, another live participant or attempt, any model/provider capability, or material autonomy/resource/data-retention scope.

No critical project decision should exist only in chat.
