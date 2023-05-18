from pathlib import Path
from typing import Union, cast


def touch_dir(dir: Union[Path, str]) -> Path:
    if isinstance(dir, str) is True:
        dir = Path(dir).resolve()

    dir = cast(Path, dir)
    if dir.exists() is False:
        dir.mkdir()
    return dir


def write_file(path: Path, *content: str) -> None:
    path.touch()
    if content:
        path.write_text("\n".join(content))
