from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
import contextlib
from typing import AsyncIterator, Iterator
from sqlalchemy import create_engine


class DataBaseSessionManager:
    def __init__(self, async_database_url: str, sync_database_url: str):
        """Initialize both async and sync database engines and sessionmakers."""
        # Async Engine & Session
        self._async_engine = create_async_engine(
            url=async_database_url,
            pool_size=5,
            max_overflow=2,
            pool_timeout=10,
            pool_recycle=600,
        )
        self._async_sessionmaker = async_sessionmaker(
            bind=self._async_engine, expire_on_commit=False, class_=AsyncSession
        )

        # Sync Engine & Session
        self._sync_engine = create_engine(
            url=sync_database_url,
            pool_size=5,
            max_overflow=2,
            pool_timeout=10,
            pool_recycle=600,
        )
        self._sync_sessionmaker = sessionmaker(
            bind=self._sync_engine, expire_on_commit=False, class_=Session
        )

    async def close(self):
        """Dispose of the async engine."""
        if self._async_engine:
            await self._async_engine.dispose()
            self._async_engine = None
            self._async_sessionmaker = None
        if self._sync_engine:
            self._sync_engine.dispose()
            self._sync_engine = None
            self._sync_sessionmaker = None

    async def create_all_tables(self, base):
        """Create all tables asynchronously."""
        if self._async_engine is None:
            raise Exception("DataBaseSessionManager is not initialized")
        async with self._async_engine.begin() as conn:
            await conn.run_sync(base.metadata.create_all)

    def create_all_tables_sync(self, base):
        """Create all tables synchronously."""
        if self._sync_engine is None:
            raise Exception("DataBaseSessionManager is not initialized")
        base.metadata.create_all(self._sync_engine)

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

    @contextlib.contextmanager
    def sync_session(self) -> Iterator[Session]:
        """Provide a sync session."""
        if self._sync_sessionmaker is None:
            raise Exception("DataBaseSessionManager is not initialized")
        session = self._sync_sessionmaker()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
