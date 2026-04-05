from src.modules.users.domain.exceptions.exceptions import UserAlreadyExistsError
from src.modules.users.application.commands.commands import CreateUserCommand
from src.modules.users.application.use_cases.create_user import CreateUserUseCase
from unittest.mock import AsyncMock
from tests.config import make_user
import pytest


pytestmark = pytest.mark.unit


class TestCreateUserUseCase:
    @pytest.mark.asyncio
    async def test_create_user(self) -> None:
        user = make_user()

        mock_repo = AsyncMock()
        mock_repo.get_one.return_value = None
        mock_repo.add_one.return_value = user
        
        mock_password_service = AsyncMock()
        mock_password_service.hash.return_value = user.hashed_password

        use_case = CreateUserUseCase(mock_repo, mock_password_service)

        command = CreateUserCommand(
            email=user.email,
            password="password",
            first_name=user.name,
            last_name=user.name,
            role=user.role,)
        result = await use_case(command)

        assert result == user

    @pytest.mark.asyncio
    async def test_create_user_raises_error(self) -> None:
        user = make_user()

        mock_repo = AsyncMock()
        mock_repo.get_one.return_value = user
        mock_repo.add_one.return_value = user

        mock_password_service = AsyncMock()
        mock_password_service.hash.return_value = user.hashed_password

        use_case = CreateUserUseCase(mock_repo, mock_password_service)

        command = CreateUserCommand(
            email=user.email,
            password="password",
            first_name=user.name,
            last_name=user.name,
            role=user.role,)
        with pytest.raises(UserAlreadyExistsError):
            await use_case(command)