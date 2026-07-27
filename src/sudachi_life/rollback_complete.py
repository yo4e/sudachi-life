"""Audited rollback-completion physical admission and commit boundary.

The pre-repair implementation remains byte-identical in ``rollback_complete_impl``.
This module adds only current active/working-set admission and post-write committed
physical checks before the completion transaction commits.
"""

from __future__ import annotations

from contextvars import ContextVar
from pathlib import Path
from typing import Any

from . import rollback_complete_impl as _impl
from .postwrite_storage import (
    ensure_projected_committed_runtime_working_set_within_limit,
)
from .runtime_storage import (
    ensure_active_database_within_limit,
    ensure_runtime_working_set_within_limit,
)


_State = dict[str, Any]
_state: ContextVar[_State | None] = ContextVar(
    "rollback_completion_physical_state",
    default=None,
)

_original_connect_database = _impl.connect_database


class _CommitGuardConnection:
    def __init__(self, connection: Any, paths: Any) -> None:
        self._connection = connection
        self._paths = paths

    def __getattr__(self, name: str) -> Any:
        return getattr(self._connection, name)

    def commit(self) -> None:
        try:
            ensure_projected_committed_runtime_working_set_within_limit(
                self._paths,
                self._connection,
                context="rollback completion",
            )
        except _impl.SchemaValidationError as exc:
            raise _impl.RollbackCompletionRejectedError(str(exc)) from exc
        self._connection.commit()


def _scoped_connect_database(path: Path, *, read_only: bool = False):
    connection = _original_connect_database(path, read_only=read_only)
    state = _state.get()
    if (
        state is not None
        and not read_only
        and Path(path) == state["paths"].database
    ):
        return _CommitGuardConnection(connection, state["paths"])
    return connection


_impl.connect_database = _scoped_connect_database

for _name, _value in vars(_impl).items():
    if not _name.startswith("__"):
        globals()[_name] = _value

_original_complete_rollback = _impl.complete_rollback


def _admit_current_physical_state(paths: Any) -> None:
    if paths.database.is_file() and not paths.database.is_symlink():
        connection = _original_connect_database(paths.database, read_only=True)
        try:
            ensure_active_database_within_limit(
                connection,
                context="rollback completion admission",
            )
        except _impl.SchemaValidationError as exc:
            raise _impl.RollbackCompletionRejectedError(str(exc)) from exc
        finally:
            connection.close()
    try:
        ensure_runtime_working_set_within_limit(
            paths,
            context="rollback completion admission",
        )
    except _impl.SchemaValidationError as exc:
        raise _impl.RollbackCompletionRejectedError(str(exc)) from exc


def complete_rollback(
    runtime_root: Path | str,
    organism_id: str,
    transformed_candidate_id: str,
    *,
    clock: Any = None,
    protected_test_fail_after_event_insert: bool = False,
):
    """Complete or recover only within the protected physical limits."""

    paths = _impl.OrganismPaths.build(runtime_root, organism_id)
    _admit_current_physical_state(paths)
    token = _state.set({"paths": paths})
    try:
        return _original_complete_rollback(
            runtime_root,
            organism_id,
            transformed_candidate_id,
            clock=clock,
            protected_test_fail_after_event_insert=(
                protected_test_fail_after_event_insert
            ),
        )
    finally:
        _state.reset(token)


_impl.complete_rollback = complete_rollback
