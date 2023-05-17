import sys
import time
from multiprocessing import Process

import pytest

from propan.cli.main import _run
from propan.cli.utils.imports import get_app_path


@pytest.mark.rabbit
@pytest.mark.slow
def test_run_rabbit_correct(rabbit_async_project):
    module, app = get_app_path(f'{rabbit_async_project / "app" / "serve"}:app')
    sys.path.insert(0, str(module.parent))
    p = Process(target=_run, args=(module, app, {}))
    p.start()
    time.sleep(0.1)
    p.terminate()
    p.join()
