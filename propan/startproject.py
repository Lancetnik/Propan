from pathlib import Path
from typing import Optional, List


BASE_DIR = Path.cwd()


def create(dirname: str, version: str):
    project_dir = _create_project_dir(dirname, version)
    app_dir = _create_app_dir(project_dir / "app")
    _create_config_dir(app_dir / "config")
    _create_core_dir(app_dir / "core")
    _create_apps_dir(app_dir / "apps")
    exit()


def _create_project_dir(dirname: str, version: str) -> Path:
    project_dir = _touch_dir(BASE_DIR / dirname)

    if project_dir.exists() is False:
        project_dir.mkdir()

    _write_file(project_dir / 'README.md')
    _write_file(project_dir / 'Dockerfile')

    _write_file(
        project_dir / 'docker-compose.yaml',
        'version: "3"',
        '',
        'services:',
        '  rabbit:',
        '    image: rabbitmq',
        '    environment:',
        '      RABBITMQ_DEFAULT_USER: guest',
        '      RABBITMQ_DEFAULT_PASS: guest',
        '    ports:',
        '      - 5672:5672',
    )

    _write_file(
        project_dir / 'requirements.txt',
        f'propan[async_rabbit]=={version}',
        'pydantic[dotenv]'
    )

    _write_file(
        project_dir / '.gitignore',
        '*.env*',
        '__pycache__',
        'env/',
        'venv/',
    )

    return project_dir


def _create_app_dir(app: Path) -> Path:
    app_dir = _touch_dir(app)

    _write_file(
        app_dir / 'serve.py',
        'import logging',
        'from typing import Optional',
        '',
        'from propan.app import PropanApp',
        'from propan.brokers import RabbitBroker',
        'from propan.utils import Context',
        '',
        'from core import broker',
        'from config import Settings, BASE_DIR',
        '',
        'from apps import *  # import to register handlers  # NOQA',
        '',
        '',
        'app = PropanApp(broker)',
        '',
        '',
        '@app.on_startup',
        'async def init_settings(broker: RabbitBroker, env: Optional[str], context: Context):',
        '    env_file = BASE_DIR / "config" / (env or ".env")',
        '    settings = Settings(_env_file=env_file)',
        '    context.set_context("settings", settings)',
        '',
        '    logger_level = logging.DEBUG if settings.debug else logging.INFO',
        '    app.logger.setLevel(logger_level)',
        '    broker.logger.setLevel(logger_level)',
        '',
        '    await broker.connect(url=settings.rabbit.url)',
        '',
        '',
        'if __name__ == "__main__":',
        '    app.run()',
    )

    return app_dir


def _create_config_dir(config: Path) -> Path:
    config_dir = _touch_dir(config)

    _write_file(
        config_dir / '.env',
        'APP_DEBUG=True',
        'APP_RABBIT__URL=amqp://guest:guest@localhost:5672/',
    )

    _write_file(
        config_dir / 'settings.py',
        'from pathlib import Path',
        '',
        'from pydantic import BaseSettings, BaseModel, Field',
        '',
        '',
        'BASE_DIR = Path(__file__).resolve().parent.parent',
        '',
        '',
        'class RabbitSettings(BaseModel):',
        '    url: str = Field(...)',
        '',
        '',
        'class Settings(BaseSettings):',
        '    debug: bool = Field(True)',
        '    rabbit: RabbitSettings = Field(default_factory=RabbitSettings)',
        '    base_dir: Path = BASE_DIR',
        '',
        '    class Config:',
        "        env_prefix = 'APP_'",
        "        env_file_encoding = 'utf-8'",
        "        env_nested_delimiter = '__'",
    )

    _write_file(
        config_dir / '__init__.py',
        'from .settings import Settings, BASE_DIR',
    )

    return config_dir


def _create_core_dir(core: Path) -> Path:
    core_dir = _touch_dir(core)

    _write_file(
        core_dir / '__init__.py',
        'from .dependencies import broker',
    )

    _write_file(
        core_dir / 'dependencies.py',
        'from propan.brokers import RabbitBroker',
        '',
        'broker = RabbitBroker()',
    )

    return core_dir


def _create_apps_dir(apps: Path) -> Path:
    apps_dir = _touch_dir(apps)

    _write_file(
        apps_dir / '__init__.py',
        'from .handlers import base_handler',
    )
    
    _write_file(
        apps_dir / 'handlers.py',
        'from core import broker',
        '',
        'from propan.brokers import RabbitQueue, RabbitExchange',
        '',
        '',
        '@broker.handle(queue=RabbitQueue("test"),',
        '               exchange=RabbitExchange("test"))',
        'async def base_handler(body: dict, logger):',
        '    logger.info(body)',
    )

    return apps_dir


def _touch_dir(dir: Path) -> Path:
    if dir.exists() is False:
        dir.mkdir()
    return dir


def _write_file(path: Path, *content: Optional[List[str]]):
    path.touch()
    if content:
        path.write_text('\n'.join(content))
