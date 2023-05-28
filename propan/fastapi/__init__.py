from propan.__about__ import INSTALL_MESSAGE

try:
    from propan.fastapi.rabbit import RabbitRouter
except Exception:
    RabbitRouter = None  # type: ignore

try:
    from propan.fastapi.redis import RedisRouter
except Exception:
    RedisRouter = None  # type: ignore

try:
    from propan.fastapi.kafka import KafkaRouter
except Exception:
    KafkaRouter = None  # type: ignore

try:
    from propan.fastapi.nats import NatsRouter
except Exception:
    NatsRouter = None  # type: ignore

try:
    from propan.fastapi.sqs import SQSRouter
except Exception:
    SQSRouter = None  # type: ignore

assert any(
    (RabbitRouter, RedisRouter, KafkaRouter, NatsRouter, SQSRouter)
), INSTALL_MESSAGE

__all__ = ("RabbitRouter", "RedisRouter", "KafkaRouter", "NatsRouter", "SQSRouter")
