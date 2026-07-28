from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def replace_once(text: str, old: str, new: str, *, context: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{context}: expected one match, found {count}")
    return text.replace(old, new, 1)


def repair_runtime() -> None:
    path = ROOT / "src/sudachi_life/phase2_dispatch_runtime.py"
    text = path.read_text(encoding="utf-8")

    manifest_fields = '''
_CHECKPOINT_MANIFEST_FIELDS: Final = frozenset(
    {
        "budget_config_version",
        "checkpoint_format_version",
        "checkpoint_id",
        "contract_version",
        "creation_wall_time_utc_us",
        "database_filename",
        "database_sha256",
        "database_size_bytes",
        "environment_version",
        "event_sequence",
        "implementation_version",
        "lifecycle_number",
        "lineage_generation",
        "organism_id",
        "provenance",
        "schema_version",
        "snapshot_method",
        "status",
    }
)
'''
    text = replace_once(
        text,
        ")\n_FAULT_POINTS: Final = frozenset(",
        ")\n" + manifest_fields + "\n_FAULT_POINTS: Final = frozenset(",
        context="checkpoint manifest field constant",
    )

    helper = '''def _require_request_checkpoint_snapshot(
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
        snapshot_row, snapshot_envelope = _load_request(snapshot, request_id)
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
    text = replace_once(
        text,
        "def _require_admission_state(\n",
        helper + "def _require_admission_state(\n",
        context="checkpoint request snapshot helper",
    )

    old = '''    if manifest.get("checkpoint_id") != latest_checkpoint_id:
        raise DispatchAdmissionRejectedError("dispatch checkpoint manifest ID mismatch")
    if int(manifest.get("lineage_generation", -1)) != int(
        registry["lineage_generation"]
    ):
        raise DispatchAdmissionRejectedError("dispatch checkpoint manifest lineage mismatch")
    if int(manifest.get("event_sequence", -1)) != int(registry["event_sequence"]):
        raise DispatchAdmissionRejectedError("dispatch checkpoint manifest boundary mismatch")
    if manifest.get("database_sha256") != registry["database_sha256"]:
        raise DispatchAdmissionRejectedError("dispatch checkpoint database digest mismatch")
    if int(manifest.get("database_size_bytes", -1)) != int(
        registry["database_size_bytes"]
    ):
        raise DispatchAdmissionRejectedError("dispatch checkpoint database size mismatch")
    if manifest_sha != registry["manifest_sha256"]:
        raise DispatchAdmissionRejectedError("dispatch checkpoint manifest digest mismatch")
'''
    new = '''    manifest = _exact_fields(
        manifest,
        _CHECKPOINT_MANIFEST_FIELDS,
        context="dispatch checkpoint manifest",
    )
    active_organism_id = str(organism["organism_id"])
    if request_envelope["organism_id"] != active_organism_id:
        raise DispatchAdmissionRejectedError("dispatch request organism mismatch")
    if manifest["organism_id"] != active_organism_id:
        raise DispatchAdmissionRejectedError("dispatch checkpoint organism mismatch")
    if manifest["checkpoint_id"] != latest_checkpoint_id:
        raise DispatchAdmissionRejectedError("dispatch checkpoint manifest ID mismatch")
    if int(manifest["lineage_generation"]) != int(registry["lineage_generation"]):
        raise DispatchAdmissionRejectedError("dispatch checkpoint manifest lineage mismatch")
    if int(manifest["event_sequence"]) != int(registry["event_sequence"]):
        raise DispatchAdmissionRejectedError("dispatch checkpoint manifest boundary mismatch")
    if manifest["database_sha256"] != registry["database_sha256"]:
        raise DispatchAdmissionRejectedError("dispatch checkpoint database digest mismatch")
    if int(manifest["database_size_bytes"]) != int(registry["database_size_bytes"]):
        raise DispatchAdmissionRejectedError("dispatch checkpoint database size mismatch")
    if manifest_sha != registry["manifest_sha256"]:
        raise DispatchAdmissionRejectedError("dispatch checkpoint manifest digest mismatch")
    _require_request_checkpoint_snapshot(
        connection,
        checkpoint_dir,
        active_organism_id=active_organism_id,
        request_row=request_row,
        request_envelope=request_envelope,
    )
'''
    text = replace_once(
        text,
        old,
        new,
        context="checkpoint active linkage validation",
    )
    path.write_text(text, encoding="utf-8")


def repair_tests() -> None:
    path = ROOT / "tests/test_phase2_implementation_audit_repairs.py"
    text = path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "import json\nfrom pathlib import Path\n",
        "import json\nfrom pathlib import Path\nimport shutil\n",
        context="test shutil import",
    )

    addition = r'''


def _drop_table_triggers(connection, table_names: tuple[str, ...]) -> list[str]:
    placeholders = ",".join("?" for _ in table_names)
    rows = connection.execute(
        f"SELECT name, sql FROM sqlite_master WHERE type='trigger' "
        f"AND tbl_name IN ({placeholders}) ORDER BY name",
        table_names,
    ).fetchall()
    statements: list[str] = []
    for row in rows:
        if row["sql"] is None:
            raise AssertionError(f"trigger {row['name']} has no SQL")
        statements.append(str(row["sql"]))
        quoted = str(row["name"]).replace('"', '""')
        connection.execute(f'DROP TRIGGER "{quoted}"')
    return statements


def _restore_triggers(connection, statements: list[str]) -> None:
    for statement in statements:
        connection.execute(statement)


def _write_manifest(checkpoint_dir: Path, manifest: dict[str, object]) -> None:
    (checkpoint_dir / "manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def _relink_checkpoint_registry(paths, checkpoint_id: str, checkpoint_dir: Path) -> None:
    database_path = checkpoint_dir / "organism.sqlite3"
    manifest_path = checkpoint_dir / "manifest.json"
    connection = connect_database(paths.database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        trigger_sql = _drop_table_triggers(connection, ("checkpoint_registry",))
        connection.execute(
            "UPDATE checkpoint_registry SET manifest_sha256=?, database_sha256=?, "
            "database_size_bytes=? WHERE checkpoint_id=?",
            (
                hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                hashlib.sha256(database_path.read_bytes()).hexdigest(),
                database_path.stat().st_size,
                checkpoint_id,
            ),
        )
        _restore_triggers(connection, trigger_sql)
        validate_canonical_state(connection, expect_checkpoint_pending=False)
        connection.commit()
    finally:
        connection.close()


def _rewrite_snapshot(checkpoint_dir: Path, operation) -> None:
    connection = connect_database(checkpoint_dir / "organism.sqlite3")
    try:
        connection.execute("BEGIN IMMEDIATE")
        trigger_sql = _drop_table_triggers(
            connection,
            ("consultation_request", "event"),
        )
        operation(connection)
        _restore_triggers(connection, trigger_sql)
        connection.commit()
    finally:
        connection.close()


def _refresh_checkpoint_manifest_and_registry(paths, checkpoint_id: str) -> Path:
    checkpoint_dir = paths.checkpoints / checkpoint_id
    database_path = checkpoint_dir / "organism.sqlite3"
    manifest = json.loads(
        (checkpoint_dir / "manifest.json").read_text(encoding="utf-8")
    )
    manifest["database_sha256"] = hashlib.sha256(database_path.read_bytes()).hexdigest()
    manifest["database_size_bytes"] = database_path.stat().st_size
    _write_manifest(checkpoint_dir, manifest)
    _relink_checkpoint_registry(paths, checkpoint_id, checkpoint_dir)
    return checkpoint_dir


def _assert_dispatch_snapshot_rejection(root, paths, request_id: str, match: str) -> None:
    no_clock = FakeClock([])
    with pytest.raises(DispatchAdmissionRejectedError, match=match):
        admit_fixture_dispatch(
            root,
            paths.organism_id,
            request_id=request_id,
            fixture_case_id="valid-defer",
            clock=no_clock,
        )
    assert no_clock.read_count == 0
    assert _consultation_counts(paths) == (0, 0, 0, 0, 0)
    connection = connect_database(paths.database, read_only=True)
    try:
        assert int(
            connection.execute(
                "SELECT COUNT(*) FROM event WHERE event_type="
                "'consultation_dispatch_admitted'"
            ).fetchone()[0]
        ) == 0
    finally:
        connection.close()


def test_dispatch_rejects_coherently_linked_wrong_organism_checkpoint(
    tmp_path: Path,
) -> None:
    root_a, paths_a, wake_a = _init_request(
        tmp_path,
        organism_id="audit-checkpoint-owner-a",
    )
    _, paths_b, _ = _init_request(
        tmp_path,
        organism_id="audit-checkpoint-owner-b",
    )
    status_a = read_status(paths_a)
    status_b = read_status(paths_b)
    checkpoint_a = paths_a.checkpoints / status_a.latest_stable_checkpoint_id
    checkpoint_b = paths_b.checkpoints / status_b.latest_stable_checkpoint_id

    shutil.copy2(
        checkpoint_b / "organism.sqlite3",
        checkpoint_a / "organism.sqlite3",
    )
    manifest = json.loads(
        (checkpoint_b / "manifest.json").read_text(encoding="utf-8")
    )
    manifest["checkpoint_id"] = status_a.latest_stable_checkpoint_id
    _write_manifest(checkpoint_a, manifest)
    _relink_checkpoint_registry(
        paths_a,
        status_a.latest_stable_checkpoint_id,
        checkpoint_a,
    )

    _assert_dispatch_snapshot_rejection(
        root_a,
        paths_a,
        wake_a.consultation_request.request_id,
        "checkpoint organism mismatch",
    )


def test_dispatch_rejects_coherently_linked_extra_manifest_field(
    tmp_path: Path,
) -> None:
    root, paths, wake = _init_request(
        tmp_path,
        organism_id="audit-checkpoint-extra-field",
    )
    status = read_status(paths)
    checkpoint_dir = paths.checkpoints / status.latest_stable_checkpoint_id
    manifest = json.loads(
        (checkpoint_dir / "manifest.json").read_text(encoding="utf-8")
    )
    manifest["undeclared_field"] = "not-part-of-checkpoint-v1"
    _write_manifest(checkpoint_dir, manifest)
    _relink_checkpoint_registry(
        paths,
        status.latest_stable_checkpoint_id,
        checkpoint_dir,
    )

    _assert_dispatch_snapshot_rejection(
        root,
        paths,
        wake.consultation_request.request_id,
        "manifest field set mismatch",
    )


def test_dispatch_rejects_checkpoint_missing_exact_request_row(
    tmp_path: Path,
) -> None:
    root, paths, wake = _init_request(
        tmp_path,
        organism_id="audit-checkpoint-request-row",
    )
    status = read_status(paths)
    checkpoint_dir = paths.checkpoints / status.latest_stable_checkpoint_id
    request_id = wake.consultation_request.request_id
    _rewrite_snapshot(
        checkpoint_dir,
        lambda connection: connection.execute(
            "DELETE FROM consultation_request WHERE request_id=?",
            (request_id,),
        ),
    )
    _refresh_checkpoint_manifest_and_registry(
        paths,
        status.latest_stable_checkpoint_id,
    )

    _assert_dispatch_snapshot_rejection(
        root,
        paths,
        request_id,
        "checkpoint.*request",
    )


def test_dispatch_rejects_checkpoint_request_event_mismatch(
    tmp_path: Path,
) -> None:
    root, paths, wake = _init_request(
        tmp_path,
        organism_id="audit-checkpoint-request-event",
    )
    status = read_status(paths)
    checkpoint_dir = paths.checkpoints / status.latest_stable_checkpoint_id
    request_id = wake.consultation_request.request_id
    _rewrite_snapshot(
        checkpoint_dir,
        lambda connection: connection.execute(
            "UPDATE event SET payload_json='{}' WHERE event_sequence=("
            "SELECT event_sequence FROM consultation_request WHERE request_id=?"
            ")",
            (request_id,),
        ),
    )
    _refresh_checkpoint_manifest_and_registry(
        paths,
        status.latest_stable_checkpoint_id,
    )

    _assert_dispatch_snapshot_rejection(
        root,
        paths,
        request_id,
        "request event does not match",
    )
'''
    if "test_dispatch_rejects_coherently_linked_wrong_organism_checkpoint" in text:
        raise RuntimeError("focused Finding 4 tests already exist")
    path.write_text(text.rstrip() + addition + "\n", encoding="utf-8")


def main() -> None:
    repair_runtime()
    repair_tests()


if __name__ == "__main__":
    main()
