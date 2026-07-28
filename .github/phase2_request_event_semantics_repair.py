from __future__ import annotations

from pathlib import Path

SOURCE = Path("src/sudachi_life/phase2_dispatch_runtime.py")
TEST = Path("tests/test_phase2_implementation_audit_repairs.py")

old = '''def _require_request_checkpoint_snapshot(
    active_connection: sqlite3.Connection,
    checkpoint_dir: Path,
    *,
    active_organism_id: str,
    request_row: sqlite3.Row,
    request_envelope: dict[str, object],
) -> None:
    request_id = str(request_envelope["request_id"])
    request_event_sequence = int(request_row["event_sequence"])
    snapshot = connect_database(checkpoint_dir / "organism.sqlite3", read_only=True)
    try:
        try:
            snapshot_row, snapshot_envelope = _load_request(snapshot, request_id)
        except DispatchAdmissionRejectedError as exc:
            raise DispatchAdmissionRejectedError(
                f"dispatch checkpoint request is invalid: {exc}"
            ) from exc
        if snapshot_envelope != request_envelope or dict(snapshot_row) != dict(request_row):
            raise DispatchAdmissionRejectedError(
                "dispatch checkpoint request row does not match active request"
            )

        active_event = active_connection.execute(
            "SELECT * FROM event WHERE event_sequence=?",
            (request_event_sequence,),
        ).fetchone()
        if active_event is None:
            raise DispatchAdmissionRejectedError(
                "dispatch active request event is missing"
            )
        if active_event["event_type"] != "consultation_request_created":
            raise DispatchAdmissionRejectedError(
                "dispatch active request event type mismatch"
            )
        if active_event["organism_id"] != active_organism_id:
            raise DispatchAdmissionRejectedError(
                "dispatch active request event organism mismatch"
            )

        snapshot_event = snapshot.execute(
            "SELECT * FROM event WHERE event_sequence=?",
            (request_event_sequence,),
        ).fetchone()
        if snapshot_event is None:
            raise DispatchAdmissionRejectedError(
                "dispatch checkpoint request event is missing"
            )
        if dict(snapshot_event) != dict(active_event):
            raise DispatchAdmissionRejectedError(
                "dispatch checkpoint request event does not match active event"
            )
    finally:
        snapshot.close()
'''

new = '''def _require_exact_request_created_event(
    event: sqlite3.Row,
    *,
    context: str,
    active_organism_id: str,
    request_row: sqlite3.Row,
    request_envelope: dict[str, object],
) -> None:
    expected = {
        "event_sequence": int(request_row["event_sequence"]),
        "organism_id": active_organism_id,
        "lineage_generation": int(request_row["lineage_generation"]),
        "lifecycle_number": int(request_row["lifecycle_number"]),
        "event_type": "consultation_request_created",
        "source": "organism:consultation.request",
        "payload_json": canonical_json_bytes(
            {
                "canonical_size_bytes": int(request_row["canonical_size_bytes"]),
                "request": request_envelope,
            }
        ).decode("utf-8"),
        "schema_version": PHASE2_SCHEMA_VERSION,
        "environment_version": ENVIRONMENT_VERSION,
        "budget_config_version": BUDGET_CONFIG_VERSION,
    }
    actual = {
        "event_sequence": int(event["event_sequence"]),
        "organism_id": event["organism_id"],
        "lineage_generation": int(event["lineage_generation"]),
        "lifecycle_number": int(event["lifecycle_number"]),
        "event_type": event["event_type"],
        "source": event["source"],
        "payload_json": event["payload_json"],
        "schema_version": int(event["schema_version"]),
        "environment_version": event["environment_version"],
        "budget_config_version": event["budget_config_version"],
    }
    if actual != expected:
        mismatches = sorted(
            field for field in expected if actual[field] != expected[field]
        )
        raise DispatchAdmissionRejectedError(
            f"{context} request event semantics mismatch: {mismatches!r}"
        )


def _require_request_checkpoint_snapshot(
    active_connection: sqlite3.Connection,
    checkpoint_dir: Path,
    *,
    active_organism_id: str,
    request_row: sqlite3.Row,
    request_envelope: dict[str, object],
) -> None:
    request_id = str(request_envelope["request_id"])
    request_event_sequence = int(request_row["event_sequence"])
    snapshot = connect_database(checkpoint_dir / "organism.sqlite3", read_only=True)
    try:
        try:
            snapshot_row, snapshot_envelope = _load_request(snapshot, request_id)
        except DispatchAdmissionRejectedError as exc:
            raise DispatchAdmissionRejectedError(
                f"dispatch checkpoint request is invalid: {exc}"
            ) from exc
        if snapshot_envelope != request_envelope or dict(snapshot_row) != dict(request_row):
            raise DispatchAdmissionRejectedError(
                "dispatch checkpoint request row does not match active request"
            )

        active_event = active_connection.execute(
            "SELECT * FROM event WHERE event_sequence=?",
            (request_event_sequence,),
        ).fetchone()
        if active_event is None:
            raise DispatchAdmissionRejectedError(
                "dispatch active request event is missing"
            )
        _require_exact_request_created_event(
            active_event,
            context="dispatch active",
            active_organism_id=active_organism_id,
            request_row=request_row,
            request_envelope=request_envelope,
        )

        snapshot_event = snapshot.execute(
            "SELECT * FROM event WHERE event_sequence=?",
            (request_event_sequence,),
        ).fetchone()
        if snapshot_event is None:
            raise DispatchAdmissionRejectedError(
                "dispatch checkpoint request event is missing"
            )
        _require_exact_request_created_event(
            snapshot_event,
            context="dispatch checkpoint",
            active_organism_id=active_organism_id,
            request_row=request_row,
            request_envelope=request_envelope,
        )
        if dict(snapshot_event) != dict(active_event):
            raise DispatchAdmissionRejectedError(
                "dispatch checkpoint request event does not match active event"
            )
    finally:
        snapshot.close()
'''

