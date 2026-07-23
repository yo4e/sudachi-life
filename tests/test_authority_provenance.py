from __future__ import annotations

import json
from pathlib import Path
import re

import pytest

from sudachi_life.authority import (
    ADMINISTRATION,
    ORGANISM,
    AuthorityProvenanceError,
    build_authority_report,
    classify_authority_source,
)
from sudachi_life.cli import _command_report_authority, build_parser, main
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import connect_database, read_status


def _canonical_authority_rows(paths: OrganismPaths) -> tuple[tuple[object, ...], ...]:
    connection = connect_database(paths.database, read_only=True)
    try:
        return tuple(
            tuple(row)
            for row in connection.execute(
                "SELECT event_sequence, event_type, source FROM event ORDER BY event_sequence"
            ).fetchall()
        ) + tuple(
            tuple(row)
            for row in connection.execute(
                "SELECT inbox_id, event_type, source FROM inbox_event ORDER BY inbox_id"
            ).fetchall()
        )
    finally:
        connection.close()


def test_untrusted_administrative_source_rejects_before_clock_or_state(initialized) -> None:
    runtime_root, initial, _genesis = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    baseline_status = read_status(paths).as_dict()
    baseline_rows = _canonical_authority_rows(paths)

    for index, source in enumerate(("", "unknown:cli", "organism:phase1-fixed-policy"), 1):
        clock = FakeClock([ClockReading(100 + index, 1_000_000 + index)])
        with pytest.raises(AuthorityProvenanceError):
            enqueue_garden_tick(
                paths,
                f"slice-35-invalid-source-{index}",
                source=source,
                clock=clock,
            )
        assert clock.read_count == 0
        assert read_status(paths).as_dict() == baseline_status
        assert _canonical_authority_rows(paths) == baseline_rows


