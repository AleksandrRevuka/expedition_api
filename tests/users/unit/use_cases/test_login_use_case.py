from src.modules.users.domain.exceptions.exceptions import InvalidCredentialsError
from src.modules.users.application.commands.commands import LoginUserCommand
from src.modules.users.application.use_cases.login_user import LoginUserUseCase
from unittest.mock import AsyncMock, MagicMock
from tests.config import make_user
import pytest

pytestmark = pytest.mark.unit


class TestLoginUserUseCase:
    
    @pytest.mark.asyncio
    async def test_login_user_success(self):
        user = make_user()

        mock_repo = AsyncMock()
        mock_repo.get_one.return_value = user

        mock_password_service = MagicMock()
        mock_password_service.verify.return_value = True

        mock_token_service = MagicMock()
        mock_token_service.create_access_token.return_value = "token"

        use_case = LoginUserUseCase(mock_repo, mock_password_service, mock_token_service)

        command = LoginUserCommand(
            email=user.email,
            password="password",
        )
        result = await use_case(command)

        assert result == "token"

    @pytest.mark.asyncio
    async def test_login_user_error_user_is_not_found(self):
        user = make_user()

        mock_repo = AsyncMock()
        mock_repo.get_one.return_value = None

        mock_password_service = MagicMock()
        mock_password_service.verify.return_value = True

        mock_token_service = MagicMock()
        mock_token_service.create_access_token.return_value = "token"

        use_case = LoginUserUseCase(mock_repo, mock_password_service, mock_token_service)

        command = LoginUserCommand(
            email=user.email,
            password="password",
        )
        with pytest.raises(InvalidCredentialsError):
            await use_case(command)

    @pytest.mark.asyncio
    async def test_login_user_error_password_is_not_valid(self):
        user = make_user()

        mock_repo = AsyncMock()
        mock_repo.get_one.return_value = user

        mock_password_service = MagicMock()
        mock_password_service.verify.return_value = False

        mock_token_service = MagicMock()
        mock_token_service.create_access_token.return_value = "token"

        use_case = LoginUserUseCase(mock_repo, mock_password_service, mock_token_service)

        command = LoginUserCommand(
            email=user.email,
            password="password",
        )
        with pytest.raises(InvalidCredentialsError):
            await use_case(command)
