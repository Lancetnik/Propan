from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any, Tuple

import typer

from propan.cli.app import PropanApp


def try_import_propan(module: Path, app: str) -> PropanApp:
    try:
        propan_app = import_object(module, app)

        if not isinstance(propan_app, PropanApp):
            raise ValueError(f"{propan_app} is not a PropanApp")

    except (ValueError, FileNotFoundError, AttributeError) as e:
        typer.echo(e, err=True)
        typer.echo("Please, input module like [python_file:propan_app_name]", err=True)
        raise typer.Exit() from e

    else:
        return propan_app


def import_object(module: Path, app: str) -> Any:
    spec = spec_from_file_location("mode", f"{module}.py")

    if spec is None:  # pragma: no cover
        raise FileNotFoundError(module)

    mod = module_from_spec(spec)
    loader = spec.loader

    if loader is None:  # pragma: no cover
        raise ValueError(f"{spec} has no loader")

    loader.exec_module(mod)
    obj = getattr(mod, app)

    return obj


def get_app_path(app: str) -> Tuple[Path, str]:
    if ":" not in app:
        raise ValueError(f"{app} is not a PropanApp")

    module, propan_app = app.split(":", 2)

    mod_path = Path.cwd()
    for i in module.split("."):
        mod_path = mod_path / i

    return mod_path, propan_app
