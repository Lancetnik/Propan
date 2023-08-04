from pathlib import Path

from propan.cli.startproject.async_app.core import create_app_file, create_handlers_file
from propan.cli.startproject.core import (
    create_apps_dir,
    create_config_dir,
    create_env,
    create_project_dir,
)
from propan.cli.startproject.utils import touch_dir, write_file


def create_kafka(dir: Path) -> Path:
    project_dir = _create_project_dir(dir)
    app_dir = _create_app_dir(project_dir / "app")
    _create_config_dir(app_dir / "config")
    _create_apps_dir(app_dir / "apps")
    return project_dir


def _create_project_dir(dirname: Path) -> Path:
    project_dir = create_project_dir(dirname, "propan[async-kafka]")

    write_file(
        project_dir / "docker-compose.yaml",
        'version: "3"',
        "",
        "services:",
        "  kafka:",
        "    image: bitnami/kafka:3.5.0",
        "    ports:",
        "      - 9092:9092",
        "    environment:",
        "      - KAFKA_ENABLE_KRAFT=yes",
        "      - KAFKA_CFG_NODE_ID=1",
        "      - KAFKA_CFG_PROCESS_ROLES=broker,controller",
        "      - KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER",
        "      - KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093",
        "      - KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT",
        "      - KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://127.0.0.1:9092",
        "      - KAFKA_BROKER_ID=1",
        "      - KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=1@kafka:9093",
        "      - ALLOW_PLAINTEXT_LISTENER=yes",
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


def _create_apps_dir(apps: Path) -> Path:
    apps_dir = create_apps_dir(apps)

    create_handlers_file(
        apps_dir / "handlers.py",
        "KafkaRouter",
    )

    return apps_dir
