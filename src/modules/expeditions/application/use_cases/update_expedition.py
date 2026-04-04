from src.modules.expeditions.application.commands.commands import (
    UpdateExpeditionCommand,
)
from src.modules.expeditions.domain.aggregates.expedition import ExpeditionAggregate
from src.modules.expeditions.domain.exceptions import exceptions as exc
from src.modules.expeditions.infrastructure.repositories import ExpeditionsRepository


class UpdateExpeditionUseCase:
    def __init__(self, expeditions: ExpeditionsRepository) -> None:
        self._expeditions = expeditions

    async def __call__(self, command: UpdateExpeditionCommand) -> ExpeditionAggregate:
        expedition = await self._expeditions.get_one_with_relationships(
            relationships=["members"], id=command.expedition_id
        )

        if expedition is None:
            raise exc.ExpeditionNotFoundError(
                f"Expedition {command.expedition_id} not found"
            )

        expedition.update(command)
        return await self._expeditions.update_one(expedition, id=expedition.id)
