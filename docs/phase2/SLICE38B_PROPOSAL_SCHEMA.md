# Slice 38b: Exact Proposal Identities and Types

Status: merged through PR #91 as `068b3d30b91bd0bec89344a0d27b4685b3764a65`.

## Scope

This sub-slice implements the proposal identity and type-specific schema work that is independent of dispatch identity and response provenance.

Protected evidence closes:

- P2-H05: exact proposal-content identity, `proposal-content` digest, and proposal ID;
- P2-H06: proposal identity excludes response ID, preventing a proposal/response digest cycle;
- P2-I02: action candidates reference one request-allowed registered action and exact current seed-garden parameters;
- P2-I03: action candidates cannot define a new action, code, tool, path, SQL, permission, or budget field;
- P2-I04: abstain carries only `no_supported_action` and no command;
- P2-I05: defer carries only `await_state_change` and no schedule, retry, wake, or state effect;
- P2-I06: unknown actions and invalid parameter objects reject;
- P2-I07: extra fields and free text reject;
- P2-I08: proposal expiry equals the linked request expiry;
- P2-I09: required evaluator IDs equal the protected type-specific set;
- proposal-side P2-I11: confidence basis, fixture case, expiry, and evaluator sets are exact for every proposal type.

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

## Deferred design dependencies

- Issue #88: exact dispatch identity configuration-version contradiction;
- Issue #89: exact external provenance schema;
- Issue #92: versioned protected current-state projection for disposition;
- Issue #93: exact maximum request envelope and optional context.

No proposal in this sub-slice is canonical ingress state and no fixture is invoked. This is a pure protected schema/digest library for later fixture and ingress boundaries.

## Human design gate

All independent exact Slice 38 work currently available without choosing a private interpretation is complete. Dispatch, response/package, disposition identity, and maximum request evidence require decisions in Issues #88, #89, #92, and #93 before implementation proceeds honestly.

No Codex audit was used. Codex remains deferred until the complete Phase 2 implementation candidate is ready for the single implementation-completion audit.
