from functools import cached_property
from typing import List, Type, Optional, Dict, get_origin
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from FastAPIBig.orm.base.base_model import ORM


class BaseAPI:
    """
    BaseAPI is a foundational class for creating API endpoints in a FastAPI application.
    It provides mechanisms for defining schemas, methods, dependencies, and dynamically
    registering routes.

    Attributes:
        schema_in (Optional[Type[BaseModel]]): Default input schema for API methods.
        schema_out (Optional[Type[BaseModel]]): Default output schema for API methods.
        schemas_in (Dict[str, Type[BaseModel]]): Mapping of method names to input schemas.
        schemas_out (Dict[str, Type[BaseModel]]): Mapping of method names to output schemas.
        model (Type["ORM"]): ORM model associated with the API.
        methods (List[str]): List of custom methods for the API.
        post_methods (List[str]): List of methods for POST requests.
        get_methods (List[str]): List of methods for GET requests.
        list_methods (List[str]): List of methods for LIST requests.
        put_methods (List[str]): List of methods for PUT requests.
        patch_methods (List[str]): List of methods for PATCH requests.
        delete_methods (List[str]): List of methods for DELETE requests.
        _allowed_methods (List[str]): Predefined list of allowed method names.
        dependencies (List[Depends]): Global dependencies for all API methods.
        dependencies_by_method (Dict[str, List[Depends]]): Method-specific dependencies.
        prefix (Optional[str]): URL prefix for the API routes.
        tags (Optional[List[str]]): Tags for API documentation.
        include_router (bool): Whether to include the router in the application.
        schemas_out_is_list (bool): Flag to indicate if the output schema is a list.

    Methods:
        __init__(prefix: str = "", tags: Optional[List[str]] = None):
            Initializes the BaseAPI instance with optional prefix and tags.

        as_router(cls, prefix: str, tags: Optional[List[str]] = None) -> APIRouter:
            Creates an instance of the API class and returns its router.

        _get_schema_in_class(method: str = None) -> Optional[Type[BaseModel]]:
            Retrieves the input schema class for a specific method.

        _get_schema_out_class(method: str = None) -> Type[BaseModel]:
            Retrieves the output schema class for a specific method.

        _get_schema_out(method: str = None) -> Type[BaseModel] | Type[List[BaseModel]] | None:
            Retrieves the output schema for a specific method, considering list methods.

        _get_dependencies(method: str = None) -> List[Depends]:
            Retrieves the dependencies for a specific method.

        register_method_wrapper(method_name: str, set_annotations: bool = False):
            Attaches a method to the wrapper class and optionally sets type annotations.

        _register_route(method_name: str, method_type: str, path: str):
            Dynamically registers an API route based on the method type.

        _load_method(method_type: str, method_name: str, path: str = "", set_annotations: bool = False):
            Loads and validates a method, registers it with the wrapper, and creates a route.

        load_method_validate(method_name: str):
            Validates if a method name is allowed.

        allowed_methods -> List[str]:
            Returns a list of all allowed methods, including custom ones.

        all_methods -> List[str]:
            Returns a list of all methods defined in the API.
    """

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
    schemas_out_is_list: bool = False

    def __init__(self, prefix: str = "", tags: Optional[List[str]] = None):
        """
        Initializes the base API view with a router, model, and other configurations.

        Args:
            prefix (str, optional): The URL prefix for the API routes. Defaults to an empty string.
            tags (Optional[List[str]], optional): A list of tags for API documentation purposes. Defaults to None.
        """

        class Wrapper:
            pass

        self.wrapper = Wrapper
        self._model = ORM(model=self.model)
        self.router = APIRouter(prefix=self.prefix or prefix, tags=self.tags or tags)
        self.required_objects = []

    @classmethod
    def as_router(
        cls: Type["BaseAPI"], prefix: str, tags: Optional[List[str]] = None
    ) -> APIRouter:
        """
        Create an instance of the API class and return its router.

        This method is a class method that initializes an instance of the
        `BaseAPI` class (or its subclass) with the provided `prefix` and `tags`,
        and then returns the associated `APIRouter` object.

        Args:
            prefix (str): The URL prefix for the API routes.
            tags (Optional[List[str]]): A list of tags to categorize the API routes.

        Returns:
            APIRouter: The router object containing the API routes.
        """
        instance = cls(prefix=prefix, tags=tags)
        return instance.router

    def _get_schema_in_class(self, method: str = None) -> Optional[Type[BaseModel]]:
        """
        Get the input schema for a specific method.

        Args:
            method (str, optional): The method name. Defaults to None.

        Returns:
            Optional[Type[BaseModel]]: The input schema or default schema.
        """
        return self.schemas_in.get(method, self.schema_in)

    def _get_schema_out_class(self, method: str = None) -> Type[BaseModel]:
        """
        Get the output schema class for a method.

        Args:
            method (str, optional): The method name. Defaults to None.

        Returns:
            Type[BaseModel]: The output schema class or the default schema.
        """
        return self.schemas_out.get(method, self.schema_out)

    def _get_schema_out(
        self, method: str = None
    ) -> Type[BaseModel] | Type[List[BaseModel]] | None:
        """
        Determines the output schema for a given method.

        Args:
            method (str, optional): The method name for which the output schema is required.
                Can be "list", "delete", or any other method name. Defaults to None.

        Returns:
            Type[BaseModel] | Type[List[BaseModel]] | None:
                - If the method is "list" or in `self.list_methods`, returns a list of schema classes.
                - If the method is "delete" or in `self.delete_methods`, returns None.
                - Otherwise, returns the schema class corresponding to the method.
        """
        if method == "list" or method in self.list_methods:
            return List[self._get_schema_out_class(method)]
        elif method == "delete" or method in self.delete_methods:
            return None
        return self._get_schema_out_class(method)

    def _get_dependencies(self, method: str = None) -> List[Depends]:
        """
        Get dependencies for a specific method or default dependencies if not specified.

        Args:
            method (str, optional): The method name.

        Returns:
            List[Depends]: Dependencies for the method or default dependencies.
        """
        return self.dependencies_by_method.get(method, self.dependencies)

    def register_method_wrapper(self, method_name: str, set_annotations=False):
        """
        Registers a method from the current class to the `wrapper` attribute.

        This function checks if the specified method name exists in the `all_methods`
        attribute. If it does, it retrieves the method from the current class and
        assigns it to the `wrapper` attribute under the same name. Optionally, it can
        also set type annotations for the method's "data" parameter.

        Args:
            method_name (str): The name of the method to register.
            set_annotations (bool, optional): If True, sets the "data" annotation
                for the method using the schema returned by `_get_schema_in_class`.
                Defaults to False.

        Raises:
            KeyError: If the specified method is not found in the current class.

        """
        if method_name not in self.all_methods:
            return

        attr = getattr(self, method_name, None)
        if not attr:
            raise KeyError(
                f"Method '{method_name}' not found in {self.__class__.__name__}"
            )

        setattr(self.wrapper, method_name, attr)
        if set_annotations:
            attr.__annotations__["data"] = self._get_schema_in_class(method_name)

    def _register_route(self, method_name: str, method_type: str, path: str):
        """
        Registers a route to the router with the specified HTTP method, path, and handler.

        Args:
            method_name (str): The name of the method to be registered as a route.
                              This should correspond to a method in the wrapper.
            method_type (str): The HTTP method type (e.g., 'get', 'post', 'put', 'delete').
                               This should match a method available in the router.
            path (str): The URL path for the route.

        Raises:
            KeyError: If the specified method_name is not found in the wrapper.

        Notes:
            - The method_name must exist in the `all_methods` attribute for the route to be registered.
            - The method in the wrapper corresponding to method_name will be used as the handler for the route.
            - The response model and dependencies for the route are dynamically determined
              using `_get_schema_out` and `_get_dependencies` methods, respectively.
        """
        if method_name not in self.all_methods:
            return

        if not hasattr(self.wrapper, method_name):
            raise KeyError(f"Method '{method_name}' not found in wrapper.")

        route_method = getattr(self.router, method_type)
        route_method(
            path,
            response_model=self._get_schema_out(method=method_name),
            dependencies=self._get_dependencies(method_name),
            name=method_name,
        )(getattr(self.wrapper, method_name))

    def _load_method(
        self,
        method_type: str,
        method_name: str,
        path: str = "",
        set_annotations: bool = False,
    ):
        """
        Loads and registers a method for a specific HTTP route.

        Args:
            method_type (str): The HTTP method type (e.g., 'GET', 'POST', etc.).
            method_name (str): The name of the method to be loaded and registered.
            path (str, optional): The URL path for the route. Defaults to an empty string.
            set_annotations (bool, optional): Whether to set annotations for the method. Defaults to False.

        Raises:
            ValueError: If the method name fails validation.
        """
        self.load_method_validate(method_name)
        self.register_method_wrapper(method_name, set_annotations)
        self._register_route(method_name, method_type, path)

    def load_method_validate(self, method_name):
        """Validate if the method name is allowed."""
        if method_name not in self.allowed_methods:
            raise ValueError(f"Invalid method: {method_name}")

    @cached_property
    def allowed_methods(self):
        """Returns a combined list of all allowed HTTP methods."""
        return (
            self._allowed_methods
            + self.post_methods
            + self.get_methods
            + self.list_methods
            + self.put_methods
            + self.patch_methods
            + self.delete_methods
        )

    @cached_property
    def all_methods(self):
        """Aggregates all HTTP methods supported by the view."""
        return (
            self.methods
            + self.post_methods
            + self.get_methods
            + self.list_methods
            + self.put_methods
            + self.patch_methods
            + self.delete_methods
        )


