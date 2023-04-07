import logging
from pathlib import Path
from typing import Dict, Optional, Union

import typer
from propan.__about__ import __version__
from propan.cli.app import PropanApp
from propan.cli.utils.imports import get_app_object
from propan.cli.utils.logs import LogLevels, set_log_level
from propan.cli.utils.parser import parse_cli_args
from propan.log import logger

cli = typer.Typer()


def version_callback(version: bool) -> None:
    if version is True:
        import platform

        typer.echo(
            "Running propan %s with %s %s on %s"
            % (
                __version__,
                platform.python_implementation(),
                platform.python_version(),
                platform.system(),
            )
        )

        raise typer.Exit()


@cli.command()
def create(appname: str) -> None:
    """Create a new Propan project at [APPNAME] directory"""
    from propan.cli.startproject import create

    project = create(Path.cwd() / appname, __version__)
    typer.echo(f"Create Propan project template at: {project}")


@cli.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def run(
    ctx: typer.Context,
    app: str = typer.Argument(
        ..., help="[python_module:PropanApp] - path to your application"
    ),
    workers: int = typer.Option(
        1, show_default=False, help="Run [workers] applications with process spawning"
    ),
    log_level: LogLevels = typer.Option(
        LogLevels.info,
        case_sensitive=False,
        show_default=False,
        help="[INFO] default",
        autocompletion=lambda: list(LogLevels._member_map_.keys()),
    ),
    reload: bool = typer.Option(
        False, "--reload", is_flag=True, help="Restart app at directory files changes"
    ),
) -> None:
    """Run [MODULE:APP] Propan application"""
    app, extra = parse_cli_args(app, *ctx.args)

    args = (app, extra)

    if reload and workers > 1:
        raise ValueError("You can't use reload option with multiprocessing")

    set_log_level(log_level)

    if reload is True:
        from propan.cli.supervisors.watchgodreloader import WatchGodReload

        WatchGodReload(target=_run, args=args).run()

    elif workers > 1:
        from propan.cli.supervisors.multiprocess import Multiprocess

        Multiprocess(target=_run, args=(*args, logging.DEBUG), workers=workers).run()

    else:
        _run(*args)


@cli.callback()
def main(
    version: Optional[bool] = typer.Option(
        False,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show current platform, python and propan version",
    )
):
    """
    Generate, run and manage Propan apps to greater development experience
    """


def _run(
    app: PropanApp,
    context_kwargs: Dict[str, Union[bool, str]],
    log_level: int = logging.INFO,
) -> None:
    try:
        propan_app = get_app_object(app)

    except (ValueError, FileNotFoundError, AttributeError) as e:
        logger.error(e)
        logger.error("Please, input module like python_file:propan_app_name")
        exit()

    else:
        propan_app.run(log_level, **context_kwargs)
