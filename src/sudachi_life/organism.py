"""High-level organism initialization and inspection."""

from __future__ import annotations

from pathlib import Path

from .checkpoints import CheckpointResult, create_and_register_genesis_checkpoint
from .clock import Clock, RealClock
from .paths import OrganismPaths
from .storage import OrganismStatus, initialize_database, read_status


def initialize_organism(
    runtime_root: Path | str,
    organism_id: str,
    *,
    clock: Clock | None = None,
) -> tuple[OrganismStatus, CheckpointResult]:
    clock = clock or RealClock()
    paths = OrganismPaths.build(runtime_root, organism_id)
    wall_time, boundary = initialize_database(paths, clock=clock)
    checkpoint = create_and_register_genesis_checkpoint(
        paths,
        created_wall_time_utc_us=wall_time,
        event_sequence=boundary,
    )
    return read_status(paths), checkpoint


def get_status(runtime_root: Path | str, organism_id: str) -> OrganismStatus:
    return read_status(OrganismPaths.build(runtime_root, organism_id))