class RegisterCreate(BaseAPI):
    """
    A class that extends the BaseAPI to handle HTTP POST methods for creating resources.

    Methods:
        __init__(*args, **kwargs):
            Initializes the RegisterCreate instance and loads the create-related methods.

        _load_create():
            Loads the primary "create" POST method and additional POST methods.

        _load_post_methods():
            Iterates through the list of post_methods and loads each as a POST endpoint.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the instance and perform necessary setup.

        This constructor calls the parent class's initializer and then
        invokes the `_load_create` method to handle additional setup
        specific to this class.
        """
        super().__init__(*args, **kwargs)
        self._load_create()

    def _load_create(self):
        """
        Initializes and loads the "create" API endpoint.

        This method sets up the "post" HTTP method for the "create" operation
        at the root path ("/"). It also applies annotations if specified and
        subsequently loads additional POST-related methods.
        """
        self._load_method("post", "create", "/", set_annotations=True)
        self._load_post_methods()

    def _load_post_methods(self):
        """
        Loads and registers POST methods for the API.

        This method iterates through the `post_methods` attribute, which is expected
        to be a list of method names. For each method, it calls `_load_method` to
        register the method as a POST endpoint with the corresponding URL path.

        The URL path for each method is constructed as `/<method_name>`. Annotations
        can also be set for the method by passing `set_annotations=True` to `_load_method`.

        Raises:
            AttributeError: If `post_methods` is not defined or is not iterable.
        """
        for method in self.post_methods:
            self._load_method("post", method, f"/{method}", set_annotations=True)


