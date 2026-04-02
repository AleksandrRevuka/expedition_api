from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError

from src.common.exceptions.domain_exceptions import DomainValidationError

# Map exception type → HTTP status code.
# Module-specific exceptions are appended here as modules are implemented.
ERROR_STATUS_MAP: dict[type[Exception], int] = {
    RequestValidationError: 422,
    PydanticValidationError: 422,
    DomainValidationError: 422,
}
