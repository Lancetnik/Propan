import pytest
from propan.utils import Context, apply_types
from pydantic.error_wrappers import ValidationError


def test_context_getattr(context):
    a = 1000
    context.set_context("key", a)

    assert context.key is a
    assert context.key2 is None


@pytest.mark.asyncio
async def test_context_apply(context):
    a = 1000
    context.set_context("key", a)

    @apply_types
    async def use(key=Context()):
        return key is a

    assert await use()


@pytest.mark.asyncio
async def test_context_ignore(context):
    a = 3
    context.set_context("key", a)

    @apply_types
    async def use():
        return None

    assert await use() is None


@pytest.mark.asyncio
async def test_context_apply_multi(context):
    a = 1001
    context.set_context("key_a", a)

    b = 1000
    context.set_context("key_b", b)

    @apply_types
    async def use1(key_a=Context()):
        return key_a is a

    assert await use1()

    @apply_types
    async def use2(key_b=Context()):
        return key_b is b

    assert await use2()

    @apply_types
    async def use3(key_a=Context(), key_b=Context()):
        return key_a is a and key_b is b

    assert await use3()


@pytest.mark.asyncio
async def test_context_overrides(context):
    a = 1001
    context.set_context("test", a)

    b = 1000
    context.set_context("test", b)

    @apply_types
    async def use(test=Context()):
        return test is b

    assert await use()


@pytest.mark.asyncio
async def test_context_nested_apply(context):
    a = 1000
    context.set_context("key", a)

    @apply_types
    def use_nested(key=Context()):
        return key

    @apply_types
    async def use(key=Context()):
        return key is use_nested() is a

    assert await use()


@pytest.mark.asyncio
async def test_remove_context(context: Context):
    a = 1000
    context.set_context("key", a)
    context.remove_context("key")

    @apply_types
    async def use(key=Context()):  # pragma: no cover
        return key is None

    with pytest.raises(ValidationError):
        await use()


@pytest.mark.asyncio
async def test_clear_context(context: Context):
    a = 1000
    context.set_context("key", a)
    context.clear()

    @apply_types
    async def use(key=Context(required=False)):
        return key is None

    assert await use()
