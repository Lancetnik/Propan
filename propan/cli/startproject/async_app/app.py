from pathlib import Path

import typer

from propan.cli.startproject.async_app.rabbit import create_rabbit


async_app = typer.Typer(pretty_exceptions_short=True)


@async_app.command()
def rabbit(appname: str):
    """Create an asyncronous RabbiMQ Propan project at [APPNAME] directory"""
    project = create_rabbit(Path.cwd() / appname)
    typer.echo(f"Create an asyncronous RabbiMQ Propan project at: {project}")
