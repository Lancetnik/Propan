from typing import Any

import pytest
from typing_extensions import Annotated

from propan.utils import Context, ContextRepo, apply_types


@pytest.mark.asyncio
async def test_base_context_alias(context: ContextRepo):
    key = 1000
    context.set_global("key", key)

    @apply_types
    async def func(k=Context("key")):
        return k is key

    assert await func()


@pytest.mark.asyncio
async def test_nested_context_alias(context: ContextRepo):
    model = SomeModel(field=SomeModel(field=1000))
    context.set_global("model", model)

    @apply_types
    async def func(
        m=Context("model.field.field"),
        m2=Context("model.not_existed", default=None),
        m3=Context("model.not_existed.not_existed", default=None),
    ):
        return m is model.field.field and m2 is None and m3 is None

    assert await func(model=model)


@pytest.mark.asyncio
async def test_annotated_alias(context: ContextRepo):
    model = SomeModel(field=SomeModel(field=1000))
    context.set_global("model", model)

    @apply_types
    async def func(m: Annotated[int, Context("model.field.field")]):
        return m is model.field.field

    assert await func(model=model)


class SomeModel:
    field: Any = ""

    def __init__(self, field):
        self.field = field
