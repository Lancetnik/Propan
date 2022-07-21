"""Simple and fast framework to create message brokers based microservices"""
import platform

import click


__version__ = '0.0.4.0'


def print_version(ctx: click.Context, param: click.Parameter, value: bool) -> None:
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
    callback=print_version,
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
    "--uvloop",
    default=True,
    help="Use uvloop as a default event loop.",
    show_default=True,
)
@click.option(
    "--config",
    default="config.yml",
    show_default=True,
    help="Select conf file of your consume.",
)
@click.option(
    "--workers",
    default=10,
    show_default=True,
    help="Select number of consumers.",
)
def run(
    app: str, reload: bool,
    config: str, workers: int,
    start: bool, uvloop: bool
):
    args = (app, config, workers, uvloop)

    if start:
        from propan.startproject import create
        create(app, __version__)

    if reload is True:
        from propan.supervisors.watchgodreloader import WatchGodReload
        WatchGodReload(target=_run, args=args).run()

    else:
        _run(*args)


def _run(app: str, config: str, workers: int, uvloop: bool):
    from importlib.util import spec_from_file_location, module_from_spec
    from pathlib import Path

    try:
        f, func = app.split(":", 2)

        mod_path = Path.cwd()
        for i in f.split('.'):
            mod_path = mod_path / i
        BASE_DIR = mod_path.parent

        from propan.config.configuration import init_settings
        config = init_settings(
            BASE_DIR, config,
            uvloop=uvloop, 
            **{
                "MAX_CONSUMERS": workers
            }
        )

        spec = spec_from_file_location("mode", f'{mod_path}.py')
        mod = module_from_spec(spec)
        spec.loader.exec_module(mod)
        propan_app = getattr(mod, func)

    except (ValueError, FileNotFoundError, AttributeError) as e:
        from loguru import logger
        logger.error(e)
        logger.error('Please, input module like python_file:propan_app_name')
        exit()

    else:
        propan_app.run()


if __name__ == "__main__":
    run()
