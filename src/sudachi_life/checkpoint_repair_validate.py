"""Pending-checkpoint repair validation with the authorized active ceiling."""

from __future__ import annotations

import sqlite3

from . import checkpoint_repair_validate_impl as _impl
from .paths import OrganismPaths
from .runtime_storage import ensure_active_database_within_limit


for _name, _value in vars(_impl).items():
    if not _name.startswith("__"):
        globals()[_name] = _value

_original_validate_pending_checkpoint_candidate = (
    _impl.validate_pending_checkpoint_candidate
)


def validate_pending_checkpoint_candidate(
    connection: sqlite3.Connection,
    paths: OrganismPaths,
):
    """Reject an over-limit active body before reading the repair clock or writing."""

    ensure_active_database_within_limit(
        connection,
        context="pending checkpoint repair",
    )
    return _original_validate_pending_checkpoint_candidate(connection, paths)


_impl.validate_pending_checkpoint_candidate = validate_pending_checkpoint_candidate
