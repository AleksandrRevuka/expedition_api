from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.common.domain.base_models import AggregateRoot, BaseWithTimestamps
from src.conf.enums import ExpeditionStatus, MemberState
from src.modules.expeditions.application.commands.commands import (
    CreateExpeditionCommand,
    UpdateExpeditionCommand,
)
from src.modules.expeditions.domain.entities.member import ExpeditionMemberEntity
from src.modules.expeditions.domain.events import (
    ExpeditionStatusChangedEvent,
    MemberConfirmedEvent,
    MemberInvitedEvent,
    MemberRemovedEvent,
)
from src.modules.expeditions.domain.exceptions import exceptions as exc


@dataclass(kw_only=True)
class ExpeditionAggregate(BaseWithTimestamps, AggregateRoot):
    id: UUID = field(default_factory=uuid4)
    title: str
    description: str | None
    status: ExpeditionStatus = ExpeditionStatus.draft
    chief_id: UUID
    start_at: datetime
    end_at: datetime | None = None
    capacity: int

    members: list[ExpeditionMemberEntity] = field(default_factory=list)

    @staticmethod
    def create(command: CreateExpeditionCommand) -> ExpeditionAggregate:
        return ExpeditionAggregate(**command.model_dump())

    def update(self, command: UpdateExpeditionCommand) -> None:
        self._ensure_chief(command.chief_id)
        if command.title is not None:
            self.title = command.title
        if command.description is not None:
            self.description = command.description

    def invite_member(self, chief_id: UUID, user_id: UUID) -> None:
        self._ensure_chief(chief_id)

        if self.status != ExpeditionStatus.draft:
            raise exc.InvalidExpeditionStateError(
                "Cannot invite members after expedition is not in draft"
            )

        if any(m.user_id == user_id for m in self.members):
            raise exc.MemberAlreadyInvitedError(
                f"User {user_id} is already a member of this expedition"
            )

        member = ExpeditionMemberEntity(
            id=uuid4(),
            expedition_id=self.id,
            user_id=user_id,
            state=MemberState.invited,
            invited_at=datetime.now(UTC),
            confirmed_at=None,
        )
        self.members.append(member)
        self.add_event(MemberInvitedEvent(expedition_id=self.id, user_id=user_id))

    def confirm_member(self, user_id: UUID) -> None:
        if self.status != ExpeditionStatus.draft:
            raise exc.InvalidExpeditionStateError(
                "Cannot confirm members after expedition is not in draft"
            )

        if len(self._confirmed_members()) >= self.capacity:
            raise exc.ExpeditionCapacityExceededError()

        member = self._get_member(user_id)
        member.confirm(user_id)
        self.add_event(MemberConfirmedEvent(expedition_id=self.id, user_id=user_id))

    def remove_member(self, chief_id: UUID, user_id: UUID) -> ExpeditionMemberEntity:
        self._ensure_chief(chief_id)

        if self.status in (ExpeditionStatus.active, ExpeditionStatus.finished):
            raise exc.InvalidExpeditionStateError(
                "Cannot remove members from active or finished expedition"
            )

        member = self._get_member(user_id)
        self.members.remove(member)
        self.add_event(MemberRemovedEvent(expedition_id=self.id, user_id=user_id))
        return member

    def set_ready(self, actor_id: UUID) -> None:
        self._ensure_chief(actor_id)

        if self.status != ExpeditionStatus.draft:
            raise exc.InvalidExpeditionStateError(
                "Only draft expedition can be moved to ready"
            )

        self.status = ExpeditionStatus.ready
        self.add_event(
            ExpeditionStatusChangedEvent(
                expedition_id=self.id,
                new_status=self.status,
                chief_id=self.chief_id,
            )
        )

    def start(self, actor_id: UUID, active_expeditions_by_user: set[UUID]) -> None:
        self._ensure_chief(actor_id)

        if self.status != ExpeditionStatus.ready:
            raise exc.InvalidExpeditionStateError(
                "Only ready expedition can be started"
            )

        now = datetime.now(UTC)
        confirmed = self._confirmed_members()

        if self.start_at > now:
            raise exc.ExpeditionStartTooEarlyError()

        if len(confirmed) < 2:
            raise exc.NotEnoughConfirmedMembersError()

        if len(confirmed) > self.capacity:
            raise exc.ExpeditionCapacityExceededError()

        for member in confirmed:
            if member.user_id in active_expeditions_by_user:
                raise exc.MemberAlreadyInActiveExpeditionError()

        self.status = ExpeditionStatus.active
        self.add_event(
            ExpeditionStatusChangedEvent(
                expedition_id=self.id,
                new_status=self.status,
                chief_id=self.chief_id,
            )
        )

    def finish(self, actor_id: UUID) -> None:
        self._ensure_chief(actor_id)

        if self.status != ExpeditionStatus.active:
            raise exc.InvalidExpeditionStateError(
                "Only active expedition can be finished"
            )

        self.status = ExpeditionStatus.finished
        self.end_at = datetime.now(UTC)
        self.add_event(
            ExpeditionStatusChangedEvent(
                expedition_id=self.id,
                new_status=self.status,
                chief_id=self.chief_id,
            )
        )

    def change_status(
        self,
        actor_id: UUID,
        new_status: ExpeditionStatus,
        active_expeditions_by_user: set[UUID] | None = None,
    ) -> None:
        if new_status == ExpeditionStatus.ready:
            self.set_ready(actor_id)
        elif new_status == ExpeditionStatus.active:
            self.start(actor_id, active_expeditions_by_user or set())
        elif new_status == ExpeditionStatus.finished:
            self.finish(actor_id)
        else:
            raise exc.InvalidExpeditionStateError(
                f"Cannot transition to status: {new_status}"
            )

    def is_owned_by(self, user_id: UUID) -> bool:
        return self.chief_id == user_id

    def is_participant(self, user_id: UUID) -> bool:
        return self.chief_id == user_id or any(
            m.user_id == user_id for m in self.members
        )

    def _get_member(self, user_id: UUID) -> ExpeditionMemberEntity:
        for member in self.members:
            if member.user_id == user_id:
                return member
        raise exc.MemberNotFoundError()

    def _confirmed_members(self) -> list[ExpeditionMemberEntity]:
        return [m for m in self.members if m.state == MemberState.confirmed]

    def _ensure_chief(self, actor_id: UUID) -> None:
        if self.chief_id != actor_id:
            raise exc.ExpeditionAccessDeniedError()
