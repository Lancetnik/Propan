from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Tuple, Sequence, Union

from propan.cli.supervisors.basereload import BaseReload
from propan.log import logger
from propan.types import DecoratedCallable

import watchfiles


if TYPE_CHECKING:  # pragma: no cover
    import os

    DirEntry = os.DirEntry[str]


class ExtendedFilter(watchfiles.PythonFilter):
    def __init__(
        self,
        *,
        ignore_paths: Optional[Sequence[Union[str, Path]]] = None,
        extra_extensions: Sequence[str] = (),
    ) -> None:
        super().__init__(ignore_paths=ignore_paths, extra_extensions=extra_extensions)
        self.extensions = self.extensions + ('.env', '.yaml')
        self.ignore_dirs = self.ignore_dirs + ('venv', 'env', '.ruff_cache', 'htmlcov')


class WatchReloader(BaseReload):
    def __init__(
        self,
        target: DecoratedCallable,
        args: Tuple[Any, ...],
        reload_dirs: Sequence[Union[Path, str]],
        reload_delay: Optional[float] = 0.3,
    ) -> None:
        super().__init__(target, args, reload_delay)
        self.reloader_name = "WatchFiles"

        self.watcher = watchfiles.watch(
            *reload_dirs,
            step=int(reload_delay * 1000),
            watch_filter=ExtendedFilter(),
            stop_event=self.should_exit,
            yield_on_timeout=True,
        )


    def should_restart(self) -> bool:
        for changes in self.watcher:
            if changes:
                unique_paths = {Path(c[1]).name for c in changes}
                message = "WatchReloader detected file change in '%s'. Reloading..."
                logger.info(message % tuple(unique_paths))
                return True
        return False
