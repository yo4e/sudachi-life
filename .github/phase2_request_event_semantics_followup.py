from __future__ import annotations

from pathlib import Path

TEST = Path("tests/test_phase2_implementation_audit_repairs.py")
test = TEST.read_text(encoding="utf-8")

old_expectation = '''        "request event does not match",
'''
new_expectation = '''        "request event",
'''
if old_expectation not in test:
    raise SystemExit("existing request-event mismatch expectation was not found")
test = test.replace(old_expectation, new_expectation, 1)

missing_parameter = '''        ("missing", None),
'''
if missing_parameter not in test:
    raise SystemExit("generated missing-event parameter was not found")
test = test.replace(missing_parameter, "", 1)

marker = "def test_dispatch_rejects_missing_request_created_event_before_clock("
if marker in test:
    raise SystemExit("missing-event regression already exists")

test += r'''


def _relink_checkpoint_registry_without_active_validation(
    paths,
    checkpoint_id: str,
    checkpoint_dir: Path,
) -> None:
    database_path = checkpoint_dir / "organism.sqlite3"
    manifest_path = checkpoint_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["database_sha256"] = hashlib.sha256(database_path.read_bytes()).hexdigest()
    manifest["database_size_bytes"] = database_path.stat().st_size
    _write_manifest(checkpoint_dir, manifest)

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
        connection.commit()
    finally:
        connection.close()


def test_dispatch_rejects_missing_request_created_event_before_clock(
    tmp_path: Path,
) -> None:
    root, paths, wake = _init_request(
        tmp_path,
        organism_id="audit-request-event-missing",
    )
    request_id = wake.consultation_request.request_id
    status = read_status(paths)
    checkpoint_dir = paths.checkpoints / status.latest_stable_checkpoint_id

    _rewrite_request_event_database(
        paths.database,
        request_id,
        mutation=None,
    )
    _rewrite_request_event_database(
        checkpoint_dir / "organism.sqlite3",
        request_id,
        mutation=None,
    )
    _relink_checkpoint_registry_without_active_validation(
        paths,
        status.latest_stable_checkpoint_id,
        checkpoint_dir,
    )

    no_clock = FakeClock([])
    with pytest.raises(DispatchAdmissionRejectedError, match="foreign-key errors"):
        admit_fixture_dispatch(
            root,
            paths.organism_id,
            request_id=request_id,
            fixture_case_id="valid-defer",
            clock=no_clock,
        )
    assert no_clock.read_count == 0
    assert _consultation_counts(paths) == (0, 0, 0, 0, 0)
'''

TEST.write_text(test, encoding="utf-8")
