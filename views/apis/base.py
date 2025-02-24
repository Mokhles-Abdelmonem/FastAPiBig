from typing import List, Type, Optional, ClassVar, Dict
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Type, Optional, ClassVar, get_type_hints


class BaseView:
    schema_in: Optional[Type[BaseModel]] = None
    schema_out: Optional[Type[BaseModel]] = None
    schemas_in: Optional[Dict[str, BaseModel]] = {}
    schemas_out: Optional[Dict[str, BaseModel]] = {}

    model: Optional[Type] = None
    methods: List[str] = []

    post_methods: List[str] = []
    get_methods: List[str] = []
    put_methods: List[str] = []
    patch_methods: List[str] = []
    delete_methods: List[str] = []

    allowed_methods: List[str] = [
        "create",
        "get",
        "update",
        "delete",
        "list",
        "partial_update",
    ]

    def _get_schema_in_class(self, method: str = None):
        return self.schemas_in.get(method, self.schema_in)

    def _get_schema_out_class(self, method: str = None):
        return self.schemas_out.get(method, self.schema_out)

    @classmethod
    def as_router(cls: Type["APIView"], prefix: str, tags: list = None) -> APIRouter:
        router = APIRouter(prefix=prefix, tags=tags)

        # Create an instance of the view class
        instance = cls()

        class Wrapper:
            pass

        def load_method(method: str, set_annotations=False):
            attr = getattr(instance, method)
            setattr(Wrapper, method, attr)
            if set_annotations:
                attr.__annotations__["data"] = instance._get_schema_out_class(method)

        def load_api(method):
            router.post(
                f"/{method}",
                response_model=instance._get_schema_out_class(method),
                name=method,
            )(getattr(Wrapper, method))

        def load_post_methods():
            for post_method in instance.post_methods:
                load_method(post_method)
                load_api(post_method)

        def load_base_methods():
            for method in instance.methods:
                if method in instance.allowed_methods:

                    set_annotations = (
                        True
                        if method in ["create", "update", "partial_update"]
                        else False
                    )
                    load_method(method, set_annotations=set_annotations)

                    # TODO : Clean
                    #   separate each method to its own class
                    schema_out = instance._get_schema_out_class(method)
                    if method == "create":
                        router.post("/", response_model=schema_out, name=method)(
                            getattr(Wrapper, method)
                        )
                    elif method in ["update", "partial_update"]:
                        router.put("/{pk}", response_model=schema_out, name=method)(
                            getattr(Wrapper, method)
                        )
                    elif method == "get":
                        router.get("/{pk}", response_model=schema_out, name=method)(
                            getattr(Wrapper, method)
                        )
                    elif method == "list":
                        router.get("/", response_model=List[schema_out], name=method)(
                            getattr(Wrapper, method)
                        )
                    elif method == "delete":
                        router.delete("/{pk}", name=method)(getattr(Wrapper, method))

        load_base_methods()
        load_post_methods()

        return router


class APIView(BaseView):

    async def create(self, data):
        instance = await self.model.objects.create(**data.dict())
        return self.schema_out.model_validate(instance.__dict__)

    async def get(self, pk: int):
        instance = await self.model.objects.get(pk=pk)
        return self.schema_out.model_validate(instance.__dict__)

    async def update(self, pk: int, data):
        instance = await self.model.objects.save()
        return self.schema_out.model_validate(instance.__dict__)

    async def delete(self, pk: int):
        return await self.model.objects.delete(pk)

    async def list(self):
        instances = await self.model.objects.filter()
        return [
            self.schema_out.model_validate(instance.__dict__) for instance in instances
        ]

    async def partial_update(self, pk: int, data):
        instance = await self.model.objects.save()
        return self.schema_out.model_validate(instance.__dict__)
