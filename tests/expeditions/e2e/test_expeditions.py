import datetime
from collections.abc import Callable, Coroutine
from datetime import UTC
from typing import Any
from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient, Response
from src.modules.expeditions.domain.aggregates.expedition import ExpeditionAggregate
from src.modules.expeditions.domain.entities.member import ExpeditionMemberEntity
from src.modules.expeditions.presentation.api.schemas.requests import (
    ChangeStatusBody,
    CreateExpeditionBody,
    UpdateExpeditionBody,
)

from src.conf.enums import ExpeditionStatus, MemberState, Role
from tests.config import CHIEF_ID, MEMBER_ID, MEMBER_ID_2, USER_ID

type ExpeditionFactory = Callable[..., Coroutine[Any, Any, ExpeditionAggregate]]                                                                                                                                                                                                                                                                                    
type MemberFactory = Callable[..., Coroutine[Any, Any, ExpeditionMemberEntity]]  

pytestmark = pytest.mark.e2e


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_get_list_expeditions_success(
    async_client: AsyncClient,
    user_factory: MemberFactory,
    expedition_factory: ExpeditionFactory,
    access_token: Callable[..., str]
    ) -> None:
    await user_factory(persist=True)
    expeditions = [await expedition_factory(persist=True), await expedition_factory(id=uuid4(),persist=True)]
    token = access_token()
    headers = {"Authorization": f"Bearer {token}"}
    response: Response = await async_client.get(
        url="/api/expeditions",
        headers=headers
    )

    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()
    assert len(response_json) == len(expeditions)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_get_expedition_success(
    async_client: AsyncClient,
    user_factory: MemberFactory,
    expedition_factory: ExpeditionFactory,
    access_token: Callable[..., str]
    ) -> None:
    await user_factory(persist=True)
    expedition = await expedition_factory(persist=True)
    token = access_token()
    headers = {"Authorization": f"Bearer {token}"}
    response: Response = await async_client.get(
        url=f"/api/expeditions/{expedition.id}",
        headers=headers
    )

    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()
    assert response_json["id"] == str(expedition.id)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_create_expedition_success(
    async_client: AsyncClient,
    user_factory: MemberFactory,
    access_token: Callable[..., str]
    ) -> None:
    await user_factory(persist=True, role=Role.chief)
    token = access_token()
    headers = {"Authorization": f"Bearer {token}"}
    command = CreateExpeditionBody(
        title="Test Expedition",
        description="Test Description",
        start_at=datetime.datetime.now(UTC),
        capacity=5
    )

    response: Response = await async_client.post(
        url="/api/expeditions",
        headers=headers,
        json=command.model_dump(mode="json")
    )

    assert response.status_code == status.HTTP_201_CREATED

    response_json = response.json()
    assert response_json["title"] == command.title


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_create_expedition_failure(
    async_client: AsyncClient,
    user_factory: MemberFactory,
    access_token: Callable[..., str]
    ) -> None:
    await user_factory(persist=True, role=Role.member)
    token = access_token()
    headers = {"Authorization": f"Bearer {token}"}
    command = CreateExpeditionBody(
        title="Test Expedition",
        description="Test Description",
        start_at=datetime.datetime.now(UTC),
        capacity=5
    )

    response: Response = await async_client.post(
        url="/api/expeditions",
        headers=headers,
        json=command.model_dump(mode="json")
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_update_expedition_success(
    async_client: AsyncClient,
    user_factory: MemberFactory,
    expedition_factory: ExpeditionFactory,
    access_token: Callable[..., str]
    ) -> None:
    await user_factory(persist=True, role=Role.chief, id=CHIEF_ID)
    expedition = await expedition_factory(persist=True)
    token = access_token()
    headers = {"Authorization": f"Bearer {token}"}
    command = UpdateExpeditionBody(
        title="Expedition",
        description="Description",
    )

    response: Response = await async_client.patch(
        url=f"/api/expeditions/{expedition.id}",
        headers=headers,
        json=command.model_dump(mode="json")
    )

    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()
    assert response_json["title"] == command.title
    assert response_json["description"] == command.description


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_update_expedition_failure(
    async_client: AsyncClient,
    user_factory: MemberFactory,
    expedition_factory: ExpeditionFactory,
    access_token: Callable[..., str]
    ) -> None:
    await user_factory(persist=True, role=Role.member, id=USER_ID)
    expedition = await expedition_factory(persist=True)
    token = access_token()
    headers = {"Authorization": f"Bearer {token}"}
    command = UpdateExpeditionBody(
        title="Expedition",
        description="Description",
    )

    response: Response = await async_client.patch(
        url=f"/api/expeditions/{expedition.id}",
        headers=headers,
        json=command.model_dump(mode="json")
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_delete_expedition_success(
    async_client: AsyncClient,
    user_factory: MemberFactory,
    expedition_factory: ExpeditionFactory,
    access_token: Callable[..., str]
    ) -> None:
    await user_factory(persist=True, role=Role.chief, id=CHIEF_ID)
    expedition = await expedition_factory(persist=True)
    token = access_token()
    headers = {"Authorization": f"Bearer {token}"}

    response: Response = await async_client.delete(
        url=f"/api/expeditions/{expedition.id}",
        headers=headers
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_delete_expedition_failure(
    async_client: AsyncClient,
    user_factory: MemberFactory,
    expedition_factory: ExpeditionFactory,
    access_token: Callable[..., str]
    ) -> None:
    await user_factory(persist=True, role=Role.member, id=USER_ID)
    expedition = await expedition_factory(persist=True)
    token = access_token()
    headers = {"Authorization": f"Bearer {token}"}

    response: Response = await async_client.delete(
        url=f"/api/expeditions/{expedition.id}",
        headers=headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_delete_member_from_expedition_success(
    async_client: AsyncClient,
    user_factory: MemberFactory,
    expedition_factory: ExpeditionFactory,
    member_factory: MemberFactory,
    access_token: Callable[..., str]
    ) -> None:
    await user_factory(persist=True, role=Role.chief, id=CHIEF_ID)
    await user_factory(persist=True, role=Role.member, id=MEMBER_ID, email="test_member@gmail.com")

    expedition = await expedition_factory(persist=True)
    await member_factory(persist=True)
    
    token = access_token()
    headers = {"Authorization": f"Bearer {token}"}

    response: Response = await async_client.delete(
        url=f"/api/expeditions/{expedition.id}/members/{MEMBER_ID}",
        headers=headers
    )

    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()
    assert response_json["id"] == str(expedition.id)
    assert response_json["members"] == []


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_expedition",
    [
        ExpeditionStatus.draft, 
        ExpeditionStatus.ready,
        ExpeditionStatus.active,
        ExpeditionStatus.finished
    ]
)
async def test_e2e_change_status_expedition_success(
    async_client: AsyncClient,
    user_factory: MemberFactory,
    expedition_factory: ExpeditionFactory,
    member_factory: MemberFactory,
    access_token: Callable[..., str],
    status_expedition: ExpeditionStatus
    ) -> None:
    await user_factory(persist=True, role=Role.chief, id=CHIEF_ID)
    await user_factory(persist=True, role=Role.member, id=MEMBER_ID, email="test_member@gmail.com")
    await user_factory(persist=True, role=Role.member, id=MEMBER_ID_2, email="test_member_2@gmail.com")

    if status_expedition == ExpeditionStatus.draft:
        expedition = await expedition_factory(persist=True)

    if status_expedition == ExpeditionStatus.ready:
        expedition = await expedition_factory(persist=True)
        await member_factory(persist=True, state=MemberState.confirmed, user_id=MEMBER_ID)

    if status_expedition == ExpeditionStatus.active:
        expedition = await expedition_factory(persist=True, status=ExpeditionStatus.ready)
        await member_factory(persist=True, state=MemberState.confirmed, user_id=MEMBER_ID)
        await member_factory(persist=True, state=MemberState.confirmed, user_id=MEMBER_ID_2)

    if status_expedition == ExpeditionStatus.finished:
        expedition = await expedition_factory(persist=True, status=ExpeditionStatus.active)
        await member_factory(persist=True, state=MemberState.confirmed, user_id=MEMBER_ID)
        await member_factory(persist=True, state=MemberState.confirmed, user_id=MEMBER_ID_2)

    token = access_token()
    headers = {"Authorization": f"Bearer {token}"}

    body = ChangeStatusBody(
        status=status_expedition
    )

    response: Response = await async_client.patch(
        url=f"/api/expeditions/{expedition.id}/status",
        headers=headers,
        json=body.model_dump(mode="json")
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "current_status, invalid_target",
    [
        (ExpeditionStatus.draft, ExpeditionStatus.active),
        (ExpeditionStatus.ready, ExpeditionStatus.finished),
        (ExpeditionStatus.active, ExpeditionStatus.ready),
        (ExpeditionStatus.finished, ExpeditionStatus.active),
    ]
)
async def test_e2e_change_status_expedition_fail(
    async_client: AsyncClient,
    user_factory: MemberFactory,
    expedition_factory: ExpeditionFactory,
    access_token: Callable[..., str],
    current_status: ExpeditionStatus,
    invalid_target: ExpeditionStatus
    ) -> None:
    await user_factory(persist=True, role=Role.chief, id=CHIEF_ID)
    expedition = await expedition_factory(persist=True, status=current_status)

    token = access_token()
    headers = {"Authorization": f"Bearer {token}"}

    body = ChangeStatusBody(status=invalid_target)

    response: Response = await async_client.patch(
        url=f"/api/expeditions/{expedition.id}/status",
        headers=headers,
        json=body.model_dump(mode="json")
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
