"""Simple and fast framework to create message brokers based microservices"""
from typing import Optional

import click

from propan.app import PropanApp
from propan.brokers import RabbitBroker

# Imports to use at __all__
from propan.brokers import *  # noqa: F403
from propan.utils import *  # noqa: F403


__version__ = "0.0.6.8"


def _print_version(ctx: click.Context, param: click.Parameter, value: bool) -> None:
    import platform

    if not value or ctx.resilient_parsing:
        return

    click.echo(
        "Running propan %s with %s %s on %s"
        % (
            __version__,
            platform.python_implementation(),
            platform.python_version(),
            platform.system(),
        )
    )
    ctx.exit()


@click.command()
@click.argument("app")
@click.option(
    "--version",
    is_flag=True,
    callback=_print_version,
    expose_value=False,
    is_eager=True,
    help="Display the propan version and exit.",
)
@click.option(
    "--start",
    is_flag=True,
    default=False,
    help="Create a new propan project.",
)
@click.option(
    "--reload",
    is_flag=True,
    default=False,
    help="Reload app at code changing.",
    show_default=True,
)
@click.option(
    "--workers",
    default=1,
    show_default=True,
    type=int,
    help="Select number of processes.",
)
def run(
    app: str,
    reload: bool,
    start: bool,
    workers: Optional[int],
):
    if reload and workers > 1:
        raise ValueError("You can't user reload option with multiprocessing")

    mulriprocess: bool = workers > 1
    args = (app, mulriprocess)

    if start:
        from propan.startproject import create
        create(app, __version__)

    if reload is True:
        from propan.supervisors.watchgodreloader import WatchGodReload
        WatchGodReload(target=_run, args=args).run()

    elif workers > 1:
        from propan.supervisors.multiprocess import Multiprocess
        Multiprocess(target=_run, args=args, workers=workers).run()

    else:
        _run(*args)


def _run(app: str, mulriprocess: bool):
    from importlib.util import spec_from_file_location, module_from_spec
    from pathlib import Path

    try:
        f, func = app.split(":", 2)

        mod_path = Path.cwd()
        for i in f.split('.'):
            mod_path = mod_path / i

        spec = spec_from_file_location("mode", f'{mod_path}.py')
        mod = module_from_spec(spec)
        spec.loader.exec_module(mod)
        propan_app = getattr(mod, func)

        if mulriprocess is True:
            propan_app.logger = empty

    except (ValueError, FileNotFoundError, AttributeError) as e:
        from loguru import logger
        logger.error(e)
        logger.error('Please, input module like python_file:propan_app_name')
        exit()

    else:
        propan_app.run()


if __name__ == "__main__":
    run()
