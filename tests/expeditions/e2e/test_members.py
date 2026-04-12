from collections.abc import Callable, Coroutine
from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient, Response
from src.modules.expeditions.domain.aggregates.expedition import ExpeditionAggregate
from src.modules.expeditions.domain.entities.member import ExpeditionMemberEntity
from src.modules.expeditions.presentation.api.schemas.requests import InviteMemberBody

from src.conf.enums import MemberState, Role
from tests.config import CHIEF_ID, MEMBER_ID

type ExpeditionFactory = Callable[..., Coroutine[Any, Any, ExpeditionAggregate]]                                                                                                                                                                                                                                                                                    
type MemberFactory = Callable[..., Coroutine[Any, Any, ExpeditionMemberEntity]]  

pytestmark = pytest.mark.e2e


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_invite_member_success(
    async_client: AsyncClient,
    user_factory: MemberFactory,
    expedition_factory: ExpeditionFactory,
    access_token: Callable[..., str]
    ) -> None:
    chief =await user_factory(persist=True, role=Role.chief, id=CHIEF_ID)
    await user_factory(persist=True, role=Role.member, id=MEMBER_ID, email="test_member@gmail.com")
    expedition = await expedition_factory(persist=True)

    token = access_token()
    headers = {"Authorization": f"Bearer {token}"}

    body = InviteMemberBody(user_id=MEMBER_ID)

    response: Response = await async_client.post(
        url=f"/api/expeditions/{expedition.id}/members/invite",
        headers=headers,
        json=body.model_dump(mode="json")
    )

    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()
    assert response_json["chief_id"] == str(chief.id)
    assert response_json["members"][0]["user_id"] == str(MEMBER_ID)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_invite_member_fail(
    async_client: AsyncClient,
    user_factory: MemberFactory,
    expedition_factory: ExpeditionFactory,
    access_token: Callable[..., str]
    ) -> None:
    await user_factory(persist=True, role=Role.chief, id=CHIEF_ID)
    await user_factory(persist=True, role=Role.member, id=MEMBER_ID, email="test_member@gmail.com")
    expedition = await expedition_factory(persist=True)

    token = access_token()
    headers = {"Authorization": f"Bearer {token}"}

    body = InviteMemberBody(user_id=CHIEF_ID)

    response: Response = await async_client.post(
        url=f"/api/expeditions/{expedition.id}/members/invite",
        headers=headers,
        json=body.model_dump(mode="json")
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_confirm_member_success(
    async_client: AsyncClient,
    user_factory: MemberFactory,
    expedition_factory: ExpeditionFactory,
    member_factory: MemberFactory,
    access_token: Callable[..., str]
    ) -> None:
    await user_factory(persist=True, role=Role.chief, id=CHIEF_ID)
    await user_factory(persist=True, role=Role.member, id=MEMBER_ID, email="test_member@gmail.com")
    expedition = await expedition_factory(persist=True)
    await member_factory(persist=True, user_id=MEMBER_ID)

    token = access_token(email="test_member@gmail.com")
    headers = {"Authorization": f"Bearer {token}"}

    response: Response = await async_client.post(
        url=f"/api/expeditions/{expedition.id}/members/confirm",
        headers=headers
    )

    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()
    assert response_json["chief_id"] == str(CHIEF_ID)
    assert response_json["members"][0]["user_id"] == str(MEMBER_ID)
    assert response_json["members"][0]["state"] == MemberState.confirmed