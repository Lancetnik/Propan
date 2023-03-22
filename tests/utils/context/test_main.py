from propan.utils import use_context


def test_context_getattr(context):
    a = 1000
    context.set_context("key", a)

    assert context.key is a
    assert context.key2 is None


def test_context_apply(context):
    a = 1000
    context.set_context("key", a)

    @use_context
    def use(key):
        assert key is a
    use()


def test_context_ignore(context):
    a = 3
    context.set_context("key", a)

    @use_context
    def use():
        pass
    use()


def test_context_apply_multi(context):
    a = 1001
    context.set_context("key_a", a)

    b = 1000
    context.set_context("key_b", b)

    @use_context
    def use1(key_a):
        assert key_a is a
    use1()

    @use_context
    def use2(key_b):
        assert key_b is b
    use2()

    @use_context
    def use3(key_a, key_b):
        assert key_a is a
        assert key_b is b
    use3()


def test_context_overrides(context):
    a = 1001
    context.set_context("test", a)

    b = 1000
    context.set_context("test", b)

    @use_context
    def use(test):
        assert test is b
    use()
