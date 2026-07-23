from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from sudachi_life.checkpoints import validate_checkpoint_directory
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import WakeResult, perform_first_water_wake
from sudachi_life.organism import initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import connect_database, read_status


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _wake_clock() -> FakeClock:
    return FakeClock(
        [
            ClockReading(300, 10_000_000),
            ClockReading(300, 15_000_000),
            ClockReading(301, 20_000_000),
            ClockReading(302, 30_000_000),
            ClockReading(303, 40_000_000),
        ]
    )


def _run_first_wake(runtime_root: Path) -> tuple[OrganismPaths, WakeResult]:
    initial, _ = initialize_organism(
        runtime_root,
        "sudachi-0",
        clock=FakeClock.fixed(wall_time_utc_us=100, monotonic_ns=1_000_000),
    )
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    enqueue_garden_tick(
        paths,
        "repeated-run-tick",
        clock=FakeClock([ClockReading(200, 2_000_000)]),
    )
    clock = _wake_clock()
    result = perform_first_water_wake(
        runtime_root,
        initial.organism_id,
        seed=7,
        clock=clock,
    )
    assert clock.read_count == 5
    return paths, result


def _quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def _canonical_projection(database: Path) -> dict[str, Any]:
    connection = connect_database(database, read_only=True)
    try:
        schema = [
            tuple(row)
            for row in connection.execute(
                """
                SELECT type, name, tbl_name, sql
                FROM sqlite_master
                WHERE name NOT LIKE 'sqlite_%'
                ORDER BY type, name
                """
            ).fetchall()
        ]
        table_names = [
            str(row[0])
            for row in connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
                """
            ).fetchall()
        ]
        tables: dict[str, list[tuple[Any, ...]]] = {}
        for table_name in table_names:
            quoted_table = _quote_identifier(table_name)
            columns = [
                str(row[1])
                for row in connection.execute(
                    f"PRAGMA table_info({quoted_table})"
                ).fetchall()
            ]
            quoted_columns = ", ".join(_quote_identifier(column) for column in columns)
            rows = connection.execute(
                f"SELECT {quoted_columns} FROM {quoted_table} ORDER BY {quoted_columns}"
            ).fetchall()
            tables[table_name] = [tuple(row) for row in rows]

        sqlite_sequence = [
            tuple(row)
            for row in connection.execute(
                "SELECT name, seq FROM sqlite_sequence ORDER BY name"
            ).fetchall()
        ]
        return {
            "schema": schema,
            "tables": tables,
            "sqlite_sequence": sqlite_sequence,
            "user_version": int(connection.execute("PRAGMA user_version").fetchone()[0]),
        }
    finally:
        connection.close()


def _checkpoint_store_projection(checkpoints_dir: Path) -> dict[str, tuple[int, str]]:
    return {
        path.relative_to(checkpoints_dir).as_posix(): (
            path.stat().st_size,
            _sha256_file(path),
        )
        for path in sorted(checkpoints_dir.rglob("*"))
        if path.is_file()
    }


def test_identical_declared_inputs_produce_exact_first_wake_results(tmp_path: Path) -> None:
    paths_one, result_one = _run_first_wake(tmp_path / "run-one")
    paths_two, result_two = _run_first_wake(tmp_path / "run-two")

    assert result_one.as_dict() == result_two.as_dict()
    assert read_status(paths_one).as_dict() == read_status(paths_two).as_dict()

    assert result_one.checkpoint.checkpoint_id == result_two.checkpoint.checkpoint_id
    assert result_one.checkpoint.database_sha256 == result_two.checkpoint.database_sha256
    assert result_one.checkpoint.manifest_sha256 == result_two.checkpoint.manifest_sha256
    assert result_one.checkpoint.database_size_bytes == result_two.checkpoint.database_size_bytes
    assert result_one.checkpoint.event_sequence == result_two.checkpoint.event_sequence == 13
    assert result_one.checkpoint.lineage_generation == result_two.checkpoint.lineage_generation == 0

    manifest_one = validate_checkpoint_directory(result_one.checkpoint.checkpoint_dir)
    manifest_two = validate_checkpoint_directory(result_two.checkpoint.checkpoint_dir)
    assert manifest_one == manifest_two

    checkpoint_database_one = result_one.checkpoint.checkpoint_dir / "organism.sqlite3"
    checkpoint_database_two = result_two.checkpoint.checkpoint_dir / "organism.sqlite3"
    assert _sha256_file(checkpoint_database_one) == _sha256_file(checkpoint_database_two)
    assert _canonical_projection(checkpoint_database_one) == _canonical_projection(
        checkpoint_database_two
    )

    assert _sha256_file(paths_one.database) == _sha256_file(paths_two.database)
    assert _canonical_projection(paths_one.database) == _canonical_projection(
        paths_two.database
    )
    assert _checkpoint_store_projection(paths_one.checkpoints) == (
        _checkpoint_store_projection(paths_two.checkpoints)
    )

    second_one = enqueue_garden_tick(
        paths_one,
        "repeated-run-next-tick",
        clock=FakeClock([ClockReading(400, 50_000_000)]),
    )
    second_two = enqueue_garden_tick(
        paths_two,
        "repeated-run-next-tick",
        clock=FakeClock([ClockReading(400, 50_000_000)]),
    )
    assert second_one.as_dict() == second_two.as_dict()
    assert _sha256_file(paths_one.database) == _sha256_file(paths_two.database)
    assert _canonical_projection(paths_one.database) == _canonical_projection(
        paths_two.database
    )
