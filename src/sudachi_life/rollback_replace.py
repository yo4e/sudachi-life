"""Audited active-replacement physical admission boundary.

The pre-repair implementation remains byte-identical in ``rollback_replace_impl``.
This module adds only current active/working-set admission before replacement or
idempotent replacement recovery.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import rollback_replace_impl as _impl
from .runtime_storage import (
    ensure_active_database_within_limit,
    ensure_runtime_working_set_within_limit,
)


for _name, _value in vars(_impl).items():
    if not _name.startswith("__"):
        globals()[_name] = _value

_original_replace_active_with_candidate = _impl.replace_active_with_candidate


def _admit_current_physical_state(paths: Any) -> None:
    if paths.database.is_file() and not paths.database.is_symlink():
        connection = _impl.connect_database(paths.database, read_only=True)
        try:
            ensure_active_database_within_limit(
                connection,
                context="active replacement admission",
            )
        except _impl.SchemaValidationError as exc:
            raise _impl.ActiveReplacementError(str(exc)) from exc
        finally:
            connection.close()
    try:
        ensure_runtime_working_set_within_limit(
            paths,
            context="active replacement admission",
        )
    except _impl.SchemaValidationError as exc:
        raise _impl.ActiveReplacementError(str(exc)) from exc


def replace_active_with_candidate(
    runtime_root: Path | str,
    organism_id: str,
    transformed_candidate_id: str,
    *,
    protected_test_fail_before_replace: bool = False,
    protected_test_fail_after_replace: bool = False,
):
    """Replace or recover only from an admissible current physical state."""

    paths = _impl.OrganismPaths.build(runtime_root, organism_id)
    _admit_current_physical_state(paths)
    return _original_replace_active_with_candidate(
        runtime_root,
        organism_id,
        transformed_candidate_id,
        protected_test_fail_before_replace=protected_test_fail_before_replace,
        protected_test_fail_after_replace=protected_test_fail_after_replace,
    )


_impl.replace_active_with_candidate = replace_active_with_candidate
