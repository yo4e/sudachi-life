# ADR 0009: Define the zero-caregiver semantic artifact projection

- Status: Proposed after focused independent re-audit corrections
- Date: 2026-07-26
- Decision owners: project owner and repository maintainers
- Review issue: #63
- Focused design re-audit: Issue #63 comment `5082883885`, audited head `e4f3527518cbc4e4ff8ab239a90f48bfa47fdbb8`
- Supersedes: ADR 0008 sections 2, 6, 8, 10, and 11 only where they place Phase 2 configuration in the Phase 1 budget singleton or define the zero-caregiver comparison oracle

## Context

ADR 0008 requires a paired schema-v1/schema-v2-zero control while also requiring schema-v2 to contain additional empty protected SQLite objects. The accepted text says every original Phase 1 row and column compares exactly except version fields, but separately states that raw checkpoint databases and digests differ.

Those statements cannot both hold after a stable checkpoint. Additional schema objects change checkpoint database bytes and therefore propagate byte-derived differences through checkpoint IDs, manifests, canonical event payloads, repair and retention evidence, rollback archive/candidate identities, and aggregate byte accounting.

The focused independent re-audit confirmed the contradiction and concluded:

> ADR 0009 is ready after specified documentation or matrix corrections.

This revision closes the full byte-provenance graph with exact locations. It does not use wildcard, recursive, suffix, or global key-name normalization.

## Decision

### 1. Use `phase1-projection-v2`

`phase1-projection-v2` replaces `phase1-projection-v1` before any Phase 2 runtime implementation is accepted.

Paired schema-v1 and schema-v2-zero scenarios use identical declared organism IDs, inputs, seeds, wall-clock readings, monotonic readings, administrative reasons, selected semantic boundaries, fault-injection choices, and operation order.

The oracle has two stages:

1. independently validate every run and every retained artifact against its own schema, digest, size, linkage, immutability, and physical ceilings
2. compare the two validated runs after applying only the exact semantic replacements in this ADR

A value is never projected merely because its key contains `id`, `digest`, `sha`, `size`, `bytes`, `path`, or `checkpoint`.

### 2. Preserve the original Phase 1 budget singleton exactly

For schema-v2 organisms:

- the original `budget_config` singleton remains exactly `phase1-v1` with unchanged Phase 1 values
- `organism.budget_config_version` remains exactly `phase1-v1`
- every original event column and original event-payload value named `budget_config_version` remains exactly `phase1-v1`
- Phase 2 policy is stored only in a new protected singleton `consultation_configuration`

The exact new singleton is:

```sql
CREATE TABLE consultation_configuration (
    singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1),
    protocol_version INTEGER NOT NULL CHECK (protocol_version = 1),
    configuration_version TEXT NOT NULL UNIQUE,
    configuration_json TEXT NOT NULL
);
```

Exactly one row exists. `configuration_json` is canonical JSON and must equal one repository-defined protected object:

- `phase2-zero-caregiver-v1`: all consultation request, dispatch, fixture, response, proposal, disposition, clarification, logical-payload, human, model, money, declared-latency, and consultation-record allowances are zero
- `phase2-fixture-v1`: the exact finite limits accepted by ADR 0008 and Consultation Protocol v1

Unknown, missing, duplicate, mixed, noncanonical, or internally contradictory configuration fails before canonical mutation. The table schema, row cardinality, accepted JSON objects, and immutability guards are part of the protected schema fingerprint.

`consultation_configuration.configuration_version` is included in every consultation request/dispatch identity and every consultation row/event that declares configuration. It never replaces or aliases the original Phase 1 `budget_config_version`.

### 3. Exact original-state comparison

Every original Phase 1 table, column, row, event type, event sequence, authority source, parent linkage, and payload value compares exactly except for the exact locations in sections 4–8.

The only original schema-version normalization is:

- `organism.schema_version`
- `event.schema_version`
- top-level original event-payload key exactly `schema_version`
- artifact manifest field exactly `schema_version` where the Phase 1 format already declares that field

Each is replaced with the sentinel `<schema-version>`.

No `budget_config_version` normalization is permitted.

Nested keys, similar spellings, additional keys, missing keys, wrong event types, wrong JSON paths, wrong list positions, and every undeclared location compare exactly.

### 4. Semantic tokens and byte-derived values

The projection uses these typed semantic tokens:

