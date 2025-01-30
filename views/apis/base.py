from typing import List, Type

from pydantic import BaseModel


class APIView:
    schema_in: Type[BaseModel] = None
    schema_out: Type[BaseModel] | List[Type[BaseModel]] = None
    model: Type[BaseModel] = None
    methods: List[str] = [
        "create",
        "get",
        "update",
        "delete",
        "list",
        "partial_update",
    ]

    def __init__(self, model):
        self.model = model


    async def create(self, **kwargs):
        return await self.model.objects.create(**kwargs)

    async def get(self, id):
        return self.model.objects.get(id=id)

    async def update(self, id, **kwargs):
        return

    async def delete(self, id):
        return

    async def list(self):
        return

    async def partial_update(self, id, **kwargs):
        return
