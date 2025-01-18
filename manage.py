import os
import sys

def create_app_structure(app_name):
    """Creates a new app/module structure."""
    base_path = os.path.join("app", app_name)
    structure = {
        "__init__.py": "",
        "routes.py": f"""from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_{app_name}():
    return {{"message": "{app_name} app"}}""",
        "models.py": "",
        "schemas.py": "",
    }

    os.makedirs(base_path, exist_ok=True)
    for file_name, content in structure.items():
        with open(os.path.join(base_path, file_name), "w") as f:
            f.write(content)
    print(f"App '{app_name}' created successfully!")

def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: python manage.py <command> [args]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "startapp":
        if len(sys.argv) < 3:
            print("Usage: python manage.py startapp <app_name>")
            sys.exit(1)
        app_name = sys.argv[2]
        create_app_structure(app_name)
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
