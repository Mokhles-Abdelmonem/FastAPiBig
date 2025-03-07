import asyncio

from pydantic import BaseModel
from views.apis.base import (
    RegisterCreate,
    RegisterRetrieve,
    RegisterList,
    RegisterDelete,
    RegisterPartialUpdate,
    RegisterUpdate,
)
from fastapi import Request


class CreateOperation(RegisterCreate):

    async def create(self, request: Request, data: BaseModel):
        await self.pre_create(request, data)
        instance = await self._create(request, data)
        asyncio.create_task(self.on_create(request, instance))
        return self.schema_out.model_validate(instance.__dict__)

    async def _create(self, request: Request, data: BaseModel):
        return await self._model.create(**data.model_dump())

    async def pre_create(self, request: Request, data: BaseModel):
        pass

    async def on_create(self, request: Request, instance):
        pass


class RetrieveOperation(RegisterRetrieve):

    async def get(self, request: Request, pk: int):
        await self.pre_get(request, pk)
        instance = await self._get(request, pk)
        asyncio.create_task(self.on_get(request, instance))
        return self.schema_out.model_validate(instance.__dict__)

    async def _get(self, request: Request, pk: int):
        return await self._model.get(pk=pk)

    async def pre_get(self, request: Request, pk: int):
        pass

    async def on_get(self, request: Request, instance):
        pass


class UpdateOperation(RegisterUpdate):

    async def update(self, request: Request, pk: int, data: BaseModel):
        await self.pre_update(request, pk, data)
        instance = await self._update(request, pk, data)
        asyncio.create_task(self.on_update(request, instance))
        return self.schema_out.model_validate(instance.__dict__)

    async def _update(self, request: Request, pk: int, data: BaseModel):
        instance = await self._model.get(pk=pk)
        for key, value in data.model_dump().items():
            setattr(instance, key, value)
        await self._model.save(instance)
        return instance

    async def pre_update(self, request: Request, pk: int, data: BaseModel):
        pass

    async def on_update(self, request: Request, instance):
        pass


class PartialUpdateOperation(RegisterPartialUpdate):

    async def partial_update(self, request: Request, pk: int, data: BaseModel):
        await self.pre_update(request, pk, data)
        instance = await self._partial_update(request, pk, data)
        asyncio.create_task(self.on_update(request, instance))
        return self.schema_out.model_validate(instance.__dict__)

    async def _partial_update(self, request: Request, pk: int, data: BaseModel):
        instance = await self._model.get(pk=pk)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(instance, key, value)
        await self._model.save(instance)
        return instance

    async def pre_update(self, request: Request, pk: int, data: BaseModel):
        pass

    async def on_update(self, request: Request, instance):
        pass


class DeleteOperation(RegisterDelete):

    async def delete(self, request: Request, pk: int):
        await self.pre_delete(request, pk)
        instance = await self._delete(request, pk)
        asyncio.create_task(self.on_delete(request, instance))

    async def _delete(self, request: Request, pk: int):
        instance = await self._model.get(pk=pk)
        await self._model.delete(pk)
        return instance

    async def pre_delete(self, request: Request, pk: int):
        pass

    async def on_delete(self, request: Request, instance):
        pass


class ListOperation(RegisterList):

    async def list(self, request: Request):
        await self.pre_list(request)
        instances = await self._list(request)
        asyncio.create_task(self.on_list(request))
        return [
            self.schema_out.model_validate(instance.__dict__) for instance in instances
        ]

    async def _list(self, request: Request):
        return await self._model.all()

    async def pre_list(self, request: Request):
        pass

    async def on_list(self, request: Request):
        pass


class APIView(
    CreateOperation,
    RetrieveOperation,
    UpdateOperation,
    PartialUpdateOperation,
    DeleteOperation,
    ListOperation,
):
    """Combining all mixins to achieve the same functionality as BaseAPIView"""

    pass
