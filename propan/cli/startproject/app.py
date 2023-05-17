import typer

from propan.cli.startproject.async_app import async_app
from propan.cli.startproject.sync_app import sync_app

create_app = typer.Typer(pretty_exceptions_short=True)
create_app.add_typer(async_app, name="async", help="Create an asynchronous app")
create_app.add_typer(sync_app, name="sync", help="Create a synchronous app")
