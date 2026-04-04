from typing import Any, Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from src.common.domain.base_models import AggregateRoot


class BaseAsyncRepository[MT: AggregateRoot](Protocol):
    @property
    def model(self) -> type[MT]: ...

    @property
    def session(self) -> AsyncSession: ...

    async def get_all(self, **filter_by: Any) -> list[MT]: ...

    async def add_one(self, data: dict[str, Any]) -> MT: ...

    async def update_one(self, data: dict[str, Any], **filter_by: Any) -> MT: ...

    async def get_one(self, **filter_by: Any) -> MT | None: ...
