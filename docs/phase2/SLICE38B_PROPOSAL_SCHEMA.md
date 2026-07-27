# Slice 38b: Exact Proposal Identities and Types

Status: merged through PR #91 as `068b3d30b91bd0bec89344a0d27b4685b3764a65`.

## Scope

This sub-slice implements the proposal identity and type-specific schema work that is independent of dispatch identity and response provenance.

Protected evidence closes:

- P2-H05: exact proposal-content identity, `proposal-content` digest, and proposal ID;
- P2-H06: proposal identity excludes response ID, preventing a proposal/response digest cycle;
- P2-I02: exact proposal common field set;
- P2-I03: proposal expiry equals the linked request expiry;
- P2-I04: confidence basis exactly links the protected fixture case;
- P2-I05: required evaluator IDs equal the protected type-specific set;
- P2-I06: exact action-candidate subject, parameters, rationale, action allowlist, and registered schema;
- P2-I07: exact abstain objective subject and `no_supported_action` value/rationale;
- P2-I08: exact defer objective subject and `await_state_change` value/rationale;
- P2-I09: defer has no schedule, retry, wake, or state effect;
- proposal-side P2-I11: free text, commands, unknown actions, invalid parameters, wrong expiry, confidence, and evaluator sets reject.

This sub-slice does not construct a dispatch identity, response identity, external provenance, response envelope, package, ingress, or disposition.

## Exact identity

The proposal-content digest preimage contains exactly:

- proposal schema and protocol version;
- request and dispatch IDs;
- proposal ordinal `1`;
- proposal type;
- subject reference;
- proposed value;
- rationale code;
- confidence basis;
- expiry lifecycle;
- required evaluator IDs.

It excludes both proposal ID and response ID.

The proposal ID is:

```text
"consultation-proposal:" + H("proposal-content", proposal_identity)
```

Only after proposal content and response identity are independently derived does `finalize_proposal` add the response ID to the final proposal envelope. Changing only the response ID does not change the proposal content digest or proposal ID.

## Type-specific rules

### Action candidate

- subject: exactly `{"action_id": <request-allowed action>}`;
- value: exactly `{"parameters": {"plot_id": <identifier>}}` for the current protected seed-garden actions;
- rationale: `existing_action_applicable`;
- evaluators: `action-schema-v1`, `current-state-v1`, `permission-v1`.

### Abstain

- subject equals the linked request objective reference exactly;
- value: exactly `{"reason_code":"no_supported_action"}`;
- rationale: `no_supported_action`;
- evaluators: `abstain-policy-v1`, `current-state-v1`.

### Defer

- subject equals the linked request objective reference exactly;
- value: exactly `{"reason_code":"await_state_change"}`;
- rationale: `await_state_change`;
- evaluators: `current-state-v1`, `defer-policy-v1`.

Every type requires confidence basis exactly:

```json
{"basis_type":"deterministic_fixture_case","fixture_case_id":<declared case>}
```

The final proposal envelope is bounded by 16 KiB and contains no undeclared authority, cost, budget, permission, execution, command, code, path, URL, credential, schedule, retry, or free-text field.

## Test-first evidence

Tests-only head `53988a7a3969610a1d494d330b8aa7a0554b4021`, GitHub Actions run 550 failed because `sudachi_life.phase2_proposal` did not exist.

Implementation head `208d5e96290701a36841bb767ddd9fac50071d33`, run 551:

- 275 passed in 29.84 seconds.

Final exact PR head `3a0affde5e2bbd28491a02f442cd48cb82df66cf`, run 552:

- protected suite passed;
- dependency installation succeeded;
- source and test compilation succeeded;
- schema-v1 genesis CLI smoke succeeded.

All original 152 Phase 1 tests remain unchanged and included.

## Accepted follow-on definitions

Issues #88, #89, #92, and #93 were resolved by explicit project-owner adoption and ADR 0010. ADR 0010 now defines:

- dispatch identity with `configuration_version`;
- the exact three-field deterministic-fixture provenance object;
- exact response and package cardinality;
- `sudachi.consultation.current_state/v1` and disposition identity;
- no optional request context in Protocol v1;
- the largest structural request interpretation for P2-E10.

The exact restart is Slice 38c dispatch/response/package protocol validation, followed by real P2-E10 evidence and Slice 39 administrative dispatch.

No Codex audit was used. Codex remains deferred until the complete Phase 2 implementation candidate is ready for the single implementation-completion audit.