source = SOURCE.read_text(encoding="utf-8")
if old not in source:
    raise SystemExit("expected request-checkpoint helper block was not found")
SOURCE.write_text(source.replace(old, new, 1), encoding="utf-8")

marker = "def test_dispatch_rejects_coherent_request_event_semantic_mutation("
test = TEST.read_text(encoding="utf-8")
if marker in test:
    raise SystemExit("coherent event-semantic regression already exists")

test += r'''


def _rewrite_request_event_database(
    database_path: Path,
    request_id: str,
    *,
    mutation: tuple[str, object] | None,
) -> None:
    connection = connect_database(database_path)
    try:
        connection.execute("PRAGMA foreign_keys=OFF")
        connection.execute("BEGIN IMMEDIATE")
        trigger_sql = _drop_table_triggers(connection, ("event",))
        if mutation is None:
            connection.execute(
                "DELETE FROM event WHERE event_sequence=("
                "SELECT event_sequence FROM consultation_request WHERE request_id=?"
                ")",
                (request_id,),
            )
        else:
            column, value = mutation
            allowed_columns = {
                "payload_json",
                "source",
                "lineage_generation",
                "lifecycle_number",
                "schema_version",
                "environment_version",
                "budget_config_version",
                "event_type",
                "organism_id",
            }
            if column not in allowed_columns:
                raise AssertionError(column)
            connection.execute(
                f"UPDATE event SET {column}=? WHERE event_sequence=("
                "SELECT event_sequence FROM consultation_request WHERE request_id=?"
                ")",
                (value, request_id),
            )
        _restore_triggers(connection, trigger_sql)
        connection.commit()
    finally:
        connection.close()


@pytest.mark.parametrize(
    ("case", "mutation"),
    [
        ("payload", ("payload_json", "{}")),
        ("source", ("source", "caregiver:spoofed-authority")),
        ("lineage", ("lineage_generation", 99)),
        ("lifecycle", ("lifecycle_number", 99)),
        ("schema", ("schema_version", 1)),
        ("environment", ("environment_version", "spoofed-environment")),
        ("budget", ("budget_config_version", "spoofed-budget")),
        ("type", ("event_type", "consultation_request_corrupted")),
        ("organism", ("organism_id", "spoofed-organism")),
        ("missing", None),
    ],
)
def test_dispatch_rejects_coherent_request_event_semantic_mutation(
    tmp_path: Path,
    case: str,
    mutation: tuple[str, object] | None,
) -> None:
    root, paths, wake = _init_request(
        tmp_path,
        organism_id=f"audit-request-event-{case}",
    )
    request_id = wake.consultation_request.request_id
    status = read_status(paths)
    checkpoint_dir = paths.checkpoints / status.latest_stable_checkpoint_id

    _rewrite_request_event_database(
        paths.database,
        request_id,
        mutation=mutation,
    )
    _rewrite_request_event_database(
        checkpoint_dir / "organism.sqlite3",
        request_id,
        mutation=mutation,
    )
    _refresh_checkpoint_manifest_and_registry(
        paths,
        status.latest_stable_checkpoint_id,
    )

    _assert_dispatch_snapshot_rejection(
        root,
        paths,
        request_id,
        "request event",
    )
'''
TEST.write_text(test, encoding="utf-8")
