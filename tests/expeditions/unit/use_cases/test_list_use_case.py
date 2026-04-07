from typing import Callable, Any, Coroutine

import pytest
from pytest_mock import MockerFixture

from src.modules.expeditions.application.use_cases.list_expeditions import ListExpeditionsUseCase
from src.modules.expeditions.domain.aggregates.expedition import ExpeditionAggregate

pytestmark = pytest.mark.unit


class TestListExpeditionsUseCase:

    @pytest.mark.asyncio
    async def test_list_expeditions_success(
        self, mocker: MockerFixture, expedition_factory: Callable[..., Coroutine[Any, Any, ExpeditionAggregate]]
    ) -> None:
        expeditions = [await expedition_factory(), await expedition_factory()]

        mock_repo = mocker.AsyncMock()
        mock_repo.get_all_with_relationships.return_value = expeditions

        use_case = ListExpeditionsUseCase(mock_repo)
        result = await use_case()

        assert result == expeditions
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_list_expeditions_empty(self, mocker: MockerFixture) -> None:
        mock_repo = mocker.AsyncMock()
        mock_repo.get_all_with_relationships.return_value = []

        use_case = ListExpeditionsUseCase(mock_repo)
        result = await use_case()

        assert result == []
