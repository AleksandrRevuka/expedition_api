from typing import Callable, Any, Coroutine

import pytest
from pytest_mock import MockerFixture

from src.modules.users.application.commands.commands import CreateUserCommand
from src.modules.users.application.use_cases.create_user import CreateUserUseCase
from src.modules.users.domain.aggregates.user import UserAggregate
from src.modules.users.domain.exceptions.exceptions import UserAlreadyExistsError

pytestmark = pytest.mark.unit


class TestCreateUserUseCase:

    @pytest.mark.asyncio
    async def test_create_user(
        self,
        mocker: MockerFixture,
        user_factory: Callable[..., Coroutine[Any, Any, UserAggregate]],
    ) -> None:
        user = await user_factory()

        mock_repo = mocker.AsyncMock()
        mock_repo.get_one.return_value = None
        mock_repo.add_one.return_value = user

        mock_password_service = mocker.AsyncMock()
        mock_password_service.hash.return_value = user.hashed_password

        use_case = CreateUserUseCase(mock_repo, mock_password_service)

        command = CreateUserCommand(
            email=user.email,
            password="password",
            first_name=user.name,
            last_name=user.name,
            role=user.role,
        )
        result = await use_case(command)

        assert result == user

    @pytest.mark.asyncio
    async def test_create_user_raises_error(
        self,
        mocker: MockerFixture,
        user_factory: Callable[..., Coroutine[Any, Any, UserAggregate]],
    ) -> None:
        user = await user_factory()

        mock_repo = mocker.AsyncMock()
        mock_repo.get_one.return_value = user
        mock_repo.add_one.return_value = user

        mock_password_service = mocker.AsyncMock()
        mock_password_service.hash.return_value = user.hashed_password

        use_case = CreateUserUseCase(mock_repo, mock_password_service)

        command = CreateUserCommand(
            email=user.email,
            password="password",
            first_name=user.name,
            last_name=user.name,
            role=user.role,
        )
        with pytest.raises(UserAlreadyExistsError):
            await use_case(command)
