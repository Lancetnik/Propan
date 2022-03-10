import logging
import os
import signal
import threading
from socket import socket
from types import FrameType
from typing import Callable, List, Optional, Tuple

from propan.supervisors.utils import get_subprocess


HANDLED_SIGNALS = (
    signal.SIGINT,  # Unix signal 2. Sent by Ctrl+C.
    signal.SIGTERM,  # Unix signal 15. Sent by `kill <pid>`.
)


class BaseReload:
    def __init__(
        self,
        target: Callable[[Optional[List[socket]]], None],
        args: Tuple,
        reload_delay: Optional[float] = 0.5,
    ) -> None:
        self.target = target
        self.should_exit = threading.Event()
        self.pid = os.getpid()
        self.reloader_name: Optional[str] = None
        self.reload_delay = reload_delay
        self._stopped = False
        self._args = args

    def signal_handler(self, sig: signal.Signals, frame: FrameType) -> None:
        if self._stopped:
            exit()
        self._stopped = True
        self.should_exit.set()

    def run(self) -> None:
        self.startup()
        while not self.should_exit.wait(self.reload_delay):
            if self.should_restart():
                self.restart()

    def startup(self) -> None:
        message = f"Started reloader process [{self.pid}] using {self.reloader_name}"
        print(message)

        for sig in HANDLED_SIGNALS:
            signal.signal(sig, self.signal_handler)
    
        self.process = get_subprocess(
            target=self.target, args=self._args
        )
        self.process.start()

    def restart(self) -> None:
        self.process.terminate()
        self.process.join(timeout=1.0)
        print('Process successfully reloaded')
        self.process = get_subprocess(
            target=self.target, args=self._args
        )
        self.process.start()
        self._stopped = False

    def should_restart(self) -> bool:
        raise NotImplementedError("Reload strategies should override should_restart()")
