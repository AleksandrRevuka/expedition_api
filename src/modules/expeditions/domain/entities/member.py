from datetime import datetime, UTC
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from src.common.domain.base_models import AggregateRoot
from src.conf.enums import MemberState
from src.modules.expeditions.domain.exceptions import exceptions as exc


@dataclass(kw_only=True)
class ExpeditionMemberEntity(AggregateRoot):
    id: UUID = field(default_factory=uuid4)
    expedition_id: UUID
    user_id: UUID
    state: MemberState
    invited_at: datetime
    confirmed_at: datetime | None

    def confirm(self, user_id: UUID) -> None:
        if self.user_id != user_id:
            raise exc.MemberConfirmAccessDeniedError()

        if self.state != MemberState.invited:
            raise exc.InvalidMemberStateTransitionError(
                f"Cannot confirm member from state: {self.state}"
            )

        self.state = MemberState.confirmed
        self.confirmed_at = datetime.now(UTC)
