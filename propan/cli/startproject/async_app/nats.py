from pathlib import Path

from propan.cli.startproject.async_app.core import create_app_file
from propan.cli.startproject.core import (
    create_apps_dir,
    create_config_dir,
    create_core_dir,
    create_env,
    create_project_dir,
)
from propan.cli.startproject.utils import touch_dir, write_file


def create_nats(dir: Path) -> Path:
    project_dir = _create_project_dir(dir)
    app_dir = _create_app_dir(project_dir / "app")
    _create_config_dir(app_dir / "config")
    _create_core_dir(app_dir / "core")
    _create_apps_dir(app_dir / "apps")
    return project_dir


def _create_project_dir(dirname: Path) -> Path:
    project_dir = create_project_dir(dirname, "propan[async-nats]")

    write_file(
        project_dir / "docker-compose.yaml",
        'version: "3"',
        "",
        "services:",
        "  nats:",
        "    image: nats",
        "    ports:",
        "      - 4222:4222",
        "      - 8222:8222  # management",
        "",
        "  app:",
        "    build: .",
        "    environment:",
        "      APP_BROKER__URL: nats://nats:4222/",
        "    volumes:",
        "      - ./app:/home/user/app:ro",
        "    depends_on:",
        "      - nats",
    )

    return project_dir


def _create_app_dir(app: Path) -> Path:
    app_dir = touch_dir(app)
    create_app_file(app_dir, "NatsBroker")
    return app_dir


def _create_config_dir(config: Path) -> Path:
    config_dir = create_config_dir(config)
    create_env(config_dir, "nats://localhost:4222/")
    return config_dir


def _create_core_dir(core: Path) -> Path:
    core_dir = create_core_dir(core, "NatsBroker")
    return core_dir


def _create_apps_dir(apps: Path) -> Path:
    apps_dir = create_apps_dir(apps)

    write_file(
        apps_dir / "handlers.py",
        "from propan.annotations import Logger",
        "",
        "from core import broker",
        "",
        "",
        "@broker.handle('test')",
        "async def base_handler(body: dict, logger: Logger):",
        "    logger.info(body)",
    )

    return apps_dir
