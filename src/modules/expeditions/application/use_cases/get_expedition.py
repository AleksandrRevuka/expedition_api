from uuid import UUID

from src.modules.expeditions.domain.aggregates.expedition import ExpeditionAggregate
from src.modules.expeditions.domain.exceptions.exceptions import ExpeditionNotFoundError
from src.modules.expeditions.infrastructure.repositories import ExpeditionsRepository


class GetExpeditionUseCase:
    def __init__(self, expeditions: ExpeditionsRepository) -> None:
        self._expeditions = expeditions

    async def __call__(self, expedition_id: UUID) -> ExpeditionAggregate:

        expedition = await self._expeditions.get_one_with_relationships(
            relationships=["members"], id=expedition_id
        )

        if expedition is None:
            raise ExpeditionNotFoundError(f"Expedition {expedition_id} not found")

        return expedition
