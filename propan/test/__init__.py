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

try:
    from propan.test.nats import TestNatsBroker
except Exception:
    TestNatsBroker = None  # type: ignore

try:
    from propan.test.sqs import TestSQSBroker
except Exception:
    TestSQSBroker = None  # type: ignore

assert any(
    (TestRabbitBroker, TestRedisBroker, TestKafkaBroker, TestNatsBroker, TestSQSBroker)
), INSTALL_MESSAGE

__all__ = (
    "TestRabbitBroker",
    "TestRedisBroker",
    "TestKafkaBroker",
    "TestNatsBroker",
    "TestSQSBroker",
)
