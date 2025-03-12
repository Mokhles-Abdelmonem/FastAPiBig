import os
import inspect
import importlib
from fastapi import FastAPI
from FastAPIBig.views.apis.base import BaseAPI


def get_app():
    """Starts the FastAPI server."""
    app = FastAPI()
    apps_dir = os.path.join(os.getcwd(), "app")

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
                module_name = f"app.{app_name}.routes"
                import_and_register_routes(module_name, prefix=f"/{app_name}")

    # Type-based structure
    routes_dir = os.path.join(apps_dir, "routes")
    if os.path.exists(routes_dir):
        for route_file in os.listdir(routes_dir):
            if route_file.endswith(".py") and route_file != "__init__.py":
                module_name = f"app.routes.{route_file[:-3]}"
                import_and_register_routes(module_name, prefix=f"/{route_file[:-3]}")

    return app


app = get_app()
