from uuid import UUID

from src.modules.expeditions.domain.aggregates.expedition import ExpeditionAggregate
from src.modules.expeditions.infrastructure.repositories import ExpeditionsRepository


class ListExpeditionsUseCase:
    def __init__(self, expeditions: ExpeditionsRepository) -> None:
        self._expeditions = expeditions

    async def __call__(self, chief_id: UUID | None = None) -> list[ExpeditionAggregate]:

        return await self._expeditions.get_all_with_relationships(
            relationships=["members"], chief_id=chief_id
        )
