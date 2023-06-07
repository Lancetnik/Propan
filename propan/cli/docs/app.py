import sys
from pathlib import Path

import typer

from propan.cli.docs.gen import generate_doc_file, get_schema_yaml
from propan.cli.docs.serve import serve_docs
from propan.cli.utils.imports import get_app_path, try_import_propan

docs_app = typer.Typer(pretty_exceptions_short=True)


@docs_app.command(name="gen")
def gen(
    app: str = typer.Argument(
        ...,
        help="[python_module:PropanApp] - path to your application",
    ),
    filename: str = typer.Option(
        "asyncapi.yaml",
        "-f",
        "--f",
        case_sensitive=False,
        show_default=True,
        help="generated document filename",
    ),
) -> None:
    """Generate an AsyncAPI schema.yaml for your project"""
    current_dir = Path.cwd()
    generated_filepath = current_dir / filename

    module, app = get_app_path(app)
    app_dir = module.parent
    sys.path.insert(0, str(app_dir))
    propan_app = try_import_propan(module, app)

    generate_doc_file(propan_app, generated_filepath)


@docs_app.command(name="serve")
def serve(
    app: str = typer.Argument(
        ...,
        help="[python_module:PropanApp] or [asyncapi.yaml] - path to your application documentation",
    ),
    host: str = typer.Option("localhost", help="documentation hosting address"),
    port: int = typer.Option(8000, help="documentation hosting port"),
) -> None:
    """Serve project AsyncAPI scheme"""
    if ":" in app:
        module, app = get_app_path(app)
        app_dir = module.parent
        sys.path.insert(0, str(app_dir))
        propan_app = try_import_propan(module, app)

        schema = get_schema_yaml(propan_app)

    else:
        schema_filepath = Path.cwd() / app

        schema = schema_filepath.read_text()

    serve_docs(schema, host, port)