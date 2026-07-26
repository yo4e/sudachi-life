"""Public rollback artifact-graph projection API."""

from . import phase2_rollback_projection_impl as _implementation
from .phase2_rollback_projection_state import project_database_state

# The accepted rollback path can carry a latest-stable checkpoint created in the
# abandoned lineage. The implementation otherwise reuses the closed core oracle;
# only its database-state projection is replaced with the exact raw-identity
# resolver before any public operation runs.
_implementation._project_database_state = project_database_state

from .phase2_rollback_projection_impl import *  # noqa: F401,F403,E402

__all__ = _implementation.__all__
