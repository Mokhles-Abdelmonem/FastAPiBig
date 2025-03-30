import importlib


def get_project_settings():
    """
    Loads the project settings module.

    This function attempts to dynamically import the `settings` module from the
    user's project under the `core` package. If the module is not found, it falls
    back to importing the default `settings` module provided within the
    `FastAPIBig.conf.project_template.core` package.

    Returns:
        module: The imported settings module.

    Raises:
        ModuleNotFoundError: If neither the user's project settings nor the
        default settings module can be found.
    """
    try:
        settings = importlib.import_module("core.settings")
    except ModuleNotFoundError:
        from FastAPIBig.conf.project_template.core import settings

    return settings


def get_declarative_base():
    """
    Retrieves the declarative base class for SQLAlchemy models.

    This function attempts to import the `Base` class from the `core.database` module.
    If the module is not found, it falls back to importing the `Base` class from the
    `FastAPIBig.conf.project_template.core.database` module.

    Returns:
        Base: The declarative base class for SQLAlchemy models.
    """
    try:
        Base = importlib.import_module("core.database.Base")
    except ModuleNotFoundError:
        from FastAPIBig.conf.project_template.core.database import Base
    return Base
