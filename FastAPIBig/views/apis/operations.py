"""
This module provides a set of asynchronous operation classes for handling
CRUD operations with validation, pre-processing, and post-processing steps.

Each operation class follows a structured execution flow:
1. **Validation**: Ensures the input data or request meets required constraints.
2. **Pre-processing**: Executes any necessary logic before performing the main operation.
3. **Execution**: Performs the core operation (create, retrieve, list, update, or delete).
4. **Post-processing**: Triggers asynchronous hooks after the operation is completed.
5. **Response Handling**: Returns the processed instance(s) validated against the output schema.

These operation classes are designed to provide a consistent and extensible
approach to handling resource management in an asynchronous environment.
"""

import asyncio
from pydantic import BaseModel
from FastAPIBig.views.apis.base import (
    RegisterCreate,
    RegisterRetrieve,
    RegisterList,
    RegisterDelete,
    RegisterPartialUpdate,
    RegisterUpdate,
)
from fastapi import Request


class CreateOperation(RegisterCreate):
    """
    A class that handles the creation of an operation with validation, pre-processing,
    and post-processing steps.
    """

    async def create(self, request: Request, data: BaseModel):
        """
        Handles the creation of a new instance.
        """
        await self.create_validation(request, data)
        await self.pre_create(request, data)
        instance = await self._create(request, data)
        asyncio.create_task(self.on_create(request, instance))
        return self._get_schema_out_class("create").model_validate(instance.__dict__)

    async def create_validation(self, request: Request, data: BaseModel):
        """
        Asynchronously validates the provided data by performing relation and uniqueness checks.
        """
        await self._model.validate_relations(data)
        await self._model.validate_unique_fields(data)

    async def pre_create(self, request: Request, data: BaseModel):
        """
        Pre-processing hook that is executed before creating a resource.
        """
        pass

    async def _create(self, request: Request, data: BaseModel):
        """
        Asynchronously creates a new record in the database using the provided data.
        """
        return await self._model.create(**data.model_dump())

    async def on_create(self, request: Request, instance):
        """
        Handle the creation event for a given instance.
        """
        pass


class RetrieveOperation(RegisterRetrieve):
    """
    A class that handles the retrieval of an operation with validation, pre-processing,
    and post-processing steps.
    """

    async def get(self, request: Request, pk: int):
        """
        Handles the retrieval of an instance by its primary key.
        """
        await self.pre_get(request, pk)
        instance = await self._get(request, pk)
        await self.get_validation(request, pk, instance)
        asyncio.create_task(self.on_get(request, instance))
        return self._get_schema_out_class("get").model_validate(instance.__dict__)

    async def pre_get(self, request: Request, pk: int):
        """Pre-processing hook that is executed before retrieving a resource."""
        pass

    async def _get(self, request: Request, pk: int):
        """Asynchronously retrieves an instance from the database using the provided primary key."""
        return await self._model.get(pk=pk)

    async def get_validation(self, request: Request, pk: int, instance):
        """Asynchronously validates the retrieved instance, ensuring it exists."""
        if not instance:
            raise KeyError(f"Object({self.model}) with given id: {pk} not found. ")

    async def on_get(self, request: Request, instance):
        """Handles the post-retrieval event for a given instance."""
        pass


class ListOperation(RegisterList):
    """
    A class that handles listing operations with validation, pre-processing,
    and post-processing steps.
    """

    async def list(self, request: Request):
        """
        Handles the retrieval of multiple instances.
        """
        await self.list_validation(request)
        await self.pre_list(request)
        instances = await self._list(request)
        asyncio.create_task(self.on_list(request))
        return [
            self._get_schema_out_class("list").model_validate(instance.__dict__)
            for instance in instances
        ]

    async def list_validation(self, request: Request):
        """Asynchronously validates the request before listing instances."""
        pass

    async def pre_list(self, request: Request):
        """Pre-processing hook that is executed before retrieving the list of resources."""
        pass

    async def _list(self, request: Request):
        """Asynchronously retrieves all instances from the database."""
        return await self._model.all()

    async def on_list(self, request: Request):
        """Handles the post-listing event after instances are retrieved."""
        pass


class UpdateOperation(RegisterUpdate):

    async def update(self, request: Request, pk: int, data: BaseModel):
        await self.update_validation(request, pk, data)
        await self.pre_update(request, pk, data)
        instance = await self._update(request, pk, data)
        asyncio.create_task(self.on_update(request, instance))
        return self._get_schema_out_class("update").model_validate(instance.__dict__)

    async def update_validation(self, request: Request, pk: int, data: BaseModel):
        await self._model.validate_relations(data)
        await self._model.validate_unique_fields(data)

    async def pre_update(self, request: Request, pk: int, data: BaseModel):
        pass

    async def _update(self, request: Request, pk: int, data: BaseModel):
        instance = await self._model.get(pk=pk)
        for key, value in data.model_dump().items():
            setattr(instance, key, value)
        await self._model.save(instance)
        return instance

    async def on_update(self, request: Request, instance):
        pass


class UpdateOperation(RegisterUpdate):
    """
    A class that handles updating an operation with validation, pre-processing,
    and post-processing steps.
    """

    async def update(self, request: Request, pk: int, data: BaseModel):
        """
        Handles the update of an existing instance by its primary key.
        """
        await self.update_validation(request, pk, data)
        await self.pre_update(request, pk, data)
        instance = await self._update(request, pk, data)
        asyncio.create_task(self.on_update(request, instance))
        return self._get_schema_out_class("update").model_validate(instance.__dict__)

    async def update_validation(self, request: Request, pk: int, data: BaseModel):
        """Asynchronously validates the provided data by performing relation and uniqueness checks."""
        await self._model.validate_relations(data)
        await self._model.validate_unique_fields(data)

    async def pre_update(self, request: Request, pk: int, data: BaseModel):
        """Pre-processing hook that is executed before updating a resource."""
        pass

    async def _update(self, request: Request, pk: int, data: BaseModel):
        """
        Asynchronously updates an existing instance in the database using the provided primary key and data.
        """
        instance = await self._model.get(pk=pk)
        for key, value in data.model_dump().items():
            setattr(instance, key, value)
        await self._model.save(instance)
        return instance

    async def on_update(self, request: Request, instance):
        """Handles the post-update event after an instance is updated."""
        pass


class DeleteOperation(RegisterDelete):
    """
    A class that handles deleting an operation with validation, pre-processing,
    and post-processing steps.
    """

    async def delete(self, request: Request, pk: int):
        """
        Handles the deletion of an instance by its primary key.
        """
        await self.delete_validation(request, pk)
        await self.pre_delete(request, pk)
        deleted = await self._delete(request, pk)
        asyncio.create_task(self.on_delete(request, pk, deleted))
        return {"deleted": deleted}

    async def delete_validation(self, request: Request, pk: int):
        """Asynchronously validates the request before deleting an instance."""
        pass

    async def pre_delete(self, request: Request, pk: int):
        """Pre-processing hook that is executed before deleting a resource."""
        pass

    async def _delete(self, request: Request, pk: int):
        """Asynchronously deletes an instance from the database using the provided primary key."""
        await self._model.get(pk=pk)
        return await self._model.delete(pk)

    async def on_delete(self, request: Request, pk: int, deleted: bool):
        """Handles the post-deletion event after an instance is deleted."""
        pass
