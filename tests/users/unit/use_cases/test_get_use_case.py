from typing import Callable, Any, Coroutine

import pytest
from pytest_mock import MockerFixture

from src.modules.users.application.use_cases.get_user import GetUserUseCase
from src.modules.users.domain.aggregates.user import UserAggregate
from src.modules.users.domain.exceptions.exceptions import UserNotFoundError

pytestmark = pytest.mark.unit


class TestGetUserUseCase:

    @pytest.mark.asyncio
    async def test_get_user_success(
        self, mocker: MockerFixture, user_factory: Callable[..., Coroutine[Any, Any, UserAggregate]]
    ) -> None:
        user = await user_factory()

        mock_repo = mocker.MagicMock()
        mock_repo.get_one = mocker.AsyncMock(return_value=user)

        use_case = GetUserUseCase(mock_repo)
        result = await use_case(user.id)

        assert result == user

    @pytest.mark.asyncio
    async def test_get_user_error_user_is_not_found(
        self, mocker: MockerFixture, user_factory: Callable[..., Coroutine[Any, Any, UserAggregate]]
    ) -> None:
        user = await user_factory()

        mock_repo = mocker.MagicMock()
        mock_repo.get_one = mocker.AsyncMock(return_value=None)

        use_case = GetUserUseCase(mock_repo)

        with pytest.raises(UserNotFoundError):
            await use_case(user.id)
