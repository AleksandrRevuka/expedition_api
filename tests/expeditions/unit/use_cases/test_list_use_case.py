import pytest
from unittest.mock import AsyncMock

from src.modules.expeditions.application.use_cases.list_expeditions import (
    ListExpeditionsUseCase,
)
from tests.config import make_expedition

pytestmark = pytest.mark.unit


class TestListExpeditionsUseCase:

    @pytest.mark.asyncio
    async def test_list_expeditions_success(self) -> None:
        expeditions = [make_expedition(), make_expedition()]

        mock_repo = AsyncMock()
        mock_repo.get_all_with_relationships.return_value = expeditions

        use_case = ListExpeditionsUseCase(mock_repo)
        result = await use_case()

        assert result == expeditions
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_list_expeditions_empty(self) -> None:
        mock_repo = AsyncMock()
        mock_repo.get_all_with_relationships.return_value = []

        use_case = ListExpeditionsUseCase(mock_repo)
        result = await use_case()

        assert result == []
