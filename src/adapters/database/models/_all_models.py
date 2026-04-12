"""
ORM model imports for Alembic autogenerate.
Import all ORM model modules here so SQLAlchemy metadata is populated.
"""

from src.adapters.database.models._model_base import (  # noqa: F401
    BaseWithTimestamps,
    SqlAlchemyBase,
)
from src.modules.expeditions.infrastructure.db.models import (  # noqa: F401
    Expedition,
    ExpeditionMember,
)

# Module models are imported here as they are created:
from src.modules.users.infrastructure.db.models import User  # noqa: F401
