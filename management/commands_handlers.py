import os
from fastapi import FastAPI
import uvicorn

from management.project_tables import create_project_tables


def generate_routes_content(app_name):
    return f"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_{app_name}():
    return {{"message": "{app_name} app"}}
"""


def create_type_based_structure(app_name):
    """Creates a type-based (type-by-functionality) app structure."""
    base_path = os.path.join("app")
    dirs = ["routes", "models", "schemas"]

    for dir_name in dirs:
        dir_path = os.path.join(base_path, dir_name)
        os.makedirs(dir_path, exist_ok=True)

        file_path = os.path.join(dir_path, f"{app_name}.py")
        content = ""

        if dir_name == "routes":
            content = generate_routes_content(app_name)

        with open(file_path, "w") as f:
            f.write(content)

    print(f"Type-based app '{app_name}' created successfully!")


def create_feature_based_structure(app_name):
    """Creates a feature-based app structure."""
    base_path = os.path.join("app", app_name)
    structure = {
        "__init__.py": "",
        "routes.py": generate_routes_content(app_name),
        "models.py": "",
        "schemas.py": "",
    }

    os.makedirs(base_path, exist_ok=True)
    for file_name, content in structure.items():
        with open(os.path.join(base_path, file_name), "w") as f:
            f.write(content)

    print(f"Feature-based app '{app_name}' created successfully!")


def start_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = True,
    workers: int | None = None,
):
    """Starts the FastAPI server."""
    uvicorn.run(
        "management.fastapi_app:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
    )


def create_tables(argv):
    import asyncio

    asyncio.run(create_project_tables())


def startapp_handler(argv):
    if len(argv) < 3:
        print("Error: App name is required for 'startapp' command.")
        return

    app_name = argv[2]

    # Check for folder structure flag
    if "--tb" in argv:
        create_type_based_structure(app_name)
    else:
        # Default to feature-based structure
        create_feature_based_structure(app_name)


def runserver_handler(argv):
    host = "127.0.0.1"
    port = 8000
    if len(argv) >= 3:
        host = argv[2]
    if len(argv) >= 4:
        port = int(argv[3])
    # TODO: ADD more args
    start_server(host, port)


def show_help():
    print("Available commands:")
    print("  startapp <app_name> [--tb]   Create a new FastAPI app/module.")
    print("    --tb: Create type-based structure (default is feature-based)")
    print(
        "  runserver [host] [port]      Start the FastAPI server (default: 127.0.0.1:8000)."
    )


def help_handler(argv):
    print(f"Error: Unknown command '{argv[1]}'.")
    show_help()
