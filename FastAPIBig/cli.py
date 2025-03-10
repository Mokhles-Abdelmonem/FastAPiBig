import os
import shutil
import click

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "conf/project_template")


@click.command()
@click.argument("project_name")
def startproject(project_name):
    """Create a new FastAPI project with a standard structure."""
    project_path = os.path.join(os.getcwd(), project_name)

    if os.path.exists(project_path):
        click.echo("Error: Project directory already exists.")
        return

    shutil.copytree(TEMPLATE_DIR, project_path)
    click.echo(f"FastAPI project '{project_name}' created successfully!")


if __name__ == "__main__":
    startproject()
