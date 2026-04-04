from src.modules.expeditions.application.commands.commands import RemoveMemberCommand
from src.modules.expeditions.domain.aggregates.expedition import ExpeditionAggregate
from src.modules.expeditions.domain.exceptions.exceptions import ExpeditionNotFoundError
from src.modules.expeditions.infrastructure.repositories import (
    ExpeditionsRepository,
    MembersRepository,
)


class RemoveMemberUseCase:
    def __init__(
        self,
        expeditions: ExpeditionsRepository,
        members: MembersRepository,
    ) -> None:
        self._expeditions = expeditions
        self._members = members

    async def __call__(self, command: RemoveMemberCommand) -> ExpeditionAggregate:
        expedition = await self._expeditions.get_one_with_relationships(
            relationships=["members"], id=command.expedition_id
        )

        if expedition is None:
            raise ExpeditionNotFoundError(
                f"Expedition {command.expedition_id} not found"
            )

        removed_member = expedition.remove_member(command.chief_id, command.user_id)
        await self._members.delete_one(id=removed_member.id)

        return expedition
