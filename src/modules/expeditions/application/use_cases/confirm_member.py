from src.modules.expeditions.application.commands.commands import ConfirmMemberCommand
from src.modules.expeditions.domain.aggregates.expedition import ExpeditionAggregate
from src.modules.expeditions.domain.exceptions.exceptions import ExpeditionNotFoundError
from src.modules.expeditions.infrastructure.repositories import (
    ExpeditionsRepository,
    MembersRepository,
)


class ConfirmMemberUseCase:
    def __init__(
        self,
        expeditions: ExpeditionsRepository,
        members: MembersRepository,
    ) -> None:
        self._expeditions = expeditions
        self._members = members

    async def __call__(self, command: ConfirmMemberCommand) -> ExpeditionAggregate:
        expedition = await self._expeditions.get_one_with_relationships(
            relationships=["members"], id=command.expedition_id
        )

        if expedition is None:
            raise ExpeditionNotFoundError(
                f"Expedition {command.expedition_id} not found"
            )

        expedition.confirm_member(command.user_id)

        member = expedition._get_member(command.user_id)
        await self._members.update_one(member, id=member.id)

        return expedition
