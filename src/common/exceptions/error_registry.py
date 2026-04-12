from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError

from src.modules.expeditions.domain.exceptions import exceptions as exc_expeditions
from src.modules.users.domain.exceptions import exceptions as exc_users

# Map exception type → HTTP status code.
ERROR_STATUS_MAP: dict[type[Exception], int] = {
    RequestValidationError: 422,
    PydanticValidationError: 422,
    exc_users.InvalidCredentialsError: 401,
    exc_users.UserNotFoundError: 404,
    exc_users.UserAlreadyExistsError: 409,
    exc_expeditions.ExpeditionNotFoundError: 404,
    exc_expeditions.ExpeditionAccessDeniedError: 403,
    exc_expeditions.MemberAlreadyInvitedError: 409,
    exc_expeditions.InvalidStatusTransitionError: 400,
    exc_expeditions.MemberNotFoundError: 404,
    exc_expeditions.InvalidExpeditionStateError: 400,
    exc_expeditions.NotEnoughConfirmedMembersError: 400,
    exc_expeditions.ExpeditionStartTooEarlyError: 400,
    exc_expeditions.ExpeditionCapacityExceededError: 400,
    exc_expeditions.MemberAlreadyInActiveExpeditionError: 400,
    exc_expeditions.MemberConfirmAccessDeniedError: 403,
    exc_expeditions.InvalidMemberStateTransitionError: 400,
    exc_expeditions.InvalidExpeditionMemberRoleError: 400,
}
