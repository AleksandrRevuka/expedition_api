from collections.abc import Callable, Coroutine
from typing import Any

import pytest
from pytest_mock import MockerFixture
from src.modules.expeditions.application.commands.commands import ConfirmMemberCommand
from src.modules.expeditions.application.use_cases.confirm_member import ConfirmMemberUseCase
from src.modules.expeditions.domain.aggregates.expedition import ExpeditionAggregate
from src.modules.expeditions.domain.entities.member import ExpeditionMemberEntity
from src.modules.expeditions.domain.exceptions.exceptions import ExpeditionNotFoundError

from src.conf.enums import MemberState
from tests.config import EXPEDITION_ID, MEMBER_ID

pytestmark = pytest.mark.unit


class TestConfirmMemberUseCase:

    @pytest.mark.asyncio
    async def test_confirm_member_success(
        self,
        mocker: MockerFixture,
        expedition_factory: Callable[..., Coroutine[Any, Any, ExpeditionAggregate]],
        member_factory: Callable[..., Coroutine[Any, Any, ExpeditionMemberEntity]],
    ) -> None:
        member = await member_factory(state=MemberState.invited)
        expedition = await expedition_factory(members=[member])

        mock_expeditions = mocker.AsyncMock()
        mock_expeditions.get_one_with_relationships.return_value = expedition

        mock_members = mocker.AsyncMock()

        use_case = ConfirmMemberUseCase(mock_expeditions, mock_members)
        command = ConfirmMemberCommand(expedition_id=EXPEDITION_ID, user_id=MEMBER_ID)
        result = await use_case(command)

        assert result == expedition
        assert result.members[0].state == MemberState.confirmed
        mock_members.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_confirm_member_expedition_not_found_raises_error(self, mocker: MockerFixture) -> None:
        mock_expeditions = mocker.AsyncMock()
        mock_expeditions.get_one_with_relationships.return_value = None

        mock_members = mocker.AsyncMock()

        use_case = ConfirmMemberUseCase(mock_expeditions, mock_members)
        command = ConfirmMemberCommand(expedition_id=EXPEDITION_ID, user_id=MEMBER_ID)

        with pytest.raises(ExpeditionNotFoundError):
            await use_case(command)
