from typing import Optional
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    AsyncConnection,
    AsyncEngine,
    async_sessionmaker,
)
import contextlib
from typing import AsyncIterator
from sqlalchemy.orm.decl_api import DeclarativeMeta
from app.database.base import Settings, SETTINGS


class DataBaseSessionManager:
    def __init__(self, settings: Settings, base: DeclarativeMeta):
        """Initialize the database engine and sessionmaker. with connection pooling"""
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker | None = None
        self.host: str = settings.database_url
        self.pool_size: int = 5
        self.max_overflow: int = 20
        self.pool_timeout: int = 10
        self.pool_recycle: int = 600
        self.base: DeclarativeMeta = base  # This is the Base class for your models

        # Create the async engine
        self._engine = create_async_engine(
            url=self.host,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            pool_timeout=self.pool_timeout,
            pool_recycle=self.pool_recycle,
        )

        # Create the async sessionmaker
        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            class_=AsyncSession,
            autocommit=False,
        )

    async def close(self):
        """Dispose of the engine and reset sessionmaker."""
        if self._engine is None:
            raise Exception("DataBaseSessionManager is not initialized")
        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    async def create_all_tables(self):
        """Create all tables using the synchronous Base.metadata.create_all."""
        if self._engine is None:
            raise Exception("DataBaseSessionManager is not initialized")

        async with self._engine.begin() as conn:
            await conn.run_sync(self.base.metadata.create_all)

    @contextlib.asynccontextmanager
    async def _provide_session(self) -> AsyncIterator[AsyncSession]:
        """Provide an async session."""
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")
        async with self._sessionmaker() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        """Provide an async connection."""
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        async with self._engine.connect() as connection:
            try:
                yield connection
            except Exception as e:
                raise e

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Provide an async session."""
        async with self._provide_session() as session:
            yield session
