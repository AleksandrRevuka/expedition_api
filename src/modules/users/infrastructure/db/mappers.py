from src.adapters.database.models._model_base import mapper_registry
from src.modules.users.domain.aggregates.user import UserAggregate
from src.modules.users.infrastructure.db.models import User


def user_start_mapper() -> None:
    user_table = User.__table__
    mapper_registry.map_imperatively(
        UserAggregate,
        user_table,
    )
