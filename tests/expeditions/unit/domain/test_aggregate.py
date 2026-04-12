from collections.abc import Callable, Coroutine
from typing import Any
from uuid import uuid4

import pytest
from src.modules.expeditions.domain.aggregates.expedition import ExpeditionAggregate
from src.modules.expeditions.domain.entities.member import ExpeditionMemberEntity
from src.modules.expeditions.domain.exceptions import exceptions as exc

from src.conf.enums import ExpeditionStatus, MemberState
from tests.config import (
    CHIEF_ID,
    EXPEDITION_ID,
    FUTURE_DATE,
    MEMBER_ID,
    PAST_DATE,
)

type ExpeditionFactory = Callable[..., Coroutine[Any, Any, ExpeditionAggregate]]                                                                                                                                                                                                                                                                                    
type MemberFactory = Callable[..., Coroutine[Any, Any, ExpeditionMemberEntity]]  

pytestmark = pytest.mark.unit


class TestExpeditionAggregate:

    @pytest.mark.asyncio
    async def test_create_expedition_success(
        self, expedition_factory: ExpeditionFactory
    ) -> None:
        expedition = await expedition_factory()

        assert expedition.title == "Test Expedition"
        assert expedition.description == "Test Description"
        assert expedition.chief_id == CHIEF_ID
        assert expedition.status == ExpeditionStatus.draft
        assert expedition.capacity == 5
        assert expedition.members == []

    @pytest.mark.asyncio
    async def test_update_expedition_success(
        self, expedition_factory: ExpeditionFactory
    ) -> None:
        from src.modules.expeditions.application.commands.commands import (
            UpdateExpeditionCommand,
        )

        expedition = await expedition_factory()
        command = UpdateExpeditionCommand(
            expedition_id=EXPEDITION_ID,
            chief_id=CHIEF_ID,
            title="New Title",
            description="New Description",
        )
        expedition.update(command)

        assert expedition.title == "New Title"
        assert expedition.description == "New Description"

    @pytest.mark.asyncio
    async def test_update_expedition_wrong_chief_raises_error(
        self, expedition_factory: ExpeditionFactory
    ) -> None:
        from src.modules.expeditions.application.commands.commands import (
            UpdateExpeditionCommand,
        )

        expedition = await expedition_factory()
        command = UpdateExpeditionCommand(
            expedition_id=EXPEDITION_ID,
            chief_id=uuid4(),
            title="New Title",
        )

        with pytest.raises(exc.ExpeditionAccessDeniedError):
            expedition.update(command)

    @pytest.mark.asyncio
    async def test_invite_member_success(
        self, expedition_factory: ExpeditionFactory
    ) -> None:
        expedition = await expedition_factory()
        expedition.invite_member(CHIEF_ID, MEMBER_ID)

        assert len(expedition.members) == 1
        assert expedition.members[0].user_id == MEMBER_ID
        assert expedition.members[0].state == MemberState.invited

        events = expedition.pull_events()
        assert len(events) == 1

    @pytest.mark.asyncio
    async def test_invite_member_wrong_chief_raises_error(
        self, expedition_factory: ExpeditionFactory
    ) -> None:
        expedition = await expedition_factory()

        with pytest.raises(exc.ExpeditionAccessDeniedError):
            expedition.invite_member(uuid4(), MEMBER_ID)

    @pytest.mark.asyncio
    async def test_invite_member_not_draft_raises_error(
        self, expedition_factory: ExpeditionFactory
    ) -> None:
        expedition = await expedition_factory(status=ExpeditionStatus.ready)

        with pytest.raises(exc.InvalidExpeditionStateError):
            expedition.invite_member(CHIEF_ID, MEMBER_ID)

    @pytest.mark.asyncio
    async def test_invite_member_already_invited_raises_error(
        self, expedition_factory: ExpeditionFactory
    ) -> None:
        expedition = await expedition_factory()
        expedition.invite_member(CHIEF_ID, MEMBER_ID)

        with pytest.raises(exc.MemberAlreadyInvitedError):
            expedition.invite_member(CHIEF_ID, MEMBER_ID)

    @pytest.mark.asyncio
    async def test_confirm_member_success(
        self,
        expedition_factory: ExpeditionFactory,
        member_factory: MemberFactory,
    ) -> None:
        member = await member_factory(state=MemberState.invited)
        expedition = await expedition_factory(members=[member])
        expedition.confirm_member(MEMBER_ID)

        assert expedition.members[0].state == MemberState.confirmed

        events = expedition.pull_events()
        assert len(events) == 1

    @pytest.mark.asyncio
    async def test_confirm_member_not_draft_raises_error(
        self,
        expedition_factory: ExpeditionFactory,
        member_factory: MemberFactory,
    ) -> None:
        member = await member_factory(state=MemberState.invited)
        expedition = await expedition_factory(status=ExpeditionStatus.ready, members=[member])

        with pytest.raises(exc.InvalidExpeditionStateError):
            expedition.confirm_member(MEMBER_ID)

    @pytest.mark.asyncio
    async def test_confirm_member_capacity_exceeded_raises_error(
        self,
        expedition_factory: ExpeditionFactory,
        member_factory: MemberFactory,
    ) -> None:
        confirmed_member = await member_factory(user_id=uuid4(), state=MemberState.confirmed)
        invited_member = await member_factory(user_id=MEMBER_ID, state=MemberState.invited)
        expedition = await expedition_factory(capacity=1, members=[confirmed_member, invited_member])

        with pytest.raises(exc.ExpeditionCapacityExceededError):
            expedition.confirm_member(MEMBER_ID)

    @pytest.mark.asyncio
    async def test_remove_member_success(
        self,
        expedition_factory: ExpeditionFactory,
        member_factory: MemberFactory,
    ) -> None:
        member = await member_factory()
        expedition = await expedition_factory(members=[member])
        expedition.remove_member(CHIEF_ID, MEMBER_ID)

        assert len(expedition.members) == 0

        events = expedition.pull_events()
        assert len(events) == 1

    @pytest.mark.asyncio
    async def test_remove_member_wrong_chief_raises_error(
        self,
        expedition_factory: ExpeditionFactory,
        member_factory: MemberFactory,
    ) -> None:
        member = await member_factory()
        expedition = await expedition_factory(members=[member])

        with pytest.raises(exc.ExpeditionAccessDeniedError):
            expedition.remove_member(uuid4(), MEMBER_ID)

    @pytest.mark.asyncio
    async def test_remove_member_active_expedition_raises_error(
        self,
        expedition_factory: ExpeditionFactory,
        member_factory: MemberFactory,
    ) -> None:
        member = await member_factory()
        expedition = await expedition_factory(status=ExpeditionStatus.active, members=[member])

        with pytest.raises(exc.InvalidExpeditionStateError):
            expedition.remove_member(CHIEF_ID, MEMBER_ID)

    @pytest.mark.asyncio
    async def test_set_ready_success(
        self, expedition_factory: ExpeditionFactory
    ) -> None:
        expedition = await expedition_factory(status=ExpeditionStatus.draft)
        expedition.set_ready(CHIEF_ID)

        assert expedition.status == ExpeditionStatus.ready

        events = expedition.pull_events()
        assert len(events) == 1

    @pytest.mark.asyncio
    async def test_set_ready_wrong_chief_raises_error(
        self, expedition_factory: ExpeditionFactory
    ) -> None:
        expedition = await expedition_factory()

        with pytest.raises(exc.ExpeditionAccessDeniedError):
            expedition.set_ready(uuid4())

    @pytest.mark.asyncio
    async def test_set_ready_not_draft_raises_error(
        self, expedition_factory: ExpeditionFactory
    ) -> None:
        expedition = await expedition_factory(status=ExpeditionStatus.ready)

        with pytest.raises(exc.InvalidExpeditionStateError):
            expedition.set_ready(CHIEF_ID)

    @pytest.mark.asyncio
    async def test_start_success(
        self,
        expedition_factory: ExpeditionFactory,
        member_factory: MemberFactory,
    ) -> None:
        m1 = await member_factory(user_id=uuid4(), state=MemberState.confirmed)
        m2 = await member_factory(user_id=uuid4(), state=MemberState.confirmed)
        expedition = await expedition_factory(
            status=ExpeditionStatus.ready,
            start_at=PAST_DATE,
            members=[m1, m2],
        )
        expedition.start(CHIEF_ID, set())

        assert expedition.status == ExpeditionStatus.active

    @pytest.mark.asyncio
    async def test_start_too_early_raises_error(
        self,
        expedition_factory: ExpeditionFactory,
        member_factory: MemberFactory,
    ) -> None:
        m1 = await member_factory(user_id=uuid4(), state=MemberState.confirmed)
        m2 = await member_factory(user_id=uuid4(), state=MemberState.confirmed)
        expedition = await expedition_factory(
            status=ExpeditionStatus.ready,
            start_at=FUTURE_DATE,
            members=[m1, m2],
        )

        with pytest.raises(exc.ExpeditionStartTooEarlyError):
            expedition.start(CHIEF_ID, set())

    @pytest.mark.asyncio
    async def test_start_not_enough_members_raises_error(
        self,
        expedition_factory: ExpeditionFactory,
        member_factory: MemberFactory,
    ) -> None:
        m1 = await member_factory(state=MemberState.confirmed)
        expedition = await expedition_factory(
            status=ExpeditionStatus.ready,
            start_at=PAST_DATE,
            members=[m1],
        )

        with pytest.raises(exc.NotEnoughConfirmedMembersError):
            expedition.start(CHIEF_ID, set())

    @pytest.mark.asyncio
    async def test_start_member_already_in_active_expedition_raises_error(
        self,
        expedition_factory: ExpeditionFactory,
        member_factory: MemberFactory,
    ) -> None:
        m1 = await member_factory(user_id=uuid4(), state=MemberState.confirmed)
        m2 = await member_factory(user_id=uuid4(), state=MemberState.confirmed)
        expedition = await expedition_factory(
            status=ExpeditionStatus.ready,
            start_at=PAST_DATE,
            members=[m1, m2],
        )
        active_users = {m1.user_id}

        with pytest.raises(exc.MemberAlreadyInActiveExpeditionError):
            expedition.start(CHIEF_ID, active_users)

    @pytest.mark.asyncio
    async def test_finish_success(
        self, expedition_factory: ExpeditionFactory
    ) -> None:
        expedition = await expedition_factory(status=ExpeditionStatus.active)
        expedition.finish(CHIEF_ID)

        assert expedition.status == ExpeditionStatus.finished
        assert expedition.end_at is not None

        events = expedition.pull_events()
        assert len(events) == 1

    @pytest.mark.asyncio
    async def test_finish_not_active_raises_error(
        self, expedition_factory: ExpeditionFactory
    ) -> None:
        expedition = await expedition_factory(status=ExpeditionStatus.ready)

        with pytest.raises(exc.InvalidExpeditionStateError):
            expedition.finish(CHIEF_ID)

    @pytest.mark.asyncio
    async def test_is_owned_by_returns_true(
        self, expedition_factory: ExpeditionFactory
    ) -> None:
        expedition = await expedition_factory()

        assert expedition.is_owned_by(CHIEF_ID) is True

    @pytest.mark.asyncio
    async def test_is_owned_by_returns_false(
        self, expedition_factory: ExpeditionFactory
    ) -> None:
        expedition = await expedition_factory()

        assert expedition.is_owned_by(uuid4()) is False

    @pytest.mark.asyncio
    async def test_is_participant_as_chief(
        self, expedition_factory: ExpeditionFactory
    ) -> None:
        expedition = await expedition_factory()

        assert expedition.is_participant(CHIEF_ID) is True

    @pytest.mark.asyncio
    async def test_is_participant_as_member(
        self,
        expedition_factory: ExpeditionFactory,
        member_factory: MemberFactory,
    ) -> None:
        member = await member_factory()
        expedition = await expedition_factory(members=[member])

        assert expedition.is_participant(MEMBER_ID) is True

    @pytest.mark.asyncio
    async def test_is_participant_returns_false(
        self, expedition_factory: ExpeditionFactory
    ) -> None:
        expedition = await expedition_factory()

        assert expedition.is_participant(uuid4()) is False
