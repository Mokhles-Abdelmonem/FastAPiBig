import os
from fastapi import FastAPI


def get_app():
    """Starts the FastAPI server."""
    app = FastAPI()

    # Dynamically include routes
    apps_dir = os.path.join(os.getcwd(), "app")

    # For feature-based structure
    if os.path.exists(apps_dir):
        for app_name in os.listdir(apps_dir):
            app_path = os.path.join(apps_dir, app_name)
            if os.path.isdir(app_path):
                try:
                    module_name = f"app.{app_name}.routes"
                    routes_module = __import__(module_name, fromlist=["router"])
                    app.include_router(routes_module.router, prefix=f"/{app_name}")
                except (ModuleNotFoundError, AttributeError):
                    pass

    # For type-based structure
    routes_dir = os.path.join(apps_dir, "routes")
    if os.path.exists(routes_dir):
        for route_file in os.listdir(routes_dir):
            if route_file.endswith(".py") and route_file != "__init__.py":
                try:
                    module_name = f"app.routes.{route_file[:-3]}"
                    routes_module = __import__(module_name, fromlist=["router"])
                    app.include_router(routes_module.router, prefix=f"/{route_file[:-3]}")
                except (ModuleNotFoundError, AttributeError):
                    pass

    return app

app = get_app()