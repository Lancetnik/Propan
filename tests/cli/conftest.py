import pytest
from typer.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()
