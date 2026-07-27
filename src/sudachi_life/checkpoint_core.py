"""Shared immutable-checkpoint validation with the authorized artifact ceiling."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import checkpoint_core_impl as _impl
from .constants import CHECKPOINT_ARTIFACT_MAX_BYTES
from .errors import CheckpointError

# Preserve the complete pre-repair implementation surface, including the private
# helpers intentionally re-exported by checkpoints.py. The retained implementation
# blob is unchanged; only validation admission is narrowed below.
for _name, _value in vars(_impl).items():
    if not _name.startswith("__"):
        globals()[_name] = _value

_validate_checkpoint_directory_without_artifact_ceiling = (
    _impl.validate_checkpoint_directory
)


def validate_checkpoint_directory(
    checkpoint_dir: Path,
    *,
    expected_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate one checkpoint, rejecting a database above the 8 MiB ceiling."""

    database_path = checkpoint_dir / "organism.sqlite3"
    # Delegate missing, symlink, and non-file classification to the retained
    # validator so all established error ordering and messages remain unchanged.
    if database_path.is_file() and not database_path.is_symlink():
        size = database_path.stat().st_size
        if size > CHECKPOINT_ARTIFACT_MAX_BYTES:
            raise CheckpointError(
                f"checkpoint database exceeds {CHECKPOINT_ARTIFACT_MAX_BYTES} bytes"
            )
    return _validate_checkpoint_directory_without_artifact_ceiling(
        checkpoint_dir,
        expected_manifest=expected_manifest,
    )


# Internal calls made by retained checkpoint-core helpers resolve module globals
# at call time, so bind the guarded validator there as well.
_impl.validate_checkpoint_directory = validate_checkpoint_directory
