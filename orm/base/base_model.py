from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import (
    declarative_base,
    Session,
)
from typing import AsyncIterator, Optional, Type, Any, Iterator
from sqlalchemy.sql.functions import count
from orm.base.session_manager import DataBaseSessionManager


DECLARATIVE_BASE = declarative_base()

class ORMSession:
    _db_manager: Optional["DataBaseSessionManager"] = None

    @classmethod
    def initialize(cls, db_manager: "DataBaseSessionManager"):
        """Initialize the Base class with a session manager."""
        cls._db_manager = db_manager

    @classmethod
    async def _async_session(cls) -> AsyncIterator[AsyncSession]:
        """Get an async session."""
        if cls._db_manager is None:
            raise Exception("DataBaseSessionManager is not initialized for Base.")
        async with cls._db_manager.async_session() as session:
            yield session

    @classmethod
    def _sync_session(cls) -> Iterator[Session]:
        """Get an async session."""
        if cls._db_manager is None:
            raise Exception("DataBaseSessionManager is not initialized for Base.")
        with cls._db_manager.sync_session() as session:
            yield session


class ORM(ORMSession):
    def __init__(self, model: Type["DECLARATIVE_BASE"]):
        self.model = model

    async def create(self, **kwargs):
        """Create a new record."""
        async for db_session in self._async_session():
            instance = self.model(**kwargs)
            db_session.add(instance)
            await db_session.commit()
            await db_session.refresh(instance)
            return instance

    async def get(self, pk: int):
        """Retrieve a record by ID."""
        for db_session in self._sync_session():
            result = db_session.execute(select(self.model).filter(self.model.id == pk))
            return result.scalars().first()

    async def update(self, pk, **kwargs):
        """Update a record by ID."""
        async for db_session in self._async_session():
            instance = await db_session.get(self.model, pk)
            if not instance:
                return None
            for key, value in kwargs.items():
                setattr(instance, key, value)
            await db_session.commit()
            await db_session.refresh(instance)
            return instance

    async def delete(self, pk, model = None):
        """Delete a record by ID."""
        model = model or self.model
        async for db_session in self._async_session():
            instance = await db_session.get(model, pk)
            if not instance:
                return False
            await db_session.delete(instance)
            await db_session.commit()
            return True


    async def save(self, model = None):
        model = model or self.model
        async for db_session in self._async_session():
            merged_instance = await db_session.merge(
                model
            )  # Ensures no duplicate sessions
            await db_session.commit()
            await db_session.refresh(merged_instance)
            return merged_instance  # Return the updated instance

    async def all(self):
        """Retrieve all records."""
        async for db_session in self._async_session():
            query = select(self.model)
            result = await db_session.execute(query)
            return result.scalars().all()

    async def filter(self, **filters):
        """Filter records by criteria."""
        async for db_session in self._async_session():
            query = select(self.model).where(*self._filter_conditions(filters))
            result = await db_session.execute(query)
            return result.scalars().all()

    async def first(self, **filters):
        """Retrieve the first record matching the criteria."""
        async for db_session in self._async_session():
            query = select(self.model).where(*self._filter_conditions(filters))
            result = await db_session.execute(query)
            return result.scalars().first()

    async def count(self):
        """Count all records."""
        async for db_session in self._async_session():
            result = await db_session.execute(select(count()).select_from(self.model))
            return result.scalar()

    async def exists(self, **filters):
        """Check if any record matches the criteria."""
        return await self.first(**filters) is not None

    async def execute_query(self, query):
        async for db_session in self._async_session():
            result = await db_session.execute(query)
            return result

    def _filter_conditions(self, filtered_fields: dict[str, Any] = None):
        filter_conditions = []
        fields = filtered_fields or {}
        for attr, value in fields.items():
            if hasattr(self.model, attr):
                filter_conditions.append(getattr(self.model, attr) == value)
            else:
                raise AttributeError(
                    f"Model {self.model.__name__} does not have '{attr}' attribute"
                )
        return filter_conditions

    async def select_related(self, attrs: list[str] = None, **kwargs):
        attrs = attrs or []
        for attr in attrs:
            if not hasattr(self.model, attr):
                raise AttributeError(
                    f"Model {self.__name__} does not have '{attr}' attribute"
                )
        async for db_session in self._async_session():
            result = await db_session.execute(
                select(self.model).filter(*self._filter_conditions(kwargs))
            )
            instance = result.scalars().first()
            if not instance:
                return None
            await db_session.refresh(instance, attrs)
            return instance


DATABASE_URL_ASYNC = "postgresql+asyncpg://SG_USER:SG_PASS@localhost:5432/SG_DB"
DATABASE_URL_SYNC = "postgresql+psycopg://SG_USER:SG_PASS@localhost:5432/SG_DB"

db_manager = DataBaseSessionManager(DATABASE_URL_ASYNC, DATABASE_URL_SYNC)
ORMSession.initialize(db_manager)
