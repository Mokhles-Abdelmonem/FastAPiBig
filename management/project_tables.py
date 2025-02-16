import os
from orm.base.base_model import db_manager


def import_models():

    # Dynamically include routes
    apps_dir = os.path.join(os.getcwd(), "app")
    print(apps_dir)

    # For feature-based structure
    if os.path.exists(apps_dir):
        for app_name in os.listdir(apps_dir):
            app_path = os.path.join(apps_dir, app_name)
            if os.path.isdir(app_path):
                try:
                    module_name = f"app.{app_name}.models"
                    __import__(module_name)
                    print(module_name)
                except (ModuleNotFoundError, AttributeError) as e :
                    print(e)


    # For type-based structure
    routes_dir = os.path.join(apps_dir, "routes")
    if os.path.exists(routes_dir):
        for route_file in os.listdir(routes_dir):
            if route_file.endswith(".py") and route_file != "__init__.py":
                try:
                    module_name = f"app.models.{route_file[:-3]}"
                    __import__(module_name)
                    print(module_name)
                except (ModuleNotFoundError, AttributeError) as e :
                    print(e)


async def create_project_tables():
    import_models()
    await db_manager.create_all_tables()
