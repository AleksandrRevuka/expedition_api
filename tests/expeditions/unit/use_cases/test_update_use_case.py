import pytest
from unittest.mock import AsyncMock

from src.modules.expeditions.application.commands.commands import (
    UpdateExpeditionCommand,
)
from src.modules.expeditions.application.use_cases.update_expedition import (
    UpdateExpeditionUseCase,
)
from src.modules.expeditions.domain.exceptions.exceptions import (
    ExpeditionAccessDeniedError,
    ExpeditionNotFoundError,
)
from tests.config import CHIEF_ID, EXPEDITION_ID, make_expedition

pytestmark = pytest.mark.unit


class TestUpdateExpeditionUseCase:

    @pytest.mark.asyncio
    async def test_update_expedition_success(self) -> None:
        expedition = make_expedition()

        mock_repo = AsyncMock()
        mock_repo.get_one_with_relationships.return_value = expedition
        mock_repo.update_one.return_value = expedition

        use_case = UpdateExpeditionUseCase(mock_repo)
        command = UpdateExpeditionCommand(
            expedition_id=EXPEDITION_ID,
            chief_id=CHIEF_ID,
            title="Updated Title",
            description="Updated Description",
        )
        result = await use_case(command)

        assert result == expedition
        mock_repo.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_expedition_not_found_raises_error(self) -> None:
        mock_repo = AsyncMock()
        mock_repo.get_one_with_relationships.return_value = None

        use_case = UpdateExpeditionUseCase(mock_repo)
        command = UpdateExpeditionCommand(
            expedition_id=EXPEDITION_ID,
            chief_id=CHIEF_ID,
            title="Updated Title",
        )

        with pytest.raises(ExpeditionNotFoundError):
            await use_case(command)

    @pytest.mark.asyncio
    async def test_update_expedition_wrong_chief_raises_error(self) -> None:
        from uuid import uuid4

        expedition = make_expedition()

        mock_repo = AsyncMock()
        mock_repo.get_one_with_relationships.return_value = expedition

        use_case = UpdateExpeditionUseCase(mock_repo)
        command = UpdateExpeditionCommand(
            expedition_id=EXPEDITION_ID,
            chief_id=uuid4(),
            title="Updated Title",
        )

        with pytest.raises(ExpeditionAccessDeniedError):
            await use_case(command)
