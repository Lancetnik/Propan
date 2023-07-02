from pathlib import Path

from propan.cli.startproject.async_app.core import create_app_file, create_handlers_file
from propan.cli.startproject.core import (
    create_apps_dir,
    create_config_dir,
    create_env,
    create_project_dir,
)
from propan.cli.startproject.utils import touch_dir, write_file


def create_nats(dir: Path) -> Path:
    project_dir = _create_project_dir(dir, js=False)
    app_dir = _create_app_dir(project_dir / "app", js=False)
    _create_config_dir(app_dir / "config")
    _create_apps_dir(app_dir / "apps")
    return project_dir


def create_nats_js(dir: Path) -> Path:
    project_dir = _create_project_dir(dir, js=True)
    app_dir = _create_app_dir(project_dir / "app", js=True)
    _create_config_dir(app_dir / "config")
    _create_apps_dir(app_dir / "apps")
    return project_dir


def _create_project_dir(dirname: Path, js: bool) -> Path:
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
        "    command: -js" if js else "",
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


def _create_app_dir(app: Path, js: bool) -> Path:
    app_dir = touch_dir(app)
    create_app_file(app_dir, "NatsJSBroker" if js else "NatsBroker")
    return app_dir


def _create_config_dir(config: Path) -> Path:
    config_dir = create_config_dir(config)
    create_env(config_dir, "nats://localhost:4222/")
    return config_dir


def _create_apps_dir(apps: Path) -> Path:
    apps_dir = create_apps_dir(apps)

    create_handlers_file(
        apps_dir / "handlers.py",
        "NatsRouter",
    )

    return apps_dir
