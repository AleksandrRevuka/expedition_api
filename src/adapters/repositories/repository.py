import dataclasses
from typing import Any

from sqlalchemy import Select, delete, insert, inspect, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapper, Session, joinedload, selectinload

from src.common.domain.base_models import BaseDomainModel
from src.common.protocols.repository import (
    BaseAsyncRepository,
    BaseAsyncViewsRepository,
    BaseRepository,
)


def _entity_to_column_values(model: type, entity: Any) -> dict[Any, Any]:
    """Extract column values from a domain entity via the SQLAlchemy imperative mapper.

    Returns {Column: value} pairs using actual SA Column objects as keys. This avoids
    ORM attribute-name resolution in insert/update .values() calls, which would
    incorrectly match Python @property descriptors that share names with table columns.

    Handles composite VOs correctly for Pydantic dataclasses: Pydantic's __init__
    uses object.__setattr__ which bypasses SA's composite descriptor __set__, so
    the composite VO lives in entity.__dict__ but the _-prefixed raw column attrs
    in SA's instance state are unset (None). Reading via SA descriptor would yield
    None; we read from entity.__dict__ directly instead.

    Strategy:
    1. Iterate CompositeProperty mappings (mapper.composites).
       For each: read VO from entity.__dict__ (Pydantic path), fall back to
       SA descriptor (DB-loaded path). Call __composite_values__() to get columns.
    2. Iterate remaining ColumnProperty mappings (mapper.column_attrs), skipping
       columns already covered by a composite.
    """
    mapper = inspect(model)
    assert isinstance(mapper, Mapper)
    values: dict[Any, Any] = {}
    composite_col_keys: set[str] = set()

    for prop in mapper.composites:
        # entity.__dict__ holds the VO for Pydantic-created instances;
        # SA descriptor __get__ reconstructs it for DB-loaded instances.
        composite_value = entity.__dict__.get(prop.key)
        if composite_value is None:
            composite_value = getattr(entity, prop.key, None)
        for i, col in enumerate(prop.columns):
            composite_col_keys.add(col.key)
            values[col] = (
                composite_value.__composite_values__()[i] if composite_value is not None else None
            )

    # Declared dataclass fields on this entity. Columns not in this set are
    # infrastructure-managed (e.g. auto-timestamps) and should not be written
    # when the entity hasn't declared them — dataclasses.replace() doesn't
    # preserve dynamically-injected SA attributes, so they'd be None.
    declared_fields: frozenset[str] = (
        frozenset(f.name for f in dataclasses.fields(entity))
        if dataclasses.is_dataclass(entity)
        else frozenset()
    )

    for prop in mapper.column_attrs:
        col = prop.columns[0]
        if col.key in composite_col_keys:
            continue
        # Skip columns not declared on the entity (e.g. created_at/updated_at)
        # unless entity_declared_fields is empty (non-dataclass fallback: include all).
        if declared_fields and prop.key not in declared_fields:
            continue
        values[col] = getattr(entity, prop.key, None)

    return values


