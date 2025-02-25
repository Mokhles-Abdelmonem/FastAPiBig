from typing import List, Type, Optional, Dict
from fastapi import APIRouter
from pydantic import BaseModel


class BaseAPIView:
    schema_in: Optional[Type[BaseModel]] = None
    schema_out: Optional[Type[BaseModel]] = None
    schemas_in: Dict[str, Type[BaseModel]] = {}
    schemas_out: Dict[str, Type[BaseModel]] = {}

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

    def __init__(self, router: Optional[APIRouter] = None):
        class Wrapper:
            pass

        self.wrapper = Wrapper
        self.router = router or APIRouter()
        self.load_base_methods()
        self.load_post_methods()

    def _get_schema_in_class(self, method: str = None) -> Optional[Type[BaseModel]]:
        return self.schemas_in.get(method, self.schema_in)

    def _get_schema_out_class(self, method: str = None) -> Optional[Type[BaseModel]]:
        return self.schemas_out.get(method, self.schema_out)

    @classmethod
    def as_router(cls: Type["BaseAPIView"], prefix: str, tags: Optional[List[str]] = None) -> APIRouter:
        instance = cls(APIRouter(prefix=prefix, tags=tags))
        return instance.router

    def register_method_wrapper(self, method: str, set_annotations: bool = False):
        attr = getattr(self, method, None)
        if not attr:
            raise AttributeError(f"Method '{method}' not found in {self.__class__.__name__}")

        setattr(self.wrapper, method, attr)

        if set_annotations:
            attr.__annotations__["data"] = self._get_schema_out_class(method)

    def _register_route(self, method_type: str, method_name: str, path: str):
        if not hasattr(self.wrapper, method_name):
            raise AttributeError(f"Method '{method_name}' not found in wrapper.")

        route_method = getattr(self.router, method_type)
        route_method(
            path,
            response_model=self._get_schema_out_class(method_name),
            name=method_name,
        )(getattr(self.wrapper, method_name))

    def load_post(self, method: str, path: str = "/"):
        self._register_route("post", method, path)

    def load_get(self, method: str, path: str = "/{pk}"):
        self._register_route("get", method, path)

    def load_list(self, method: str, path: str = "/"):
        self._register_route("get", method, path)

    def load_put(self, method: str, path: str = "/{pk}"):
        self._register_route("put", method, path)

    def load_delete(self, method: str, path: str = "/{pk}"):
        self._register_route("delete", method, path)

    def load_post_methods(self):
        for method in self.post_methods:
            self.register_method_wrapper(method)
            self.load_post(method=method, path=f"/{method}")

    def load_base_methods(self):
        for method in self.methods:
            if method in self.allowed_methods:
                set_annotations = method in ["create", "update", "partial_update"]
                self.register_method_wrapper(method, set_annotations=set_annotations)

                if method == "create":
                    self.load_post(method)
                elif method in ["update", "partial_update"]:
                    self.load_put(method)
                elif method == "get":
                    self.load_get(method)
                elif method == "list":
                    self.load_list(method)
                elif method == "delete":
                    self.load_delete(method)


class APIView(BaseAPIView):

    async def create(self, data: BaseModel):
        instance = await self.model.objects.create(**data.dict())
        return self.schema_out.model_validate(instance.__dict__)

    async def get(self, pk: int):
        instance = await self.model.objects.get(pk=pk)
        return self.schema_out.model_validate(instance.__dict__)

    async def update(self, pk: int, data: BaseModel):
        instance = await self.model.objects.get(pk=pk)
        for key, value in data.dict().items():
            setattr(instance, key, value)
        await instance.save()
        return self.schema_out.model_validate(instance.__dict__)

    async def delete(self, pk: int):
        instance = await self.model.objects.get(pk=pk)
        await instance.delete()
        return {"detail": "Deleted successfully"}

    async def list(self):
        instances = await self.model.objects.all()
        return [self.schema_out.model_validate(instance.__dict__) for instance in instances]

    async def partial_update(self, pk: int, data: BaseModel):
        instance = await self.model.objects.get(pk=pk)
        for key, value in data.dict(exclude_unset=True).items():
            setattr(instance, key, value)
        await instance.save()
        return self.schema_out.model_validate(instance.__dict__)
