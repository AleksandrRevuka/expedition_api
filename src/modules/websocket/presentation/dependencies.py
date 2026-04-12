from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, WebSocket

from src.common.container.main_container import Container
from src.modules.expeditions.infrastructure.units_of_work import (
    ExpeditionsStorageUnitOfWork,
)
from src.modules.users.domain.aggregates.user import UserAggregate
from src.modules.users.infrastructure.token_service import TokenService
from src.modules.websocket.manager import ExpeditionConnectionManager

WebSocketManagerDep = Annotated[
    ExpeditionConnectionManager, Depends(Provide[Container.core.ws_manager])
]

ExpeditionsUoWDep = Annotated[
    ExpeditionsStorageUnitOfWork,
    Depends(Provide[Container.uows.expeditions_storage_uow]),
]


@inject
async def get_ws_current_user(
    websocket: WebSocket,
    users_uow=Depends(Provide[Container.uows.users_storage_uow]),
    token_service: TokenService = Depends(Provide[Container.services.token_service]),
) -> UserAggregate | None:
    token = websocket.query_params.get("token")
    if token is None:
        return None
    try:
        email = await token_service.get_email_from_token(token)
    except Exception:
        return None

    async with users_uow:
        return await users_uow.users.get_one(email=email)


WsCurrentUserDep = Annotated[UserAggregate | None, Depends(get_ws_current_user)]
