from tempfile import TemporaryDirectory

import pytest
from typer.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(scope="module")
def move_dir():
    with TemporaryDirectory() as dir:
        yield dir
