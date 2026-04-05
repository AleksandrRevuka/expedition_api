import pytest
from unittest.mock import AsyncMock

from src.modules.expeditions.application.commands.commands import (
    DeleteExpeditionCommand,
)
from src.modules.expeditions.application.use_cases.delete_expedition import (
    DeleteExpeditionUseCase,
)
from src.modules.expeditions.domain.exceptions.exceptions import (
    ExpeditionAccessDeniedError,
    ExpeditionNotFoundError,
)
from tests.config import CHIEF_ID, EXPEDITION_ID, make_expedition

pytestmark = pytest.mark.unit


class TestDeleteExpeditionUseCase:

    @pytest.mark.asyncio
    async def test_delete_expedition_success(self) -> None:
        expedition = make_expedition()

        mock_repo = AsyncMock()
        mock_repo.get_one_with_relationships.return_value = expedition

        use_case = DeleteExpeditionUseCase(mock_repo)
        command = DeleteExpeditionCommand(
            expedition_id=EXPEDITION_ID,
            chief_id=CHIEF_ID,
        )
        await use_case(command)

        mock_repo.delete_one.assert_called_once_with(id=EXPEDITION_ID)

    @pytest.mark.asyncio
    async def test_delete_expedition_not_found_raises_error(self) -> None:
        mock_repo = AsyncMock()
        mock_repo.get_one_with_relationships.return_value = None

        use_case = DeleteExpeditionUseCase(mock_repo)
        command = DeleteExpeditionCommand(
            expedition_id=EXPEDITION_ID,
            chief_id=CHIEF_ID,
        )

        with pytest.raises(ExpeditionNotFoundError):
            await use_case(command)

    @pytest.mark.asyncio
    async def test_delete_expedition_wrong_chief_raises_error(self) -> None:
        from uuid import uuid4

        expedition = make_expedition()

        mock_repo = AsyncMock()
        mock_repo.get_one_with_relationships.return_value = expedition

        use_case = DeleteExpeditionUseCase(mock_repo)
        command = DeleteExpeditionCommand(
            expedition_id=EXPEDITION_ID,
            chief_id=uuid4(),
        )

        with pytest.raises(ExpeditionAccessDeniedError):
            await use_case(command)
