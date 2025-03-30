from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, inspect
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncIterator, Optional, Type, Any
from sqlalchemy.sql.functions import count
from FastAPIBig.orm.base.session_manager import DataBaseSessionManager


class ORMSession:
    """
    ORMSession is a utility class that provides a mechanism to manage and access
    asynchronous database sessions using a session manager.

    Attributes:
        _db_manager (Optional[DataBaseSessionManager]): A class-level attribute that holds
            the reference to the database session manager. It must be initialized before
            using the session-related methods.

    Methods:
        initialize(cls, db_manager: DataBaseSessionManager):
            Initializes the ORMSession class with a database session manager instance.
            This method must be called before attempting to access a database session.

        _async_session(cls) -> AsyncIterator[AsyncSession]:
            Provides an asynchronous context manager for accessing a database session.
            Raises an exception if the session manager is not initialized.
    """
    _db_manager: Optional["DataBaseSessionManager"] = None

    @classmethod
    def initialize(cls, db_manager: "DataBaseSessionManager"):
        """
        Initializes the class with a database session manager.

        This method sets up the database session manager for the class, allowing
        it to interact with the database through the provided `DataBaseSessionManager` instance.

        Args:
            db_manager (DataBaseSessionManager): An instance of the database session manager
                that will be used for database operations.
        """
        cls._db_manager = db_manager

    @classmethod
    async def _async_session(cls) -> AsyncIterator[AsyncSession]:
        """
        Creates an asynchronous session for database operations.

        This method is a coroutine that yields an `AsyncSession` object, which can be used
        to interact with the database asynchronously. It ensures that the session is properly
        managed and closed after use.

        Raises:
            Exception: If the `_db_manager` is not initialized for the Base class.

        Yields:
            AsyncIterator[AsyncSession]: An asynchronous session for database operations.
        """
        if cls._db_manager is None:
            raise Exception("DataBaseSessionManager is not initialized for Base.")
        async with cls._db_manager.async_session() as session:
            yield session


