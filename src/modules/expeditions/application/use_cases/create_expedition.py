from src.modules.expeditions.application.commands.commands import (
    CreateExpeditionCommand,
)
from src.modules.expeditions.domain.aggregates.expedition import ExpeditionAggregate
from src.modules.expeditions.infrastructure.repositories import ExpeditionsRepository


class CreateExpeditionUseCase:
    def __init__(self, expeditions: ExpeditionsRepository) -> None:
        self._expeditions = expeditions

    async def __call__(self, command: CreateExpeditionCommand) -> ExpeditionAggregate:

        expedition = ExpeditionAggregate.create(command)

        return await self._expeditions.add_one(expedition)
