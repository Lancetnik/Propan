from typing import Any

import pytest
from propan.utils.context import Alias, Context, use_context

from tests.tools.marks import needs_py310


@pytest.mark.asyncio
async def test_base_kwargs_alias():
    key = 1000

    @use_context
    async def func(*args, k=Alias("key"), **kwargs):
        return k is key

    assert await func(key=key)


@pytest.mark.asyncio
async def test_base_nested_kwargs_alias():
    model = SomeModel(field=SomeModel(field=1000))

    @use_context
    async def func(*args, m=Alias("model.field.field"), **kwargs):
        return m is model.field.field

    assert await func(model=model)


@pytest.mark.asyncio
async def test_base_context_alias(context: Context):
    key = 1000
    context.set_context("key", key)

    @use_context
    async def func(*args, k=Alias("key"), **kwargs):
        return k is key

    assert await func()


@pytest.mark.asyncio
async def test_nested_context_alias(context: Context):
    model = SomeModel(field=SomeModel(field=1000))
    context.set_context("model", model)

    @use_context
    async def func(
        *args,
        m=Alias("model.field.field"),
        m2=Alias("model.not_existed"),
        m3=Alias("model.not_existed.not_existed"),
        **kwargs,
    ):
        return m is model.field.field and m2 is None and m3 is None

    assert await func(model=model)


@needs_py310
@pytest.mark.asyncio
async def test_annotated_alias(context: Context):
    from typing import Annotated

    F = Annotated[int, Alias("model.field.field")]

    model = SomeModel(field=SomeModel(field=1000))
    context.set_context("model", model)

    @use_context
    async def func(*args, m: F, **kwargs):
        return m is model.field.field

    assert await func(model=model)


class SomeModel:
    field: Any = ""

    def __init__(self, field):
        self.field = field
