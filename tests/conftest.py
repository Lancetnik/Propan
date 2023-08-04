from unittest.mock import AsyncMock, Mock

import pytest

from propan.__about__ import __version__
from propan.utils import context as global_context


def pytest_collection_modifyitems(items):
    for item in items:
        item.add_marker("all")


@pytest.fixture
def mock():
    m = Mock()
    yield m
    m.reset_mock()


@pytest.fixture
def async_mock():
    m = AsyncMock()
    yield m
    m.reset_mock()


@pytest.fixture(scope="session")
def version():
    return __version__


@pytest.fixture
def context():
    yield global_context
    global_context.clear()
