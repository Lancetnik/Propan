import os
from pathlib import Path


def get_models_ways(models_way: str) -> tuple[str]:
    dirname = _construct_dir_name(models_way)

    current_filename = __name__.split('.')[-1] + '.py'
    files = os.listdir(path=dirname)

    py_files = list(filter(lambda x: x.endswith('.py'), files))
    if "__init__.py" in py_files:
        py_files.remove('__init__.py')

    models = tuple(f'{models_way}.{file.rstrip(".py")}' for file in py_files)
    return models


def _construct_dir_name(models_way: str) -> Path:
    dirname = Path.cwd()
    for dir in models_way.split('.'):
        dirname = dirname / dir
    return dirname
