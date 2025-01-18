import os
import sys
from fastapi import FastAPI
import uvicorn

routes_content = lambda app_name: f"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_{app_name}():
    return {{"message": "{app_name} app"}}
"""

def create_mvc_structure(app_name):
    """Creates a new app/module structure."""
    base_path = os.path.join("app", app_name)
    structure = {
        "__init__.py": "",
        "routes.py": routes_content(app_name),
        "models.py": "",
        "schemas.py": "",
    }

    os.makedirs(base_path, exist_ok=True)
    for file_name, content in structure.items():
        with open(os.path.join(base_path, file_name), "w") as f:
            f.write(content)
    print(f"App '{app_name}' created successfully!")

def start_server(host="127.0.0.1", port=8000):
    """Starts the FastAPI server."""
    app = FastAPI()

    # Dynamically include all routes from the apps
    apps_dir = os.path.join(os.getcwd(), "app")
    if os.path.exists(apps_dir):
        for app_name in os.listdir(apps_dir):
            app_path = os.path.join(apps_dir, app_name)
            if os.path.isdir(app_path):
                try:
                    module_name = f"app.{app_name}.routes"
                    routes_module = __import__(module_name, fromlist=["router"])
                    app.include_router(routes_module.router, prefix=f"/{app_name}")
                except (ModuleNotFoundError, AttributeError) as e:
                    print(f"Warning: Failed to include routes from '{app_name}': {e}")

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
            create_mvc_structure(app_name)

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
        print("  startapp <app_name>      Create a new FastAPI app/module.")
        print("  runserver [host] [port]  Start the FastAPI server (default: 127.0.0.1:8000).")
