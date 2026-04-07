from src.conf.logging_config import LOGGER
from sqlalchemy.orm import Mapper, joinedload, selectinload
from typing import Any

from sqlalchemy import delete, insert, select, update, Select, inspect
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.domain.base_models import AggregateRoot
from src.common.protocols.repository import BaseAsyncRepository


class AsyncRepository[MT: AggregateRoot](BaseAsyncRepository[MT]):
    """
    Repository implementation for SQLAlchemy models.
    """

    def __init__(self, model: type[MT], session: AsyncSession):
        self._model = model
        self._session = session

    @property
    def model(self) -> type[MT]:
        return self._model

    @property
    def session(self) -> AsyncSession:
        return self._session

    async def get_all(self, **filter_by: Any) -> list[MT]:
        """
        Retrieve all entities of the model from the database.

        :return: List of all entities of the model type.
        """
        stmt = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(stmt)
        entities = result.scalars().all()
        assert isinstance(entities, list)
        return entities

    def _strip_relationships(self, data: dict[str, Any]) -> dict[str, Any]:
        mapper: Mapper[MT] | None = inspect(self.model)
        if not mapper:
            return data
        rel_keys = {r.key for r in mapper.relationships}
        return {k: v for k, v in data.items() if k not in rel_keys}

    async def add_one(self, data: MT | dict[str, Any]) -> MT:
        """
        Add a new entity to the database. Accepts either a Pydantic model instance or dictionary of data.

        :param data: Pydantic model or dictionary containing data for the new entity.
        :return: The newly added entity.
        """
        data_dict = data if isinstance(data, dict) else data.to_dict()
        data_dict = self._strip_relationships(data_dict)

        stmt = insert(self.model).values(**data_dict)
        await self.session.execute(stmt)
        entity: MT = self.model(**data_dict)
        return entity

    async def update_one(
        self,
        data: MT | dict[str, Any],
        **filter_by: Any,
    ) -> MT:
        """
        Update an entity in the database based on filter criteria.

        :param data: Pydantic model or dictionary containing the updated data.
        :param filter_by: Key-value pairs for filtering the entity to update.
        :return: The updated entity.
        """
        data_dict = data if isinstance(data, dict) else data.to_dict()
        data_dict = self._strip_relationships(data_dict)

        stmt = (
            update(self.model)
            .values(**data_dict)
            .filter_by(**filter_by)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        entity: MT = result.scalar_one()
        return entity

    async def delete_one(
        self,
        **filter_by: Any,
    ) -> None:
        """
        Delete an entity based on filter criteria.

        :param filter_by: Key-value pairs to identify the entity to delete.
        """
        stmt = delete(self.model).filter_by(**filter_by).returning(self.model)
        await self.session.execute(stmt)

    async def get_one(self, **filter_by: Any) -> MT | None:
        """
        Retrieve a single entity based on filter criteria.

        :param filter_by: Key-value pairs to filter the entity.
        :return: The entity if found, or None if not found.
        """
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        entity = result.scalar_one_or_none()
        return entity if entity else None

    def _apply_relationship_loaders(
        self, stmt: Select[tuple[MT]], relationships: list[str]
    ) -> Select[tuple[MT]]:
        """
        Apply eager loading for specified relationships to the SQLAlchemy statement.

        :param stmt: The base SQLAlchemy select statement.
        :param relationships: List of relationships to load.
        :return: Modified statement with eager loading options.
        :raises ValueError: If relationship is missing or direction is unknown.
        """
        mapper: Mapper[MT] | None = inspect(self.model)

        if not mapper:
            return stmt

        for relationship in relationships:
            rel_property = mapper.relationships.get(relationship)

            if not rel_property:
                raise ValueError(
                    f"Relationship {relationship} not found in {self.model.__name__}"
                )

            if rel_property.direction.name in {"MANYTOONE", "ONETOONE"}:
                loader = joinedload(getattr(self.model, relationship))
            elif rel_property.direction.name in {"ONETOMANY", "MANYTOMANY"}:
                loader = selectinload(getattr(self.model, relationship))
            else:
                raise ValueError(
                    f"Unknown relationship direction: {rel_property.direction.name}"
                )

            stmt = stmt.options(loader)

        return stmt

    async def get_all_with_relationships(
        self,
        limit: int | None = None,
        offset: int | None = None,
        relationships: list[str] | None = None,
        **filter_by: Any,
    ) -> list[MT]:
        """
        Retrieve all entities of the model from the database, optionally loading related entities.

        :param limit: Maximum number of entities to retrieve.
        :param offset: Number of entities to skip.
        :param relationships: List of related entities to load eagerly.
        :param filter_by: Key-value pairs for filtering the main entity.
        :return: List of retrieved entities.
        :raises ValueError: If a specified relationship is not found or has an unknown direction.
        """
        stmt = select(self.model).filter_by(**filter_by)

        if relationships:
            stmt = self._apply_relationship_loaders(stmt, relationships)

        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)

        result = await self.session.execute(stmt)
        entities = result.scalars().all()
        assert isinstance(entities, list)
        return entities

    async def get_one_with_relationships(
        self,
        relationships: list[str] | None = None,
        **filter_by: Any,
    ) -> MT | None:
        """
        Retrieve a single entity with optional related entities loaded eagerly.

        :param relationships: List of related entities to load.
        :param filter_by: Key-value pairs for filtering the main entity.
        :return: The entity with specified relationships, or None if not found.
        :raises ValueError: If a specified relationship is not found or has an unknown direction.
        """
        stmt = select(self.model).filter_by(**filter_by)

        if relationships:
            stmt = self._apply_relationship_loaders(stmt, relationships)

        result = await self.session.execute(stmt)
        entity = result.unique().scalar_one_or_none()
        return entity if entity else None
