from .adapter.rabbit_queue import AsyncRabbitQueueAdapter


RabbitBroker = AsyncRabbitQueueAdapter

__all__ = (
    'RabbitBroker',
)
