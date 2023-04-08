import asyncio
from unittest.mock import Mock
import sys
if sys.version_info < (3, 8):
    from asyncmock import AsyncMock
else:
    from unittest.mock import AsyncMock

import pytest
from propan.utils import context as global_context
from propan.__about__ import __version__

from tests.tools import marks


@pytest.fixture
def mock():
    return Mock()


@pytest.fixture
def async_mock():
    return AsyncMock()


@pytest.fixture(scope="session")
def version():
    return __version__


@pytest.fixture(scope="session")
def wait_for_mock():
    async def _wait_for_message(mock: Mock, max_tries=20):
        tries = 0
        call_count = mock.call_count
        while tries < max_tries and call_count == mock.call_count:
            await asyncio.sleep(0.1)
            tries += 1

    return _wait_for_message


@pytest.fixture
def context():
    yield global_context
    global_context.clear()
