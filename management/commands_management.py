import os
import sys
from fastapi import FastAPI
import uvicorn


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


def start_server(host="127.0.0.1", port=8000):
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

    uvicorn.run(app, host=host, port=port)


class ManageCommands:
    def __init__(self, argv: list = None):
        self.argv = argv or []

    def execute(self):
        if len(self.argv) < 2:
            self.show_help()
            return

        command = self.argv[1]

        if command == "startapp":
            if len(self.argv) < 3:
                print("Error: App name is required for 'startapp' command.")
                return

            app_name = self.argv[2]

            # Check for folder structure flag
            if "--tb" in self.argv:
                create_type_based_structure(app_name)
            else:
                # Default to feature-based structure
                create_feature_based_structure(app_name)

        elif command == "runserver":
            host = "127.0.0.1"
            port = 8000
            if len(self.argv) >= 3:
                host = self.argv[2]
            if len(self.argv) >= 4:
                port = int(self.argv[3])
            start_server(host, port)

        else:
            print(f"Error: Unknown command '{command}'.")
            self.show_help()

    @staticmethod
    def show_help():
        print("Available commands:")
        print("  startapp <app_name> [--tb]   Create a new FastAPI app/module.")
        print("    --tb: Create type-based structure (default is feature-based)")
        print("  runserver [host] [port]      Start the FastAPI server (default: 127.0.0.1:8000).")


def main():
    ManageCommands(sys.argv).execute()


if __name__ == "__main__":
    main()