from pathlib import Path
from typing import Optional, List


BASE_DIR = Path.cwd()


def _write_file(path: Path, *content: Optional[List[str]]):
    path.touch()
    if content:
        path.write_text('\n'.join(content))


def _create_project_dir(dirname: str, version: str) -> Path:
    project_dir = BASE_DIR / dirname

    if project_dir.exists() is False:
        project_dir.mkdir()

    _write_file(project_dir / 'README.md')
    _write_file(project_dir / 'Dockerfile')

    _write_file(
        project_dir / 'docker-compose.yml',
        'services:',
        '    rabbit:',
        '        image: rabbitmq:3',
        '        environment:',
        '            - RABBITMQ_DEFAULT_USER=user',
        '            - RABBITMQ_DEFAULT_PASS=password',
        '        ports:',
        '            - 5672:5672'
    )

    _write_file(project_dir / 'requirements.txt', f'propan=={version}')

    _write_file(
        project_dir / '.gitignore',
        'config.yml',
        '__pycache__',
        'env/',
        'venv/'
    )

    return project_dir


def _create_app_dir(project_dir: Path) -> Path:
    app_dir = project_dir / 'app'

    if app_dir.exists() is False:
        app_dir.mkdir()

    return app_dir


def _create_config_dir(app_dir: Path) -> Path:
    config_dir = app_dir / 'config'

    if config_dir.exists() is False:
        config_dir.mkdir()

    _write_file(
        config_dir / 'config.yml',
        'RABBIT:',
        '   HOST: 127.0.0.1',
        '   PORT: 5672',
        '   LOGIN: user',
        '   PASSWORD: password',
        '   VHOST: /'
    )

    _write_file(
        config_dir / 'settings.py',
        'from propan.config import settings\n'
    )

    _write_file(config_dir / '__init__.py')
    return config_dir


def create(dirname: str, version):
    project_dir = _create_project_dir(dirname, version)
    app_dir = _create_app_dir(project_dir)
    config_dir = _create_config_dir(app_dir)

    _write_file(
        app_dir / 'serve.py',
        'from propan.app import PropanApp\n',
        'from dependencies import broker\n\n',
        'app = PropanApp(broker)\n\n',
        '@app.handle(queue_name="test")',
        'async def base_handler(message):',
        '   print(message)\n\n',
        'if __name__=="__main__":',
        '   app.run()\n'
    )

    _write_file(
        app_dir / 'dependencies.py',
        'from propan.config import settings',
        'from propan.brokers import RabbitBroker',
        'from propan.logger import loguru\n\n',
        'broker = RabbitBroker(',
        '   host=settings.RABBIT_HOST,',
        '   login=settings.RABBIT_LOGIN,',
        '   password=settings.RABBIT_PASSWORD,',
        '   vhost=settings.RABBIT_VHOST,',
        '   logger=loguru',
        ')\n'
    )

    _write_file(app_dir / '__init__.py')
    exit()
