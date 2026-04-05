import pytest
from unittest.mock import AsyncMock

from src.modules.expeditions.application.use_cases.get_expedition import (
    GetExpeditionUseCase,
)
from src.modules.expeditions.domain.exceptions.exceptions import ExpeditionNotFoundError
from tests.config import EXPEDITION_ID, make_expedition

pytestmark = pytest.mark.unit


class TestGetExpeditionUseCase:

    @pytest.mark.asyncio
    async def test_get_expedition_success(self) -> None:
        expedition = make_expedition()

        mock_repo = AsyncMock()
        mock_repo.get_one_with_relationships.return_value = expedition

        use_case = GetExpeditionUseCase(mock_repo)
        result = await use_case(EXPEDITION_ID)

        assert result == expedition

    @pytest.mark.asyncio
    async def test_get_expedition_not_found_raises_error(self) -> None:
        mock_repo = AsyncMock()
        mock_repo.get_one_with_relationships.return_value = None

        use_case = GetExpeditionUseCase(mock_repo)

        with pytest.raises(ExpeditionNotFoundError):
            await use_case(EXPEDITION_ID)
