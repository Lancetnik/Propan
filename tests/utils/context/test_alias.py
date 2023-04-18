from typing import Any

import pytest
from propan.utils import Context, apply_types
from typing_extensions import Annotated

from tests.tools.marks import needs_py310


@pytest.mark.asyncio
async def test_base_context_alias(context: Context):
    key = 1000
    context.set_context("key", key)

    @apply_types
    async def func(k=Context("key")):
        return k is key

    assert await func()


@pytest.mark.asyncio
async def test_nested_context_alias(context: Context):
    model = SomeModel(field=SomeModel(field=1000))
    context.set_context("model", model)

    @apply_types
    async def func(
        m=Context("model.field.field"),
        m2=Context("model.not_existed", required=False),
        m3=Context("model.not_existed.not_existed", required=False),
    ):
        return m is model.field.field and m2 is None and m3 is None

    assert await func(model=model)


@needs_py310
@pytest.mark.asyncio
async def test_annotated_alias(context: Context):
    model = SomeModel(field=SomeModel(field=1000))
    context.set_context("model", model)

    @apply_types
    async def func(m: Annotated[int, Context("model.field.field")]):
        return m is model.field.field

    assert await func(model=model)


class SomeModel:
    field: Any = ""

    def __init__(self, field):
        self.field = field
