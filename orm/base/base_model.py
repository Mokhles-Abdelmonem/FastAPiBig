from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import Column, Integer, String, select, ForeignKey
from sqlalchemy.orm import as_declarative, declared_attr, declarative_base
import contextlib
from typing import AsyncIterator, Optional, Type, Any

from sqlalchemy.sql.functions import count

DATABASE_URL = "postgresql+asyncpg://SG_USER:SG_PASS@localhost:5432/SG_DB"
DECLARATIVE_BASE = declarative_base()


class ORM:
    def __init__(self, model: "BaseORM"):
        self.model = model

    async def create(self, **kwargs):
        """Create a new record."""
        async for db_session in self.model._get_session():
            instance = self.model(**kwargs)
            db_session.add(instance)
            await db_session.commit()
            await db_session.refresh(instance)
            return instance

    async def get(self, id):
        """Retrieve a record by ID."""
        async for db_session in self.model._get_session():
            return await db_session.get(self.model, id)

    async def update(self, id, **kwargs):
        """Update a record by ID."""
        async for db_session in self.model._get_session():
            instance = await db_session.get(self.model, id)
            if not instance:
                return None
            for key, value in kwargs.items():
                setattr(instance, key, value)
            await db_session.commit()
            await db_session.refresh(instance)
            return instance

    async def delete(self, id):
        """Delete a record by ID."""
        async for db_session in self.model._get_session():
            instance = await db_session.get(self.model, id)
            if not instance:
                return False
            await db_session.delete(instance)
            await db_session.commit()
            return True

    async def all(self):
        """Retrieve all records."""
        async for db_session in self.model._get_session():
            query = select(self.model)
            result = await db_session.execute(query)
            return result.scalars().all()

    async def filter(self, **filters):
        """Filter records by criteria."""
        async for db_session in self.model._get_session():
            query = select(self.model).where(*self._filter_conditions(filters))
            result = await db_session.execute(query)
            return result.scalars().all()

    async def first(self, **filters):
        """Retrieve the first record matching the criteria."""
        async for db_session in self.model._get_session():
            query = select(self.model).where(*self._filter_conditions(filters))
            result = await db_session.execute(query)
            return result.scalars().first()

    async def count(self):
        """Count all records."""
        async for db_session in self.model._get_session():
            result = await db_session.execute(select(count()).select_from(self.model))
            return result.scalar()

    async def exists(self, **filters):
        """Check if any record matches the criteria."""
        return await self.first(**filters) is not None

    async def execute_query(self, query):
        async for db_session in self.model._get_session():
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


@as_declarative()
class BaseORM:
    id: int
    __name__: str

    _db_manager: Optional["DataBaseSessionManager"] = None
    _orm_instance: Optional[ORM] = None

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    @classmethod
    def column_objects(cls):
        """Returns a dictionary of column objects for the model."""
        if hasattr(cls, '__table__'):
            for col in cls.__table__.c:
                column_name = col.name
                column_type = col.type
                is_primary = col.primary_key
                has_relation = bool(col.foreign_keys)

                print(f"Column: {column_name}, Type: {column_type}, Primary: {is_primary}")

                if has_relation:
                    foreign_keys = [fk.target_fullname for fk in col.foreign_keys]
                    print(f"   🔗 Foreign Key Relation to: {foreign_keys}")

                yield col
        return None

    @classmethod
    def initialize(cls, db_manager: "DataBaseSessionManager"):
        """Initialize the Base class with a session manager."""
        cls._db_manager = db_manager

    @classmethod
    async def _get_session(cls) -> AsyncIterator[AsyncSession]:
        """Get an async session."""
        if cls._db_manager is None:
            raise Exception("DataBaseSessionManager is not initialized for Base.")
        async with cls._db_manager.session() as session:
            yield session

    @classmethod
    @property
    def objects(cls) -> ORM:
        """Return an ORM instance for the class."""
        return ORM(_class=cls)

    async def save(self):
        async for db_session in self._get_session():
            merged_instance = await db_session.merge(
                self
            )  # Ensures no duplicate sessions
            await db_session.commit()
            await db_session.refresh(merged_instance)
            return merged_instance  # Return the updated instance


# Define your models by inheriting from Base
class User(BaseORM):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    profile_id = Column(Integer, ForeignKey('profile.id'))  # Example foreign key

class DataBaseSessionManager:
    def __init__(self, database_url: str):
        """Initialize the database engine and sessionmaker with connection pooling."""
        self._engine = create_async_engine(
            url=database_url,
            pool_size=5,  # Adjust pool size as needed
            max_overflow=2,  # Adjust overflow size as needed
            pool_timeout=10,
            pool_recycle=600,
        )
        self._sessionmaker = async_sessionmaker(
            bind=self._engine, expire_on_commit=False, class_=AsyncSession
        )

    async def close(self):
        """Dispose of the engine and reset sessionmaker."""
        if self._engine is None:
            raise Exception("DataBaseSessionManager is not initialized")
        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    async def create_all_tables(self):
        """Create all tables."""
        if self._engine is None:
            raise Exception("DataBaseSessionManager is not initialized")

        async with self._engine.begin() as conn:
            await conn.run_sync(DECLARATIVE_BASE.metadata.create_all)

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Provide an async session."""
        if self._sessionmaker is None:
            raise Exception("DataBaseSessionManager is not initialized")
        async with self._sessionmaker() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e


# Create tables (if not already created)
db_manager = DataBaseSessionManager(DATABASE_URL)
BaseORM.initialize(db_manager)

if __name__ == "__main__":
    test_num = 15
    import asyncio

    async def main():
        await db_manager.create_all_tables()
        #
        # Create multiple users
        user  = User(
            name="John Doe", email=f"john_{test_num}.doe@example.com"
        )
        print([d for d in User.column_objects()])
        # await User.objects.create(
        #     name="Jane Doe", email=f"jane_{test_num}.doe@example.com"
        # )

        # # Update a user
        # user = await User.objects.get(id=33)
        # if user:
        #     user.name = "John Doe Updated"
        #     await user.save()
        #
        # # Delete a user
        # await User.objects.delete(id=33)
        #
        # # Get all users
        # users = await User.objects.all()
        # print([user.__dict__ for user in users])
        #
        # # Filter users
        # filtered_users = await User.objects.filter(name="Jane Doe")
        # print([user.__dict__ for user in filtered_users])
        #
        # # Get the first user
        # first_user = await User.objects.first(name="Jane Doe")
        # print(first_user.__dict__)
        #
        # # Count users
        # user_count = await User.objects.count()
        # print(f"Total users: {user_count}")
        #
        # # Check if a user exists
        # exists = await User.objects.exists(email=f"john_{test_num}.doe@example.com")
        # print(f"User exists: {exists}")

    asyncio.run(main())
