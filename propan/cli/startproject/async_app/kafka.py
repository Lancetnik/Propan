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


def create_kafka(dir: Path) -> Path:
    project_dir = _create_project_dir(dir)
    app_dir = _create_app_dir(project_dir / "app")
    _create_config_dir(app_dir / "config")
    _create_core_dir(app_dir / "core")
    _create_apps_dir(app_dir / "apps")
    return project_dir


def _create_project_dir(dirname: Path) -> Path:
    project_dir = create_project_dir(dirname, "propan[async-kafka]")

    write_file(
        project_dir / "docker-compose.yaml",
        'version: "3"',
        "",
        "services:",
        "  zookeeper:",
        "    image: wurstmeister/zookeeper",
        "    ports:",
        "      - 2181:2181",
        "",
        "  kafka:",
        "    image: wurstmeister/kafka",
        "    ports:",
        "      - 9092:9092",
        "    expose:",
        "      - 9093",
        "    environment:",
        "      KAFKA_ADVERTISED_LISTENERS: INSIDE://kafka:9093,OUTSIDE://localhost:9092",
        "      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: INSIDE:PLAINTEXT,OUTSIDE:PLAINTEXT",
        "      KAFKA_LISTENERS: INSIDE://0.0.0.0:9093,OUTSIDE://0.0.0.0:9092",
        "      KAFKA_INTER_BROKER_LISTENER_NAME: INSIDE",
        '      KAFKA_CFG_AUTO_CREATE_TOPICS_ENABLE: "true"',
        "      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181",
        '      KAFKA_CREATE_TOPICS: "topic_test:1:1"',
        "    depends_on:",
        "      - zookeeper",
        "",
        "  app:",
        "    build: .",
        "    environment:",
        "      APP_BROKER__URL: kafka:9092",
        "    volumes:",
        "      - ./app:/home/user/app:ro",
        "    depends_on:",
        "      - kafka",
    )

    return project_dir


def _create_app_dir(app: Path) -> Path:
    app_dir = touch_dir(app)
    create_app_file(app_dir, "KafkaBroker")
    return app_dir


def _create_config_dir(config: Path) -> Path:
    config_dir = create_config_dir(config)
    create_env(config_dir, "localhost:9092")
    return config_dir


def _create_core_dir(core: Path) -> Path:
    core_dir = create_core_dir(core, "KafkaBroker")
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
