import os
import signal
import threading
from multiprocessing.context import SpawnProcess
from types import FrameType
from typing import Callable, List, Optional, Iterable, Any

from propan.supervisors.utils import get_subprocess

from propan.logger.model.usecase import LoggerUsecase
from propan.logger.adapter.empty import EmptyLogger


HANDLED_SIGNALS = (
    signal.SIGINT,  # Unix signal 2. Sent by Ctrl+C.
    signal.SIGTERM,  # Unix signal 15. Sent by `kill <pid>`.
)


class Multiprocess:
    def __init__(
        self,
        target: Callable,
        args: Iterable[Any],
        workers: int
    ) -> None:
        self._target = target
        self._args = args

        self.workers = workers
        self.processes: List[SpawnProcess] = []
        
        self.should_exit = threading.Event()
        self.pid = os.getpid()
        self._stopped = False

    def signal_handler(self, sig: int, frame: Optional[FrameType]) -> None:
        """
        A signal handler that is registered with the parent process.
        """
        if self._stopped:
            exit()
        self._stopped = True
        self.should_exit.set()

    def run(self) -> None:
        self.startup()
        self.should_exit.wait()
        self.shutdown()

    def startup(self) -> None:
        print(f"Started parent process [{self.pid}]")

        for sig in HANDLED_SIGNALS:
            signal.signal(sig, self.signal_handler)

        for idx in range(self.workers):
            process = get_subprocess(target=self._target, args=self._args)
            process.start()
            self.processes.append(process)

    def shutdown(self) -> None:
        for process in self.processes:
            process.terminate()
            process.join()

        print(f"Stopping parent process [{self.pid}]")
