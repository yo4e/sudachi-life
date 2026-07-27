"""Public checkpoint-retention API with protected working-set admission."""

from .checkpoint_retention_prune import (
    enforce_checkpoint_retention as _enforce_checkpoint_retention,
)
from .checkpoint_retention_reconcile import reconcile_checkpoint_retention_staging
from .checkpoint_retention_types import CheckpointRetentionReconciliationResult
from .errors import CheckpointError, SchemaValidationError
from .runtime_storage import ensure_runtime_working_set_within_limit


def enforce_checkpoint_retention(
    paths,
    *,
    latest_checkpoint_id: str,
    latest_event_sequence: int,
    wall_time_utc_us: int,
    protected_test_retention_failure_after_stage: bool = False,
    protected_test_retention_cleanup_failure_after_commit: bool = False,
) -> None:
    """Prune only after the current protected working set is admissible."""

    try:
        ensure_runtime_working_set_within_limit(
            paths,
            context="checkpoint retention admission",
        )
    except SchemaValidationError as exc:
        raise CheckpointError(str(exc)) from exc
    _enforce_checkpoint_retention(
        paths,
        latest_checkpoint_id=latest_checkpoint_id,
        latest_event_sequence=latest_event_sequence,
        wall_time_utc_us=wall_time_utc_us,
        protected_test_retention_failure_after_stage=(
            protected_test_retention_failure_after_stage
        ),
        protected_test_retention_cleanup_failure_after_commit=(
            protected_test_retention_cleanup_failure_after_commit
        ),
    )


__all__ = [
    "CheckpointRetentionReconciliationResult",
    "enforce_checkpoint_retention",
    "reconcile_checkpoint_retention_staging",
]
