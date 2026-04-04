from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    message: str = Field(examples=["Resource not found"])
    exception: str | None = Field(default=None, examples=["NotFoundError: ..."])
    error: bool = Field(default=True, frozen=True)

    @classmethod
    def respond(cls, message: str, exception: str | None = None) -> dict[str, str]:
        return cls(message=message, exception=exception).model_dump()


class SuccessResponse(BaseModel):
    message: str = Field(examples=["Operation successful"])
    error: bool = Field(default=False, frozen=True)

    @classmethod
    def respond(cls, message: str = "") -> dict[str, str]:
        return cls(message=message).model_dump()


class BaseResponseModel(BaseModel): ...
