import os
import shutil
import click
import uvicorn

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
def startapp(app_name):
    """Create a new FastAPI app inside the project."""
    if not os.path.exists("app"):
        os.makedirs("app")

    app_path = os.path.join("app", app_name)

    if os.path.exists(app_path):
        click.echo("Error: App directory already exists.")
        return

    shutil.copytree(APP_TEMPLATE_DIR, app_path)
    click.echo(f"FastAPI app '{app_name}' created successfully!")


@cli.command()
@click.option("--host", default="127.0.0.1", help="Host address to bind the server.")
@click.option("--port", default=8000, type=int, help="Port to run the server on.")
def runserver(host, port):
    """Run the FastAPI development server."""
    click.echo(f"Starting FastAPI server at http://{host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    cli()