class ORM(ORMSession):
    """
    ORM class provides an abstraction layer for interacting with the database using SQLAlchemy's ORM.
    It includes methods for common CRUD operations, query execution, and validation.

    Methods:
        __init__(model: Type["DeclarativeBase"]):
            Initialize the ORM instance with a specific model.

        create(**kwargs):
            Create a new record in the database.

        get(pk: int):
            Retrieve a record by its primary key (ID).

        update(pk: int, **kwargs):
            Update a record by its primary key (ID) with the provided fields.

        delete(pk: int, model=None):
            Delete a record by its primary key (ID). Optionally, a different model can be specified.

        save(model=None):
            Save changes to the database for the given model instance. Ensures no duplicate sessions.

        all():
            Retrieve all records of the model.

        filter(**filters):
            Retrieve records that match the specified filter criteria.

        first(**filters):
            Retrieve the first record that matches the specified filter criteria.

        count():
            Count the total number of records for the model.

        exists(**filters):
            Check if any record matches the specified filter criteria.

        execute_query(query):
            Execute a custom SQLAlchemy query.

        _filter_conditions(filtered_fields: dict[str, Any] = None):
            Generate filter conditions for queries based on the provided fields.

        select_related(attrs: list[str] = None, **kwargs):
            Retrieve a record along with its related attributes.

        validate_relations(data: BaseModel):
            Validate the relationships of the model based on the provided data.

        validate_unique_fields(data: BaseModel):
            Validate that unique fields in the model do not violate constraints.

    Attributes:
        model: The SQLAlchemy model associated with this ORM instance.
    """
    def __init__(self, model: Type["DeclarativeBase"]):
        self.model = model

    async def create(self, **kwargs):
        """
        Asynchronously creates a new instance of the model with the provided keyword arguments,
        adds it to the database session, commits the transaction, and refreshes the instance
        to reflect the latest state from the database.

        Args:
            **kwargs: Arbitrary keyword arguments representing the fields and their values
                      for the model instance to be created.

        Returns:
            instance: The newly created and persisted instance of the model.

        Raises:
            Any exceptions raised during the database session operations, such as integrity
            errors or connection issues.
        """
        async for db_session in self._async_session():
            instance = self.model(**kwargs)
            db_session.add(instance)
            await db_session.commit()
            await db_session.refresh(instance)
            return instance

    async def get(self, pk: int):
        """
        Retrieve a single record from the database by its primary key.

        Args:
            pk (int): The primary key of the record to retrieve.

        Returns:
            Optional[Base]: The retrieved record as an instance of the model, 
            or None if no record with the specified primary key exists.
        """
        async for db_session in self._async_session():
            result = await db_session.execute(
                select(self.model).filter(self.model.id == pk)
            )
            return result.scalars().first()

    async def update(self, pk, **kwargs):
        """
        Update an instance of the model with the given primary key (pk) and new values.

        Args:
            pk (Any): The primary key of the instance to update.
            **kwargs: Key-value pairs representing the fields to update and their new values.

        Returns:
            Optional[Model]: The updated instance of the model if found, otherwise None.

        Notes:
            - This method uses an asynchronous database session to fetch, update, and save the instance.
            - If the instance with the given primary key does not exist, the method returns None.
            - After updating the instance, the session is committed and the instance is refreshed.
        """
        async for db_session in self._async_session():
            instance = await db_session.get(self.model, pk)
            if not instance:
                return None
            for key, value in kwargs.items():
                setattr(instance, key, value)
            await db_session.commit()
            await db_session.refresh(instance)
            return instance

    async def delete(self, pk, model=None):
        """
        Asynchronously deletes an instance of the specified model by primary key.

        Args:
            pk (Any): The primary key of the instance to delete.
            model (Optional[Type[Base]]): The SQLAlchemy model class. If not provided, 
                the default model associated with the class will be used.

        Returns:
            bool: True if the instance was successfully deleted, False if the instance 
            was not found.

        Raises:
            SQLAlchemyError: If an error occurs during the database operation.
        """
        model = model or self.model
        async for db_session in self._async_session():
            instance = await db_session.get(model, pk)
            if not instance:
                return False
            await db_session.delete(instance)
            await db_session.commit()
            return True

    async def save(self, model=None):
        """
        Save the given model instance to the database.

        If no model is provided, the instance associated with `self.model` will be used.
        The method ensures no duplicate sessions by merging the instance into the current
        database session. After committing the changes, the instance is refreshed to reflect
        the latest state from the database.

        Args:
            model (Optional[BaseModel]): The model instance to save. Defaults to `self.model`.

        Returns:
            BaseModel: The updated and saved model instance.
        """
        model = model or self.model
        async for db_session in self._async_session():
            merged_instance = await db_session.merge(
                model
            )  # Ensures no duplicate sessions
            await db_session.commit()
            await db_session.refresh(merged_instance)
            return merged_instance  # Return the updated instance

    async def all(self):
        """
        Retrieve all records of the model from the database.

        This asynchronous method creates a database session, executes a query
        to select all records of the associated model, and returns the results
        as a list of model instances.

        Returns:
            list: A list of all records of the model.
        """
        async for db_session in self._async_session():
            query = select(self.model)
            result = await db_session.execute(query)
            return result.scalars().all()

    async def filter(self, **filters):
        """
        Filters records in the database based on the provided keyword arguments.

        Args:
            **filters: Arbitrary keyword arguments representing the filter conditions.
                       Each key-value pair corresponds to a column and its desired value.

        Returns:
            list: A list of model instances that match the filter conditions.

        Raises:
            Exception: If there is an issue with the database session or query execution.

        Example:
            # Assuming `self.model` has a column `name`:
            results = await instance.filter(name="John Doe")
        """
        async for db_session in self._async_session():
            query = select(self.model).where(*self._filter_conditions(filters))
            result = await db_session.execute(query)
            return result.scalars().all()

    async def first(self, **filters):
        """
        Retrieve the first record from the database that matches the given filters.

        Args:
            **filters: Arbitrary keyword arguments representing the filter conditions
                       to apply to the query.

        Returns:
            The first matching record as an instance of the model, or None if no match is found.

        Raises:
            Any exceptions raised during the database query execution.
        """
        async for db_session in self._async_session():
            query = select(self.model).where(*self._filter_conditions(filters))
            result = await db_session.execute(query)
            return result.scalars().first()

    async def count(self):
        """
        Asynchronously counts the total number of records in the database table 
        associated with the model.

        Returns:
            int: The total count of records in the table.
        """
        async for db_session in self._async_session():
            result = await db_session.execute(select(count()).select_from(self.model))
            return result.scalar()

    async def exists(self, **filters):
        """
        Asynchronously checks if a record exists in the database that matches the given filters.

        Args:
            **filters: Arbitrary keyword arguments representing the filter criteria.

        Returns:
            bool: True if a matching record exists, False otherwise.
        """
        return await self.first(**filters) is not None

    async def execute_query(self, query):
        """
        Executes a given SQL query within an asynchronous database session.

        Args:
            query: The SQL query to be executed.

        Returns:
            The result of the executed query.

        Note:
            This method uses an asynchronous session to execute the query and 
            returns the result. Ensure that the query is compatible with the 
            database engine being used.
        """
        async for db_session in self._async_session():
            result = await db_session.execute(query)
            return result

    def _filter_conditions(self, filtered_fields: dict[str, Any] = None):
        """
        Generate a list of filter conditions based on the provided dictionary of field-value pairs.

        Args:
            filtered_fields (dict[str, Any], optional): A dictionary where keys are field names 
                and values are the corresponding values to filter by. Defaults to None.

        Returns:
            list: A list of filter conditions to be used in queries.

        Raises:
            AttributeError: If the specified field does not exist in the model.
        """
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
        """
        Asynchronously retrieves a related model instance from the database with optional 
        attributes to refresh.

        Args:
            attrs (list[str], optional): A list of attribute names to refresh on the 
                retrieved model instance. Defaults to an empty list.
            **kwargs: Arbitrary keyword arguments used to filter the query.

        Raises:
            AttributeError: If any attribute in `attrs` does not exist on the model.

        Returns:
            Optional[Model]: The first instance of the model that matches the filter 
                conditions, with the specified attributes refreshed, or `None` if no 
                matching instance is found.
        """
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

    async def validate_relations(self, data: BaseModel):
        """
        Validates the relationships of a given data model instance against the database.

        This method checks if the provided data contains valid foreign key references
        for the relationships defined in the SQLAlchemy model. If a required foreign key
        value is missing or does not correspond to an existing entity in the database,
        an exception is raised.

        Args:
            data (BaseModel): The Pydantic model instance containing the data to validate.

        Raises:
            KeyError: If a required foreign key value is missing in the provided data.
            ValueError: If a foreign key value does not correspond to an existing entity
                        in the database.
        """
        data_dict = data.model_dump()
        for rel in inspect(self.model).relationships:
            for attr in dir(rel):
                if attr.startswith("_"):
                    continue
            local_col = list(rel.local_columns)[0]
            remote_side = list(rel.remote_side)[0]
            if not local_col.primary_key:
                col_val = data_dict.get(local_col.name)
                if col_val is None:
                    raise KeyError(
                        f"Key '{local_col.name}' not found in provided body."
                    )

                async for db_session in self._async_session():
                    result = await db_session.execute(
                        select(rel.mapper.entity).filter(
                            getattr(rel.mapper.entity, remote_side.name) == col_val
                        )
                    )
                    if not result.first():
                        raise ValueError(
                            f"Entity({rel.mapper.entity}) with primary key: {col_val} not found."
                        )

    async def validate_unique_fields(self, data: BaseModel):
        """
        Validates that the unique fields in the provided data do not violate
        the unique constraints defined in the database model.

        Args:
            data (BaseModel): The data to validate, represented as a Pydantic model.

        Raises:
            ValueError: If the primary key is manually included in the data or if
                        a unique constraint is violated for any column.

        Notes:
            - The primary key field is excluded from validation to prevent manual
              overrides.
            - For each column marked as unique, the method checks if the provided
              value already exists in the database. If a duplicate is found, a
              `ValueError` is raised.
        """
        data_dict = data.model_dump()

        # Remove primary key from data to prevent manual override
        pk_column = inspect(self.model).primary_key[0]
        if pk_column in data_dict:
            raise ValueError(f"Cannot create or change primary key '{pk_column.name}'.")

        for column in inspect(self.model).columns:
            if column.unique:
                col_val = data_dict.get(column.name)
                if col_val is not None:
                    async for db_session in self._async_session():
                        result = await db_session.execute(
                            select(self.model).filter(
                                getattr(self.model, column.name) == col_val
                            )
                        )
                        if result.first():
                            raise ValueError(
                                f"Unique constraint violation: '{column.name}' with value '{col_val}' already exists."
                            )
