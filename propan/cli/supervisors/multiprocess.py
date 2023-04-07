import os
import threading
from multiprocessing.context import SpawnProcess
from typing import Any, Callable, List, Tuple

from propan.cli.supervisors.basereload import BaseReload
from propan.cli.supervisors.utils import get_subprocess, set_exit
from propan.log import logger


class Multiprocess(BaseReload):
    def __init__(
        self,
        target: Callable[..., Any],
        args: Tuple[Any, ...],
        workers: int
    ) -> None:
        super().__init__(target, args, None)

        self.workers = workers
        self.processes: List[SpawnProcess] = []

    def startup(self) -> None:
        logger.info(f"Started parent process [{self.pid}]")

        for _ in range(self.workers):
            process = self._start_process()
            logger.info(f"Started child process [{process.pid}]")
            self.processes.append(process)

    def shutdown(self) -> None:
        for process in self.processes:
            process.terminate()
            logger.info(f"Stopping child process [{process.pid}]")
            process.join()

        logger.info(f"Stopping parent process [{self.pid}]")
