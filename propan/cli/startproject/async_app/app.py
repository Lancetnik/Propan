from pathlib import Path

import typer

from propan.cli.startproject.async_app.rabbit import create_rabbit
from propan.cli.startproject.async_app.redis import create_redis

async_app = typer.Typer(pretty_exceptions_short=True)


@async_app.command()
def rabbit(appname: str) -> None:
    """Create an asyncronous RabbiMQ Propan project at [APPNAME] directory"""
    project = create_rabbit(Path.cwd() / appname)
    typer.echo(f"Create an asyncronous RabbiMQ Propan project at: {project}")


@async_app.command()
def redis(appname: str) -> None:
    """Create an asyncronous Redis Propan project at [APPNAME] directory"""
    project = create_redis(Path.cwd() / appname)
    typer.echo(f"Create an asyncronous Redis Propan project at: {project}")
