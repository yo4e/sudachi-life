"""Protected Phase 1 constants from Contract v0.2 and ADRs 0001-0006."""

from __future__ import annotations

from dataclasses import asdict, dataclass

CONTRACT_VERSION = "0.2"
SCHEMA_VERSION = 1
ENVIRONMENT_VERSION = "seed-garden-v1"
BUDGET_CONFIG_VERSION = "phase1-v1"
CHECKPOINT_FORMAT_VERSION = 1
DEVELOPMENTAL_STAGE = "seed"

ACTIVE_DATABASE_MAX_BYTES = 8 * 1024 * 1024
CHECKPOINT_ARTIFACT_MAX_BYTES = 8 * 1024 * 1024
CHECKPOINT_STORE_MAX_BYTES = 40 * 1024 * 1024
RUNTIME_WORKING_SET_MAX_BYTES = 64 * 1024 * 1024
CHECKPOINT_RETENTION_LIMIT = 4
CONSECUTIVE_FAILURE_LIMIT = 3
MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT = "consecutive_failure_limit_reached"


@dataclass(frozen=True, slots=True)
class Phase1BudgetConfig:
    """The accepted protected Phase 1 budget defaults."""

    input_events: int = 1
    observations: int = 1
    action_attempts: int = 1
    environment_mutations: int = 1
    caregiver_consultations: int = 0
    network_calls: int = 0
    subprocess_calls: int = 0
    external_mutable_writes: int = 0
    lifecycle_steps: int = 12
    canonical_records: int = 16
    lifecycle_wall_time_ms: int = 2_000
    cleanup_grace_ms: int = 250
    checkpoint_wall_time_ms: int = 5_000
    active_database_max_bytes: int = ACTIVE_DATABASE_MAX_BYTES
    checkpoint_artifact_max_bytes: int = CHECKPOINT_ARTIFACT_MAX_BYTES
    checkpoint_store_max_bytes: int = CHECKPOINT_STORE_MAX_BYTES
    runtime_working_set_max_bytes: int = RUNTIME_WORKING_SET_MAX_BYTES
    checkpoint_retention_limit: int = CHECKPOINT_RETENTION_LIMIT
    consecutive_failure_limit: int = CONSECUTIVE_FAILURE_LIMIT

    def as_dict(self) -> dict[str, int]:
        return asdict(self)


PHASE1_BUDGETS = Phase1BudgetConfig()
