from typing import List, Type, Optional
from fastapi import APIRouter
from pydantic import BaseModel


class APIView:
    schema_in: Optional[Type[BaseModel]] = None
    schema_out: Optional[Type[BaseModel]] = None
    model: Optional[Type] = None
    methods: List[str] = []

    allowed_methods: List[str] = ["create", "get", "update", "delete", "list", "partial_update"]

    async def create(self, **kwargs):
        return await self.model.objects.create(**kwargs)

    async def get(self, id):
        return self.model.objects.get(id=id)

    async def update(self, id, **kwargs):
        return self.model.objects.save()

    async def delete(self, id):
        return self.model.objects.delete()

    async def list(self):
        return self.model.objects.filter()

    async def partial_update(self, id, **kwargs):
        return self.model.objects.save()

    @classmethod
    def as_router(cls, prefix: str = "", tags: list = None ) -> APIRouter:
        router = APIRouter(prefix=prefix, tags=tags)

        # Create an instance of the class
        instance = cls()

        for method in cls.methods:
            if method in cls.allowed_methods:
                endpoint = getattr(instance, method)
                async def create_endpoint(data: cls.schema_in):  # Ensure this works
                    return await endpoint(**data.dict())

                if method == "list":
                    router.get("/", response_model=List[cls.schema_out], name=method)(endpoint)
                elif method == "create":
                    router.post("/", response_model=cls.schema_out, name=method)(create_endpoint)
                elif method == "get":
                    router.get("/{id}", response_model=cls.schema_out, name=method)(endpoint)
                elif method in ["update", "partial_update"]:
                    router.put("/{id}", response_model=cls.schema_out, name=method)(create_endpoint)
                elif method == "delete":
                    router.delete("/{id}", name=method)(endpoint)

        return router
