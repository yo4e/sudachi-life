# ADR 0009: Define the zero-caregiver semantic checkpoint projection

- Status: Proposed
- Date: 2026-07-26
- Decision owners: project owner and repository maintainers
- Review issue: #63
- Supersedes: ADR 0008 section 11 and only the zero-caregiver projection rules in Consultation Protocol v1 and the Phase 2 test matrix

## Context

ADR 0008 requires a paired schema-v1/schema-v2-zero control while also requiring schema-v2 to contain additional empty protected SQLite objects. The accepted text says every original Phase 1 row and column compares exactly except `schema_version` and `budget_config_version`, but separately states that raw checkpoint databases and digests differ.

Those statements cannot both hold after a stable checkpoint. Additional schema objects necessarily change checkpoint database bytes and therefore change artifact-derived values stored in original Phase 1 locations, including checkpoint IDs, database digests, manifest digests, database sizes, and the organism's latest stable checkpoint ID.

Implementation must not hide this contradiction through an undocumented projection.

## Decision

### 1. Use `phase1-projection-v2`

`phase1-projection-v2` replaces `phase1-projection-v1` before any Phase 2 runtime implementation is accepted.

Paired schema-v1 and schema-v2-zero organisms use identical declared inputs, seeds, wall-clock readings, monotonic readings, and operation order.

### 2. Preserve the original Phase 1 budget singleton exactly

For schema-v2 organisms:

- the original `budget_config` singleton remains exactly `phase1-v1` with the unchanged Phase 1 values
- the original `organism.budget_config_version` and original event `budget_config_version` remain `phase1-v1`
- a new protected singleton `consultation_configuration` stores schema-v2 consultation protocol and either `phase2-zero-caregiver-v1` or `phase2-fixture-v1`

This keeps every original Phase 1 budget row and field semantically exact. Consultation configuration never masquerades as a Phase 1 budget configuration.

### 3. Exact original-state comparison

The projection compares every original Phase 1 table, column, row, event type, event sequence, authority source, parent linkage, and payload value exactly except for the explicitly listed locations below.

The only version normalization is:

- original `organism.schema_version`
- original `event.schema_version`
- top-level original event-payload key exactly `schema_version`

No `budget_config_version` normalization remains necessary because the original Phase 1 budget configuration stays exact.

Nested keys, similar spellings, additional keys, missing keys, and every undeclared location compare exactly.

### 4. Exact checkpoint semantic projection

Checkpoint artifact identity is compared by semantic boundary rather than byte-derived identity.

The following original locations are projected:

- `organism.latest_stable_checkpoint_id` becomes `(lineage_generation, latest_stable_event_sequence)` when present
- `checkpoint_registry.checkpoint_id` is replaced by `(lineage_generation, event_sequence)`
- `checkpoint_registry.manifest_sha256` is omitted from the paired equality projection
- `checkpoint_registry.database_sha256` is omitted from the paired equality projection
- `checkpoint_registry.database_size_bytes` is omitted from the paired equality projection

Every other original checkpoint-registry field compares exactly, including lineage, event sequence, creation time, registration time, and protection flag.

Checkpoint manifests are compared field-for-field after projecting only:

- checkpoint ID to `(lineage_generation, event_sequence)`
- schema version to the declared schema-version sentinel
- database SHA-256
- database size bytes

All remaining manifest fields compare exactly. Raw checkpoint database bytes, raw manifest bytes, manifest digests, and checkpoint directory names are not equal and are not claimed equal.

### 5. Schema-v2 absence remains strict

Under `phase2-zero-caregiver-v1`:

- the protected `consultation_configuration` singleton exists and is exact
- all operational consultation tables are empty
- operational consultation tables have no `sqlite_sequence` entry
- no consultation event, source, cost, adapter invocation, terminal outcome, disposition, or caregiver-derived effect exists
- no Phase 2 caregiver runtime module is invoked by a zero-caregiver run

### 6. Behavior and eligibility remain exact

The paired control still requires exact equality of:

- consumed inputs and garden decisions
- environment mutations and outcomes
- lifecycle and failure streak
- maintenance state
- pending/stable checkpoint boundaries
- rollback eligibility and lineage semantics
- organism and administration authority classification

Only byte-derived checkpoint artifact identity and declared schema-version locations are projected.

## Consequences

Positive:

- the zero-caregiver oracle is implementable and independently reconstructable
- Phase 1 budget configuration remains truly frozen
- schema-v2 checkpoint differences are acknowledged without weakening behavioral equality
- no wildcard or recursive normalization can hide a regression

Negative:

- the projection has a small explicit list of artifact-derived exceptions
- checkpoint byte identity cannot serve as the paired zero-caregiver oracle
- ADR 0008, protocol text, matrix IDs P2-B01–P2-B03 and P2-C01–P2-C09, AGENTS, HANDOFF, and Issue #61 require synchronization

## Scope

This ADR changes only consultation-configuration placement and the zero-caregiver comparison oracle. It does not change caregiver authority, transaction boundaries, request/dispatch/ingress/disposition behavior, budgets, expiry, lineage epochs, storage ceilings, or explicit exclusions.

Slice 36 remains blocked until this ADR is accepted and merged. Because the correction changes the same zero-caregiver boundary identified by the design audit, the project owner must decide whether ordinary review is sufficient or whether one focused read-only design re-audit is required before acceptance.
