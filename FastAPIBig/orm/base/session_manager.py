from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
import contextlib
from typing import AsyncIterator, Any
from sqlalchemy import create_engine, NullPool


class DataBaseSessionManager:
    def __init__(self, database_url: str, **kwargs: Any):
        """Initialize both async and sync database engines and sessionmakers."""
        # Async Engine & Session
        self._async_engine = create_async_engine(
            url=database_url,
        )
        self._async_sessionmaker = async_sessionmaker(
            bind=self._async_engine, expire_on_commit=False, class_=AsyncSession
        )

    async def close(self):
        """Dispose of the async engine."""
        await self._async_engine.dispose()
        self._async_engine = None
        self._async_sessionmaker = None

    async def create_all_tables(self, base):
        """Create all tables asynchronously."""
        async with self._async_engine.begin() as conn:
            await conn.run_sync(base.metadata.create_all)

    @contextlib.asynccontextmanager
    async def async_session(self) -> AsyncIterator[AsyncSession]:
        """Provide an async session."""
        if self._async_sessionmaker is None:
            raise Exception("DataBaseSessionManager is not initialized")
        async with self._async_sessionmaker() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
