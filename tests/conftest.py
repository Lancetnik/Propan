import asyncio
from unittest.mock import Mock, AsyncMock

import pytest

from propan.utils import context as global_context


@pytest.fixture
def mock():
    return Mock()


@pytest.fixture
def async_mock():
    return AsyncMock()


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
