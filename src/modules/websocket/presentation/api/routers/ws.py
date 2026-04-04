from uuid import UUID

from dependency_injector.wiring import inject
from fastapi import APIRouter, WebSocket
from fastapi.websockets import WebSocketDisconnect

from src.modules.websocket.presentation.dependencies import (
    ExpeditionsUoWDep,
    WebSocketManagerDep,
    WsCurrentUserDep,
)

ws_router = APIRouter()


@ws_router.websocket("/expeditions/{expedition_id}")
@inject
async def expedition_websocket(
    websocket: WebSocket,
    expedition_id: UUID,
    ws_manager: WebSocketManagerDep,
    expeditions_uow: ExpeditionsUoWDep,
    current_user: WsCurrentUserDep,
) -> None:
    if current_user is None:
        await websocket.close(code=1008)
        return

    async with expeditions_uow:
        expedition = await expeditions_uow.expeditions.get_one_with_relationships(
            relationships=["members"], id=expedition_id
        )

    if expedition is None or not expedition.is_participant(current_user.id):
        await websocket.close(code=1008)
        return

    await websocket.accept()
    await ws_manager.connect(websocket, expedition_id, current_user.id)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, expedition_id, current_user.id)
