from pathlib import Path

from .lazy import settings
from .configuration import init_settings


settings_dir = 'config'

conf_file = Path.cwd() / settings_dir / 'config.yml'
if conf_file.exists() is True:
    settings = init_settings(Path.cwd(), settings_dir=settings_dir)

__all__ = (
    'settings'
)
