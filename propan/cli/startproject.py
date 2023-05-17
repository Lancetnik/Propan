from pathlib import Path
from typing import Union, cast


def create(project_dir: Path, version: str) -> Path:
    project_dir = _create_project_dir(project_dir, version)
    app_dir = _create_app_dir(project_dir / "app")
    _create_config_dir(app_dir / "config")
    _create_core_dir(app_dir / "core")
    _create_apps_dir(app_dir / "apps")
    return project_dir


def _create_project_dir(dirname: Path, version: str) -> Path:
    project_dir = _touch_dir(dirname)

    _write_file(project_dir / "README.md")

    _write_file(
        project_dir / "Dockerfile",
        "FROM python:3.11.3-slim",
        "",
        "ENV PYTHONUNBUFFERED=1 \\",
        "PYTHONDONTWRITEBYTECODE=1 \\",
        "PIP_DISABLE_PIP_VERSION_CHECK=on",
        "",
        "RUN useradd -ms /bin/bash user",
        "",
        "USER user",
        "WORKDIR /home/user",
        "",
        "COPY requirements.txt requirements.txt",
        "",
        "RUN pip install -r requirements.txt",
        "",
        "COPY ./app ./app",
        "",
        'ENTRYPOINT [ "python", "-m", "propan", "run", "app.serve:app" ]',
    )

    _write_file(
        project_dir / "docker-compose.yaml",
        'version: "3"',
        "",
        "services:",
        "  rabbit:",
        "    image: rabbitmq",
        "    environment:",
        "      RABBITMQ_DEFAULT_USER: guest",
        "      RABBITMQ_DEFAULT_PASS: guest",
        "    healthcheck:",
        "      test: rabbitmq-diagnostics -q ping",
        "      interval: 3s",
        "      timeout: 30s",
        "      retries: 3",
        "    ports:",
        "      - 5672:5672",
        "",
        "  app:",
        "    build: .",
        "    environment:",
        "      APP_BROKER__URL: amqp://guest:guest@rabbit:5672/",
        "    volumes:",
        "      - ./app:/home/user/app:ro",
        "    depends_on:",
        "      rabbit:",
        "        condition: service_healthy",
    )

    _write_file(
        project_dir / "requirements.txt",
        f"propan[async_rabbit]=={version}",
        "python-dotenv",
    )

    _write_file(
        project_dir / ".gitignore",
        "*.env*",
        "__pycache__",
        "env/",
        "venv/",
    )

    return project_dir


def _create_app_dir(app: Path) -> Path:
    app_dir = _touch_dir(app)

    _write_file(
        app_dir / "serve.py",
        "import logging",
        "from typing import Optional",
        "",
        "from propan import PropanApp",
        "from propan.annotations import RabbitBroker, ContextRepo"
        "",
        "from core import broker",
        "from config import init_settings",
        "",
        "from apps import *  # import to register handlers  # NOQA",
        "",
        "",
        "app = PropanApp(broker)",
        "",
        "",
        "@app.on_startup",
        "async def init_app(broker: RabbitBroker, context: ContextRepo, env: Optional[str] = None):",
        "    settings = init_settings(env)",
        '    context.set_global("settings", settings)',
        "",
        "    logger_level = logging.DEBUG if settings.debug else logging.INFO",
        "    app.logger.setLevel(logger_level)",
        "    broker.logger.setLevel(logger_level)",
        "",
        "    await broker.connect(url=settings.broker.url)",
        "",
        "",
        'if __name__ == "__main__":',
        "    app.run()",
    )

    return app_dir


def _create_config_dir(config: Path) -> Path:
    config_dir = _touch_dir(config)

    _write_file(
        config_dir / ".env",
        "APP_DEBUG=True",
        "APP_BROKER__URL=amqp://guest:guest@localhost:5672/",
    )

    _write_file(
        config_dir / "settings.py",
        "from pathlib import Path",
        "from typing import Optional",
        "",
        "from pydantic import BaseSettings, BaseModel, Field",
        "",
        "",
        "CONFIG_DIR = Path(__file__).resolve().parent",
        "BASE_DIR = CONFIG_DIR.parent",
        "",
        "",
        "class BrokerSettings(BaseModel):",
        "    url: str = Field(...)",
        "",
        "",
        "class Settings(BaseSettings):",
        "    debug: bool = Field(True)",
        "    broker: BrokerSettings = Field(default_factory=BrokerSettings)",
        "    base_dir: Path = BASE_DIR",
        "",
        "    class Config:",
        "        env_prefix = 'APP_'",
        "        env_file_encoding = 'utf-8'",
        "        env_nested_delimiter = '__'",
        "",
        "",
        "def init_settings(env_file: Optional[str] = None) -> Settings:",
        '    env_file = CONFIG_DIR / (env_file or ".env")',
        "    if env_file.exists():",
        "        settings = Settings(_env_file=env_file)",
        "    else:",
        "        settings = Settings()",
        "    return settings",
    )

    _write_file(
        config_dir / "__init__.py",
        "from .settings import Settings, init_settings",
    )

    return config_dir


def _create_core_dir(core: Path) -> Path:
    core_dir = _touch_dir(core)

    _write_file(
        core_dir / "__init__.py",
        "from .dependencies import broker",
    )

    _write_file(
        core_dir / "dependencies.py",
        "from propan.brokers.rabbit import RabbitBroker",
        "",
        "broker = RabbitBroker()",
    )

    return core_dir


def _create_apps_dir(apps: Path) -> Path:
    apps_dir = _touch_dir(apps)

    _write_file(
        apps_dir / "__init__.py",
        "from .handlers import base_handler",
    )

    _write_file(
        apps_dir / "handlers.py",
        "from core import broker",
        "",
        "from propan.brokers.rabbit import RabbitQueue, RabbitExchange",
        "",
        "",
        '@broker.handle(queue=RabbitQueue("test"),',
        '               exchange=RabbitExchange("test"))',
        "async def base_handler(body: dict, logger):",
        "    logger.info(body)",
    )

    return apps_dir


def _touch_dir(dir: Union[Path, str]) -> Path:
    if isinstance(dir, str) is True:
        dir = Path(dir).resolve()

    dir = cast(Path, dir)
    if dir.exists() is False:
        dir.mkdir()
    return dir


def _write_file(path: Path, *content: str) -> None:
    path.touch()
    if content:
        path.write_text("\n".join(content))
