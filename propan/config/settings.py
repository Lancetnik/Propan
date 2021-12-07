import importlib
from functools import partial
import os
from pathlib import Path
import sys
from typing import NoReturn, Generator, Optional

import yaml

from propan.config.lazy import settings


BASE_DIR = Path.cwd()


def _get_recursive_name(config, name=None) -> Generator[tuple, None, tuple]:
    for k, v in config.items():
        if isinstance(v, dict):
            for i, j in _get_recursive_name(v, k):
                yield i, j
        else:
            if name:
                k = f'{name}_{k}'
            yield k.upper(), v

def _parse_yml_config(conffile: Optional[str]) -> dict:
    config = {}
    if conffile:
        conf = BASE_DIR / 'app' / 'config' / conffile
        with open(conf, 'r') as f:
            if (data := yaml.safe_load(f)):
                for key, value in _get_recursive_name(data):
                    config[key] = os.getenv(key, default=value)
    return config


def init_settings(conffile: Optional[str], **options) -> NoReturn:
    config = {
        "BASE_DIR": BASE_DIR,
        **_parse_yml_config(conffile),
        **options
    }
    sys.path.append(str(BASE_DIR))
    i = importlib.import_module('app.config.settings')
    settings.configure(i, **config)
    return settings
