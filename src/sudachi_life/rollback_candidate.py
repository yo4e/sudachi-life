"""Audited restore-candidate publication with exact working-set closure.

The pre-repair implementation remains byte-identical in
``rollback_candidate_impl``. This public module preserves that surface and
adds exact admission and publication guards around its durable directory rename.
"""

from __future__ import annotations

from contextvars import ContextVar
from pathlib import Path
from typing import Callable

from . import rollback_candidate_impl as _impl
from .runtime_storage import ensure_runtime_working_set_within_limit

_Replace = Callable[[Path | str, Path | str], None]
_ReplaceGuard = Callable[[_Replace, Path | str, Path | str], None]
_replace_guard: ContextVar[_ReplaceGuard | None] = ContextVar(
    "restore_candidate_replace_guard",
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
        raise RestoreCandidateError(str(exc)) from exc


def _remove_failed_candidate(path: Path, *, context: str) -> None:
    try:
        if path.exists():
            shutil.rmtree(path)
        _fsync_dir(path.parent)
    except OSError as exc:
        raise RestoreCandidateError(f"{context}: candidate cleanup failed") from exc


def _guarded_candidate_replace(paths: OrganismPaths) -> _ReplaceGuard:
    def guarded_replace(
        replace: _Replace,
        source: Path | str,
        destination: Path | str,
    ) -> None:
        try:
            _working_set_error(paths, context="restore candidate pre-publication")
        except RestoreCandidateError:
            _remove_failed_candidate(
                Path(source),
                context="restore candidate pre-publication",
            )
            raise

        replace(source, destination)
        try:
            _working_set_error(paths, context="restore candidate publication")
        except RestoreCandidateError:
            _remove_failed_candidate(
                Path(destination),
                context="restore candidate publication",
            )
            raise

    return guarded_replace


def build_restore_candidate(
    runtime_root: Path | str,
    organism_id: str,
    *,
    protected_test_fail_before_publish: bool = False,
) -> RestoreCandidateResult:
    """Construct or reuse a candidate only within the protected working set."""

    paths = OrganismPaths.build(runtime_root, organism_id)
    _working_set_error(paths, context="restore candidate admission")
    token = _replace_guard.set(_guarded_candidate_replace(paths))
    try:
        return _impl.build_restore_candidate(
            runtime_root,
            organism_id,
            protected_test_fail_before_publish=protected_test_fail_before_publish,
        )
    finally:
        _replace_guard.reset(token)