class AsyncRepository[MT: BaseDomainModel](BaseAsyncRepository[MT]):
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

    async def add_one(self, data: MT | dict[str, Any]) -> MT:
        """
        Add a new entity to the database. Accepts either a Pydantic model instance or dictionary of data.

        :param data: Pydantic model or dictionary containing data for the new entity.
        :return: The newly added entity.
        """
        if isinstance(data, dict):
            stmt = insert(self.model).values(**data).returning(self.model)  # type: ignore[arg-type]
            result = await self.session.execute(stmt)
            entity: MT = result.scalar_one()
            return entity
        else:
            # Raw SQL path: session.add() fails for Pydantic dataclasses with
            # composite VOs because Pydantic's __init__ bypasses SA composite
            # descriptor __set__, leaving _-prefixed column attrs unset in SA
            # instance state → INSERT omits those columns → NOT NULL constraint.
            # Uses Column objects as keys to bypass ORM attribute-name resolution
            # (which would incorrectly match Python @property descriptors).
            entity_data = _entity_to_column_values(self.model, data)
            pk_col_names = frozenset(col.key for col in inspect(self.model).primary_key)
            # Exclude None PK values (let DB assign); keep None for other columns (explicit NULL).
            insert_data = {
                col: v
                for col, v in entity_data.items()
                if v is not None or col.key not in pk_col_names
            }
            stmt = insert(self.model).values(insert_data).returning(self.model)
            result = await self.session.execute(stmt)
            entity: MT = result.scalar_one()
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
        if isinstance(data, dict):
            # Convert str keys → Column objects to bypass ORM composite descriptor
            # resolution. update().values(attr_name=val) routes through SA ORM mapper
            # which raises ArgumentError for composite attributes.
            mapper = inspect(self.model)
            assert isinstance(mapper, Mapper)
            col_map = {c.key: c for prop in mapper.column_attrs for c in prop.columns}
            col_keyed = {
                col_map[k]: v for k, v in data.items() if isinstance(k, str) and k in col_map
            }
            stmt = (
                update(self.model).values(col_keyed).filter_by(**filter_by).returning(self.model)
            )
            result = await self.session.execute(stmt)
            entity: MT = result.scalar_one()
            return entity
        else:
            entity_data = _entity_to_column_values(self.model, data)
            pk_col_names = frozenset(col.key for col in inspect(self.model).primary_key)
            update_data = {col: v for col, v in entity_data.items() if col.key not in pk_col_names}
            stmt = (
                update(self.model).values(update_data).filter_by(**filter_by).returning(self.model)
            )
            result = await self.session.execute(stmt)
            return result.scalar_one()

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

    async def save(self, entity: MT) -> MT:
        """
        Save an entity using the aggregate persistence pattern.

        Handles both new entities and updates created via dataclass replace().
        Uses SQL statements directly instead of session.merge() because
        dataclasses.replace() on Pydantic dataclasses creates uninstrumented
        instances that merge() rejects with UnmappedInstanceError.

        Filters entity fields to only mapped columns (auto-excludes non-persisted
        domain attributes). Tries UPDATE first; if no rows affected, falls back
        to INSERT.

        :param entity: Domain entity to persist.
        :return: Persisted entity returned via RETURNING clause.
        """
        mapper = inspect(self._model)
        assert isinstance(mapper, Mapper)
        pk_col_names = frozenset(col.key for col in mapper.primary_key)

        # {Column: value} — Column objects as keys bypass ORM attribute-name resolution,
        # preventing incorrect matches against Python @property descriptors.
        data = _entity_to_column_values(self._model, entity)
        update_data = {col: v for col, v in data.items() if col.key not in pk_col_names}
        pk_filter = {col.key: v for col, v in data.items() if col.key in pk_col_names}

        # New entity: any PK is None → raw SQL INSERT.
        # session.add() fails for Pydantic dataclasses with composite VOs (see add_one()).
        if any(v is None for v in pk_filter.values()):
            insert_data = {col: v for col, v in data.items() if v is not None}
            insert_stmt = insert(self.model).values(insert_data).returning(self.model)
            result = await self.session.execute(insert_stmt)
            return result.scalar_one()

        # Existing entity: try raw UPDATE first (works for dataclasses.replace() instances).
        if update_data:
            update_stmt = (
                update(self.model).filter_by(**pk_filter).values(update_data).returning(self.model)
            )
            result = await self.session.execute(update_stmt)
            saved = result.scalar_one_or_none()
            if saved is not None:
                return saved

        # Exclude None values so SQLAlchemy column defaults apply for omitted fields.
        # Explicitly passing None in values() overrides Python-side defaults (e.g. avatar).
        insert_data = {col: v for col, v in data.items() if v is not None}
        insert_stmt = insert(self.model).values(insert_data).returning(self.model)
        result = await self.session.execute(insert_stmt)
        return result.scalar_one()


