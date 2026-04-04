from __future__ import annotations

from uuid import UUID

from fastapi import WebSocket

from src.conf.logging_config import LOGGER


class ExpeditionConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[UUID, dict[UUID, set[WebSocket]]] = {}

    async def connect(
        self,
        ws: WebSocket,
        expedition_id: UUID,
        user_id: UUID,
    ) -> None:
        LOGGER.debug(
            "New expedition connection: expedition_id=%s, user_id=%s",
            expedition_id,
            user_id,
        )

        self._connections.setdefault(expedition_id, {})
        self._connections[expedition_id].setdefault(user_id, set()).add(ws)

    def disconnect(
        self,
        ws: WebSocket,
        expedition_id: UUID,
        user_id: UUID,
    ) -> None:
        users = self._connections.get(expedition_id, {})
        sockets = users.get(user_id, set())

        sockets.discard(ws)

        if not sockets:
            users.pop(user_id, None)

        if not users:
            self._connections.pop(expedition_id, None)

    async def broadcast_to_expedition(
        self,
        expedition_id: UUID,
        event: dict,
    ) -> None:
        LOGGER.debug(f"{self._connections}")
        users = self._connections.get(expedition_id, {})

        dead = []

        for user_id, sockets in users.items():
            for ws in sockets:
                try:
                    await ws.send_json(event)
                except Exception:
                    dead.append((user_id, ws))

        for user_id, ws in dead:
            self.disconnect(ws, expedition_id, user_id)