- `CP(g,e)`: checkpoint at lineage generation `g` and checkpoint event sequence `e`
- `RA(g,a,s)`: pre-rollback archive for abandoned lineage `g`, active event sequence `a`, and selected checkpoint event sequence `s`
- `RC(g,r,s)`: source restore candidate for abandoned lineage `g`, `rollback_started` event sequence `r`, and selected checkpoint event sequence `s`
- `TC(g,r)`: transformed candidate for new lineage `g` and `rollback_lineage_prepared` event sequence `r`
- `STAGE(CP(g,e))`: retention staging directory for exactly that checkpoint boundary

An omitted cross-run byte value is represented as `<validated-byte-derived>`. Omission is legal only after each side independently recomputes and validates the exact value against its own artifact and verifies all links and physical ceilings.

### 5. Checkpoint registry, directories, and manifests

| Exact location | Projection | Retained invariant |
| --- | --- | --- |
| `organism.latest_stable_checkpoint_id` | `CP(organism.lineage_generation, organism.latest_stable_event_sequence)` when non-null | status, pending state, lineage, event boundary, and all other organism fields exact |
| `checkpoint_registry.checkpoint_id` | `CP(row.lineage_generation, row.event_sequence)` | one row per semantic boundary; equal ordered boundary set |
| `checkpoint_registry.manifest_sha256` | `<validated-byte-derived>` | equals SHA-256 of that run's canonical manifest bytes |
| `checkpoint_registry.database_sha256` | `<validated-byte-derived>` | equals SHA-256 of that run's database artifact |
| `checkpoint_registry.database_size_bytes` | `<validated-byte-derived>` | equals actual database length and obeys artifact ceiling |
| checkpoint directory basename | `CP(manifest.lineage_generation, manifest.event_sequence)` | directory is safe, unique, bijective with registry row and manifest |
| checkpoint manifest `checkpoint_id` | `CP(manifest.lineage_generation, manifest.event_sequence)` | manifest/registry semantic boundary exact |
| checkpoint manifest `database_sha256` | `<validated-byte-derived>` | independently recomputed |
| checkpoint manifest `database_size_bytes` | `<validated-byte-derived>` | independently measured |
| checkpoint manifest `schema_version` | `<schema-version>` | every other manifest field exact |

Creation/registration times, lifecycle number, contract/environment/budget versions, provenance, protection, snapshot method, implementation version, filename, status, and every other manifest/registry field compare exactly.

### 6. Exact canonical event projection

Only the following event-type and top-level JSON-path combinations are projected. Every other event payload location compares exactly.

