from tests.config import EXPEDITION_ID, USER_ID, MEMBER_ID
from fastapi import WebSocket
from src.modules.websocket.manager import ExpeditionConnectionManager
import pytest
from pytest_mock import MockerFixture

pytestmark = pytest.mark.unit

class TestWSManager:
    @pytest.mark.asyncio
    async def test_ws_manager_connect(self, mocker: MockerFixture, ws_manager: ExpeditionConnectionManager) -> None:
        ws = mocker.MagicMock(spec=WebSocket)
        ws.send_json = mocker.AsyncMock()
        await ws_manager.connect(ws, EXPEDITION_ID, USER_ID)

        assert ws in ws_manager._connections[EXPEDITION_ID][USER_ID]

    @pytest.mark.asyncio
    async def test_ws_manager_disconnect(self, mocker: MockerFixture, ws_manager: ExpeditionConnectionManager) -> None:
        ws = mocker.MagicMock(spec=WebSocket)
        ws.send_json = mocker.AsyncMock()
        ws_1 = mocker.MagicMock(spec=WebSocket)
        ws_1.send_json = mocker.AsyncMock()
        await ws_manager.connect(ws, EXPEDITION_ID, USER_ID)
        await ws_manager.connect(ws_1, EXPEDITION_ID, USER_ID)

        ws_manager.disconnect(ws, EXPEDITION_ID, USER_ID)

        assert ws not in ws_manager._connections[EXPEDITION_ID][USER_ID]

    @pytest.mark.asyncio
    async def test_ws_manager_broadcast_to_expedition(self, mocker: MockerFixture, ws_manager: ExpeditionConnectionManager) -> None:
        ws = mocker.MagicMock(spec=WebSocket)
        ws.send_json = mocker.AsyncMock()
        await ws_manager.connect(ws, EXPEDITION_ID, USER_ID)

        await ws_manager.broadcast_to_expedition(EXPEDITION_ID, {"event": "test"})

        assert ws.send_json.call_count == 1

    @pytest.mark.asyncio
    async def test_disconnect_removes_user_and_expedition(self, mocker: MockerFixture, ws_manager: ExpeditionConnectionManager) -> None:
        ws = mocker.MagicMock(spec=WebSocket)
        ws.send_json = mocker.AsyncMock()
        await ws_manager.connect(ws, EXPEDITION_ID, USER_ID)
        ws_manager.disconnect(ws, EXPEDITION_ID, USER_ID)

        assert EXPEDITION_ID not in ws_manager._connections

    @pytest.mark.asyncio
    async def test_broadcast_multiple_users(self, mocker: MockerFixture, ws_manager: ExpeditionConnectionManager) -> None:
        ws1 = mocker.MagicMock(spec=WebSocket)
        ws1.send_json = mocker.AsyncMock()
        ws2 = mocker.MagicMock(spec=WebSocket)
        ws2.send_json = mocker.AsyncMock()
        await ws_manager.connect(ws1, EXPEDITION_ID, USER_ID)
        await ws_manager.connect(ws2, EXPEDITION_ID, MEMBER_ID)

        await ws_manager.broadcast_to_expedition(EXPEDITION_ID, {"event": "test"})

        assert ws1.send_json.called
        assert ws2.send_json.called

    @pytest.mark.asyncio
    async def test_broadcast_removes_dead_connections(self, mocker: MockerFixture, ws_manager: ExpeditionConnectionManager) -> None:
        ws = mocker.MagicMock(spec=WebSocket)
        ws.send_json = mocker.AsyncMock()

        async def fail(*args, **kwargs):
            raise RuntimeError()

        ws.send_json = mocker.AsyncMock(side_effect=fail)

        await ws_manager.connect(ws, EXPEDITION_ID, USER_ID)

        await ws_manager.broadcast_to_expedition(EXPEDITION_ID, {"event": "test"})

        assert EXPEDITION_ID not in ws_manager._connections

    def test_disconnect_idempotent(self, mocker: MockerFixture, ws_manager: ExpeditionConnectionManager) -> None:
        ws = mocker.MagicMock(spec=WebSocket)
        ws.send_json = mocker.AsyncMock()

        ws_manager.disconnect(ws, EXPEDITION_ID, USER_ID) 