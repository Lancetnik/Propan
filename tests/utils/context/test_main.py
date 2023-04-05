import pytest

from propan.utils import use_context, Context


def test_context_getattr(context):
    a = 1000
    context.set_context("key", a)

    assert context.key is a
    assert context.key2 is None


@pytest.mark.asyncio
async def test_context_apply(context):
    a = 1000
    context.set_context("key", a)

    @use_context
    async def use(key):
        return key is a
    assert await use()


@pytest.mark.asyncio
async def test_context_ignore(context):
    a = 3
    context.set_context("key", a)

    @use_context
    async def use():
        pass
    assert await use() is None


@pytest.mark.asyncio
async def test_context_apply_multi(context):
    a = 1001
    context.set_context("key_a", a)

    b = 1000
    context.set_context("key_b", b)

    @use_context
    async def use1(key_a):
        return key_a is a
    assert await use1()

    @use_context
    async def use2(key_b):
        return key_b is b
    assert await use2()

    @use_context
    async def use3(key_a, key_b):
        return key_a is a and key_b is b
    assert await use3()


@pytest.mark.asyncio
async def test_context_overrides(context):
    a = 1001
    context.set_context("test", a)

    b = 1000
    context.set_context("test", b)

    @use_context
    async def use(test):
        return test is b
    assert await use()


@pytest.mark.asyncio
async def test_context_nested_apply(context):
    a = 1000
    context.set_context("key", a)

    @use_context
    def use_nested(key):
        return key

    @use_context
    async def use(key):
        return key is use_nested() is a
    assert await use()


@pytest.mark.asyncio
async def test_remove_context(context: Context):
    a = 1000
    context.set_context("key", a)
    context.remove_context("key")

    @use_context
    async def use(key):
        return key is None
    assert await use()


@pytest.mark.asyncio
async def test_clear_context(context: Context):
    a = 1000
    context.set_context("key", a)
    context.clear()

    @use_context
    async def use(key):
        return key is None
    assert await use()
