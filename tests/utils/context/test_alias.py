import asyncio
from typing import Any

import pytest

from propan.brokers import RabbitBroker
from propan.utils.context import Alias, Context, use_context


@pytest.mark.asyncio
async def test_base_kwargs_alias():
    key = 1000

    @use_context
    async def func(*args, k = Alias("key"), **kwargs):
        return k is key
    
    assert await func(key=key)


@pytest.mark.asyncio
async def test_base_nested_kwargs_alias():
    model = SomeModel(field=SomeModel(field=1000))

    @use_context
    async def func(*args, m = Alias("model.field.field"), **kwargs):
        return m is model.field.field
    
    assert await func(model=model)


@pytest.mark.asyncio
async def test_base_context_alias(context: Context, broker: RabbitBroker):
    await broker.connect()
    await broker.init_channel()

    key = 1000
    context.set_context("key", key)

    message = None
    async def consumer(body, k = Alias("key")):
        nonlocal message
        message = body
        message = (k is key)

    broker.handle("test_base_alias")(consumer)

    await broker.start()

    await broker.publish_message(message="hello", queue="test_base_alias")

    tries = 0
    while tries < 20:
        await asyncio.sleep(0.1)
        if message is not None:
            break
        else:
            tries += 1
    
    assert message


@pytest.mark.asyncio
async def test_nested_context_alias(context: Context, broker: RabbitBroker):
    await broker.connect()
    await broker.init_channel()

    model = SomeModel(field=SomeModel(field=1000))
    context.set_context("model", model)

    message = None
    async def consumer(body, m = Alias("model.field.field")):
        nonlocal message
        message = (m is model.field.field)

    broker.handle("test_nested_alias")(consumer)

    await broker.start()

    await broker.publish_message(message="hello", queue="test_nested_alias")

    tries = 0
    while tries < 20:
        await asyncio.sleep(0.1)
        if message is not None:
            break
        else:
            tries += 1
    
    assert message


class SomeModel:
    field: Any = ""

    def __init__(self, field):
        self.field = field