class RegisterRetrieve(BaseAPI):
    """
    A class that extends the BaseAPI to handle retrieval operations for a resource.

    Methods:
        __init__(*args, **kwargs):
            Initializes the RegisterRetrieve instance and loads the retrieve methods.

        _load_retrieve():
            Loads the default retrieval method and additional GET methods.

        _load_get_methods():
            Iterates through the list of GET methods and loads them with their respective routes.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the class and perform necessary setup.

        This constructor calls the parent class's initializer and then
        invokes the `_load_retrieve` method to perform additional setup.
        """
        super().__init__(*args, **kwargs)
        self._load_retrieve()

    def _load_retrieve(self):
        """
        Configures the retrieval-related API endpoints for the resource.

        This method sets up the "get" HTTP method for retrieving a single resource
        by its primary key (pk) and initializes additional "get" methods specific
        to the resource.

        The endpoint for retrieving a single resource is defined as "/{pk}".
        """
        self._load_method("get", "get", "/{pk}")
        self._load_get_methods()

    def _load_get_methods(self):
        """
        Dynamically loads and registers HTTP GET methods for the API.

        This method iterates over the `get_methods` attribute, which is expected
        to be a collection of method names. For each method, it constructs a URL
        path by appending the method name and a placeholder for a primary key (`pk`).
        It then calls the `_load_method` function to register the method with the
        HTTP GET verb and the constructed URL path.

        Example:
            If `get_methods` contains ["user", "product"], this method will register:
            - GET /user/{pk}
            - GET /product/{pk}

        Raises:
            AttributeError: If `get_methods` is not defined or is not iterable.
        """
        for method in self.get_methods:
            self._load_method("get", method, f"/{method}" + "/{pk}")


