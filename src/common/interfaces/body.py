from abc import ABC

from pydantic import BaseModel


class AbstractBody(ABC, BaseModel):
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"
