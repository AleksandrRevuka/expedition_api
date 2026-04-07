from collections.abc import Callable
from src.modules.users.domain.aggregates.user import UserAggregate
from src.conf.enums import Role
from src.modules.users.application.commands.commands import CreateUserCommand
from fastapi import status
from httpx import AsyncClient, Response
import pytest


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_register_user_success(async_client: AsyncClient) -> None:
    body_create_user = CreateUserCommand(
        email="i4m9o@example.com",
        password="password",
        first_name="John",
        last_name="Doe",
        role=Role.member,
    )

    response: Response = await async_client.post(
        url="/api/auth/register", json=body_create_user.model_dump(),
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == "John Doe"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_login_user_success(async_client: AsyncClient, user_factory) -> None:
    test_user = await user_factory(persist=True)
    response: Response = await async_client.post(
        url="/api/auth/login",
        data={"username": test_user.email, "password": "password"},
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_get_me_success(async_client: AsyncClient, test_user: UserAggregate, access_token: Callable[..., str]) -> None:
    token = access_token()
    headers = {"Authorization": f"Bearer {token}"}
    response: Response = await async_client.get(
        url="/api/users/me", headers=headers
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_get_user_success(async_client: AsyncClient, test_user: UserAggregate, access_token: Callable[..., str]) -> None:
    token = access_token()
    headers = {"Authorization": f"Bearer {token}"}
    response: Response = await async_client.get(
        url=f"/api/users/{test_user.id}", headers=headers
    )

    assert response.status_code == status.HTTP_200_OK