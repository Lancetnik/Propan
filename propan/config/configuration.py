from importlib.util import spec_from_file_location, module_from_spec
import os
from pathlib import Path

import sys
from typing import Generator, Tuple

import yaml
from loguru import logger

from propan.config.lazy import settings, LazySettings


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
        return config

    with conf.open('r') as f:
        if (data := yaml.safe_load(f)):
            for key, value in _get_recursive_name(data):
                config[key] = os.getenv(key, default=value)

    return config


def init_settings(
    base_dir: Path,
    conffile: str = 'config.yml',
    settings_dir: str = 'config',
    default_settings: str = 'settings',
    uvloop: bool = True,
    **options
) -> LazySettings:
    conf_dir = base_dir
    for i in settings_dir.split('.'):
        conf_dir = conf_dir / i
    base_dir = conf_dir.parent

    config = {
        "BASE_DIR": base_dir,
        **_parse_yml_config(conf_dir, conffile),
        **options
    }
    settings.configure(None, **config)
    sys.path.append(str(base_dir))

    spec = spec_from_file_location("app", f'{conf_dir / default_settings}.py')
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    settings.configure(mod, **config)

    try:
        user_uv = getattr(mod, 'UVLOOP')
    except Exception:
        user_uv = True

    if uvloop and user_uv is not False:
        import uvloop
        uvloop.install()

    return settings
