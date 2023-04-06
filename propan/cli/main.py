"""Simple and fast framework to create message brokers based microservices"""
import logging
import sys
from typing import Dict, Sequence, Union

import click
from propan.__about__ import __version__
from propan.cli.app import PropanApp
from propan.log import access_logger, logger

LOG_LEVELS: Dict[str, int] = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
}


@click.group()
def cli() -> None:
    pass


@cli.add_command
@click.command()
def version() -> None:
    return _print_version()


@cli.add_command
@click.command(help="Create new Propan project at [APPNAME] directory")
@click.argument("appname")
def create(appname: str) -> None:
    from propan.cli.startproject import create

    create(appname, __version__)


@cli.add_command
@click.command(
    context_settings={
        "ignore_unknown_options": True,
        "allow_extra_args": True,
    },
    help="Run Propan app from [module:app]",
)
@click.argument("app")
@click.option(
    "--reload",
    is_flag=True,
    default=False,
    help="Reload app at code changing.",
    show_default=True,
)
@click.option(
    "--workers",
    type=int,
    default=1,
    help="Select number of processes.",
    show_default=True,
)
@click.option(
    "--log-level",
    type=click.Choice(tuple(LOG_LEVELS.keys())),
    default="info",
    help="Log level. [default: info]",
    show_default=True,
)
@click.pass_context
def run(
    ctx: click.Context,
    app: str,
    log_level: str = "info",
    reload: bool = False,
    workers: int = 1,
) -> None:
    if reload and workers > 1:
        raise ValueError("You can't use reload option with multiprocessing")

    _set_log_level(log_level)

    args = (app, _parse_cli_extra_options(ctx.args))

    if reload is True:
        from propan.cli.supervisors.watchgodreloader import WatchGodReload

        WatchGodReload(target=_run, args=args).run()

    elif workers > 1:
        from propan.cli.supervisors.multiprocess import Multiprocess

        Multiprocess(target=_run, args=(*args, logging.DEBUG), workers=workers).run()

    else:
        _run(*args)


def _run(
    app: str, context_kwargs: Dict[str, Union[bool, str]], log_level: int = logging.INFO
) -> None:
    try:
        propan_app = _get_app_object(app)

    except (ValueError, FileNotFoundError, AttributeError) as e:
        logger.error(e)
        logger.error("Please, input module like python_file:propan_app_name")
        exit()

    else:
        propan_app.run(log_level, **context_kwargs)


def _get_app_object(app: str) -> PropanApp:
    from importlib.util import module_from_spec, spec_from_file_location
    from pathlib import Path

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


def _parse_cli_extra_options(args: Sequence[str]) -> Dict[str, Union[bool, str]]:
    extra_kwargs: Dict[str, Union[bool, str]] = {}
    for item in args:
        arg = item.split("=")

        v: Union[bool, str]
        if len(arg) == 0:
            k, v = arg[0], True
        elif len(arg) == 2:
            k, v = arg
        else:
            raise ValueError(f"{arg} is not a valid argument")

        k = k.strip("-").strip().replace("-", "_")
        extra_kwargs[k] = v
    return extra_kwargs


def _set_log_level(level: str) -> None:
    log_level = LOG_LEVELS[level]
    logger.setLevel(log_level)
    access_logger.setLevel(log_level)


def _print_version() -> None:
    import platform

    click.echo(
        "Running propan %s with %s %s on %s"
        % (
            __version__,
            platform.python_implementation(),
            platform.python_version(),
            platform.system(),
        )
    )
