from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import contextlib
from typing import AsyncIterator, Any


class DataBaseSessionManager:
    """
    DataBaseSessionManager is a utility class for managing asynchronous database sessions 
    and operations using SQLAlchemy. It provides methods to initialize database engines, 
    create tables, and manage database sessions.

    Attributes:
        _async_engine (AsyncEngine): The asynchronous database engine.
        _async_sessionmaker (async_sessionmaker): The sessionmaker for creating async sessions.

    Methods:
        __init__(database_url: str, **kwargs: Any):
            Initializes the async database engine and sessionmaker.
        close():
            Disposes of the async engine and cleans up resources.
        create_all_tables(base):
            Creates all tables defined in the provided SQLAlchemy declarative base.
        async_session():
            Provides an asynchronous context manager for database sessions.
    """
    def __init__(self, database_url: str, **kwargs: Any):
        """Initializes the SessionManager with a database URL and optional keyword arguments."""
        self._async_engine = create_async_engine(
            url=database_url,
        )
        self._async_sessionmaker = async_sessionmaker(
            bind=self._async_engine, expire_on_commit=False, class_=AsyncSession
        )

    async def close(self):
        """
        Asynchronously closes the database connection and disposes of the engine.

        This method disposes of the asynchronous database engine, effectively 
        closing all connections. It also sets the engine and sessionmaker 
        attributes to None to release resources.

        Raises:
            Any exception that may occur during the disposal of the engine.
        """
        await self._async_engine.dispose()
        self._async_engine = None
        self._async_sessionmaker = None

    async def create_all_tables(self, base):
        """
        Asynchronously creates all tables defined in the provided SQLAlchemy Base metadata.

        Args:
            base (sqlalchemy.ext.declarative.api.DeclarativeMeta): 
                The SQLAlchemy Base class containing the metadata for table definitions.

        Returns:
            None
        """
        async with self._async_engine.begin() as conn:
            await conn.run_sync(base.metadata.create_all)

    @contextlib.asynccontextmanager
    async def async_session(self) -> AsyncIterator[AsyncSession]:
        """
        Provides an asynchronous context manager for database sessions.

        This method yields an `AsyncSession` object that can be used to interact
        with the database. It ensures proper handling of transactions by committing
        changes if no exceptions occur, or rolling back changes in case of an error.

        Raises:
            Exception: If the `DataBaseSessionManager` is not initialized.

        Yields:
            AsyncIterator[AsyncSession]: An asynchronous session object for database operations.
        """
        if self._async_sessionmaker is None:
            raise Exception("DataBaseSessionManager is not initialized")
        async with self._async_sessionmaker() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
