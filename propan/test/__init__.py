try:
    from propan.test.rabbit import TestRabbitBroker
except Exception:
    TestRabbitBroker = None  # type: ignore

__all__ = ("TestRabbitBroker",)
