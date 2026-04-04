from src.modules.expeditions.application.commands.commands import (
    DeleteExpeditionCommand,
)
from src.modules.expeditions.domain.exceptions.exceptions import (
    ExpeditionAccessDeniedError,
    ExpeditionNotFoundError,
)
from src.modules.expeditions.infrastructure.repositories import ExpeditionsRepository


class DeleteExpeditionUseCase:
    def __init__(self, expeditions: ExpeditionsRepository) -> None:
        self._expeditions = expeditions

    async def __call__(self, command: DeleteExpeditionCommand) -> None:

        expedition = await self._expeditions.get_one_with_relationships(
            relationships=["members"], id=command.expedition_id
        )

        if expedition is None:
            raise ExpeditionNotFoundError(
                f"Expedition {command.expedition_id} not found"
            )

        if not expedition.is_owned_by(command.chief_id):
            raise ExpeditionAccessDeniedError(
                "Only the chief can delete this expedition"
            )

        await self._expeditions.delete_one(id=command.expedition_id)
