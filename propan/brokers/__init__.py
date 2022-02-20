from .adapter.rabbit_queue import AsyncRabbitQueueAdapter


RabbitAdapter = AsyncRabbitQueueAdapter

__all__ = (
    'RabbitAdapter',
)
