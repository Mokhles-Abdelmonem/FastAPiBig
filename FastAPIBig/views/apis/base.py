from functools import cached_property
from typing import List, Type, Optional, Dict, ClassVar
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

    _allowed_methods: List[str] = [
        "create",
        "get",
        "update",
        "delete",
        "list",
        "partial_update",
    ]

    dependencies: List[Depends] = []
    dependencies_by_method: Dict[str, List[Depends]] = {}

    prefix: Optional[str] = ""
    tags: Optional[List[str]] = None

    include_router: bool = False

    def __init__(self, prefix: str = "", tags: Optional[List[str]] = None):

        class Wrapper:
            pass

        self.wrapper = Wrapper
        self._model = ORM(model=self.model)
        self.router = APIRouter(prefix=self.prefix or prefix, tags=self.tags or tags)
        self.load_all_methods()  # Dynamically load methods from all mixins

    @classmethod
    def as_router(
        cls: Type["BaseAPI"], prefix: str, tags: Optional[List[str]] = None
    ) -> APIRouter:
        """Create an instance of the API class and return its router."""
        instance = cls(prefix=prefix, tags=tags)
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

    def register_method_wrapper(self, method_name: str, set_annotations=False):
        """Attach method to wrapper class and optionally set type annotations."""
        if method_name not in self.all_methods:
            return

        attr = getattr(self, method_name, None)
        if not attr:
            raise KeyError(f"Method '{method_name}' not found in {self.__class__.__name__}")

        setattr(self.wrapper, method_name, attr)
        if set_annotations:
            attr.__annotations__["data"] = self._get_schema_in_class(method_name)

    def _register_route(self, method_name: str, method_type: str, path: str):
        """Dynamically register API route based on the method type."""
        if method_name not in self.all_methods:
            return

        if not hasattr(self.wrapper, method_name):
            raise KeyError(f"Method '{method_name}' not found in wrapper.")

        route_method = getattr(self.router, method_type)
        as_list = True if method_name == "list" else False

        # Generate a unique operation ID
        operation_id = f"{self.__class__.__name__.lower()}_{path.strip('/').replace('/', '_')}_{method_name}"
        # TODO: check how many routes have the same name, methods loaded multiple times

        route_method(
            path,
            response_model=self._get_schema_out_class(
                method=method_name, as_list=as_list
            ),
            dependencies=self._get_dependencies(method_name),
            name=method_name,
            operation_id=operation_id,  # Ensure uniqueness
        )(getattr(self.wrapper, method_name))

    def load_all_methods(self):
        """Dynamically call _load_methods() from all mixins in order."""
        for base in self.__class__.mro():
            if hasattr(base, "_load_methods"):
                base._load_methods(self)

    def _load_method(
        self,
        method_type: str,
        method_name: str,
        path: str = "",
        set_annotations: bool = False,
    ):
        self.load_method_validate(method_name)
        self.register_method_wrapper(method_name, set_annotations)
        self._register_route(method_name, method_type , path)

    def load_method_validate(self, method_name):
        if method_name not in self.allowed_methods:
            raise ValueError(f"Invalid method: {method_name}")


    @cached_property
    def allowed_methods(self):
        return (
            self._allowed_methods
            + self.post_methods
            + self.get_methods
            + self.put_methods
            + self.patch_methods
            + self.delete_methods
        )

    @cached_property
    def all_methods(self):
        return (
            self.methods
            + self.post_methods
            + self.get_methods
            + self.put_methods
            + self.patch_methods
            + self.delete_methods
        )


class RegisterCreate(BaseAPI):
    def _load_methods(self):
        self._load_method("post", "create", "/", set_annotations=True)
        self._load_post_methods()

    def _load_post_methods(self):
        for method in self.post_methods:
            self._load_method("post", method, f"/{method}", set_annotations=True)


class RegisterRetrieve(BaseAPI):
    def _load_methods(self):
        self._load_method("get", "get", "/{pk}")
        self._load_get_methods()

    def _load_get_methods(self):
        for method in self.get_methods:
            self._load_method("get", method, f"/{method}" + "/{pk}")


class RegisterUpdate(BaseAPI):
    def _load_methods(self):
        self._load_method("put", "update", "/{pk}", set_annotations=True)
        self._load_put_methods()

    def _load_put_methods(self):
        for method in self.put_methods:
            self._load_method(
                "put", method, f"/{method}/" + "/{pk}", set_annotations=True
            )


class RegisterPartialUpdate(BaseAPI):
    def _load_methods(self):
        self._load_method("patch", "partial_update", "/{pk}", set_annotations=True)
        self._load_patch_methods()

    def _load_patch_methods(self):
        for method in self.delete_methods:
            self._load_method(
                "patch", method, f"/{method}/" + "/{pk}", set_annotations=True
            )


class RegisterDelete(BaseAPI):
    def _load_methods(self):
        self._load_method("delete", "delete", "/{pk}")
        self._load_delete_methods()

    def _load_delete_methods(self):
        for method in self.delete_methods:
            self._load_method("delete", method, f"/{method}/" + "/{pk}")


class RegisterList(BaseAPI):
    def _load_methods(self):
        self._load_method("get", "list", "/")
        self._load_list_methods()

    def _load_list_methods(self):
        for method in self.list_methods:
            self._load_method("get", method, f"/{method}")
