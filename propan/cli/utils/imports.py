from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location
from typing import Tuple, Any


def import_object(module: Path, app: str) -> Any:
    spec = spec_from_file_location("mode", f"{module}.py")

    if spec is None: # pragma: no cover
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
