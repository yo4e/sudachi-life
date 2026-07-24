"""Result types for checkpoint-retention repair operations."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CheckpointRetentionReconciliationResult:
    organism_id: str
    removed_staging_directories: tuple[str, ...]
    remaining_staging_directories: tuple[str, ...]
    status: str
    maintenance_reason: str | None
    audit_event_sequence: int | None

    def as_dict(self) -> dict[str, object]:
        return {
            "organism_id": self.organism_id,
            "removed_staging_directories": list(self.removed_staging_directories),
            "remaining_staging_directories": list(self.remaining_staging_directories),
            "status": self.status,
            "maintenance_reason": self.maintenance_reason,
            "audit_event_sequence": self.audit_event_sequence,
        }
