import typer

from propan.cli.app import PropanApp


def generate_doc_file(app: PropanApp) -> None:
    typer.echo(app)
