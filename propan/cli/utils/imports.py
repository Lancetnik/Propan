import sys

from propan.cli.app import PropanApp


def get_app_object(app: str) -> PropanApp:
    from importlib.util import module_from_spec, spec_from_file_location
    from pathlib import Path

    if ":" not in app:
        raise ValueError(f"{app} is not a PropanApp")

    f, func = app.split(":", 2)

    mod_path = Path.cwd()
    for i in f.split("."):
        mod_path = mod_path / i

    sys.path.insert(0, str(mod_path.parent))

    spec = spec_from_file_location("mode", f"{mod_path}.py")
    if spec is None:
        raise FileNotFoundError(f"{mod_path}.py not found")

    mod = module_from_spec(spec)
    loader = spec.loader
    if loader is None:
        raise ValueError(f"{spec} has no loader")

    loader.exec_module(mod)
    app = getattr(mod, func)
    if not isinstance(app, PropanApp):
        raise ValueError(f"{app} is not a PropanApp")

    return app
