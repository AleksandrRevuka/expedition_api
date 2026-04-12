from sqlalchemy.orm import relationship

from src.adapters.database.models._model_base import mapper_registry
from src.modules.expeditions.domain.aggregates.expedition import ExpeditionAggregate
from src.modules.expeditions.domain.entities.member import ExpeditionMemberEntity
from src.modules.expeditions.infrastructure.db.models import (
    Expedition,
    ExpeditionMember,
)


def expedition_start_mapper() -> None:
    expedition_table = Expedition.__table__
    mapper_registry.map_imperatively(
        ExpeditionAggregate,
        expedition_table,
        properties={"members": relationship(ExpeditionMemberEntity, viewonly=True)},
    )


def expedition_member_start_mapper() -> None:
    expedition_member_table = ExpeditionMember.__table__
    mapper_registry.map_imperatively(
        ExpeditionMemberEntity,
        expedition_member_table,
    )
