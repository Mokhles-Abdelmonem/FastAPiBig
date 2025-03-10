from typing import List, Type, Optional, Dict
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from FastAPIBig.orm.base.base_model import ORM


class BaseAPI:
    """Base class that provides shared logic for all operations."""

    schema_in: Optional[Type[BaseModel]] = None
    schema_out: Optional[Type[BaseModel]] = None
    schemas_in: Dict[str, Type[BaseModel]] = {}
    schemas_out: Dict[str, Type[BaseModel]] = {}

    model: Type["ORM"] = None
    methods: List[str] = []

    post_methods: List[str] = []
    get_methods: List[str] = []
    list_methods: List[str] = []
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

    dependencies: List[Depends] = []
    dependencies_by_method: Dict[str, List[Depends]] = {}

    request: Request

    def __init__(self, router: Optional[APIRouter] = None):
        self._model = ORM(model=self.model)

        class Wrapper:
            pass

        self.wrapper = Wrapper
        self.router = router or APIRouter()
        self.load_all_methods()  # Dynamically load methods from all mixins

    @classmethod
    def as_router(
        cls: Type["BaseAPI"], prefix: str, tags: Optional[List[str]] = None
    ) -> APIRouter:
        """Create an instance of the API class and return its router."""
        instance = cls(APIRouter(prefix=prefix, tags=tags))
        return instance.router

    def _get_schema_in_class(self, method: str = None) -> Optional[Type[BaseModel]]:
        return self.schemas_in.get(method, self.schema_in)

    def _get_schema_out_class(
        self, method: str = None, as_list: bool = False
    ) -> Type[BaseModel]:
        schema = self.schemas_out.get(method, self.schema_out)
        return List[schema] if as_list else schema

    def _get_dependencies(self, method: str = None) -> List[Depends]:
        return self.dependencies_by_method.get(method, self.dependencies)

    def register_method_wrapper(self, method: str, set_annotations=False):
        """Attach method to wrapper class and optionally set type annotations."""
        attr = getattr(self, method, None)
        if not attr:
            raise KeyError(f"Method '{method}' not found in {self.__class__.__name__}")

        setattr(self.wrapper, method, attr)
        if set_annotations:
            attr.__annotations__["data"] = self._get_schema_in_class(method)

    def _register_route(self, method_type: str, method_name: str, path: str):
        """Dynamically register API route based on the method type."""
        if not hasattr(self.wrapper, method_name):
            raise KeyError(f"Method '{method_name}' not found in wrapper.")

        route_method = getattr(self.router, method_type)
        as_list = True if method_name == "list" else False
        route_method(
            path,
            response_model=self._get_schema_out_class(method=method_name, as_list=as_list),
            dependencies=self._get_dependencies(method_name),
            name=method_name,
        )(getattr(self.wrapper, method_name))

    def load_all_methods(self):
        """Dynamically call _load_methods() from all mixins in order."""
        for base in self.__class__.mro():
            if hasattr(base, "_load_methods"):
                base._load_methods(self)


class RegisterCreate(BaseAPI):
    def _load_methods(self):
        self.register_method_wrapper("create", set_annotations=True)
        self._register_route("post", "create", "/")
        self._load_post_methods()

    def _load_post_methods(self):
        for method in self.post_methods:
            self.register_method_wrapper(method, set_annotations=True)
            self._register_route("post", method, f"/{method}")


class RegisterRetrieve(BaseAPI):
    def _load_methods(self):
        self.register_method_wrapper("get")
        self._register_route("get", "get", "/{pk}")
        self._load_get_methods()

    def _load_get_methods(self):
        for method in self.get_methods:
            self.register_method_wrapper(method)
            self._register_route("get", method, f"/{method}")


class RegisterUpdate(BaseAPI):
    def _load_methods(self):
        self.register_method_wrapper("update", set_annotations=True)
        self._register_route("put", "update", "/{pk}")
        self._load_put_methods()

    def _load_put_methods(self):
        for method in self.put_methods:
            self.register_method_wrapper(method, set_annotations=True)
            self._register_route("put", method, f"/{method}/" + "/{pk}")


class RegisterPartialUpdate(BaseAPI):
    def _load_methods(self):
        self.register_method_wrapper("partial_update", set_annotations=True)
        self._register_route("patch", "partial_update", "/{pk}")
        self._load_patch_methods()

    def _load_patch_methods(self):
        for method in self.delete_methods:
            self.register_method_wrapper(method, set_annotations=True)
            self._register_route("patch", method, f"/{method}/" + "/{pk}")


class RegisterDelete(BaseAPI):
    def _load_methods(self):
        self.register_method_wrapper("delete")
        self._register_route("delete", "delete", "/{pk}")
        self._load_delete_methods()

    def _load_delete_methods(self):
        for method in self.delete_methods:
            self.register_method_wrapper(method)
            self._register_route("delete", method, f"/{method}/" + "/{pk}")


class RegisterList(BaseAPI):
    def _load_methods(self):
        self.register_method_wrapper("list")
        self._register_route("get", "list", "/")
        self._load_list_methods()

    def _load_list_methods(self):
        for method in self.list_methods:
            self.register_method_wrapper(method)
            self._register_route("get", method, f"/{method}")