class RegisterUpdate(BaseAPI):
    """
    A class that extends the BaseAPI to handle HTTP PUT methods for updating resources.

    Methods:
        __init__(*args, **kwargs):
            Initializes the RegisterUpdate instance and loads the update methods.

        _load_update():
            Loads the primary update method and additional PUT methods.

        _load_put_methods():
            Iterates through the `put_methods` attribute and loads each PUT method
            with its corresponding endpoint.

    Attributes:
        put_methods (list):
            A list of additional PUT methods to be loaded dynamically.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the class instance and perform necessary setup.

        This constructor calls the parent class's initializer and then
        invokes the `_load_update` method to handle any additional
        initialization logic specific to this class.
        """
        super().__init__(*args, **kwargs)
        self._load_update()

    def _load_update(self):
        """
        Loads the update method for the API view.

        This method sets up the "PUT" HTTP method for updating a resource
        by defining the route "/{pk}" where "pk" represents the primary key
        of the resource. It also ensures that annotations are set for the method
        and calls additional setup for PUT methods.

        """
        self._load_method("put", "update", "/{pk}", set_annotations=True)
        self._load_put_methods()

    def _load_put_methods(self):
        """
        Loads and registers HTTP PUT methods for the API.

        This method iterates over the `put_methods` attribute, which is expected to
        contain a list of method names. For each method, it calls the `_load_method`
        function to register the method as a PUT endpoint. The endpoint URL is
        constructed dynamically using the method name and includes a path parameter
        `pk`.

        The `_load_method` function is invoked with the following parameters:
            - HTTP method: "put"
            - Method name: The current method from `put_methods`
            - URL path: A dynamically constructed path in the format `/{method}/{pk}`
            - set_annotations: A flag set to True to enable annotations for the method
        """
        for method in self.put_methods:
            self._load_method(
                "put", method, f"/{method}/" + "/{pk}", set_annotations=True
            )


class RegisterPartialUpdate(BaseAPI):
    """
    A class that extends the BaseAPI to handle partial update operations
    using HTTP PATCH methods.

    Methods:
        __init__(*args, **kwargs):
            Initializes the RegisterPartialUpdate instance and loads
            the partial update methods.

        _load_partial_update():
            Loads the primary partial update method and additional
            patch methods.

        _load_patch_methods():
            Iterates through the delete_methods attribute and loads
            corresponding patch methods for each delete method.

    Attributes:
        delete_methods (list):
            A list of method names that are used to dynamically load
            additional patch methods.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the instance and perform any necessary setup.

        This constructor calls the parent class's initializer and then
        invokes a method to load partial update functionality.
        """
        super().__init__(*args, **kwargs)
        self._load_partial_update()

    def _load_partial_update(self):
        """
        Configures the partial update functionality for the API view.

        This method sets up the "patch" HTTP method for partial updates,
        associates it with the "partial_update" handler, and defines the
        endpoint path as "/{pk}". It also ensures that type annotations
        are set for the method and loads any additional patch-related methods.
        """
        self._load_method("patch", "partial_update", "/{pk}", set_annotations=True)
        self._load_patch_methods()

    def _load_patch_methods(self):
        """
        Loads and registers HTTP PATCH methods for the specified delete methods.

        This method iterates over the `delete_methods` attribute and registers
        each method as a PATCH endpoint. The endpoint URL is constructed using
        the method name and includes a path parameter `pk`.

        The `_load_method` function is used to perform the registration, with
        the `set_annotations` parameter set to True.
        """
        for method in self.delete_methods:
            self._load_method(
                "patch", method, f"/{method}/" + "/{pk}", set_annotations=True
            )


