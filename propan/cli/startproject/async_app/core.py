from pathlib import Path
from typing import Sequence

from propan.cli.startproject.utils import write_file


def create_app_file(
    app_dir: Path,
    broker_class: str,
    imports: Sequence[str] = (),
    broker_init: Sequence[str] = ("    await broker.connect(settings.broker.url)",),
) -> None:
    write_file(app_dir / "__init__.py")

    write_file(
        app_dir / "serve.py",
        "import logging",
        "from typing import Optional",
        "",
        "import anyio",
        *imports,
        f"from propan import PropanApp, {broker_class}",
        f"from propan.annotations import {broker_class} as Broker, ContextRepo",
        "",
        "from config import init_settings",
        "from apps import router",
        "",
        "",
        f"broker = {broker_class}()",
        "broker.include_router(router)",
        "",
        "app = PropanApp(broker)",
        "",
        "",
        "@app.on_startup",
        "async def init_app(broker: Broker, context: ContextRepo, env: Optional[str] = None):",
        "    settings = init_settings(env)",
        '    context.set_global("settings", settings)',
        "",
        "    logger_level = logging.DEBUG if settings.debug else logging.INFO",
        "    app.logger.setLevel(logger_level)",
        "    broker.logger.setLevel(logger_level)",
        "",
        *broker_init,
        "",
        "",
        'if __name__ == "__main__":',
        "    anyio.run(app.run)",
    )


def create_handlers_file(
    filepath: Path,
    router_class: str,
) -> None:
    write_file(
        filepath,
        f"from propan import {router_class}",
        "from propan.annotations import Logger",
        "",
        f"router = {router_class}()",
        "",
        '@router.handle("test")',
        "async def base_handler(body: dict, logger: Logger):",
        "    logger.info(body)",
    )
