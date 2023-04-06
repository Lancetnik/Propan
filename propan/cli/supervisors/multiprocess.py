import os
import threading
from multiprocessing.context import SpawnProcess
from types import FrameType
from typing import Any, Callable, Iterable, List, Optional

from propan.cli.supervisors.utils import get_subprocess, set_exit
from propan.log import logger


class Multiprocess:
    def __init__(self, target: Callable, args: Iterable[Any], workers: int) -> None:
        self._target = target
        self._args = args

        self.workers = workers
        self.processes: List[SpawnProcess] = []

        self.should_exit = threading.Event()
        self.pid = os.getpid()

    def signal_handler(self, sig: int, frame: Optional[FrameType]) -> None:
        """
        A signal handler that is registered with the parent process.
        """
        self.should_exit.set()

    def run(self) -> None:
        self.startup()
        self.should_exit.wait()
        self.shutdown()

    def startup(self) -> None:
        logger.info(f"Started parent process [{self.pid}]")

        set_exit(self.signal_handler)

        for _ in range(self.workers):
            process = get_subprocess(target=self._target, args=self._args)
            process.start()
            logger.info(f"Started child process [{process.pid}]")
            self.processes.append(process)

    def shutdown(self) -> None:
        for process in self.processes:
            process.terminate()
            logger.info(f"Stopping child process [{process.pid}]")
            process.join()

        logger.info(f"Stopping parent process [{self.pid}]")
