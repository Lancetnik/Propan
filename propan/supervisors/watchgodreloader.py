import logging
from pathlib import Path
from socket import socket
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Tuple

from watchgod import DefaultWatcher

from propan.supervisors.basereload import BaseReload
from propan.supervisors.utils import Config


if TYPE_CHECKING:  # pragma: no cover
    import os

    DirEntry = os.DirEntry[str]

config = Config()


class CustomWatcher(DefaultWatcher):
    def __init__(self, root_path: Path):
        default_includes = ["*.py"]
        self.includes = [
            default
            for default in default_includes
            if default not in config.reload_excludes
        ]
        self.includes.extend(config.reload_includes)
        self.includes = list(set(self.includes))

        default_excludes = [".*", ".py[cod]", ".sw.*", "~*"]
        self.excludes = [
            default
            for default in default_excludes
            if default not in config.reload_includes
        ]
        self.excludes.extend(config.reload_excludes)
        self.excludes = list(set(self.excludes))

        self.watched_dirs: Dict[str, bool] = {}
        self.watched_files: Dict[str, bool] = {}
        self.dirs_includes = set(config.reload_dirs)
        self.dirs_excludes = set(config.reload_dirs_excludes)
        self.resolved_root = root_path
        super().__init__(str(root_path))

    def should_watch_dir(self, entry: "DirEntry") -> bool:
        cached_result = self.watched_dirs.get(entry.path)
        if cached_result is not None:
            return cached_result

        entry_path = Path(entry)

        if entry_path in self.dirs_excludes:
            self.watched_dirs[entry.path] = False
            return False

        for exclude_pattern in self.excludes:
            if entry_path.match(exclude_pattern):
                is_watched = False
                if entry_path in self.dirs_includes:
                    is_watched = True

                for directory in self.dirs_includes:
                    if directory in entry_path.parents:
                        is_watched = True

                if is_watched:
                    print(
                        f"WatchGodReload detected a new excluded dir '{entry_path.relative_to(self.resolved_root)}' in '{str(self.resolved_root)}'; "
                        "Adding to exclude list."
                    )
                self.watched_dirs[entry.path] = False
                self.dirs_excludes.add(entry_path)
                return False

        if entry_path in self.dirs_includes:
            self.watched_dirs[entry.path] = True
            return True

        for directory in self.dirs_includes:
            if directory in entry_path.parents:
                self.watched_dirs[entry.path] = True
                return True

        for include_pattern in self.includes:
            if entry_path.match(include_pattern):
                print(
                    f"WatchGodReload detected a new reload dir '{str(entry_path.relative_to(self.resolved_root))}' in '{str(self.resolved_root)}'; "
                    "Adding to watch list."
                )
                self.dirs_includes.add(entry_path)
                self.watched_dirs[entry.path] = True
                return True

        self.watched_dirs[entry.path] = False
        return False


class WatchGodReload(BaseReload):
    def __init__(
        self,
        target: Callable[[Optional[List[socket]]], None],
        args: Tuple,
        reload_delay: Optional[float] = 0.5,
    ) -> None:
        super().__init__(target, args, reload_delay)
        self.reloader_name = "watchgod"
        self.watchers = []
        reload_dirs = []
        for directory in config.reload_dirs:
            if Path.cwd() not in directory.parents:
                reload_dirs.append(directory)
        if Path.cwd() not in reload_dirs:
            reload_dirs.append(Path.cwd())
        for w in reload_dirs:
            self.watchers.append(CustomWatcher(w.resolve()))

    def should_restart(self) -> bool:
        for watcher in self.watchers:
            change = watcher.check()
            if change != set():
                message = "WatchGodReload detected file change in '%s'. Reloading..."
                print(message % [c[1] for c in change])
                return True
        return False
