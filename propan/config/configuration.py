from importlib.util import spec_from_file_location
import os
from pathlib import Path
import sys
from typing import Generator, Dict, Tuple

import yaml
from loguru import logger

from propan.config.lazy import settings, LazySettings

import uvloop
uvloop.install()


def _get_recursive_name(config, name=None) -> Generator[Tuple, None, Tuple]:
    for k, v in config.items():
        if isinstance(v, dict):
            yield from _get_recursive_name(v, k)
        else:
            if name:
                k = f'{name}_{k}'
            yield k.upper(), v


def _parse_yml_config(conf_dir: Path, conffile: str = 'config.yml') -> dict:
    config = {}
    conf = conf_dir / conffile
    if conf.exists() is False:
        logger.error(f'FileNotFoundError: {conf}')
        exit()

    with conf.open('r') as f:
        if (data := yaml.safe_load(f)):
            for key, value in _get_recursive_name(data):
                config[key] = os.getenv(key, default=value)
    return config


def init_settings(
    base_dir: Path,
    conffile: str = 'config.yml',
    settings_dir: str = 'app.config',
    default_settings: str = 'settings',
    **options
) -> LazySettings:
    conf_dir = base_dir
    for i in settings_dir.split('.'):
        conf_dir = conf_dir / i

    config = {
        "BASE_DIR": base_dir,
        **_parse_yml_config(conf_dir, conffile),
        **options
    }
    sys.path.append(str(base_dir))

    i = spec_from_file_location("app", f'{conf_dir / default_settings}.py')
    settings.configure(i, **config)
    return settings
