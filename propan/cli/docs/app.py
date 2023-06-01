import sys

import typer

from propan.cli.docs.gen import generate_doc_file
from propan.cli.utils.imports import get_app_path, try_import_propan

docs_app = typer.Typer(pretty_exceptions_short=True)


@docs_app.command(name="gen")
def gen(
    app: str = typer.Argument(
        ..., help="[python_module:PropanApp] - path to your application"
    ),
) -> None:
    """Generate an AsyncAPI schema.yaml for your project"""
    module, app = get_app_path(app)
    app_dir = module.parent
    sys.path.insert(0, str(app_dir))
    propan_app = try_import_propan(module, app)

    generate_doc_file(propan_app)