class Repository[MT: BaseDomainModel](BaseRepository[MT]):
    """
    Repository implementation for SQLAlchemy models.
    """

    def __init__(self, model: type[MT], session: Session):
        self._model = model
        self._session = session

    @property
    def model(self) -> type[MT]:
        return self._model

    @property
    def session(self) -> Session:
        return self._session

    def get_all(self, **filter_by: Any) -> list[MT]:
        """
        Retrieve all entities of the model from the database.

        :return: List of all entities of the model type.
        """
        stmt = select(self.model).filter_by(**filter_by)
        result = self.session.execute(stmt)
        entities = result.scalars().all()
        return list(entities)

    def add_one(self, data: MT | dict[str, Any]) -> MT:
        """
        Add a new entity to the database. Accepts either a Pydantic model instance or dictionary of data.

        :param data: Pydantic model or dictionary containing data for the new entity.
        :return: The newly added entity.
        """
        if isinstance(data, dict):
            stmt = insert(self.model).values(**data).returning(self.model)  # type: ignore[arg-type]
            result = self.session.execute(stmt)
            entity: MT = result.scalar_one()
            return entity
        else:
            entity_values = _entity_to_column_values(self.model, data)
            pk_col_names = frozenset(col.key for col in inspect(self.model).primary_key)
            insert_values = {
                col: v
                for col, v in entity_values.items()
                if v is not None or col.key not in pk_col_names
            }
            stmt = insert(self.model).values(insert_values).returning(self.model)
            result = self.session.execute(stmt)
            entity = result.scalar_one()
            return entity

    def update_one(self, data: MT | dict[str, Any], **filter_by: Any) -> MT:
        """
        Update an entity in the database based on filter criteria.

        :param data: Pydantic model or dictionary containing the updated data.
        :param filter_by: Key-value pairs for filtering the entity to update.
        :return: The updated entity.
        """
        if isinstance(data, dict):
            stmt = update(self.model).values(**data).filter_by(**filter_by).returning(self.model)  # type: ignore[arg-type]
            result = self.session.execute(stmt)
            entity: MT = result.scalar_one()
            return entity
        else:
            entity_values = _entity_to_column_values(self.model, data)
            pk_col_names = frozenset(col.key for col in inspect(self.model).primary_key)
            update_values = {k: v for k, v in entity_values.items() if k not in pk_col_names}
            stmt = (
                update(self.model)
                .values(**update_values)
                .filter_by(**filter_by)
                .returning(self.model)
            )
            result = self.session.execute(stmt)
            entity = result.scalar_one()
            return entity

    def delete_one(self, **filter_by: Any) -> None:
        """
        Delete an entity based on filter criteria.

        :param filter_by: Key-value pairs to identify the entity to delete.
        """
        stmt = delete(self.model).filter_by(**filter_by).returning(self.model)
        self.session.execute(stmt)

    def get_one(self, **filter_by: Any) -> MT | None:
        """
        Retrieve a single entity based on filter criteria.

        :param filter_by: Key-value pairs to filter the entity.
        :return: The entity if found, or None if not found.
        """
        stmt = select(self.model).filter_by(**filter_by)
        result = self.session.execute(stmt)
        entity = result.scalar_one_or_none()
        return entity if entity else None


class AsyncViewsRepository[MT_View](BaseAsyncViewsRepository[MT_View]):
    """
    Repository implementation for SQLAlchemy models.
    """

    def __init__(self, model: type[MT_View], session: AsyncSession):
        self._model = model
        self._session = session

    @property
    def model(self) -> type[MT_View]:
        return self._model

    @property
    def session(self) -> AsyncSession:
        return self._session

    def _apply_relationship_loaders(
        self, stmt: Select[tuple[MT_View]], relationships: list[str]
    ) -> Select[tuple[MT_View]]:
        """
        Apply eager loading for specified relationships to the SQLAlchemy statement.

        :param stmt: The base SQLAlchemy select statement.
        :param relationships: List of relationships to load.
        :return: Modified statement with eager loading options.
        :raises ValueError: If relationship is missing or direction is unknown.
        """
        mapper: Mapper[MT_View] | None = inspect(self.model)

        if not mapper:
            return stmt

        for relationship in relationships:
            rel_property = mapper.relationships.get(relationship)

            if not rel_property:
                raise ValueError(f"Relationship {relationship} not found in {self.model.__name__}")

            if rel_property.direction.name in {"MANYTOONE", "ONETOONE"}:
                loader = joinedload(getattr(self.model, relationship))
            elif rel_property.direction.name in {"ONETOMANY", "MANYTOMANY"}:
                loader = selectinload(getattr(self.model, relationship))
            else:
                raise ValueError(f"Unknown relationship direction: {rel_property.direction.name}")

            stmt = stmt.options(loader)

        return stmt

    async def get_all(
        self,
        limit: int | None = None,
        offset: int | None = None,
        relationships: list[str] | None = None,
        **filter_by: Any,
    ) -> list[MT_View]:
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
    ) -> MT_View | None:
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
