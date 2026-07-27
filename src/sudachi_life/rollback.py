"""Audited rollback archive publication boundary.

The pre-repair shared rollback implementation is retained byte-for-byte in
``rollback_impl``. This module preserves that surface and adds only the
owner-authorized cleanup invariant for a newly published pre-rollback archive.
"""

from __future__ import annotations

from contextvars import ContextVar
import os as _os
from pathlib import Path
import shutil
from typing import Any

from . import rollback_impl as _impl


_PublicationState = dict[str, Any]
_publication_state: ContextVar[_PublicationState | None] = ContextVar(
    "rollback_archive_publication_state",
    default=None,
)


class _ScopedOsProxy:
    """Delegate to os while observing only this function's archive rename."""

    def __getattr__(self, name: str) -> Any:
        return getattr(_os, name)

    def replace(self, source: Any, destination: Any) -> None:
        _os.replace(source, destination)
        state = _publication_state.get()
        if state is None:
            return
        source_path = Path(source)
        destination_path = Path(destination)
        archive_root = state["archive_root"]
        if (
            source_path.parent == archive_root
            and source_path.name.startswith(".tmp-pre-rollback-")
            and destination_path.parent == archive_root
        ):
            state["published_final"] = destination_path


# Limit the interception to rollback_impl's own module reference. The process-wide
# os module and unrelated publication paths remain unchanged.
_impl.os = _ScopedOsProxy()

# Preserve the complete existing public and private module surface for callers
# that import shared validation helpers from sudachi_life.rollback.
for _name, _value in vars(_impl).items():
    if not _name.startswith("__"):
        globals()[_name] = _value

_original_prepare_rollback_archive = _impl.prepare_rollback_archive


def prepare_rollback_archive(
    runtime_root: Path | str,
    organism_id: str,
    source_event_sequence: int,
    *,
    protected_test_fail_after_snapshot: bool = False,
):
    """Run the frozen implementation and remove only a failed new publication."""

    archive_root = _impl.OrganismPaths.build(
        runtime_root,
        organism_id,
    ).rollback_archives
    state: _PublicationState = {
        "archive_root": archive_root,
        "published_final": None,
    }
    token = _publication_state.set(state)
    completed = False
    try:
        result = _original_prepare_rollback_archive(
            runtime_root,
            organism_id,
            source_event_sequence,
            protected_test_fail_after_snapshot=protected_test_fail_after_snapshot,
        )
        completed = True
        return result
    finally:
        _publication_state.reset(token)
        published_final = state["published_final"]
        if (
            not completed
            and published_final is not None
            and published_final.exists()
        ):
            shutil.rmtree(published_final, ignore_errors=True)
            if published_final.exists():
                raise _impl.RollbackArchiveError(
                    "failed to remove rejected newly published rollback archive"
                )
            if archive_root.exists():
                _impl._fsync_dir(archive_root)


# Ensure introspection and direct implementation-module users see the repaired
# shared function rather than bypassing the cleanup boundary.
_impl.prepare_rollback_archive = prepare_rollback_archive
