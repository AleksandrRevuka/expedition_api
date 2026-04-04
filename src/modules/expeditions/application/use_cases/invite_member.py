from src.modules.expeditions.application.commands.commands import InviteMemberCommand
from src.modules.expeditions.domain.aggregates.expedition import ExpeditionAggregate
from src.modules.expeditions.domain.exceptions.exceptions import ExpeditionNotFoundError
from src.modules.expeditions.infrastructure.repositories import (
    ExpeditionsRepository,
    MembersRepository,
)


class InviteMemberUseCase:
    def __init__(
        self,
        expeditions: ExpeditionsRepository,
        members: MembersRepository,
    ) -> None:
        self._expeditions = expeditions
        self._members = members

    async def __call__(self, command: InviteMemberCommand) -> ExpeditionAggregate:
        expedition = await self._expeditions.get_one_with_relationships(
            relationships=["members"], id=command.expedition_id
        )

        if expedition is None:
            raise ExpeditionNotFoundError(
                f"Expedition {command.expedition_id} not found"
            )

        expedition.invite_member(command.chief_id, command.user_id)

        new_member = expedition.members[-1]
        await self._members.add_one(new_member)

        return expedition
