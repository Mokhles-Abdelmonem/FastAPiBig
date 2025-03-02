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


class CreateOperation(RegisterCreate):

    async def create(self, data: BaseModel):
        await self.pre_create(data)
        instance = await self.model.objects.create(**data.dict())
        asyncio.create_task(self.on_create(instance))
        return self.schema_out.model_validate(instance.__dict__)

    async def pre_create(self, data: BaseModel):
        pass

    async def on_create(self, instance):
        pass


class RetrieveOperation(RegisterRetrieve):

    async def get(self, pk: int):
        await self.pre_get(pk)
        instance = await self.model.objects.get(pk=pk)
        asyncio.create_task(self.on_get(instance))
        return self.schema_out.model_validate(instance.__dict__)

    async def pre_get(self, pk: int):
        pass

    async def on_get(self, instance):
        pass


class UpdateOperation(RegisterUpdate):

    async def update(self, pk: int, data: BaseModel):
        await self.pre_update(pk, data)
        instance = await self.model.objects.get(pk=pk)
        for key, value in data.dict().items():
            setattr(instance, key, value)
        await instance.save()
        asyncio.create_task(self.on_update(instance))
        return self.schema_out.model_validate(instance.__dict__)

    async def pre_update(self, pk: int, data: BaseModel):
        pass

    async def on_update(self, instance):
        pass


class PartialUpdateOperation(RegisterPartialUpdate):

    async def partial_update(self, pk: int, data: BaseModel):
        await self.pre_update(pk, data)
        instance = await self.model.objects.get(pk=pk)
        for key, value in data.dict(exclude_unset=True).items():
            setattr(instance, key, value)
        await instance.save()
        asyncio.create_task(self.on_update(instance))
        return self.schema_out.model_validate(instance.__dict__)

    async def pre_update(self, pk: int, data: BaseModel):
        pass

    async def on_update(self, instance):
        pass


class DeleteOperation(RegisterDelete):

    async def delete(self, pk: int):
        await self.pre_delete(pk)
        instance = await self.model.objects.get(pk=pk)
        await instance.delete(pk)
        asyncio.create_task(self.on_delete(instance))
        return {"detail": "Deleted successfully"}

    async def pre_delete(self, pk: int):
        pass

    async def on_delete(self, instance):
        pass


class ListOperation(RegisterList):

    async def list(self):
        await self.pre_list()
        instances = await self.model.objects.all()
        asyncio.create_task(self.on_list())
        return [
            self.schema_out.model_validate(instance.__dict__) for instance in instances
        ]

    async def pre_list(self):
        pass

    async def on_list(self):
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
