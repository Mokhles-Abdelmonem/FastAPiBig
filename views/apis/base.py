from typing import List, Type, Optional, ClassVar
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Type, Optional, ClassVar, get_type_hints


class APIView:
    schema_in: Optional[Type[BaseModel]] = None
    schema_out: Optional[Type[BaseModel]] = None
    model: Optional[Type] = None
    methods: List[str] = []

    apis: ClassVar[dict] = {}

    allowed_methods: List[str] = ["create", "get", "update", "delete", "list", "partial_update"]


    async def create(self, data):
        return await self.model.objects.create(**data.dict())

    async def get(self, pk: int):
        return await self.model.objects.get(pk=pk)

    async def update(self, pk: int, data):
        return await self.model.objects.save()

    async def delete(self, pk: int):
        return await self.model.objects.delete(pk)

    async def list(self):
        return await self.model.objects.filter()

    async def partial_update(self, pk: int, data):
        return await self.model.objects.save()

    @classmethod
    def as_router(cls, prefix: str, tags: list = None ) -> APIRouter:
        router = APIRouter(prefix=prefix, tags=tags)

        # Create an instance of the class
        instance = cls()

        class Wrapper:
            pass

        for method in cls.allowed_methods:
            attr = getattr(instance, method)
            if method in ["create", "update", "partial_update"]:
                attr.__annotations__['data'] = attr.__annotations__.get('data', cls.schema_in)
            setattr(Wrapper, method, attr)

        for method in cls.methods:
            if method in cls.allowed_methods:
                if method == "create":
                    router.post("/", response_model=cls.schema_out, name=method)(getattr(Wrapper, method))
                elif method in ["update", "partial_update"]:
                    router.put("/{pk}", response_model=cls.schema_out, name=method)(getattr(Wrapper, method))
                elif method == "get":
                    router.get("/{pk}", response_model=cls.schema_out, name=method)(getattr(Wrapper, method))
                elif method == "list":
                    router.get("/", response_model=List[cls.schema_out], name=method)(getattr(Wrapper, method))
                elif method == "delete":
                    router.delete("/{pk}", name=method)(getattr(Wrapper, method))

        return router
