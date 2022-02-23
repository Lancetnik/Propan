from pathlib import Path

from .configuration import init_settings


settings = init_settings(Path.cwd(), settings_dir='config')

__all__ = (
    'settings',
)
