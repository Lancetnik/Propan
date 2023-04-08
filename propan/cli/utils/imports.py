from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location
from typing import Tuple

from propan.cli.app import PropanApp


def get_app_object(module: Path, app: str) -> PropanApp:
    spec = spec_from_file_location("mode", f"{module}.py")
    if spec is None:
        raise FileNotFoundError(f"{module}.py not found")

    mod = module_from_spec(spec)
    loader = spec.loader
    if loader is None:
        raise ValueError(f"{spec} has no loader")

    loader.exec_module(mod)
    app_obj = getattr(mod, app)
    if not isinstance(app_obj, PropanApp):
        raise ValueError(f"{app_obj} is not a PropanApp")

    return app_obj


def get_app_path(app: str) -> Tuple[Path, str]:
    if ":" not in app:
        raise ValueError(f"{app} is not a PropanApp")

    module, propan_app = app.split(":", 2)

    mod_path = Path.cwd()
    for i in module.split("."):
        mod_path = mod_path / i

    return mod_path, propan_app
