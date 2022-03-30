from pathlib import Path
import traceback

from loguru import logger

from .lazy import settings
from .configuration import init_settings


SETTINGS_DIR = 'config'

def _check_conf_file(base_dir: Path) -> bool:
    conf_file = base_dir / SETTINGS_DIR / 'config.yml'
    return conf_file.exists()


base_dir = Path.cwd()
if _check_conf_file(base_dir) is False:
    called_from = traceback.StackSummary.extract(traceback.walk_stack(None))[-1]
    base_dir = Path(called_from.filename).parent

    if _check_conf_file(base_dir) is False:
        if 'python' not in str(base_dir):
            logger.error(f"There is not config file in {base_dir / SETTINGS_DIR}")
            exit()

if _check_conf_file(base_dir) is True:
    settings = init_settings(base_dir, settings_dir=SETTINGS_DIR)

__all__ = (
    'settings'
)
