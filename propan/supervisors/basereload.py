import logging
import os
import signal
import threading
from socket import socket
from types import FrameType
from typing import Callable, List, Optional

from propan.supervisors.utils import get_subprocess


class BaseReload:
    def __init__(
        self,
        target: Callable[[Optional[List[socket]]], None],
        reload_delay: Optional[float] = None,
    ) -> None:
        self.target = target
        self.should_exit = threading.Event()
        self.pid = os.getpid()
        self.reloader_name: Optional[str] = None
        self.reload_delay = reload_delay or 0.25

    def signal_handler(self, sig: signal.Signals, frame: FrameType) -> None:
        self.should_exit.set()

    def run(self) -> None:
        self.startup()
        while not self.should_exit.wait(self.reload_delay):
            if self.should_restart():
                self.restart()

            if self.process.exitcode is not None:
                break

        self.shutdown()

    def startup(self) -> None:
        message = f"Started reloader process [{self.pid}] using {self.reloader_name}"
        print(message)

        self.process = get_subprocess(
            target=self.target
        )
        self.process.start()

    def restart(self) -> None:
        self.process.terminate()
        self.process.join(timeout=1.0)
        print('Process successfully reloaded')
        self.process = get_subprocess(
            target=self.target
        )
        self.process.start()

    def shutdown(self) -> None:
        self.process.terminate()
        self.process.join(timeout=1.0)
        message = "Stopping reloader process [{}]".format(str(self.pid))
        print(message)
        exit()

    def should_restart(self) -> bool:
        raise NotImplementedError("Reload strategies should override should_restart()")
