import os

from FastAPIBig.management import db_manager
from core.database import Base


def import_models():
    """
    Dynamically imports model modules from the project structure.

    This function scans the project directory for model modules and imports them
    to ensure they are registered and available for use. It supports two types
    of project structures:

    1. Feature-based structure:
       - Looks for `models` modules inside each app directory under the `apps` folder.
       - Example: `apps/<app_name>/models.py`

    2. Type-based structure:
       - Looks for model files inside the `apps/models` directory.
       - Example: `apps/models/<model_file>.py`

    Any `ModuleNotFoundError` or `AttributeError` encountered during the import
    process is caught and printed to the console.

    """

    # Dynamically include routes
    apps_dir = os.path.join(os.getcwd(), "apps")

    # For feature-based structure
    if os.path.exists(apps_dir):
        for app_name in os.listdir(apps_dir):
            app_path = os.path.join(apps_dir, app_name)
            if os.path.isdir(app_path):
                try:
                    module_name = f"apps.{app_name}.models"
                    __import__(module_name)
                except (ModuleNotFoundError, AttributeError) as e:
                    print(e)

    # For type-based structure
    routes_dir = os.path.join(apps_dir, "routes")
    if os.path.exists(routes_dir):
        for route_file in os.listdir(routes_dir):
            if route_file.endswith(".py") and route_file != "__init__.py":
                try:
                    module_name = f"apps.models.{route_file[:-3]}"
                    __import__(module_name)
                except (ModuleNotFoundError, AttributeError) as e:
                    print(e)


async def create_project_tables():
    import_models()
    await db_manager.create_all_tables(Base)
