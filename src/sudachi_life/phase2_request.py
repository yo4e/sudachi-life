"""Public request-construction surface with exact protocol validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import phase2_request_impl as _impl
from .errors import SchemaValidationError
from .phase2_protocol import canonical_json_bytes, validate_request_envelope


for _name, _value in vars(_impl).items():
    if not _name.startswith("__"):
        globals()[_name] = _value


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

    return _impl.maybe_create_fixture_request(
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
