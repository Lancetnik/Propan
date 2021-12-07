import os
from pathlib import Path


BASE_DIR = Path.cwd()


def _create_project_dir(dirname: str) -> Path:
    project_dir = BASE_DIR / dirname
    if not os.path.isdir(project_dir):
        os.mkdir(project_dir)

    with open(str(project_dir / 'README.md'), "w") as f:
        pass

    with open(str(project_dir / 'Dockerfile'), "w") as f:
        pass

    with open(str(project_dir / 'reqyirements.txt'), "w") as f:
        f.write("propan")
    
    return project_dir


def _create_app_dir(project_dir: Path) -> Path:
    app_dir = project_dir / 'app'

    if not os.path.isdir(app_dir):
        os.mkdir(app_dir)

    return app_dir


def _create_config_dir(app_dir: Path) -> Path:
    config_dir = app_dir / 'config'

    if not os.path.isdir(config_dir):
        os.mkdir(config_dir)
    
    with open(str(config_dir / 'config.yml'), "w") as f:
        pass
    
    with open(str(config_dir / 'settings.py'), "w") as f:
        pass

    return config_dir


def create(dirname: str):
    project_dir = _create_project_dir(dirname)
    app_dir = _create_app_dir(project_dir)
    config_dir = _create_config_dir(app_dir)
    
    with open(str(app_dir / 'serve.py'), "w") as f:
        pass

    with open(str(app_dir / 'dependencies.py'), "w") as f:
        pass