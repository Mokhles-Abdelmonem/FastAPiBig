import importlib


def get_project_settings():
    """
    Tries to load a `settings` module from the user's project.
    Falls back to default settings inside the package.
    """
    try:
        settings = importlib.import_module("core.settings")
    except ModuleNotFoundError:
        raise Exception("Could not import settings module.")

    return settings