| Event type | Exact payload path | Projection |
| --- | --- | --- |
| `checkpoint_stabilized` | `checkpoint_id` | `CP(event.lineage_generation, payload.event_sequence)` |
| `maintenance_entered` | `checkpoint_id` when `checkpoint_event_sequence` is present | `CP(event.lineage_generation, payload.checkpoint_event_sequence)` |
| `checkpoint_registration_repaired` | `checkpoint_id` | `CP(payload.lineage_generation, payload.event_sequence)` |
| `checkpoint_registration_repaired` | `previous_latest_stable_checkpoint_id` | null stays null; otherwise `CP(payload.lineage_generation, payload.previous_latest_stable_event_sequence)` |
| `checkpoint_registration_repaired` | `database_sha256`, `manifest_sha256`, `database_size_bytes`, `checkpoint_store_bytes` | `<validated-byte-derived>` |
| `checkpoint_pruned` | `latest_stable_checkpoint_id` | `CP(event.lineage_generation, payload.latest_stable_event_sequence)` |
| `checkpoint_pruned` | `pruned_checkpoint_id` | `CP(payload.pruned_lineage_generation, payload.pruned_event_sequence)` |
| `checkpoint_pruned` | `pruned_artifact_size_bytes`, `pruned_database_size_bytes`, `retained_checkpoint_store_bytes` | `<validated-byte-derived>` |
| `checkpoint_retention_failed` | `candidate_checkpoint_id` | `CP(event.lineage_generation, payload.candidate_event_sequence)` |
| `checkpoint_retention_failed` | `latest_stable_checkpoint_id` | `CP(event.lineage_generation, payload.latest_stable_event_sequence)` |
| `checkpoint_retention_failed` | `staging_directory` when present | `STAGE(CP(event.lineage_generation, payload.candidate_event_sequence))` |
| `checkpoint_retention_failed` | `checkpoint_store_bytes` | `<validated-byte-derived>` |
| `checkpoint_retention_cleanup_reconciliation_pending` | `checkpoint_ids[*]` | elementwise semantic boundaries proved from each staged manifest, preserving list order |
| `checkpoint_retention_cleanup_reconciliation_pending` | `staging_directories[*]` | elementwise `STAGE` tokens for the same ordered boundaries |
| `checkpoint_retention_cleanup_reconciled` | `removed_staging_directories[*]` | elementwise `STAGE` tokens from the referenced pending reconciliation event |
| `rollback_started` | `latest_stable_checkpoint_id` | `CP(event.lineage_generation, payload.latest_stable_event_sequence)` |
| `rollback_started` | `selected_checkpoint_id` | `CP(payload.selected_checkpoint_lineage_generation, payload.selected_checkpoint_event_sequence)` |
| `rollback_started` | `archive_id` | `RA(payload.pre_rollback_lineage_generation, payload.pre_rollback_event_sequence, payload.selected_checkpoint_event_sequence)` |
| `rollback_started` | `archive_database_sha256`, `archive_manifest_sha256`, `selected_checkpoint_database_sha256`, `selected_checkpoint_manifest_sha256` | `<validated-byte-derived>` |
| `rollback_lineage_prepared` | `selected_checkpoint_id` | `CP(payload.selected_checkpoint_lineage_generation, payload.selected_checkpoint_event_sequence)` |
| `rollback_lineage_prepared` | `archive_id` | `RA(payload.abandoned_lineage_generation, payload.abandoned_event_sequence, payload.selected_checkpoint_event_sequence)` |
| `rollback_lineage_prepared` | `source_restore_candidate_id` | `RC(payload.abandoned_lineage_generation, payload.rollback_started_event_sequence, payload.selected_checkpoint_event_sequence)` |
| `rollback_lineage_prepared` | `archive_database_sha256`, `archive_manifest_sha256`, `selected_checkpoint_database_sha256`, `selected_checkpoint_manifest_sha256`, `source_restore_candidate_database_sha256`, `source_restore_candidate_manifest_sha256` | `<validated-byte-derived>` |
| `rollback_completed` | `selected_checkpoint_id` | `CP(payload.selected_checkpoint_lineage_generation, payload.selected_checkpoint_event_sequence)` |
| `rollback_completed` | `archive_id` | `RA(payload.abandoned_lineage_generation, payload.abandoned_event_sequence, payload.selected_checkpoint_event_sequence)` |
| `rollback_completed` | `source_restore_candidate_id` | `RC(payload.abandoned_lineage_generation, payload.rollback_started_event_sequence, payload.selected_checkpoint_event_sequence)` |
| `rollback_completed` | `transformed_candidate_id` | `TC(payload.new_lineage_generation, payload.restoration_event_sequence)` |
| `rollback_completed` | `archive_database_sha256`, `archive_manifest_sha256`, `selected_checkpoint_database_sha256`, `selected_checkpoint_manifest_sha256`, `source_restore_candidate_database_sha256`, `source_restore_candidate_manifest_sha256`, `transformed_candidate_database_sha256`, `transformed_candidate_manifest_sha256` | `<validated-byte-derived>` |

The `rollback_lineage_prepared` protected payload schema contains exactly the six digest paths listed in its final row. The implementation must reject any extra path and must not use a suffix matcher.

### 7. Rollback artifact projection

| Artifact kind and exact manifest fields | Projection |
| --- | --- |
| pre-rollback archive directory and `archive_id` | `RA(active_lineage_generation, active_event_sequence, selected_checkpoint_event_sequence)` |
| pre-rollback archive `latest_stable_checkpoint_id` | `CP(active_lineage_generation, latest_stable_event_sequence)` |
| pre-rollback archive `selected_checkpoint_id` | `CP(selected_checkpoint_lineage_generation, selected_checkpoint_event_sequence)` |
| pre-rollback archive database/manifest SHA and database/selected-checkpoint size/SHA fields | `<validated-byte-derived>` |
| restore-candidate directory and `candidate_id` | `RC(active_lineage_generation, rollback_started_event_sequence, source_event_sequence)` |
| restore-candidate `archive_id` | matching `RA` token |
| restore-candidate `selected_checkpoint_id` | matching `CP` token |
| restore-candidate source-checkpoint, archive, candidate database/manifest SHA and size fields | `<validated-byte-derived>` |
| transformed-candidate directory and `transformed_candidate_id` | `TC(new_lineage_generation, restoration_event_sequence)` |
| transformed-candidate `source_restore_candidate_id`, `archive_id`, `selected_checkpoint_id` | matching `RC`, `RA`, and `CP` tokens |
| transformed-candidate source/archive/selected/transformed database/manifest SHA and size fields | `<validated-byte-derived>` |
| transformed candidate's embedded `organism.latest_stable_checkpoint_id` and restored `checkpoint_registry` identity fields | the checkpoint rules in section 5 |

