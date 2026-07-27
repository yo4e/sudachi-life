"""Audited pending-checkpoint repair commit boundary.

The pre-repair atomic write sequence remains byte-identical in
``checkpoint_repair_commit_impl``. This module adds only a pre-commit check of
the projected committed working set so rejection can roll back canonically.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import checkpoint_repair_commit_impl as _impl
from .paths import OrganismPaths
from .postwrite_storage import (
    ensure_projected_committed_runtime_working_set_within_limit,
)


for _name, _value in vars(_impl).items():
    if not _name.startswith("__"):
        globals()[_name] = _value

_original_commit_pending_checkpoint_candidate = (
    _impl.commit_pending_checkpoint_candidate
)


class _CommitGuardConnection:
    def __init__(self, connection: Any, paths: OrganismPaths) -> None:
        self._connection = connection
        self._paths = paths

    def __getattr__(self, name: str) -> Any:
        return getattr(self._connection, name)

    def commit(self) -> None:
        try:
            ensure_projected_committed_runtime_working_set_within_limit(
                self._paths,
                self._connection,
                context="pending checkpoint repair",
            )
        except _impl.PendingCheckpointRepairRejectedError:
            raise
        except Exception as exc:
            raise _impl.PendingCheckpointRepairRejectedError(str(exc)) from exc
        self._connection.commit()


def commit_pending_checkpoint_candidate(
    connection: Any,
    candidate: Any,
    *,
    clock: Any,
):
    organism_id = str(candidate.organism["organism_id"])
    candidate_dir = Path(candidate.candidate_dir)
    runtime_root = candidate_dir.parents[2]
    paths = OrganismPaths.build(runtime_root, organism_id)
    guarded = _CommitGuardConnection(connection, paths)
    return _original_commit_pending_checkpoint_candidate(
        guarded,
        candidate,
        clock=clock,
    )


_impl.commit_pending_checkpoint_candidate = commit_pending_checkpoint_candidate
