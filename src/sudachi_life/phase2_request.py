"""Public request-construction surface with exact protocol validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import phase2_request_impl as _impl
from .errors import SchemaValidationError
from .phase2_protocol import canonical_json_bytes, validate_request_envelope


LINEAGE_REQUEST_LIMIT_REFUSAL_REASON = (
    "consultation_request_not_created_lineage_request_limit"
)


for _name, _value in vars(_impl).items():
    if not _name.startswith("__"):
        globals()[_name] = _value


def _lineage_limit_refusal_if_exactly_eligible(
    connection,
    *,
    organism_id: str,
    lineage_generation: int,
    lifecycle_number: int,
    checkpoint_payload: dict[str, Any],
    budget_snapshot: dict[str, Any] | None,
):
    configuration_version, limits = _impl._configuration_limits(connection)
    if configuration_version != _impl.FIXTURE_CONFIGURATION_VERSION:
        return None
    if checkpoint_payload.get("final_status") == "maintenance_required":
        return None
    if budget_snapshot is None:
        return None

    decision, observation, _observation_event_sequence = _impl._current_lifecycle_payload(
        connection,
        lineage_generation=lineage_generation,
        lifecycle_number=lifecycle_number,
    )
    if decision.get("reason") != "no_applicable_action":
        return None
    if observation.get("objective_complete") is not False:
        return None

    request_count = int(
        connection.execute(
            "SELECT COUNT(*) FROM consultation_request "
            "WHERE organism_id=? AND lineage_generation=?",
            (organism_id, lineage_generation),
        ).fetchone()[0]
    )
    if request_count < int(limits["requests_per_lineage"]):
        return None
    if _impl._has_outstanding_request(
        connection,
        organism_id=organism_id,
        lineage_generation=lineage_generation,
        lifecycle_number=lifecycle_number,
    ):
        return None
    return _impl.ConsultationRequestResult(
        created=False,
        reason=LINEAGE_REQUEST_LIMIT_REFUSAL_REASON,
        request_id=None,
        event_sequence=None,
        canonical_size_bytes=None,
    )


def maybe_create_fixture_request(
    connection,
    *,
    runtime_root: Path,
    organism_id: str,
    lineage_generation: int,
    lifecycle_number: int,
    wall_time_utc_us: int,
    checkpoint_payload: dict[str, Any],
    budget_snapshot: dict[str, Any] | None,
    append_event,
    protected_test_reject_before_write: bool = False,
    protected_test_reject_after_write: bool = False,
):
    """Delegate request construction and validate exact bytes before event write."""

    def validating_append_event(event_connection, **event_arguments):
        if event_arguments.get("event_type") == "consultation_request_created":
            payload = event_arguments.get("payload")
            if not isinstance(payload, dict) or frozenset(payload) != frozenset(
                {"canonical_size_bytes", "request"}
            ):
                raise SchemaValidationError(
                    "request event payload field set is not exact"
                )
            envelope = validate_request_envelope(payload["request"])
            canonical_size = payload["canonical_size_bytes"]
            if (
                isinstance(canonical_size, bool)
                or not isinstance(canonical_size, int)
                or canonical_size != len(canonical_json_bytes(envelope))
            ):
                raise SchemaValidationError(
                    "request event canonical size does not match exact envelope bytes"
                )
        return append_event(event_connection, **event_arguments)

    result = _impl.maybe_create_fixture_request(
        connection,
        runtime_root=runtime_root,
        organism_id=organism_id,
        lineage_generation=lineage_generation,
        lifecycle_number=lifecycle_number,
        wall_time_utc_us=wall_time_utc_us,
        checkpoint_payload=checkpoint_payload,
        budget_snapshot=budget_snapshot,
        append_event=validating_append_event,
        protected_test_reject_before_write=protected_test_reject_before_write,
        protected_test_reject_after_write=protected_test_reject_after_write,
    )
    if result is not None:
        return result
    return _lineage_limit_refusal_if_exactly_eligible(
        connection,
        organism_id=organism_id,
        lineage_generation=lineage_generation,
        lifecycle_number=lifecycle_number,
        checkpoint_payload=checkpoint_payload,
        budget_snapshot=budget_snapshot,
    )