Every artifact first passes safe-directory checks, exact entry set, SQLite integrity/foreign-key checks, protected schema validation, canonical manifest validation, digest and size recomputation, and one-to-one linkage to its semantic source boundary.

### 8. Export and noncanonical result treatment

Administrative result objects, CLI report wrappers, filesystem paths, raw artifact bytes, raw manifest bytes, and their presentation-level sizes/digests are not compared as canonical cross-run state.

Event export is compared semantically:

- exported event records are parsed and projected by sections 3 and 6
- export manifest `source_checkpoint_id` becomes the corresponding `CP` token
- export path, raw export bytes, export SHA, and export size are excluded from cross-run equality only after each side independently validates canonical JSONL, exact event range/count/order, source checkpoint linkage, and its own measured size/digest

No noncanonical exclusion may alter canonical organism state or hide an additional/missing event.

### 9. Physical accounting and paired-scenario scope

Schema-v2 has legitimate structural byte overhead. `phase1-projection-v2` therefore does not claim identical byte-threshold decisions at a physical ceiling.

For paired semantic scenarios:

- each requested operation must be independently admitted by both runs
- after admission, status, lifecycle, failure, maintenance, event order, selected semantic boundary, retention count, rollback eligibility, and authority must compare exactly
- byte totals listed in sections 5–8 are projected only after independent validation

Separate protected physical tests must prove:

- schema-v2-zero active database overhead over its paired schema-v1 state is at most 256 KiB
- each schema-v2-zero checkpoint/archive/candidate database overhead over its paired schema-v1 artifact is at most 256 KiB
- aggregate schema-v2-zero additional manifest/directory metadata across the retained working set is at most 1 MiB
- schema-v2-zero independently obeys the absolute 8 MiB active database, 8 MiB artifact, 40 MiB checkpoint store, 64 MiB working set, and 1 MiB next-wake reserve limits
- real near-ceiling checkpoint, repair, retention, rollback, and reserve scenarios fail or proceed according to the accepted absolute limits without partial canonical mutation

These overhead caps are implementation acceptance limits, not new spending authority.

### 10. Strict zero-caregiver absence

Under `phase2-zero-caregiver-v1`:

- the protected `consultation_configuration` singleton exists and is exact
- all operational consultation tables are empty
- operational AUTOINCREMENT consultation tables have no `sqlite_sequence` entry
- no consultation event, source, cost, adapter invocation, terminal outcome, disposition, or caregiver-derived effect exists
- no Phase 2 fixture or caregiver runtime module is imported or invoked by a zero-caregiver run

### 11. Anti-regression requirements

Protected tests must reject:

- an allowed value moved to another event type, key, nested path, list position, table, or column
- a wildcard, recursive walk, suffix match, prefix match, or global key-name normalizer
- an added or missing key at an allowed event
- a corrupted projected-away SHA or size
- duplicate or missing semantic boundaries
- a manifest, directory, registry row, event, or rollback object linked to the wrong token
- an unrelated original field difference
- unknown, missing, duplicate, mixed, or mutated consultation configuration
- zero-caregiver consultation rows, sequences, events, imports, or effects

The oracle implementation must be a closed typed map whose accepted locations are independently asserted by tests.

## Consequences

Positive:

- the zero-caregiver oracle is implementable and independently reconstructable
- Phase 1 budget configuration remains truly frozen
- checkpoint, repair, retention, rollback, and export byte differences are acknowledged without weakening semantic equality
- projected-away values remain protected by per-side integrity and physical-budget validation
- no wildcard normalization can hide a regression

Negative:

- the projection is larger than the original design expected
- checkpoint and rollback byte identity cannot serve as the paired control
- physical-threshold behavior requires dedicated absolute-limit tests rather than cross-version byte equality
- implementation must maintain an exact-location map as Phase 1 artifact formats evolve

## Scope

This ADR changes only consultation-configuration placement and the zero-caregiver semantic artifact oracle. It does not change caregiver authority, transaction boundaries, request/dispatch/ingress/disposition behavior, logical consultation budgets, expiry, lineage epochs, absolute storage ceilings, or explicit exclusions.

Slice 36 remains blocked until this ADR, the synchronized protocol/matrix/continuity updates, and PR #64 are accepted and merged.
