from unittest.mock import Mock

import pytest

from propan import RabbitBroker
from propan.test import TestRabbitBroker
from propan.test.rabbit import build_message


@pytest.mark.asyncio
async def test_global(mock: Mock):
    async def custom_decode(msg, original):
        mock.decode()
        return await original(msg)

    async def custom_parse(msg, original):
        mock.parse()
        return await original(msg)

    broker = TestRabbitBroker(
        RabbitBroker(
            decode_message=custom_decode,
            parse_message=custom_parse,
        )
    )

    @broker.handle("test")
    async def handler():
        return 1

    msg = build_message("Hi", "test")
    r = await handler(msg, True)
    assert r == 1

    mock.decode.assert_called_once()
    mock.parse.assert_called_once()


@pytest.mark.asyncio
async def test_local(mock: Mock):
    async def custom_decode(msg, original):
        mock.decode()
        return await original(msg)

    async def custom_parse(msg, original):
        mock.parse()
        return await original(msg)

    broker = TestRabbitBroker(RabbitBroker())

    @broker.handle(
        "test",
        decode_message=custom_decode,
        parse_message=custom_parse,
    )
    async def handler():
        return 1

    msg = build_message("Hi", "test")
    r = await handler(msg, True)
    assert r == 1

    mock.decode.assert_called_once()
    mock.parse.assert_called_once()


@pytest.mark.asyncio
async def test_override(mock: Mock):
    async def custom_decode_global(msg, original):  # pragma: no cover
        mock.decode()
        return await original(msg)

    async def custom_parse_global(msg, original):  # pragma: no cover
        mock.parse()
        return await original(msg)

    async def custom_decode(msg, original):
        mock.decode_local()
        return await original(msg)

    async def custom_parse(msg, original):
        mock.parse_local()
        return await original(msg)

    broker = TestRabbitBroker(
        RabbitBroker(
            decode_message=custom_decode_global,
            parse_message=custom_parse_global,
        )
    )

    @broker.handle(
        "test",
        decode_message=custom_decode,
        parse_message=custom_parse,
    )
    async def handler():
        return 1

    msg = build_message("Hi", "test")
    r = await handler(msg, True)
    assert r == 1

    assert not mock.decode.called
    assert not mock.parse.called
    mock.decode_local.assert_called_once()
    mock.parse_local.assert_called_once()
