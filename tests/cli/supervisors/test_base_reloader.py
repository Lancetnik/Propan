import signal

from propan.cli.supervisors.basereload import BaseReload


class PatchedBaseReload(BaseReload):
    def restart(self) -> None:
        super().restart()
        self.should_exit.set()

    def should_restart(self) -> bool:
        return True


def empty():
    pass


def test_base():
    processor = PatchedBaseReload(target=empty, args=())

    processor._args = (processor.pid,)
    processor.run()

    code = abs(processor._process.exitcode)
    assert code == signal.SIGTERM.value or code == 0