def test_phase1_events_and_command_reports_distinguish_authority(
    initialized,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    runtime_root, initial, _genesis = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)

    enqueue_garden_tick(
        paths,
        "slice-35-authority-tick",
        source="administration:experiment-harness",
        clock=FakeClock([ClockReading(200, 2_000_000)]),
    )
    wake_clock = FakeClock(
        [
            ClockReading(300, 10_000_000),
            ClockReading(300, 15_000_000),
            ClockReading(301, 20_000_000),
            ClockReading(302, 30_000_000),
            ClockReading(303, 40_000_000),
        ]
    )
    result = perform_garden_wake(
        runtime_root,
        initial.organism_id,
        seed=35,
        clock=wake_clock,
    )
    assert result.status == "sleeping"
    assert wake_clock.read_count == 5

    connection = connect_database(paths.database, read_only=True)
    try:
        events = tuple(
            (str(row["event_type"]), str(row["source"]))
            for row in connection.execute(
                "SELECT event_type, source FROM event ORDER BY event_sequence"
            ).fetchall()
        )
        inbox_sources = tuple(
            str(row["source"])
            for row in connection.execute(
                "SELECT source FROM inbox_event ORDER BY inbox_id"
            ).fetchall()
        )
    finally:
        connection.close()

    classified_events = tuple(
        (event_type, classify_authority_source(source).category)
        for event_type, source in events
    )
    assert ("organism_initialized", ADMINISTRATION) in classified_events
    assert ("input_enqueued", ADMINISTRATION) in classified_events
    assert ("wake_accepted", ORGANISM) in classified_events
    assert ("action_completed", ORGANISM) in classified_events
    assert ("checkpoint_stabilized", ADMINISTRATION) in classified_events
    assert {category for _event_type, category in classified_events} == {
        ADMINISTRATION,
        ORGANISM,
    }
    assert all(classify_authority_source(source).category == ADMINISTRATION for source in inbox_sources)

    parser = build_parser()
    command_cases = (
        (["init", "sudachi-x"], ADMINISTRATION, "administration:init"),
        (
            ["enqueue", "sudachi-x", "synthetic:garden_tick", "--id", "tick-x"],
            ADMINISTRATION,
            "administration:cli",
        ),
        (["wake", "sudachi-x", "--seed", "1"], ORGANISM, "organism:phase1-fixed-policy"),
        (["status", "sudachi-x"], ADMINISTRATION, "administration:status"),
        (
            ["maintenance", "inspect", "sudachi-x"],
            ADMINISTRATION,
            "administration:maintenance-inspect",
        ),
        (
            ["maintenance", "clear", "sudachi-x", "--reason", "reviewed"],
            ADMINISTRATION,
            "administration:maintenance-clear",
        ),
        (
            ["checkpoint", "repair-pending", "sudachi-x"],
            ADMINISTRATION,
            "administration:checkpoint-repair",
        ),
        (
            ["export", "events", "sudachi-x", "--event-sequence", "2"],
            ADMINISTRATION,
            "administration:event-export",
        ),
        (
            ["rollback", "prepare", "sudachi-x", "--event-sequence", "2"],
            ADMINISTRATION,
            "administration:rollback-prepare",
        ),
        (
            ["rollback", "begin", "sudachi-x", "--archive-id", "archive-x"],
            ADMINISTRATION,
            "administration:rollback",
        ),
        (
            ["rollback", "build-candidate", "sudachi-x"],
            ADMINISTRATION,
            "administration:rollback-candidate",
        ),
        (
            [
                "rollback",
                "transform-candidate",
                "sudachi-x",
                "--candidate-id",
                "candidate-x",
                "--reason",
                "reviewed",
            ],
            ADMINISTRATION,
            "administration:rollback",
        ),
        (
            [
                "rollback",
                "replace-active",
                "sudachi-x",
                "--candidate-id",
                "candidate-x",
            ],
            ADMINISTRATION,
            "administration:rollback-replace",
        ),
        (
            ["rollback", "complete", "sudachi-x", "--candidate-id", "candidate-x"],
            ADMINISTRATION,
            "administration:rollback",
        ),
    )
    for argv, expected_category, expected_source in command_cases:
        provenance = _command_report_authority(parser.parse_args(argv))
        assert provenance.category == expected_category
        assert provenance.source == expected_source

    assert main(
        [
            "--runtime-dir",
            str(runtime_root),
            "status",
            initial.organism_id,
            "--json",
        ]
    ) == 0
    status_report = json.loads(capsys.readouterr().out)
    assert status_report["authority_category"] == ADMINISTRATION
    assert status_report["authority_source"] == "administration:status"

    source_root = Path(__file__).resolve().parents[1] / "src" / "sudachi_life"
    literal_sources = {
        match
        for source_path in source_root.glob("*.py")
        for match in re.findall(
            r"[\"']((?:organism|administration):[a-z0-9][a-z0-9._-]*)[\"']",
            source_path.read_text(encoding="utf-8"),
        )
    }
    assert "organism:phase1-fixed-policy" in literal_sources
    assert "administration:init" in literal_sources
    assert "administration:rollback" in literal_sources
    assert all(classify_authority_source(source).source == source for source in literal_sources)


def test_report_publication_rejects_unknown_cross_category_and_spoofed_authority() -> None:
    payload = {"status": "sleeping"}
    report = build_authority_report(
        payload,
        source="administration:status",
        expected_category=ADMINISTRATION,
    )
    assert report == {
        "authority_category": ADMINISTRATION,
        "authority_source": "administration:status",
        "status": "sleeping",
    }
    assert payload == {"status": "sleeping"}

    with pytest.raises(AuthorityProvenanceError):
        build_authority_report(
            payload,
            source="organism:phase1-fixed-policy",
            expected_category=ADMINISTRATION,
        )
    with pytest.raises(AuthorityProvenanceError):
        build_authority_report(
            payload,
            source="unknown:status",
            expected_category=ADMINISTRATION,
        )
    with pytest.raises(AuthorityProvenanceError):
        build_authority_report(
            {"authority_category": ORGANISM},
            source="administration:status",
            expected_category=ADMINISTRATION,
        )
