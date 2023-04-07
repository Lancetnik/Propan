import multiprocessing
import os
import signal
import sys
from multiprocessing.context import SpawnProcess
from pathlib import Path
from types import FrameType
from typing import Any, Callable, List, Optional, Sequence, Tuple, TypeVar, Union

from propan.log import logger

multiprocessing.allow_connection_pickling()
spawn = multiprocessing.get_context("spawn")


HANDLED_SIGNALS = (
    signal.SIGINT,  # Unix signal 2. Sent by Ctrl+C.
    signal.SIGTERM,  # Unix signal 15. Sent by `kill <pid>`.
)


DIR = TypeVar("DIR", bound=Union[Path, str])
DIRS = TypeVar("DIRS", bound=Union[Sequence[DIR], DIR, None])


def set_exit(func: Callable[[int, Optional[FrameType]], Any]) -> None:
    for sig in HANDLED_SIGNALS:
        signal.signal(sig, func)


def get_subprocess(target: Callable[..., None], args: Any) -> SpawnProcess:
    stdin_fileno: Optional[int]
    try:
        stdin_fileno = sys.stdin.fileno()
    except OSError:
        stdin_fileno = None

    return spawn.Process(
        target=subprocess_started,
        args=args,
        kwargs={"t": target, "stdin_fileno": stdin_fileno},
    )


def subprocess_started(
    *args: Any,
    t: Callable[..., None],
    stdin_fileno: Optional[int],
) -> None:
    if stdin_fileno is not None:
        sys.stdin = os.fdopen(stdin_fileno)
    t(*args)


def is_dir(path: Path) -> bool:
    try:
        if not path.is_absolute():
            path = path.resolve()
        return path.is_dir()
    except OSError:
        return False


def _normalize_dirs(dirs: DIRS) -> List[str]:
    if dirs is None:
        return []
    if isinstance(dirs, Sequence):
        return list(set(map(str, dirs)))
    else:
        return [str(dirs)]


def resolve_reload_patterns(
    patterns_list: List[str], directories_list: List[str]
) -> Tuple[List[str], List[Path]]:
    directories: List[Path] = list(set(map(Path, directories_list.copy())))
    patterns: List[str] = patterns_list.copy()

    current_working_directory = Path.cwd()
    for pattern in patterns_list:
        if pattern == ".*":
            continue
        patterns.append(pattern)
        if is_dir(Path(pattern)):
            directories.append(Path(pattern))
        else:
            for match in current_working_directory.glob(pattern):
                if is_dir(match):
                    directories.append(match)

    directories = list(set(directories))
    directories = list(map(Path, directories))
    directories = [x.resolve() for x in directories]
    directories = list(
        {reload_path for reload_path in directories if is_dir(reload_path)}
    )

    children = []
    for j in range(len(directories)):
        for k in range(j + 1, len(directories)):
            if directories[j] in directories[k].parents:
                children.append(directories[k])
            elif directories[k] in directories[j].parents:
                children.append(directories[j])

    directories = list(set(directories).difference(set(children)))

    return list(set(patterns)), directories


class Config:
    def __init__(
        self,
        reload_dirs: DIRS = None,
        reload_includes: DIRS = None,
        reload_excludes: DIRS = None,
    ):
        reload_dirs = _normalize_dirs(reload_dirs)
        reload_includes = _normalize_dirs(reload_includes)
        reload_excludes = _normalize_dirs(reload_excludes)

        self.reload_includes, self.reload_dirs = resolve_reload_patterns(
            reload_includes, reload_dirs
        )

        self.reload_excludes, self.reload_dirs_excludes = resolve_reload_patterns(
            reload_excludes, []
        )

        reload_dirs_tmp = self.reload_dirs.copy()

        for directory in self.reload_dirs_excludes:
            for reload_directory in reload_dirs_tmp:
                if (
                    directory == reload_directory
                    or directory in reload_directory.parents
                ):
                    try:
                        self.reload_dirs.remove(reload_directory)
                    except ValueError:
                        pass

        for pattern in self.reload_excludes:
            if pattern in self.reload_includes:
                self.reload_includes.remove(pattern)
        if not self.reload_dirs:
            if reload_dirs:
                logger.debug(
                    (
                        "Provided reload directories %s did not contain valid "
                        "directories, watching current working directory."
                    ),
                    reload_dirs,
                )
            self.reload_dirs = [Path.cwd() / "app"]

        logger.debug(
            f"Will watch for changes in these directories: {sorted(map(str, self.reload_dirs))}",
        )
