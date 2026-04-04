from src.conf.enums import ExpeditionStatus, MemberState
from src.modules.expeditions.application.commands.commands import (
    ChangeExpeditionStatusCommand,
)
from src.modules.expeditions.domain.aggregates.expedition import ExpeditionAggregate
from src.modules.expeditions.domain.exceptions.exceptions import (
    ExpeditionNotFoundError,
)
from src.modules.expeditions.infrastructure.repositories import (
    ExpeditionsRepository,
    MembersRepository,
)


class ChangeExpeditionStatusUseCase:
    def __init__(
        self, expeditions: ExpeditionsRepository, members: MembersRepository
    ) -> None:
        self._expeditions = expeditions
        self._members = members

    async def __call__(
        self, command: ChangeExpeditionStatusCommand
    ) -> ExpeditionAggregate:

        expedition = await self._expeditions.get_one_with_relationships(
            relationships=["members"], id=command.expedition_id
        )

        if expedition is None:
            raise ExpeditionNotFoundError(
                f"Expedition {command.expedition_id} not found"
            )

        if expedition.status == command.new_status:
            return expedition

        active_users: set = set()

        if command.new_status == ExpeditionStatus.active:
            confirmed_ids = {
                m.user_id
                for m in expedition.members
                if m.state == MemberState.confirmed
            }
            active_users = await self._members.get_users_in_active_expeditions(
                user_ids=confirmed_ids,
                exclude_expedition_id=expedition.id,
            )

        expedition.change_status(command.chief_id, command.new_status, active_users)

        return await self._expeditions.update_one(expedition, id=expedition.id)
