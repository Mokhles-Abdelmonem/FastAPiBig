from typing import List

from pydantic import BaseModel


class APIView:
    schema_in: BaseModel = None
    schema_out: BaseModel | List[BaseModel] = None
    model: BaseModel = None
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
        return
    async def get(self, id):
        return
    async def update(self, id, **kwargs):
        return
    async def delete(self, id):
        return
    async def list(self):
        return
    async def partial_update(self, id, **kwargs):
        return
