"""Simple and fast framework to create message brokers based microservices"""
import click

# Imports to use at __all__
from propan.brokers import *  # noqa: F403
from propan.utils import *  # noqa: F403
from propan.log import *  # noqa: F403


__version__ = "0.0.7.0"


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


@click.command()
def version():
    return _print_version()


@click.command(help="Create new Propan project at [APPNAME] directory")
@click.argument("appname")
def create(appname: str):
    from propan.startproject import create
    create(appname, __version__)


@click.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True,
), help="Run Propan app from [module:app]")
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
    default=1,
    show_default=True,
    type=int,
    help="Select number of processes.",
)
@click.pass_context
def run(
    ctx: click.Context,
    app: str,
    reload: bool = False,
    workers: int = 1,
):
    extra_kwargs = dict()
    for item in ctx.args:
        args = item.split("=")
        if len(args) == 0:
            k, v = args[0], True
        else:
            k, v = args
        extra_kwargs[k.strip("-").strip()] = v

    if reload and workers > 1:
        raise ValueError("You can't user reload option with multiprocessing")

    args = (app, extra_kwargs)

    if reload is True:
        from propan.supervisors.watchgodreloader import WatchGodReload
        WatchGodReload(target=_run, args=args).run()

    elif workers > 1:
        from propan.supervisors.multiprocess import Multiprocess
        Multiprocess(target=_run, args=args, workers=workers).run()

    else:
        _run(*args)


def _run(app: str, context_kwargs: dict):
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

    except (ValueError, FileNotFoundError, AttributeError) as e:
        from loguru import logger
        logger.error(e)
        logger.error('Please, input module like python_file:propan_app_name')
        exit()

    else:
        propan_app.run(**context_kwargs)


@click.group()
def cli():
    pass


cli.add_command(version)
cli.add_command(create)
cli.add_command(run)

if __name__ == "__main__":
    cli()
