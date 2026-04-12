from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, status

from src.common.container.main_container import Container
from src.common.role_routers import AuthenticatedAPIRouter, ChiefAPIRouter
from src.common.security.auth_dependencies import get_current_user
from src.modules.expeditions.application.commands.commands import (
    ChangeExpeditionStatusCommand,
    CreateExpeditionCommand,
    DeleteExpeditionCommand,
    RemoveMemberCommand,
    UpdateExpeditionCommand,
)
from src.modules.expeditions.application.use_cases.get_expedition import (
    GetExpeditionUseCase,
)
from src.modules.expeditions.application.use_cases.list_expeditions import (
    ListExpeditionsUseCase,
)
from src.modules.expeditions.presentation.api.schemas.requests import (
    ChangeStatusBody,
    CreateExpeditionBody,
    UpdateExpeditionBody,
)
from src.modules.expeditions.presentation.api.schemas.responses import (
    ExpeditionResponse,
)
from src.modules.expeditions.presentation.dependencies import MessagebusExpeditionsDep

chief_router = ChiefAPIRouter()
auth_router = AuthenticatedAPIRouter()


@auth_router.get("", response_model=list[ExpeditionResponse])
@inject
async def list_expeditions(
    uow=Depends(Provide[Container.uows.expeditions_storage_uow]),
) -> list[ExpeditionResponse]:
    async with uow:
        use_case = ListExpeditionsUseCase(uow.expeditions)
        expeditions = await use_case()
    return [ExpeditionResponse.from_domain(e) for e in expeditions]


@auth_router.get("/{expedition_id}", response_model=ExpeditionResponse)
@inject
async def get_expedition(
    expedition_id: UUID,
    uow=Depends(Provide[Container.uows.expeditions_storage_uow]),
) -> ExpeditionResponse:
    async with uow:
        use_case = GetExpeditionUseCase(uow.expeditions)

        expedition = await use_case(expedition_id)

    return ExpeditionResponse.from_domain(expedition)


@chief_router.post(
    "", response_model=ExpeditionResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def create_expedition(
    body: CreateExpeditionBody,
    bus: MessagebusExpeditionsDep,
    current_user=Depends(get_current_user),
) -> ExpeditionResponse:
    command = CreateExpeditionCommand(
        title=body.title,
        description=body.description,
        chief_id=current_user.id,
        start_at=body.start_at,
        capacity=body.capacity,
    )
    expedition = await bus.handle(command)
    return ExpeditionResponse.from_domain(expedition)


@chief_router.patch("/{expedition_id}", response_model=ExpeditionResponse)
@inject
async def update_expedition(
    expedition_id: UUID,
    body: UpdateExpeditionBody,
    bus: MessagebusExpeditionsDep,
    current_user=Depends(get_current_user),
) -> ExpeditionResponse:
    command = UpdateExpeditionCommand(
        expedition_id=expedition_id,
        chief_id=current_user.id,
        title=body.title,
        description=body.description,
    )

    expedition = await bus.handle(command)

    return ExpeditionResponse.from_domain(expedition)


@chief_router.delete("/{expedition_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_expedition(
    expedition_id: UUID,
    bus: MessagebusExpeditionsDep,
    current_user=Depends(get_current_user),
) -> None:
    command = DeleteExpeditionCommand(
        expedition_id=expedition_id,
        chief_id=current_user.id,
    )

    await bus.handle(command)


@chief_router.delete(
    "/{expedition_id}/members/{user_id}", response_model=ExpeditionResponse
)
@inject
async def delete_member(
    expedition_id: UUID,
    user_id: UUID,
    bus: MessagebusExpeditionsDep,
    current_user=Depends(get_current_user),
) -> ExpeditionResponse:
    command = RemoveMemberCommand(
        expedition_id=expedition_id, chief_id=current_user.id, user_id=user_id
    )

    expedition = await bus.handle(command)
    return ExpeditionResponse.from_domain(expedition)


@chief_router.patch("/{expedition_id}/status", response_model=ExpeditionResponse)
@inject
async def change_status(
    expedition_id: UUID,
    body: ChangeStatusBody,
    # status: ExpeditionStatus,
    bus: MessagebusExpeditionsDep,
    current_user=Depends(get_current_user),
) -> ExpeditionResponse:
    command = ChangeExpeditionStatusCommand(
        expedition_id=expedition_id,
        chief_id=current_user.id,
        new_status=body.status,
    )

    expedition = await bus.handle(command)

    return ExpeditionResponse.from_domain(expedition)
