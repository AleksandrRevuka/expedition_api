from fastapi import Depends
from src.modules.expeditions.domain.exceptions.exceptions import (
    InvalidExpeditionMemberRoleError,
)
from src.conf.enums import Role
from src.modules.users.application.use_cases.get_user import GetUserUseCase
from src.common.container.main_container import Container
from src.common.role_routers import MemberAPIRouter, ChiefAPIRouter
from uuid import UUID

from dependency_injector.wiring import inject, Provide

from src.common.security.auth_dependencies import get_current_user
from src.modules.expeditions.application.commands.commands import (
    ConfirmMemberCommand,
    InviteMemberCommand,
)
from src.modules.expeditions.presentation.api.schemas.requests import (
    InviteMemberBody,
)
from src.modules.expeditions.presentation.api.schemas.responses import (
    ExpeditionResponse,
)
from src.modules.expeditions.presentation.dependencies import MessagebusExpeditionsDep

members_router = MemberAPIRouter()
chief_router = ChiefAPIRouter()


@chief_router.post("/{expedition_id}/members/invite", response_model=ExpeditionResponse)
@inject
async def invite_member(
    expedition_id: UUID,
    body: InviteMemberBody,
    bus: MessagebusExpeditionsDep,
    current_user=Depends(get_current_user),
    users_uow=Depends(Provide[Container.uows.users_storage_uow]),
) -> ExpeditionResponse:
    async with users_uow:
        use_case = GetUserUseCase(users_uow.users)

        target_user = await use_case(body.user_id)

    if target_user.role != Role.member:
        raise InvalidExpeditionMemberRoleError(
            "Only users with role 'member' can be invited to an expedition"
        )

    command = InviteMemberCommand(
        expedition_id=expedition_id,
        user_id=body.user_id,
        chief_id=current_user.id,
    )

    expedition = await bus.handle(command)

    return ExpeditionResponse.from_domain(expedition)


@members_router.post(
    "/{expedition_id}/members/confirm", response_model=ExpeditionResponse
)
@inject
async def confirm_member(
    expedition_id: UUID,
    bus: MessagebusExpeditionsDep,
    current_user=Depends(get_current_user),
) -> ExpeditionResponse:
    command = ConfirmMemberCommand(
        expedition_id=expedition_id,
        user_id=current_user.id,
    )

    expedition = await bus.handle(command)

    return ExpeditionResponse.from_domain(expedition)
