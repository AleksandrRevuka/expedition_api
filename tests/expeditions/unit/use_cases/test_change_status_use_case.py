from collections.abc import Callable, Coroutine
from typing import Any
from uuid import uuid4

import pytest
from pytest_mock import MockerFixture
from src.modules.expeditions.application.commands.commands import ChangeExpeditionStatusCommand
from src.modules.expeditions.application.use_cases.change_status import (
    ChangeExpeditionStatusUseCase,
)
from src.modules.expeditions.domain.aggregates.expedition import ExpeditionAggregate
from src.modules.expeditions.domain.entities.member import ExpeditionMemberEntity
from src.modules.expeditions.domain.exceptions.exceptions import ExpeditionNotFoundError

from src.conf.enums import ExpeditionStatus, MemberState
from tests.config import CHIEF_ID, EXPEDITION_ID, PAST_DATE

pytestmark = pytest.mark.unit


class TestChangeExpeditionStatusUseCase:

    @pytest.mark.asyncio
    async def test_change_status_to_ready_success(
        self, mocker: MockerFixture, expedition_factory: Callable[..., Coroutine[Any, Any, ExpeditionAggregate]]
    ) -> None:
        expedition = await expedition_factory(status=ExpeditionStatus.draft)

        mock_expeditions = mocker.AsyncMock()
        mock_expeditions.get_one_with_relationships.return_value = expedition
        mock_expeditions.update_one.return_value = expedition

        mock_members = mocker.AsyncMock()

        use_case = ChangeExpeditionStatusUseCase(mock_expeditions, mock_members)
        command = ChangeExpeditionStatusCommand(
            expedition_id=EXPEDITION_ID,
            chief_id=CHIEF_ID,
            new_status=ExpeditionStatus.ready,
        )
        result = await use_case(command)

        assert result.status == ExpeditionStatus.ready
        mock_expeditions.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_change_status_same_status_returns_early(
        self, mocker: MockerFixture, expedition_factory: Callable[..., Coroutine[Any, Any, ExpeditionAggregate]]
    ) -> None:
        expedition = await expedition_factory(status=ExpeditionStatus.draft)

        mock_expeditions = mocker.AsyncMock()
        mock_expeditions.get_one_with_relationships.return_value = expedition

        mock_members = mocker.AsyncMock()

        use_case = ChangeExpeditionStatusUseCase(mock_expeditions, mock_members)
        command = ChangeExpeditionStatusCommand(
            expedition_id=EXPEDITION_ID,
            chief_id=CHIEF_ID,
            new_status=ExpeditionStatus.draft,
        )
        result = await use_case(command)

        assert result == expedition
        mock_expeditions.update_one.assert_not_called()

    @pytest.mark.asyncio
    async def test_change_status_expedition_not_found_raises_error(self, mocker: MockerFixture) -> None:
        mock_expeditions = mocker.AsyncMock()
        mock_expeditions.get_one_with_relationships.return_value = None

        mock_members = mocker.AsyncMock()

        use_case = ChangeExpeditionStatusUseCase(mock_expeditions, mock_members)
        command = ChangeExpeditionStatusCommand(
            expedition_id=EXPEDITION_ID,
            chief_id=CHIEF_ID,
            new_status=ExpeditionStatus.ready,
        )

        with pytest.raises(ExpeditionNotFoundError):
            await use_case(command)

    @pytest.mark.asyncio
    async def test_change_status_to_active_success(
        self,
        mocker: MockerFixture,
        expedition_factory: Callable[..., Coroutine[Any, Any, ExpeditionAggregate]],
        member_factory: Callable[..., Coroutine[Any, Any, ExpeditionMemberEntity]],
    ) -> None:
        m1 = await member_factory(user_id=uuid4(), state=MemberState.confirmed)
        m2 = await member_factory(user_id=uuid4(), state=MemberState.confirmed)
        expedition = await expedition_factory(
            status=ExpeditionStatus.ready,
            start_at=PAST_DATE,
            members=[m1, m2],
        )

        mock_expeditions = mocker.AsyncMock()
        mock_expeditions.get_one_with_relationships.return_value = expedition
        mock_expeditions.update_one.return_value = expedition

        mock_members = mocker.AsyncMock()
        mock_members.get_users_in_active_expeditions.return_value = set()

        use_case = ChangeExpeditionStatusUseCase(mock_expeditions, mock_members)
        command = ChangeExpeditionStatusCommand(
            expedition_id=EXPEDITION_ID,
            chief_id=CHIEF_ID,
            new_status=ExpeditionStatus.active,
        )
        result = await use_case(command)

        assert result.status == ExpeditionStatus.active

    @pytest.mark.asyncio
    async def test_change_status_to_finished_success(
        self, mocker: MockerFixture, expedition_factory: Callable[..., Coroutine[Any, Any, ExpeditionAggregate]]
    ) -> None:
        expedition = await expedition_factory(status=ExpeditionStatus.active)

        mock_expeditions = mocker.AsyncMock()
        mock_expeditions.get_one_with_relationships.return_value = expedition
        mock_expeditions.update_one.return_value = expedition

        mock_members = mocker.AsyncMock()

        use_case = ChangeExpeditionStatusUseCase(mock_expeditions, mock_members)
        command = ChangeExpeditionStatusCommand(
            expedition_id=EXPEDITION_ID,
            chief_id=CHIEF_ID,
            new_status=ExpeditionStatus.finished,
        )
        result = await use_case(command)

        assert result.status == ExpeditionStatus.finished
