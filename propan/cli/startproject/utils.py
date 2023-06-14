from pathlib import Path


def touch_dir(dir: Path) -> Path:
    if not dir.exists():  # pragma: no branch
        dir.mkdir()
    return dir


def write_file(path: Path, *content: str) -> None:
    path.touch()
    if content:
        path.write_text("\n".join(content))
