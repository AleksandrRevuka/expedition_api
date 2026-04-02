"""
ORM mapper registry.
Mapper callables are added here as infrastructure modules are implemented.
"""
from collections.abc import Callable

# Each entry is a zero-argument callable that registers imperative mappers.
# Example:
#   from src.modules.users.infrastructure.db.mappers import user_start_mapper
#   mappers.append(user_start_mapper)

mappers: list[Callable[[], None]] = []
