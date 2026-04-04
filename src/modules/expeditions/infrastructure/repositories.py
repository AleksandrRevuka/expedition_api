from src.conf.enums import ExpeditionStatus, MemberState
from sqlalchemy import select
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.repositories.repository import AsyncRepository
from src.modules.expeditions.domain.aggregates.expedition import ExpeditionAggregate
from src.modules.expeditions.domain.entities.member import ExpeditionMemberEntity
from src.modules.expeditions.infrastructure.db.models import (
    Expedition as ExpeditionModel,
    ExpeditionMember as ExpeditionMemberModel,
)


class ExpeditionsRepository(AsyncRepository[ExpeditionAggregate]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ExpeditionAggregate, session)


class MembersRepository(AsyncRepository[ExpeditionMemberEntity]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ExpeditionMemberEntity, session)

    async def get_users_in_active_expeditions(
        self,
        user_ids: set[UUID],
        exclude_expedition_id: UUID,
    ) -> set[UUID]:
        """Return subset of user_ids that are confirmed in any active expedition
        other than exclude_expedition_id."""
        if not user_ids:
            return set()

        stmt = (
            select(ExpeditionMemberModel.user_id)
            .join(
                ExpeditionModel,
                ExpeditionMemberModel.expedition_id == ExpeditionModel.id,
            )
            .where(
                ExpeditionMemberModel.user_id.in_(user_ids),
                ExpeditionMemberModel.state == MemberState.confirmed,
                ExpeditionModel.status == ExpeditionStatus.active,
                ExpeditionModel.id != exclude_expedition_id,
            )
        )
        result = await self._session.execute(stmt)
        return set(result.scalars().all())
