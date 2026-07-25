from __future__ import annotations

import pytest

from sudachi_life.errors import SchemaValidationError
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import connect_database, read_status


def test_unexpected_mutating_trigger_is_rejected(initialized) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    connection = connect_database(paths.database)
    try:
        connection.execute(
            """CREATE TRIGGER hidden_inventory_mutator
               AFTER INSERT ON inbox_event
               BEGIN
                   UPDATE inventory
                   SET water_units = water_units + 1
                   WHERE singleton_id = 1;
               END"""
        )
    finally:
        connection.close()

    with pytest.raises(SchemaValidationError, match="unexpected mutable object"):
        read_status(paths)
