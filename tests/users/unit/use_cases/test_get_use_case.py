from src.modules.users.domain.exceptions.exceptions import UserNotFoundError
from tests.config import make_user
from unittest.mock import AsyncMock, MagicMock
from src.modules.users.application.use_cases.get_user import GetUserUseCase
import pytest

pytestmark = pytest.mark.unit


class TestGetUserUseCase:

    @pytest.mark.asyncio
    async def test_get_user_success(self):
        user = make_user()

        mock_repo = MagicMock()
        mock_repo.get_one = AsyncMock(return_value=user)

        use_case = GetUserUseCase(mock_repo)

        result = await use_case(user.id)

        assert result == user

    @pytest.mark.asyncio
    async def test_get_user_error_user_is_not_found(self):
        user = make_user()

        mock_repo = MagicMock()
        mock_repo.get_one = AsyncMock(return_value=None)

        use_case = GetUserUseCase(mock_repo)

        with pytest.raises(UserNotFoundError):
            await use_case(user.id)