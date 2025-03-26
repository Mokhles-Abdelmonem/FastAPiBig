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
    """FastAPI CLI tool"""
    pass


@cli.command()
@click.argument("project_name")
def createproject(project_name):
    """Create a new FastAPI project with a standard structure."""
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
    """Create a new FastAPI app inside the project."""
    base_path = "app"
    app_path = os.path.join(base_path, app_name)

    if os.path.exists(app_path):
        click.echo("Error: App directory already exists.")
        return

    os.makedirs(base_path, exist_ok=True)

    if tb:
        # Create type-based structure
        dirs = ["routes", "models", "schemas"]
        for dir_name in dirs:
            dir_path = os.path.join(base_path, dir_name)
            os.makedirs(dir_path, exist_ok=True)

        for file_name in os.listdir(APP_TEMPLATE_DIR):
            file_path = os.path.join(APP_TEMPLATE_DIR, file_name)
            if os.path.isfile(file_path):
                for dir_name in dirs:
                    dest_path = os.path.join(base_path, dir_name, file_name)
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
    """Run the FastAPI development server."""
    click.echo(f"Starting FastAPI server at http://{host}:{port}")
    uvicorn.run("FastAPIBig.management.fastapi_app:app", host=host, port=port, reload=reload, workers=workers)


@cli.command()
def createtables():
    """Create database tables asynchronously."""
    asyncio.run(create_project_tables())
    click.echo("Database tables created successfully!")


if __name__ == "__main__":
    cli()
