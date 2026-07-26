# Slice 36a: Schema-v2 genesis and protected consultation configuration

Status: **Implemented on draft PR #65; merge pending final CI and review**

Issue: #61

Accepted evidence scope:

- P2-A01–P2-A05
- P2-B01–P2-B12
- P2-C06–P2-C07 at genesis/configuration absence
- P2-O15 genesis active-database overhead

## Test-first evidence

The first Slice 36a commit added only `tests/test_phase2_genesis.py`.

GitHub Actions run 409 failed before runtime implementation with:

```text
ModuleNotFoundError: No module named 'sudachi_life.phase2_schema'
```

The failure artifact was retained. This established the missing schema-v2/configuration boundary before implementation.

The minimum implementation then made the original Phase 1 suite and the new genesis tests green. Later internal review added explicit regression and golden-profile tests before merge.

## Public initialization boundary

Schema-v1 remains the default and preserves the existing surface:

```python
initialize_organism(runtime_root, organism_id, clock=clock)
```

Schema-v2 requires both explicit declarations:

```python
initialize_organism(
    runtime_root,
    organism_id,
    clock=clock,
    schema_version=2,
    consultation_configuration_version="phase2-zero-caregiver-v1",
)
```

The CLI equivalent is:

```text
sudachi init ORGANISM_ID \
  --schema-version 2 \
  --consultation-config phase2-zero-caregiver-v1
```

Accepted configuration versions are exactly:

- `phase2-zero-caregiver-v1`
- `phase2-fixture-v1`

Schema-v1 rejects a consultation configuration. Schema-v2 rejects a missing or unknown configuration. Unsupported schema versions fail before organism-directory creation. No migration or downgrade command exists.

## Frozen Phase 1 state

Schema-v2 preserves:

- every original Phase 1 table and column
- the original `budget_config` singleton exactly as `phase1-v1`
- every original organism/event `budget_config_version` as `phase1-v1`
- the original action registry, seed garden, inventory, authority sources, and genesis event shape

The Phase 1 public status dictionary remains unchanged. Schema-v2 status adds only the non-Phase-1 key `consultation_configuration_version`.

A dedicated regression test preserves the prior Phase 1 validator behavior that accepts semantically equal, noncanonical JSON formatting in the frozen Phase 1 budget row. Schema-v2 requires canonical Phase 1 budget JSON as part of its stricter accepted profile without retroactively tightening schema-v1.

## Protected schema-v2 configuration

Schema-v2 adds exactly one protected singleton:

```sql
consultation_configuration(
    singleton_id,
    protocol_version,
    configuration_version,
    configuration_json
)
```

The row is exact, canonical, and immutable. The accepted zero-caregiver object sets every consultation allowance to zero. The accepted fixture object fixes the finite ADR 0008/0009 limits.

Independent golden tests hard-code both accepted objects instead of deriving expectations from implementation constants.

## Empty protected operational objects

Schema-v2 genesis creates these empty immutable tables:

- `consultation_request`
- `consultation_dispatch`
- `consultation_cost_charge`
- `consultation_cost_completion`
- `consultation_response`
- `consultation_proposal`
- `consultation_ingress_receipt`
- `consultation_disposition`
- `consultation_dispatch_terminal`

Every consultation table has protected update/delete abort guards. The schema also fixes foreign-key linkage, response-versus-terminal mutual exclusion, successful-response proposal admission, and cost-completion linkage before later slices may write rows.

The complete schema-v2 SQLite profile contains exactly 46 protected SQL objects:

- 19 tables
- 27 triggers

Normalized profile SHA-256:

```text
41ee900df99b3c1b44700e2de628d3151e907c8d0069f87098eb9fd72a3f6fec
```

Unknown mutable objects, changed protected SQL, missing guards, altered accepted configuration, and corrupted checkpoint configuration fail validation.

## Checkpoint boundary

Genesis produces a normal stable checkpoint. Checkpoint validation accepts schema version 1 or 2 only, verifies that manifest and snapshot schema versions match, then runs the version-specific exact protected-schema/configuration validator.

Schema-v2 checkpoint creation does not create consultation events or operational consultation rows.

## Zero-caregiver absence and overhead

At schema-v2 zero-caregiver genesis:

- every operational consultation table is empty
- no operational consultation `sqlite_sequence` entry exists
- no consultation event or source exists
- no fixture/caregiver runtime module is imported
- the active database remains within the accepted 256 KiB overhead cap over paired schema-v1 genesis
- the inherited 8 MiB active-database ceiling remains enforced

The complete checkpoint/repair/retention/rollback/export semantic projection remains Slice 36b scope.

## Explicit non-deliverables

Slice 36a does not implement:

- consultation request creation
- dispatch or charging
- fixture execution
- response/proposal ingress
- terminal reconciliation
- disposition wakes
- migration or downgrade
- live caregiver/API/human chat
- memory, skills, training, arbitrary code, network, subprocess, or continuous execution

## Next boundary

After PR #65 merges, Slice 36b implements the accepted `phase1-projection-v2` artifact oracle for P2-C01–P2-C05, P2-C08–P2-C18, and P2-O16–P2-O22. Slice 37 remains blocked until both Slice 36a and Slice 36b are merged and no blocker/high/medium boundary defect remains.
