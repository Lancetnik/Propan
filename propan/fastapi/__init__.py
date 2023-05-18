try:
    from propan.fastapi.rabbit import RabbitRouter
except Exception:
    RabbitRouter = None  # type: ignore

try:
    from propan.fastapi.redis import RedisRouter
except Exception:
    RedisRouter = None  # type: ignore

__all__ = ("RabbitRouter", "RedisRouter")
