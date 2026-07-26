from __future__ import annotations

import json
from pathlib import Path

from sudachi_life.clock import FakeClock
from sudachi_life.constants import PHASE1_BUDGETS
from sudachi_life.organism import initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import connect_database, read_status


def test_phase1_noncanonical_but_equal_budget_json_remains_supported(
    tmp_path: Path,
) -> None:
    runtime_root = tmp_path / "runtime"
    status, _ = initialize_organism(
        runtime_root,
        "phase1-budget",
        clock=FakeClock.fixed(
            wall_time_utc_us=1_700_000_000_000_000,
            monotonic_ns=10_000_000,
        ),
    )
    paths = OrganismPaths.build(runtime_root, status.organism_id)
    connection = connect_database(paths.database)
    try:
        connection.execute(
            "UPDATE budget_config SET config_json=? WHERE singleton_id=1",
            (json.dumps(PHASE1_BUDGETS.as_dict(), indent=2),),
        )
    finally:
        connection.close()

    assert read_status(paths).as_dict() == status.as_dict()
