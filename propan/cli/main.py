import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, Optional

import typer

from propan.__about__ import __version__
from propan.cli.app import PropanApp
from propan.cli.utils.imports import get_app_path, import_object
from propan.cli.utils.logs import LogLevels, get_log_level, set_log_level
from propan.cli.utils.parser import SettingField, parse_cli_args
from propan.log import logger

cli = typer.Typer()


def version_callback(version: bool) -> None:
    if version is True:
        import platform

        typer.echo(
            "Running Propan %s with %s %s on %s"
            % (
                __version__,
                platform.python_implementation(),
                platform.python_version(),
                platform.system(),
            )
        )

        raise typer.Exit()


@cli.callback()
def main(
    version: Optional[bool] = typer.Option(
        False,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show current platform, python and propan version",
    )
) -> None:
    """
    Generate, run and manage Propan apps to greater development experience
    """


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
        LogLevels.info, case_sensitive=False, show_default=False, help="[INFO] default"
    ),
    reload: bool = typer.Option(
        False, "--reload", is_flag=True, help="Restart app at directory files changes"
    ),
) -> None:
    """Run [MODULE:APP] Propan application"""
    app, extra = parse_cli_args(app, *ctx.args)
    casted_log_level = get_log_level(log_level)

    module, app = get_app_path(app)

    app_dir = module.parent
    sys.path.insert(0, str(app_dir))

    args = (module, app, extra, casted_log_level)

    if reload and workers > 1:
        raise ValueError("You can't use reload option with multiprocessing")

    if reload is True:
        from propan.cli.supervisors.watchfiles import WatchReloader

        WatchReloader(target=_run, args=args, reload_dirs=(app_dir,)).run()

    elif workers > 1:
        from propan.cli.supervisors.multiprocess import Multiprocess

        Multiprocess(target=_run, args=(*args, logging.DEBUG), workers=workers).run()

    else:
        _run(module=module, app=app, extra_options=extra, log_level=casted_log_level)


def _run(
    module: Path,
    app: str,
    extra_options: Dict[str, SettingField],
    log_level: int = logging.INFO,
    app_level: int = logging.INFO,
) -> None:
    try:
        propan_app = import_object(module, app)

        if not isinstance(propan_app, PropanApp):
            raise ValueError(f"{propan_app} is not a PropanApp")

    except (ValueError, FileNotFoundError, AttributeError) as e:
        logger.error(e)
        logger.error("Please, input module like [python_file:propan_app_name]")
        exit()

    else:
        set_log_level(log_level, propan_app)

        propan_app._command_line_options = extra_options

        if sys.platform not in ("win32", "cygwin", "cli"):
            import uvloop

            if sys.version_info >= (3, 11):
                with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
                    runner.run(propan_app.run(log_level=app_level))
                    return

            else:
                uvloop.install()

        asyncio.run(propan_app.run(log_level=app_level))
