"""In-memory WebSocket connection manager for expedition event broadcasting."""

from __future__ import annotations

import dataclasses
from uuid import UUID

from fastapi import WebSocket

from src.conf.logging_config import LOGGER


@dataclasses.dataclass
class ExpeditionConnection:
    websocket: WebSocket
    user_id: UUID
    role: str


class ExpeditionConnectionManager:
    """Manages WebSocket connections grouped by expedition_id."""

    def __init__(self) -> None:
        # expedition_id → list of active connections
        self._connections: dict[UUID, list[ExpeditionConnection]] = {}

    async def connect(
        self,
        ws: WebSocket,
        expedition_id: UUID,
        user_id: UUID,
        role: str,
    ) -> None:
        await ws.accept()
        self._connections.setdefault(expedition_id, []).append(
            ExpeditionConnection(websocket=ws, user_id=user_id, role=role)
        )
        LOGGER.debug(
            "WebSocket connected",
            expedition_id=str(expedition_id),
            user_id=str(user_id),
            role=role,
        )

    def disconnect(self, ws: WebSocket, expedition_id: UUID) -> None:
        connections = self._connections.get(expedition_id, [])
        self._connections[expedition_id] = [c for c in connections if c.websocket is not ws]
        LOGGER.debug("WebSocket disconnected", expedition_id=str(expedition_id))

    async def broadcast_to_expedition(self, expedition_id: UUID, event: dict) -> None:  # type: ignore[type-arg]
        connections = self._connections.get(expedition_id, [])
        dead: list[ExpeditionConnection] = []
        for conn in connections:
            try:
                await conn.websocket.send_json(event)
            except Exception:
                dead.append(conn)
        for d in dead:
            self._connections[expedition_id].remove(d)
