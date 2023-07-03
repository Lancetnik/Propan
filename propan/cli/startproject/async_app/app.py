from pathlib import Path

import typer

from propan.cli.startproject.async_app.kafka import create_kafka
from propan.cli.startproject.async_app.nats import create_nats, create_nats_js
from propan.cli.startproject.async_app.rabbit import create_rabbit
from propan.cli.startproject.async_app.redis import create_redis
from propan.cli.startproject.async_app.sqs import create_sqs

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


@async_app.command()
def nats(appname: str) -> None:
    """Create an asyncronous Nats Propan project at [APPNAME] directory"""
    project = create_nats(Path.cwd() / appname)
    typer.echo(f"Create an asyncronous Nats Propan project at: {project}")


@async_app.command(name="nats-js")
def nats_js(appname: str) -> None:
    """Create an asyncronous NatsJS Propan project at [APPNAME] directory"""
    project = create_nats_js(Path.cwd() / appname)
    typer.echo(f"Create an asyncronous NatsJS Propan project at: {project}")


@async_app.command()
def kafka(appname: str) -> None:
    """Create an asyncronous Kafka Propan project at [APPNAME] directory"""
    project = create_kafka(Path.cwd() / appname)
    typer.echo(f"Create an asyncronous Kafka Propan project at: {project}")


@async_app.command()
def sqs(appname: str) -> None:
    """Create an asyncronous SQS Propan project at [APPNAME] directory"""
    project = create_sqs(Path.cwd() / appname)
    typer.echo(f"Create an asyncronous SQS Propan project at: {project}")
