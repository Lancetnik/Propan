from pathlib import Path


BASE_DIR = Path.cwd()


def _create_project_dir(dirname: str) -> Path:
    project_dir = BASE_DIR / dirname

    if project_dir.exists() is False:
        project_dir.mkdir()

    (project_dir / 'README.md').touch()
    (project_dir / 'Dockerfile').touch()
    (project_dir / 'requirements.txt').touch()
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

    (config_dir / 'config.yml').touch()
    (config_dir / 'settings.py').touch()
    (config_dir / '__init__.py').touch()
    return config_dir


def create(dirname: str):
    project_dir = _create_project_dir(dirname)
    app_dir = _create_app_dir(project_dir)
    config_dir = _create_config_dir(app_dir)

    (app_dir / 'serve.py').touch()
    (app_dir / 'dependencies.py').touch()
    (app_dir / '__init__.py').touch()
