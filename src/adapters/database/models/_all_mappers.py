"""
ORM mapper registry.
Mapper callables are added here as infrastructure modules are implemented.
"""

from collections.abc import Callable

from src.modules.expeditions.infrastructure.db.mappers import (
    expedition_member_start_mapper,
    expedition_start_mapper,
)
from src.modules.users.infrastructure.db.mappers import user_start_mapper

mappers: list[Callable[[], None]] = [
    user_start_mapper,
    expedition_start_mapper,
    expedition_member_start_mapper,
]