class RegisterDelete(BaseAPI):
    """
    A class that extends the BaseAPI to provide functionality for handling
    DELETE HTTP methods in a FastAPI application.

    Methods:
        __init__(*args, **kwargs):
            Initializes the RegisterDelete instance and loads the DELETE methods.

        _load_delete():
            Configures the DELETE HTTP method for the base endpoint and
            initializes additional DELETE methods.

        _load_delete_methods():
            Iterates through the `delete_methods` attribute and configures
            DELETE HTTP methods for each specified method with a dynamic URL pattern.

    Attributes:
        delete_methods (list):
            A list of additional DELETE method names to be configured dynamically.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the instance and perform necessary setup.

        This constructor calls the parent class's initializer and then
        invokes the `_load_delete` method to perform additional setup.
        """
        super().__init__(*args, **kwargs)
        self._load_delete()

    def _load_delete(self):
        """
        Configures the DELETE HTTP method for the API.

        This method sets up the DELETE route by calling `_load_method` with the
        appropriate parameters and then invokes `_load_delete_methods` to handle
        additional DELETE-specific configurations.
        """
        self._load_method("delete", "delete", "/{pk}")
        self._load_delete_methods()

    def _load_delete_methods(self):
        """
        Loads and registers delete methods as API endpoints.

        This method iterates over the `delete_methods` attribute, which is expected
        to be a list of method names. For each method, it constructs a URL path
        using the method name and a placeholder for a primary key (`{pk}`), and
        registers the method as a "delete" operation.

        The resulting endpoint URL pattern will be in the format:
        `/<method_name>/{pk}`.

        Example:
            If `delete_methods` contains ["remove_user", "delete_item"], this method
            will register the following endpoints:
            - DELETE /remove_user/{pk}
            - DELETE /delete_item/{pk}
        """
        for method in self.delete_methods:
            self._load_method("delete", method, f"/{method}/" + "/{pk}")


class RegisterList(BaseAPI):
    """
    A class that extends the BaseAPI to handle the registration of list-related API endpoints.

    Methods:
        __init__(*args, **kwargs):
            Initializes the RegisterList instance and loads the list-related API methods.

        _load_list():
            Loads the default list-related API methods, including the base "list" endpoint.

        _load_list_methods():
            Iterates through the `list_methods` attribute and loads additional list-related API methods.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the instance and perform any necessary setup.

        This constructor calls the parent class's initializer and then
        invokes a method to load list functionality.
        """
        super().__init__(*args, **kwargs)
        self._load_list()

    def _load_list(self):
        """
        Loads the list-related API endpoints for the current view.

        This method sets up the "list" endpoint with the HTTP GET method
        and the root path ("/"). It also invokes additional methods to
        load other list-related functionalities.
        """
        self._load_method("get", "list", "/")
        self._load_list_methods()

    def _load_list_methods(self):
        """
        Dynamically loads and registers a list of methods as HTTP GET endpoints.

        This method iterates over the `list_methods` attribute, which is expected to
        contain method names. For each method, it calls the `_load_method` function
        to register it as a GET endpoint with a corresponding URL path.

        Example:
            If `list_methods` contains ["method1", "method2"], this function will
            register the following endpoints:
            - GET /method1
            - GET /method2
        """
        for method in self.list_methods:
            self._load_method("get", method, f"/{method}")
