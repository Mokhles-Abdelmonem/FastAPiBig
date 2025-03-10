import importlib
import sys

print("<<<<<<<<<<<<<<<<<<<<<<<<<< sys.path >>>>>>>>>>>>>>>>>>>>>>>>>>")
print(sys.path)

def get_project_settings():
    """
    Tries to load a `settings` module from the user's project.
    Falls back to default settings inside the package.
    """
    try:
        settings = importlib.import_module("settings")
        print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< settings >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print(settings)
    except ModuleNotFoundError:
        from FastAPIBig.management import default_settings as settings  # Fallback to internal defaults

    return settings
