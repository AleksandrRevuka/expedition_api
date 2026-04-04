from enum import StrEnum


class Environment(StrEnum):
    dev = "dev"
    prod = "prod"
    test = "test"


class Role(StrEnum):
    chief = "chief"
    member = "member"


class ExpeditionStatus(StrEnum):
    draft = "draft"
    ready = "ready"
    active = "active"
    finished = "finished"


class MemberState(StrEnum):
    invited = "invited"
    confirmed = "confirmed"
