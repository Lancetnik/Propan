import sys
import time
from multiprocessing import Process

import pytest

from propan.cli.main import _run
from propan.cli.utils.imports import get_app_path


@pytest.mark.rabbit
def test_run_correct(project_dir):
    module, app = get_app_path(f'{project_dir / "app" / "serve"}:app')
    sys.path.insert(0, str(module.parent))
    p = Process(target=_run, args=(module, app, {}))
    p.start()
    time.sleep(0.1)
    p.terminate()
    p.join()
