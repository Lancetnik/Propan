from propan.__about__ import INSTALL_MESSAGE

try:
    from propan.test.rabbit import TestRabbitBroker
except Exception:
    TestRabbitBroker = None  # type: ignore

try:
    from propan.test.redis import TestRedisBroker
except Exception:
    TestRedisBroker = None  # type: ignore

try:
    from propan.test.kafka import TestKafkaBroker
except Exception:
    TestKafkaBroker = None  # type: ignore

assert any((TestRabbitBroker, TestRedisBroker, TestKafkaBroker)), INSTALL_MESSAGE

__all__ = (
    "TestRabbitBroker",
    "TestRedisBroker",
    "TestKafkaBroker",
)
