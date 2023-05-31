from propan import __about__ as about

try:
    from propan.test.rabbit import TestRabbitBroker
except Exception:
    TestRabbitBroker = about.INSTALL_RABBIT

try:
    from propan.test.redis import TestRedisBroker
except Exception:
    TestRedisBroker = about.INSTALL_REDIS

try:
    from propan.test.kafka import TestKafkaBroker
except Exception:
    TestKafkaBroker = about.INSTALL_KAFKA

try:
    from propan.test.nats import TestNatsBroker
except Exception:
    TestNatsBroker = about.INSTALL_NATS

try:
    from propan.test.sqs import TestSQSBroker
except Exception:
    TestSQSBroker = about.INSTALL_SQS

assert any(
    (TestRabbitBroker, TestRedisBroker, TestKafkaBroker, TestNatsBroker, TestSQSBroker)
), about.INSTALL_MESSAGE

__all__ = (
    "TestRabbitBroker",
    "TestRedisBroker",
    "TestKafkaBroker",
    "TestNatsBroker",
    "TestSQSBroker",
)
