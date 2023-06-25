from pathlib import Path

from propan.cli.startproject.async_app.core import create_app_file, create_handlers_file
from propan.cli.startproject.core import (
    create_apps_dir,
    create_config_dir,
    create_env,
    create_project_dir,
)
from propan.cli.startproject.utils import touch_dir, write_file


def create_redis(dir: Path) -> Path:
    project_dir = _create_project_dir(dir)
    app_dir = _create_app_dir(project_dir / "app")
    _create_config_dir(app_dir / "config")
    _create_apps_dir(app_dir / "apps")
    return project_dir


def _create_project_dir(dirname: Path) -> Path:
    project_dir = create_project_dir(dirname, "propan[async-redis]")

    write_file(
        project_dir / "docker-compose.yaml",
        'version: "3"',
        "",
        "services:",
        "  redis:",
        "    image: redis",
        "    healthcheck:",
        "      test: ['CMD', 'redis-cli', 'ping']",
        "      interval: 3s",
        "      timeout: 30s",
        "      retries: 3",
        "    ports:",
        "      - 6379:6379",
        "",
        "  app:",
        "    build: .",
        "    environment:",
        "      APP_BROKER__URL: redis://redis:6379/",
        "    volumes:",
        "      - ./app:/home/user/app:ro",
        "    depends_on:",
        "      redis:",
        "        condition: service_healthy",
    )

    return project_dir


def _create_app_dir(app: Path) -> Path:
    app_dir = touch_dir(app)
    create_app_file(app_dir, "RedisBroker")
    return app_dir


def _create_config_dir(config: Path) -> Path:
    config_dir = create_config_dir(config)
    create_env(config_dir, "redis://localhost:6379/")
    return config_dir


def _create_apps_dir(apps: Path) -> Path:
    apps_dir = create_apps_dir(apps)

    create_handlers_file(
        apps_dir / "handlers.py",
        "RedisRouter",
    )

    return apps_dir
