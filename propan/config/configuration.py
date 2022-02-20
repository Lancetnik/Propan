import importlib
import os
from pathlib import Path
import sys
from typing import Generator, Optional, Dict, Tuple

import yaml

from propan.config.lazy import settings, LazySettings


BASE_DIR = Path.cwd()


def _get_recursive_name(config, name=None) -> Generator[Tuple, None, Tuple]:
    for k, v in config.items():
        if isinstance(v, dict):
            yield from _get_recursive_name(v, k)
        else:
            if name:
                k = f'{name}_{k}'
            yield k.upper(), v


def _parse_yml_config(conffile: str = 'config.yml') -> dict:
    config = {}
    conf = BASE_DIR / 'app' / 'config' / conffile
    with conf.open('r') as f:
        if (data := yaml.safe_load(f)):
            for key, value in _get_recursive_name(data):
                config[key] = os.getenv(key, default=value)
    return config


def init_settings(
    conffile: str = 'config.yml',
    default_settings: str = 'app.config.settings',
    **options
) -> LazySettings:
    config = {
        "BASE_DIR": BASE_DIR,
        **_parse_yml_config(conffile),
        **options
    }
    sys.path.append(str(BASE_DIR))
    i = importlib.import_module(default_settings)
    settings.configure(i, **config)
    return settings
