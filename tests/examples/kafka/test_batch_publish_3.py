import pytest

from examples.kafka.batch_publish_3 import app, handle, handle_response
from propan import TestApp as T


@pytest.mark.asyncio
@pytest.mark.kafka
async def test_example():
    async with T(app):
        await handle.wait_call(3)
        await handle_response.wait_call(3)

    handle.mock.assert_called_with("hi")
    assert set(handle_response.mock.call_args[0][0]) == {"hi", "propan"}
