import pytest
from unittest.mock import AsyncMock

from src.modules.expeditions.application.commands.commands import (
    CreateExpeditionCommand,
)
from src.modules.expeditions.application.use_cases.create_expedition import (
    CreateExpeditionUseCase,
)
from tests.config import CHIEF_ID, PAST_DATE, make_expedition

pytestmark = pytest.mark.unit


class TestCreateExpeditionUseCase:

    @pytest.mark.asyncio
    async def test_create_expedition_success(self) -> None:
        expedition = make_expedition()

        mock_repo = AsyncMock()
        mock_repo.add_one.return_value = expedition

        use_case = CreateExpeditionUseCase(mock_repo)
        command = CreateExpeditionCommand(
            title=expedition.title,
            description=expedition.description or "Test Description",
            chief_id=CHIEF_ID,
            start_at=PAST_DATE,
            capacity=expedition.capacity,
        )
        result = await use_case(command)

        assert result == expedition
        mock_repo.add_one.assert_called_once()
