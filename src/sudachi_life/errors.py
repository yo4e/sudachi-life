"""Typed errors for the SUDACHI-0 foundation."""


class SudachiError(Exception):
    """Base class for expected SUDACHI errors."""


class InvalidOrganismIdError(SudachiError):
    """Raised when an organism identifier is not valid."""


class OrganismExistsError(SudachiError):
    """Raised when initialization would overwrite an organism."""


class OrganismNotFoundError(SudachiError):
    """Raised when the requested organism does not exist."""


class ClockExhaustedError(SudachiError):
    """Raised when deterministic code performs an unexpected clock read."""


class SchemaValidationError(SudachiError):
    """Raised when canonical schema or protected state is invalid."""


class CheckpointError(SudachiError):
    """Raised when checkpoint creation or validation fails."""
