from collections.abc import Callable, Coroutine
from typing import Any

import httpx
import pytest
from httpx_ws import WebSocketDisconnect, aconnect_ws
from httpx_ws.transport import ASGIWebSocketTransport
from src.modules.expeditions.domain.aggregates.expedition import ExpeditionAggregate
from src.modules.users.domain.aggregates.user import UserAggregate

from src.app import CustomFastAPI
from src.conf.enums import Role
from tests.config import CHIEF_ID, EXPEDITION_ID

pytestmark = [pytest.mark.e2e, pytest.mark.asyncio]


class TestExpeditionWebSocket:

    @pytest.mark.asyncio
    async def test_connect_without_token_closes(
        self,
        test_app: CustomFastAPI,
    ):
        async with httpx.AsyncClient(
            transport=ASGIWebSocketTransport(test_app),
            base_url="http://testserver",
        ) as client:
            with pytest.raises(WebSocketDisconnect) as exc_info:
                async with aconnect_ws(f"/api/ws/expeditions/{EXPEDITION_ID}", client):
                    pass

        assert exc_info.value.code == 1008

    @pytest.mark.asyncio
    async def test_connect_with_invalid_token_closes(
        self,
        test_app: CustomFastAPI,
    ):
        async with httpx.AsyncClient(
            transport=ASGIWebSocketTransport(test_app),
            base_url="http://testserver",
        ) as client:
            with pytest.raises(WebSocketDisconnect) as exc_info:
                async with aconnect_ws(
                    f"/api/ws/expeditions/{EXPEDITION_ID}?token=invalid", client
                ):
                    pass

        assert exc_info.value.code == 1008

    @pytest.mark.asyncio
    async def test_connect_non_participant_closes(
        self,
        test_app: CustomFastAPI,
        map_models_to_orm,
        test_db,
        access_token: Callable[..., str],
    ):
        token = access_token()
        async with httpx.AsyncClient(
            transport=ASGIWebSocketTransport(test_app),
            base_url="http://testserver",
        ) as client:
            with pytest.raises(WebSocketDisconnect) as exc_info:
                async with aconnect_ws(
                    f"/api/ws/expeditions/{EXPEDITION_ID}?token={token}", client
                ):
                    pass

        assert exc_info.value.code == 1008

    async def test_connect_participant_accepts(
        self,
        test_app: CustomFastAPI,
        map_models_to_orm: None,
        test_db,
        user_factory: Callable[..., Coroutine[Any, Any, UserAggregate]],
        expedition_factory: Callable[..., Coroutine[Any, Any, ExpeditionAggregate]],
        access_token: Callable[..., str],
    ) -> None:
        user: UserAggregate = await user_factory(persist=True, role=Role.chief, id=CHIEF_ID)
        expedition: ExpeditionAggregate = await expedition_factory(
            chief_id=CHIEF_ID, persist=True
        )
        token = access_token(user.email)

        async with httpx.AsyncClient(
            transport=ASGIWebSocketTransport(test_app),
            base_url="http://testserver",
        ) as client:
            async with aconnect_ws(
                f"/api/ws/expeditions/{expedition.id}?token={token}", client
            ) as ws:
                await ws.send_text("ping")
