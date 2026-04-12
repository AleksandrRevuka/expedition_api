from collections.abc import Callable, Coroutine
from typing import Any

import pytest
from pytest_mock import MockerFixture
from src.modules.users.application.use_cases.login_user import LoginUserUseCase
from src.modules.users.domain.aggregates.user import UserAggregate
from src.modules.users.domain.exceptions.exceptions import InvalidCredentialsError

from src.modules.users.application.commands.commands import LoginUserCommand

pytestmark = pytest.mark.unit


class TestLoginUserUseCase:

    @pytest.mark.asyncio
    async def test_login_user_success(
        self, mocker: MockerFixture, user_factory: Callable[..., Coroutine[Any, Any, UserAggregate]]
    ) -> None:
        user = await user_factory()

        mock_repo = mocker.AsyncMock()
        mock_repo.get_one.return_value = user

        mock_password_service = mocker.MagicMock()
        mock_password_service.verify.return_value = True

        mock_token_service = mocker.MagicMock()
        mock_token_service.create_access_token.return_value = "token"

        use_case = LoginUserUseCase(mock_repo, mock_password_service, mock_token_service)

        command = LoginUserCommand(email=user.email, password="password")
        result = await use_case(command)

        assert result == "token"

    @pytest.mark.asyncio
    async def test_login_user_error_user_is_not_found(
        self, mocker: MockerFixture, user_factory: Callable[..., Coroutine[Any, Any, UserAggregate]]
    ) -> None:
        user = await user_factory()

        mock_repo = mocker.AsyncMock()
        mock_repo.get_one.return_value = None

        mock_password_service = mocker.MagicMock()
        mock_password_service.verify.return_value = True

        mock_token_service = mocker.MagicMock()
        mock_token_service.create_access_token.return_value = "token"

        use_case = LoginUserUseCase(mock_repo, mock_password_service, mock_token_service)

        command = LoginUserCommand(email=user.email, password="password")
        with pytest.raises(InvalidCredentialsError):
            await use_case(command)

    @pytest.mark.asyncio
    async def test_login_user_error_password_is_not_valid(
        self, mocker: MockerFixture, user_factory: Callable[..., Coroutine[Any, Any, UserAggregate]]
    ) -> None:
        user = await user_factory()

        mock_repo = mocker.AsyncMock()
        mock_repo.get_one.return_value = user

        mock_password_service = mocker.MagicMock()
        mock_password_service.verify.return_value = False

        mock_token_service = mocker.MagicMock()
        mock_token_service.create_access_token.return_value = "token"

        use_case = LoginUserUseCase(mock_repo, mock_password_service, mock_token_service)

        command = LoginUserCommand(email=user.email, password="password")
        with pytest.raises(InvalidCredentialsError):
            await use_case(command)
