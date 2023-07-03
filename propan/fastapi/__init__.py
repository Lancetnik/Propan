from propan import __about__ as about

try:
    from propan.fastapi.rabbit import RabbitRouter
except ImportError:
    RabbitRouter = about.INSTALL_RABBIT  # type: ignore

try:
    from propan.fastapi.redis import RedisRouter
except ImportError:
    RedisRouter = about.INSTALL_REDIS  # type: ignore

try:
    from propan.fastapi.kafka import KafkaRouter
except ImportError:
    KafkaRouter = about.INSTALL_KAFKA  # type: ignore

try:
    from propan.fastapi.nats import NatsJSRouter, NatsRouter
except ImportError:
    NatsRouter = NatsJSRouter = about.INSTALL_NATS  # type: ignore

try:
    from propan.fastapi.sqs import SQSRouter
except ImportError:
    SQSRouter = about.INSTALL_SQS  # type: ignore

assert any(
    (RabbitRouter, RedisRouter, KafkaRouter, NatsRouter, SQSRouter)
), about.INSTALL_MESSAGE

__all__ = (
    "RabbitRouter",
    "RedisRouter",
    "KafkaRouter",
    "NatsRouter",
    "SQSRouter",
    "NatsJSRouter",
)
