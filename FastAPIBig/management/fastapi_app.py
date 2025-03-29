import os
import inspect
import importlib
import sys

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

from FastAPIBig.views.apis.base import BaseAPI


def is_locally_defined(cls):

    """
    Check if a class is defined locally within its module.

    This function determines whether a given class is defined in the module
    it belongs to, rather than being imported from another module.

    Args:
        cls (type): The class to check.

    Returns:
        bool: True if the class is defined locally in its module, False otherwise.
    Raises:
        ValueError: If the provided class is not a type.
    """
    # Get the module where the class is defined
    module = sys.modules.get(cls.__module__)

    # Check if the class's module matches the current module
    # and the class is defined directly in that module
    return (module is not None and
            hasattr(module, cls.__name__) and
            getattr(module, cls.__name__) is cls)




def get_app():
    """
    Initializes and configures a FastAPI application instance.

    This function dynamically imports and registers middlewares, routes, and API endpoints
    based on the application's directory structure. It supports both feature-based and 
    type-based project structures.

    Returns:
        FastAPI: The configured FastAPI application instance.

    Functionality:
        - Dynamically imports and adds middlewares from the `core.middlewares` module.
        - Dynamically imports and registers routes and API endpoints:
            - Feature-based structure: Scans the `apps` directory for subdirectories,
              and imports routes from `apps.<feature>.routes`.
            - Type-based structure: Scans the `apps/routes` directory for Python files,
              and imports routes from `apps.routes.<route_file>`.
        - Automatically includes routers defined in modules or subclasses of `BaseAPI` 
          with the `include_router` attribute set to `True`.

    Notes:
        - Middlewares are added only if they are subclasses of `BaseHTTPMiddleware` 
          and are locally defined.
        - Routes are included only if the module contains a `router` object or 
          subclasses of `BaseAPI` with the `include_router` attribute set to `True`.
        - Handles exceptions such as `ModuleNotFoundError`, `AttributeError`, and 
          `ImportError` gracefully during dynamic imports.
    """

    app_module = importlib.import_module("core.app")
    app = getattr(app_module, "FASTAPI_APP", None) or FastAPI()


    def add_middlewares():
        middlewares_module = importlib.import_module("core.middlewares")
        for name, obj in inspect.getmembers(middlewares_module, inspect.isclass):
            if (issubclass(obj, BaseHTTPMiddleware) and
                    obj is not BaseHTTPMiddleware and  # Exclude the base class itself
                    is_locally_defined(obj)):  # Only include locally defined subclasses
                if not any(obj is middleware.cls for middleware in app.user_middleware):
                    app.add_middleware(obj)

    add_middlewares()

    apps_dir = os.path.join(os.getcwd(), "apps")
    def import_and_register_routes(module_name: str, prefix: str):
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, "router"):
                app.include_router(module.router)

            # Dynamically find and register subclasses of BaseAPI
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseAPI) and obj.include_router:
                    app.include_router(
                        obj.as_router(prefix=prefix, tags=[prefix.strip("/")])
                    )

        except (ModuleNotFoundError, AttributeError, ImportError):
            pass

    # Feature-based structure
    if os.path.exists(apps_dir):
        for app_name in os.listdir(apps_dir):
            app_path = os.path.join(apps_dir, app_name)
            if os.path.isdir(app_path):
                module_name = f"apps.{app_name}.routes"
                import_and_register_routes(module_name, prefix=f"/{app_name}")

    # Type-based structure
    routes_dir = os.path.join(apps_dir, "routes")
    if os.path.exists(routes_dir):
        for route_file in os.listdir(routes_dir):
            if route_file.endswith(".py") and route_file != "__init__.py":
                module_name = f"apps.routes.{route_file[:-3]}"
                import_and_register_routes(module_name, prefix=f"/{route_file[:-3]}")

    return app


app = get_app()
