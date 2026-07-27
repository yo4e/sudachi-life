"""Audited checkpoint creation publication and registration boundary.

The pre-repair implementation remains byte-identical in ``checkpoint_creation_impl``.
This module adds only the authorized post-write working-set admission and cleanup
of a newly published checkpoint when that admission rolls back registration.
"""

from __future__ import annotations

from contextvars import ContextVar
import os as _os
from pathlib import Path
import shutil
from typing import Any

from . import checkpoint_creation_impl as _impl
from .postwrite_storage import (
    ensure_projected_committed_runtime_working_set_within_limit,
)


_State = dict[str, Any]
_state: ContextVar[_State | None] = ContextVar(
    "checkpoint_creation_postwrite_state",
    default=None,
)


class _ScopedOsProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(_os, name)

    def replace(self, source: Any, destination: Any) -> None:
        _os.replace(source, destination)
        state = _state.get()
        if state is None:
            return
        source_path = Path(source)
        destination_path = Path(destination)
        checkpoints = state["paths"].checkpoints
        if (
            source_path.parent == checkpoints
            and source_path.name.startswith(".tmp-checkpoint-")
            and destination_path.parent == checkpoints
        ):
            state["published_final"] = destination_path


class _CommitGuardConnection:
    def __init__(self, connection: Any, state: _State) -> None:
        self._connection = connection
        self._state = state

    def __getattr__(self, name: str) -> Any:
        return getattr(self._connection, name)

    def commit(self) -> None:
        try:
            ensure_projected_committed_runtime_working_set_within_limit(
                self._state["paths"],
                self._connection,
                context="checkpoint registration",
            )
        except _impl.SchemaValidationError as exc:
            self._state["storage_rejected"] = True
            raise _impl.CheckpointError(str(exc)) from exc
        self._connection.commit()


_original_connect_database = _impl.connect_database


def _scoped_connect_database(path: Path, *, read_only: bool = False):
    connection = _original_connect_database(path, read_only=read_only)
    state = _state.get()
    if (
        state is not None
        and not read_only
        and Path(path) == state["paths"].database
    ):
        return _CommitGuardConnection(connection, state)
    return connection


_impl.os = _ScopedOsProxy()
_impl.connect_database = _scoped_connect_database

for _name, _value in vars(_impl).items():
    if not _name.startswith("__"):
        globals()[_name] = _value

_original_genesis = _impl.create_and_register_genesis_checkpoint
_original_lifecycle = _impl.create_and_register_lifecycle_checkpoint


def _run_with_storage_guard(paths: Any, operation: Any):
    state: _State = {
        "paths": paths,
        "published_final": None,
        "storage_rejected": False,
    }
    token = _state.set(state)
    try:
        return operation()
    finally:
        _state.reset(token)
        published_final = state["published_final"]
        if (
            state["storage_rejected"]
            and published_final is not None
            and published_final.exists()
        ):
            shutil.rmtree(published_final, ignore_errors=True)
            if published_final.exists():
                raise _impl.CheckpointError(
                    "failed to remove storage-rejected newly published checkpoint"
                )
            if paths.checkpoints.exists():
                _impl._fsync_dir(paths.checkpoints)


def create_and_register_genesis_checkpoint(
    paths: Any,
    *,
    created_wall_time_utc_us: int,
    event_sequence: int,
):
    return _run_with_storage_guard(
        paths,
        lambda: _original_genesis(
            paths,
            created_wall_time_utc_us=created_wall_time_utc_us,
            event_sequence=event_sequence,
        ),
    )


def create_and_register_lifecycle_checkpoint(
    paths: Any,
    *,
    clock: Any,
    protected_test_retention_failure_after_stage: bool = False,
    protected_test_retention_cleanup_failure_after_commit: bool = False,
):
    return _run_with_storage_guard(
        paths,
        lambda: _original_lifecycle(
            paths,
            clock=clock,
            protected_test_retention_failure_after_stage=(
                protected_test_retention_failure_after_stage
            ),
            protected_test_retention_cleanup_failure_after_commit=(
                protected_test_retention_cleanup_failure_after_commit
            ),
        ),
    )


_impl.create_and_register_genesis_checkpoint = create_and_register_genesis_checkpoint
_impl.create_and_register_lifecycle_checkpoint = create_and_register_lifecycle_checkpoint
