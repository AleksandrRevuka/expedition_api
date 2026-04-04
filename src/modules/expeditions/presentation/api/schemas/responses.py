from datetime import datetime
from uuid import UUID

from src.common.schemas.responses import BaseResponseModel
from src.conf.enums import ExpeditionStatus, MemberState
from src.modules.expeditions.domain.aggregates.expedition import ExpeditionAggregate
from src.modules.expeditions.domain.entities.member import ExpeditionMemberEntity


class MemberResponse(BaseResponseModel):
    id: UUID
    user_id: UUID
    expedition_id: UUID
    state: MemberState
    invited_at: datetime
    confirmed_at: datetime | None

    @classmethod
    def from_domain(cls, member: ExpeditionMemberEntity) -> "MemberResponse":
        return cls(
            id=member.id,
            user_id=member.user_id,
            expedition_id=member.expedition_id,
            state=member.state,
            invited_at=member.invited_at,
            confirmed_at=member.confirmed_at,
        )


class ExpeditionResponse(BaseResponseModel):
    id: UUID
    title: str
    description: str | None
    status: ExpeditionStatus
    chief_id: UUID
    start_at: datetime
    end_at: datetime | None
    capacity: int
    members: list[MemberResponse]

    @classmethod
    def from_domain(cls, expedition: ExpeditionAggregate) -> "ExpeditionResponse":
        return cls(
            id=expedition.id,
            title=expedition.title,
            description=expedition.description,
            status=expedition.status,
            chief_id=expedition.chief_id,
            start_at=expedition.start_at,
            end_at=expedition.end_at,
            capacity=expedition.capacity,
            members=[MemberResponse.from_domain(m) for m in expedition.members],
        )
