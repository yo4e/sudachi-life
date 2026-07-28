"""Public ingress runtime with exact ADR 0016 lineage accounting."""

from __future__ import annotations

from . import phase2_ingress_runtime_impl as _impl


LOGICAL_PAYLOAD_LIMIT_BYTES = 64 * 1024


def _byte_count(value: object, *, context: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise _impl.IngressRejectedError(
            f"{context} byte count must be a nonnegative integer"
        )
    return value


def validate_lineage_payload_projection(
    current_request_bytes: object,
    current_success_package_bytes: object,
    candidate_success_package_bytes: object,
) -> int:
    """Return the exact projected logical payload or reject above 64 KiB."""

    request_bytes = _byte_count(
        current_request_bytes,
        context="current request payload",
    )
    package_bytes = _byte_count(
        current_success_package_bytes,
        context="current successful package payload",
    )
    candidate_bytes = _byte_count(
        candidate_success_package_bytes,
        context="candidate successful package payload",
    )
    projected = request_bytes + package_bytes + candidate_bytes
    if projected > LOGICAL_PAYLOAD_LIMIT_BYTES:
        raise _impl.IngressRejectedError(
            "current lineage logical consultation payload exceeds 64 KiB"
        )
    return projected


def _require_logical_payload_capacity(
    connection,
    *,
    organism_id: str,
    lineage_generation: int,
    new_package_bytes: int,
) -> None:
    request_bytes = int(
        connection.execute(
            "SELECT COALESCE(SUM(canonical_size_bytes), 0) FROM consultation_request "
            "WHERE organism_id=? AND lineage_generation=?",
            (organism_id, lineage_generation),
        ).fetchone()[0]
    )
    package_bytes = int(
        connection.execute(
            "SELECT COALESCE(SUM(r.measured_package_bytes), 0) "
            "FROM consultation_ingress_receipt r "
            "JOIN consultation_request q ON q.request_id=r.request_id "
            "WHERE q.organism_id=? AND q.lineage_generation=?",
            (organism_id, lineage_generation),
        ).fetchone()[0]
    )
    validate_lineage_payload_projection(
        request_bytes,
        package_bytes,
        new_package_bytes,
    )


def _require_common_state(
    connection,
    paths,
    *,
    organism,
    request: dict[str, object],
    dispatch: dict[str, object],
) -> None:
    """Admit exact stable sleeping or maintenance evidence-recording states."""

    if int(organism["schema_version"]) != _impl.PHASE2_SCHEMA_VERSION:
        raise _impl.IngressRejectedError("consultation ingress requires schema-v2")
    status = organism["status"]
    maintenance_reason = organism["maintenance_reason"]
    if status not in {"sleeping", "maintenance_required"} or bool(
        organism["checkpoint_pending"]
    ):
        raise _impl.IngressRejectedError(
            "consultation ingress requires a stable sleeping or maintenance state "
            "with no pending checkpoint"
        )
    if status == "sleeping" and maintenance_reason is not None:
        raise _impl.IngressRejectedError(
            "sleeping consultation ingress has an unexpected maintenance reason"
        )
    if status == "maintenance_required" and maintenance_reason is None:
        raise _impl.IngressRejectedError(
            "maintenance consultation ingress is missing its reason"
        )
    if request["configuration_version"] != _impl.FIXTURE_CONFIGURATION_VERSION:
        raise _impl.IngressRejectedError(
            "consultation ingress requires fixture configuration"
        )
    if int(request["lineage_generation"]) != int(organism["lineage_generation"]):
        raise _impl.IngressRejectedError(
            "consultation work is not in the current lineage"
        )
    if dispatch["lineage_generation"] != request["lineage_generation"]:
        raise _impl.IngressRejectedError("dispatch lineage does not match request")
    if dispatch["organism_id"] != organism["organism_id"]:
        raise _impl.IngressRejectedError(
            "dispatch organism does not match canonical organism"
        )
    if dispatch["request_id"] != request["request_id"]:
        raise _impl.IngressRejectedError("dispatch request linkage does not match")
    _impl.ensure_active_database_within_limit(
        connection,
        context="consultation ingress preflight",
    )
    _impl.ensure_active_database_has_wake_reserve(
        connection,
        context="consultation ingress preflight",
    )
    _impl.ensure_checkpoint_store_within_limit(
        paths,
        context="consultation ingress preflight",
    )
    _impl.ensure_runtime_working_set_within_limit(
        paths,
        context="consultation ingress preflight",
    )


_impl._require_logical_payload_capacity = _require_logical_payload_capacity
_impl._require_common_state = _require_common_state

for _name, _value in vars(_impl).items():
    if not _name.startswith("__"):
        globals()[_name] = _value

# Restore the public helpers after re-exporting implementation globals.
globals()["validate_lineage_payload_projection"] = validate_lineage_payload_projection
globals()["LOGICAL_PAYLOAD_LIMIT_BYTES"] = LOGICAL_PAYLOAD_LIMIT_BYTES

__all__ = [
    *_impl.__all__,
    "LOGICAL_PAYLOAD_LIMIT_BYTES",
    "validate_lineage_payload_projection",
]
