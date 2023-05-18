from pathlib import Path

from propan.__about__ import __version__
from propan.cli.startproject.utils import touch_dir, write_file


def create_project_dir(dirname: Path, version: str) -> Path:
    project_dir = touch_dir(dirname)
    create_readme(project_dir)
    create_dockerfile(project_dir)
    create_requirements(project_dir, version)
    create_gitignore(project_dir)
    return project_dir


def create_readme(project_dir: Path) -> None:
    write_file(project_dir / "README.md")


def create_dockerfile(project_dir: Path) -> None:
    write_file(
        project_dir / "Dockerfile",
        "FROM python:3.11.3-slim",
        "",
        "ENV PYTHONUNBUFFERED=1 \\",
        "    PYTHONDONTWRITEBYTECODE=1 \\",
        "    PIP_DISABLE_PIP_VERSION_CHECK=on",
        "",
        "RUN useradd -ms /bin/bash user",
        "",
        "USER user",
        "WORKDIR /home/user",
        "",
        "COPY requirements.txt requirements.txt",
        "",
        "RUN pip install --no-warn-script-location --no-cahche-dir -r requirements.txt",
        "",
        "COPY ./app ./app",
        "",
        'ENTRYPOINT [ "python", "-m", "propan", "run", "app.serve:app" ]',
    )


def create_gitignore(project_dir: Path) -> None:
    write_file(
        project_dir / ".gitignore",
        "*.env*",
        "__pycache__",
        "env/",
        "venv/",
    )


def create_requirements(project_dir: Path, version: str) -> None:
    write_file(
        project_dir / "requirements.txt",
        f"{version}=={__version__}",
        "python-dotenv",
    )


def create_env(config_dir: Path, url: str) -> None:
    write_file(
        config_dir / ".env",
        "APP_DEBUG=True",
        f"APP_BROKER__URL={url}",
    )


def create_config_dir(config: Path) -> Path:
    config_dir = touch_dir(config)

    write_file(
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

    write_file(
        config_dir / "__init__.py",
        "from .settings import Settings, init_settings",
    )

    return config_dir


def create_core_dir(core: Path, broker_class: str) -> Path:
    core_dir = touch_dir(core)

    write_file(
        core_dir / "__init__.py",
        "from .dependencies import broker",
    )

    write_file(
        core_dir / "dependencies.py",
        f"from propan import {broker_class}",
        "",
        f"broker = {broker_class}()",
    )

    return core_dir


def create_apps_dir(apps: Path) -> Path:
    apps_dir = touch_dir(apps)

    write_file(
        apps_dir / "__init__.py",
        "from .handlers import base_handler",
    )

    return apps_dir
