import os
import signal

from propan.cli.supervisors.multiprocess import Multiprocess


def exit(parent_id):  # pragma: no cover
    os.kill(parent_id, signal.SIGINT)


def test_base():
    processor = Multiprocess(target=exit, args=(), workers=5)
    processor._args = (processor.pid,)
    processor.run()

    for p in processor.processes:
        code = abs(p.exitcode)
        assert code == signal.SIGTERM.value or code == 0
