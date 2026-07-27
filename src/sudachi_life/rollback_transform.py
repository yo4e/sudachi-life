"""Audited transformed-candidate publication with exact working-set closure.

The pre-repair implementation remains byte-identical in
``rollback_transform_impl``. This public module preserves that surface and
adds exact admission and publication guards around its durable directory rename.
"""

from __future__ import annotations

from contextvars import ContextVar
from pathlib import Path
from typing import Callable

from . import rollback_transform_impl as _impl
from .runtime_storage import ensure_runtime_working_set_within_limit

_Replace = Callable[[Path | str, Path | str], None]
_ReplaceGuard = Callable[[_Replace, Path | str, Path | str], None]
_replace_guard: ContextVar[_ReplaceGuard | None] = ContextVar(
    "transformed_candidate_replace_guard",
    default=None,
)


class _GuardedOs:
    def __init__(self, base: object) -> None:
        self._base = base

    def __getattr__(self, name: str) -> object:
        return getattr(self._base, name)

    def replace(self, source: Path | str, destination: Path | str) -> None:
        guard = _replace_guard.get()
        if guard is None:
            self._base.replace(source, destination)
            return
        guard(self._base.replace, source, destination)


if not isinstance(_impl.os, _GuardedOs):
    _impl.os = _GuardedOs(_impl.os)

for _name, _value in vars(_impl).items():
    if not _name.startswith("__"):
        globals()[_name] = _value
del _name, _value


def _working_set_error(paths: OrganismPaths, *, context: str) -> None:
    try:
        ensure_runtime_working_set_within_limit(paths, context=context)
    except SchemaValidationError as exc:
        raise CandidateTransformError(str(exc)) from exc


def _remove_failed_candidate(path: Path, *, context: str) -> None:
    try:
        if path.exists():
            shutil.rmtree(path)
        _fsync_dir(path.parent)
    except OSError as exc:
        raise CandidateTransformError(f"{context}: candidate cleanup failed") from exc


def _guarded_candidate_replace(paths: OrganismPaths) -> _ReplaceGuard:
    def guarded_replace(
        replace: _Replace,
        source: Path | str,
        destination: Path | str,
    ) -> None:
        try:
            _working_set_error(
                paths,
                context="transformed candidate pre-publication",
            )
        except CandidateTransformError:
            _remove_failed_candidate(
                Path(source),
                context="transformed candidate pre-publication",
            )
            raise

        replace(source, destination)
        try:
            _working_set_error(paths, context="transformed candidate publication")
        except CandidateTransformError:
            _remove_failed_candidate(
                Path(destination),
                context="transformed candidate publication",
            )
            raise

    return guarded_replace


def transform_restore_candidate(
    runtime_root: Path | str,
    organism_id: str,
    source_candidate_id: str,
    administrative_reason: str,
    *,
    clock: Clock | None = None,
    protected_test_fail_after_event_insert: bool = False,
    protected_test_fail_before_publish: bool = False,
) -> CandidateTransformResult:
    """Transform or reuse a candidate only within the protected working set."""

    paths = OrganismPaths.build(runtime_root, organism_id)
    _working_set_error(paths, context="transformed candidate admission")
    token = _replace_guard.set(_guarded_candidate_replace(paths))
    try:
        return _impl.transform_restore_candidate(
            runtime_root,
            organism_id,
            source_candidate_id,
            administrative_reason,
            clock=clock,
            protected_test_fail_after_event_insert=(
                protected_test_fail_after_event_insert
            ),
            protected_test_fail_before_publish=protected_test_fail_before_publish,
        )
    finally:
        _replace_guard.reset(token)
