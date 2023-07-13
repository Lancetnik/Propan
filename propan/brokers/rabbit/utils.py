from typing import Optional, Union, overload

from propan.brokers.rabbit.schemas import RabbitExchange, RabbitQueue


@overload
def validate_exchange(
    exchange: None = None,
) -> None:
    ...


@overload
def validate_exchange(
    exchange: Union[str, RabbitExchange],
) -> RabbitExchange:
    ...


def validate_exchange(
    exchange: Union[str, RabbitExchange, None] = None,
) -> Optional[RabbitExchange]:
    if exchange is not None:  # pragma: no branch
        if isinstance(exchange, str):
            exchange = RabbitExchange(name=exchange)
        elif not isinstance(exchange, RabbitExchange):
            raise ValueError(
                f"Exchange '{exchange}' should be 'str' | 'RabbitExchange' instance"
            )
    return exchange


@overload
def validate_queue(
    queue: None = None,
) -> None:
    ...


@overload
def validate_queue(
    queue: Union[str, RabbitQueue],
) -> RabbitQueue:
    ...


def validate_queue(
    queue: Union[str, RabbitQueue, None] = None
) -> Optional[RabbitQueue]:
    if queue is not None:  # pragma: no branch
        if isinstance(queue, str):
            queue = RabbitQueue(name=queue)
        elif not isinstance(queue, RabbitQueue):
            raise ValueError(
                f"Queue '{queue}' should be 'str' | 'RabbitQueue' instance"
            )
    return queue
