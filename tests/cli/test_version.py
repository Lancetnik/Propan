import platform

from propan.__about__ import __version__
from propan.cli.main import cli


def test_version(runner):
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout
    assert platform.python_implementation() in result.stdout
    assert platform.python_version() in result.stdout
    assert platform.system() in result.stdout
