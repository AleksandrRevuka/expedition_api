from abc import ABC

from pydantic import BaseModel, ConfigDict


class AbstractEvent(ABC, BaseModel):
    model_config = ConfigDict(frozen=True)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"
