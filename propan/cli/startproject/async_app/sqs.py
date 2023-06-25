from pathlib import Path

from propan.cli.startproject.async_app.core import create_app_file, create_handlers_file
from propan.cli.startproject.core import (
    create_apps_dir,
    create_config_dir,
    create_env,
    create_project_dir,
)
from propan.cli.startproject.utils import touch_dir, write_file


def create_sqs(dir: Path) -> Path:
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
        "  sqs:",
        "    image: softwaremill/elasticmq-native",
        "    ports:",
        "      - 9324:9324",
        "      - 9325:9325  # management",
        "",
        "  app:",
        "    build: .",
        "    environment:",
        "      APP_BROKER__URL: http://sqs:9324/",
        "    volumes:",
        "      - ./app:/home/user/app:ro",
        "    depends_on:",
        "      - sqs",
    )

    return project_dir


def _create_app_dir(app: Path) -> Path:
    app_dir = touch_dir(app)
    create_app_file(
        app_dir,
        "SQSBroker",
        imports=(
            "from botocore import UNSIGNED",
            "from aiobotocore.config import AioConfig",
        ),
        broker_init=(
            "    if settings.debug is True:",
            "        config = AioConfig(signature_version=UNSIGNED)",
            "    else:",
            "        config = None",
            "",
            "    await broker.connect(",
            "        settings.broker.url,",
            "        region_name=settings.broker.region,",
            "        config=config,",
            "    )",
        ),
    )
    return app_dir


def _create_config_dir(config: Path) -> Path:
    config_dir = create_config_dir(
        config,
        "class BrokerSettings(BaseModel):",
        "    url: str = Field(...)",
        '    region: str = "us-west-2"',
    )
    create_env(config_dir, "http://localhost:9324/")
    return config_dir


def _create_apps_dir(apps: Path) -> Path:
    apps_dir = create_apps_dir(apps)

    create_handlers_file(
        apps_dir / "handlers.py",
        "SQSRouter",
    )

    return apps_dir
