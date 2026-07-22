"""Validated runtime paths."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from .errors import InvalidOrganismIdError

_ORGANISM_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def validate_organism_id(organism_id: str) -> str:
    if not _ORGANISM_ID_RE.fullmatch(organism_id):
        raise InvalidOrganismIdError(
            "organism_id must be 1-64 ASCII letters, digits, dots, underscores, or hyphens "
            "and must start with a letter or digit"
        )
    return organism_id


@dataclass(frozen=True, slots=True)
class OrganismPaths:
    runtime_root: Path
    organism_id: str

    @classmethod
    def build(cls, runtime_root: Path | str, organism_id: str) -> "OrganismPaths":
        return cls(Path(runtime_root), validate_organism_id(organism_id))

    @property
    def organism_dir(self) -> Path:
        return self.runtime_root / self.organism_id

    @property
    def database(self) -> Path:
        return self.organism_dir / "organism.sqlite3"

    @property
    def checkpoints(self) -> Path:
        return self.organism_dir / "checkpoints"

    @property
    def rollback_archives(self) -> Path:
        return self.organism_dir / "rollback-archives"

    @property
    def exports(self) -> Path:
        return self.organism_dir / "exports"

    @property
    def diagnostics(self) -> Path:
        return self.organism_dir / "diagnostics"
