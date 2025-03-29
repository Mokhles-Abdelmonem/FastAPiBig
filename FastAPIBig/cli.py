import os
import shutil
import click
import uvicorn
import asyncio
from FastAPIBig.management.project_tables import create_project_tables

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "conf/project_template")
APP_TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "conf/app_template")


@click.group()
def cli():
    """
    Defines a CLI (Command Line Interface) group for the FastAPI CLI tool.

    This serves as the entry point for defining and organizing CLI commands
    using the Click library.
    """
    pass


@cli.command()
@click.argument("project_name")
def createproject(project_name):
    """
    Create a new FastAPI project with a standard structure.

    This command generates a new FastAPI project in the specified directory
    using a predefined template structure.

    Args:
        project_name (str): The name of the new project directory to be created.

    Behavior:
        - Checks if a directory with the given project name already exists.
        - If the directory exists, displays an error message and exits.
        - If the directory does not exist, copies the template structure
          from the predefined template directory to the new project directory.
        - Displays a success message upon successful creation of the project.

    Raises:
        None
    """

    project_path = os.path.join(os.getcwd(), project_name)

    if os.path.exists(project_path):
        click.echo("Error: Project directory already exists.")
        return

    shutil.copytree(TEMPLATE_DIR, project_path)
    click.echo(f"FastAPI project '{project_name}' created successfully!")


@cli.command()
@click.argument("app_name")
@click.option("--tb", is_flag=True, help="Create a type-based structure instead of feature-based.")
def startapp(app_name, tb):
    """
    Command to create a new FastAPI app inside the project.

    This command allows the user to generate a new FastAPI application structure
    within the project directory. The user can choose between a type-based or
    feature-based structure for the app.

    Arguments:
        app_name (str): The name of the new FastAPI app to be created.

    Options:
        --tb (bool): If provided, creates a type-based structure instead of the
                     default feature-based structure.

    Behavior:
        - Checks if the apps directory already exists. If it does, an error message
          is displayed, and the command exits.
        - Creates the base directory for the apps if it does not already exist.
        - Depending on the `--tb` option:
            - Type-based structure: Copies specific template files into
              corresponding type-based directories (e.g., routes, models, etc.).
            - Feature-based structure: Copies the entire template directory into
              the apps directory.
        - Displays a success message upon successful creation of the apps.

    Raises:
        None

    Dependencies:
        - os: Used for path operations and directory creation.
        - shutil: Used for copying files and directories.
        - click: Used for command-line interface handling.
    """

    base_path = "apps"
    app_path = os.path.join(base_path, app_name)

    if os.path.exists(app_path):
        click.echo("Error: App directory already exists.")
        return

    os.makedirs(base_path, exist_ok=True)

    if tb:
        for file_name in os.listdir(APP_TEMPLATE_DIR):
            if file_name.startswith('__'):
                continue
            dir_name = file_name.split(".")[0]
            dest_dir = os.path.join(base_path, dir_name)
            os.makedirs(dest_dir, exist_ok=True)

            file_path = os.path.join(APP_TEMPLATE_DIR, file_name)
            dest_path = os.path.join(dest_dir, app_name + ".py")
            shutil.copy(file_path, dest_path)
    else:
        # Create feature-based structure
        shutil.copytree(APP_TEMPLATE_DIR, app_path)

    click.echo(f"FastAPI app '{app_name}' created successfully!")


@cli.command()
@click.option("--host", default="127.0.0.1", help="Host address to bind the server.")
@click.option("--port", default=8000, type=int, help="Port to run the server on.")
@click.option("--reload", is_flag=True, help="Enable auto-reloading.")
@click.option("--workers", default=None, type=int, help="Number of worker processes.")
def runserver(host, port, reload, workers):
    """
    Run the FastAPI development server.

    This command starts the FastAPI application using Uvicorn. It allows you to specify
    the host address, port, and other server configurations.

    Options:
        --host (str): The host address to bind the server. Defaults to "127.0.0.1".
        --port (int): The port to run the server on. Defaults to 8000.
        --reload (bool): Enable auto-reloading for development. Defaults to False.
        --workers (int): The number of worker processes to use. Defaults to None (determined by Uvicorn).

    Example:
        To run the server on the default host and port:
            $ python cli.py runserver

        To run the server on a custom host and port with auto-reload enabled:
            $ python cli.py runserver --host 0.0.0.0 --port 8080 --reload
    """
    uvicorn.run("FastAPIBig.management.fastapi_app:app", host=host, port=port, reload=reload, workers=workers)


@cli.command()
def createtables():
    """
    Command to create database tables asynchronously.

    This command uses asyncio to run the `create_project_tables` function,
    which is responsible for creating the necessary database tables for the project.
    Once the tables are created, a success message is displayed.

    Usage:
        Run this command from the CLI to initialize the database tables.

    Raises:
        Any exceptions raised during the execution of `create_project_tables` will
        propagate and should be handled appropriately.
    """
    asyncio.run(create_project_tables())
    click.echo("Database tables created successfully!")


if __name__ == "__main__":
    cli()
