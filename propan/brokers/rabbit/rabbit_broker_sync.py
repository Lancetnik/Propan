from functools import wraps
from threading import Event
from types import TracebackType
from typing import Any, Callable, List, Optional, Sequence, Tuple, Type, Union
from uuid import uuid4

import pika
from fast_depends.dependencies import Depends
from pika import spec
from pika.adapters import blocking_connection
from typing_extensions import TypeAlias

from propan._compat import model_to_dict
from propan.brokers._model.broker_usecase import (
    BrokerSyncUsecase,
    HandlerCallable,
    T_HandlerReturn,
)
from propan.brokers._model.schemas import PropanMessage
from propan.brokers.exceptions import WRONG_PUBLISH_ARGS
from propan.brokers.push_back_watcher import (
    BaseWatcher,
    NotPushBackWatcher,
    WatcherContext,
)
from propan.brokers.rabbit.logging import RabbitLoggingMixin
from propan.brokers.rabbit.schemas import Handler, RabbitExchange, RabbitQueue
from propan.brokers.rabbit.utils import RABBIT_REPLY, validate_exchange, validate_queue
from propan.types import AnyDict, DecodedMessage, SendableMessage
from propan.utils import context

PIKA_RAW_MESSAGE: TypeAlias = Tuple[
    blocking_connection.BlockingChannel,
    spec.Basic.Deliver,
    spec.BasicProperties,
    bytes,
]
PikaMessage: TypeAlias = PropanMessage[PIKA_RAW_MESSAGE]


class RabbitSyncBroker(
    RabbitLoggingMixin,
    BrokerSyncUsecase[
        PIKA_RAW_MESSAGE,
        blocking_connection.BlockingChannel,
    ],
):
    handlers: List[Handler]
    _connection: Optional[blocking_connection.BlockingChannel]
    _channel: Optional[blocking_connection.BlockingChannel]

    def __init__(
        self,
        url=None,
        *,
        log_fmt: Optional[str] = None,
        consumers: Optional[int] = None,
        protocol: str = "amqp",
        protocol_version: str = "0.9.1",
        **kwargs: AnyDict,
    ) -> None:
        super().__init__(
            url,
            log_fmt=log_fmt,
            url_=url or "amqp://guest:guest@localhost:5672/",
            protocol=protocol,
            protocol_version=protocol_version,
            **kwargs,
        )
        self._max_consumers = consumers

        self._channel = None

        self.__max_queue_len = 4
        self.__max_exchange_len = 4
        self._queues = {}
        self._exchanges = {}

    def _connect(self, **kwargs: Any) -> blocking_connection.BlockingConnection:
        connection = pika.BlockingConnection()

        if self._channel is None:
            max_consumers = self._max_consumers
            self._channel = connection.channel()

            if max_consumers:
                c = self._get_log_context(None, RabbitQueue(""), RabbitExchange(""))
                self._log(f"Set max consumers to {max_consumers}", extra=c)
                self._channel.basic_qos(prefetch_count=int(max_consumers))

        return connection

    def close(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exec_tb: Optional[TracebackType] = None,
    ) -> None:
        super().close()
        if self._channel is not None:
            self._channel.stop_consuming()
            self._channel = None

        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def start(self) -> None:
        context.set_local(
            "log_context",
            self._get_log_context(None, RabbitQueue(""), RabbitExchange("")),
        )

        super().start()

        for handler in self.handlers:
            self._init_handler(handler)
            func = handler.callback

            c = self._get_log_context(None, handler.queue, handler.exchange)
            self._log(f"`{func.__name__}` waiting for messages", extra=c)

            self._channel.basic_consume(
                queue=handler.queue.name,
                on_message_callback=func,
            )

        self._channel.start_consuming()

    def handle(
        self,
        queue: Union[str, RabbitQueue],
        exchange: Union[str, RabbitExchange, None] = None,
        *,
        dependencies: Sequence[Depends] = (),
        description: str = "",
        **original_kwargs: Any,
    ) -> Callable[
        [HandlerCallable[T_HandlerReturn]],
        Callable[[Any, bool], T_HandlerReturn],
    ]:
        super().handle()

        queue, exchange = validate_queue(queue), validate_exchange(exchange)

        self._setup_log_context(queue, exchange)

        def wrapper(func):
            func, dependant = self._wrap_handler(
                func,
                queue=queue,
                exchange=exchange,
                extra_dependencies=dependencies,
                **original_kwargs,
            )
            handler = Handler(
                callback=_wrap_pika_msg(func),
                queue=queue,
                exchange=exchange,
                _description=description,
                dependant=dependant,
            )
            self.handlers.append(handler)

            return func

        return wrapper

    def _parse_message(self, message: PIKA_RAW_MESSAGE) -> PikaMessage:
        _, _, header_frame, body = message
        return PropanMessage(
            body=body,
            raw_message=message,
            reply_to=header_frame.reply_to or "",
            content_type=header_frame.content_type or "",
            message_id=header_frame.message_id or str(uuid4()),
            headers=header_frame.headers or {},
        )

    def _process_message(
        self,
        func,
        watcher: Optional[BaseWatcher] = None,
    ):
        if watcher is None:  # pragma: no branch
            watcher = NotPushBackWatcher()

        @wraps(func)
        def wrapper(message):
            channel: blocking_connection.BlockingChannel
            method_frame: spec.Basic.Deliver
            header_frame: spec.BasicProperties
            channel, method_frame, header_frame, _ = message.raw_message

            context = WatcherContext(
                watcher,
                message.message_id,
                on_success=lambda: channel.basic_ack(method_frame.delivery_tag),
                on_error=lambda: channel.basic_nack(
                    method_frame.delivery_tag, requeue=True
                ),
                on_max=lambda: channel.basic_reject(
                    method_frame.delivery_tag, requeue=False
                ),
            )

            with context:
                r = func(message)

                if message.reply_to:
                    self.publish(
                        message=r,
                        routing_key=message.reply_to,
                        correlation_id=header_frame.correlation_id,
                    )

                return r

        return wrapper

    def publish(
        self,
        message: SendableMessage = "",
        queue: Union[RabbitQueue, str] = "",
        exchange: Union[RabbitExchange, str, None] = None,
        *,
        routing_key: str = "",
        mandatory: bool = True,
        immediate: bool = False,
        # callback kwargs
        callback: bool = False,
        callback_timeout: Optional[float] = 30.0,
        raise_timeout: bool = False,
        reply_to: Optional[str] = None,
        # message kwargs
        headers=None,
        content_type: Optional[str] = None,
        content_encoding: Optional[str] = None,
        persist: bool = False,
        priority: Optional[int] = None,
        correlation_id: Optional[str] = None,
        expiration=None,
        message_id: Optional[str] = None,
        timestamp=None,
        type_: Optional[str] = None,
        user_id: Optional[str] = None,
        app_id: Optional[str] = None,
    ) -> DecodedMessage | None:
        if self._channel is None:
            raise ValueError("RabbitBroker channel not started yet")

        queue, exchange = validate_queue(queue), validate_exchange(exchange)

        message, content_type = super()._encode_message(message)

        response_event: Optional[Event] = None
        if callback is True:
            if reply_to is not None:
                raise WRONG_PUBLISH_ARGS

            reply_to = RABBIT_REPLY
            response_event = Event()

            def handle_response(
                channel: blocking_connection.BlockingChannel,
                method_frame: spec.Basic.Deliver,
                header_frame: spec.BasicProperties,
                body: bytes,
            ):
                # TODO: return message
                response_event.set()

            response_consumer_tag = self._channel.basic_consume(
                queue=reply_to,
                on_message_callback=handle_response,
                auto_ack=True,
            )

        self._channel.basic_publish(
            exchange=exchange.name if exchange else "",
            routing_key=routing_key or queue.routing or "",
            body=message,
            mandatory=mandatory,
            properties=pika.BasicProperties(
                content_type=content_type,
                content_encoding=content_encoding,
                priority=priority or 0,
                delivery_mode=(2 if persist else 1),
                headers=headers or {},
                message_id=message_id or str(uuid4()),
                reply_to=reply_to or "",
                user_id=user_id,
                app_id=app_id,
                type=type_,
                timestamp=timestamp,
                expiration=expiration,
                correlation_id=correlation_id or str(uuid4()),
            ),
        )

        if response_event is not None:
            self._channel._process_data_events(callback_timeout)
            response_event.wait()
            self._channel.basic_cancel(response_consumer_tag)

    def _init_handler(self, handler: Handler) -> None:
        self.declare_queue(handler.queue)
        if handler.exchange is not None and handler.exchange.name != "default":
            self.declare_exchange(handler.exchange)
            self._channel.queue_bind(
                queue=handler.queue.name,
                exchange=handler.exchange.name,
                routing_key=handler.queue.routing,
                arguments=handler.queue.bind_arguments,
            )

    def declare_queue(self, queue: RabbitQueue) -> None:
        q = self._queues.get(queue)
        if q is None:
            q = self._channel.queue_declare(
                queue=queue.name,
                **model_to_dict(
                    queue,
                    include={
                        "passive",
                        "durable",
                        "exclusive",
                        "auto_delete",
                        "arguments",
                    },
                ),
            )
            self._queues[queue] = q

    def declare_exchange(self, exchange: RabbitExchange) -> None:
        exch = self._exchanges.get(exchange)

        if exch is None:
            self._channel.exchange_declare(
                exchange=exchange.name,
                exchange_type=exchange.type,
                **model_to_dict(
                    exchange,
                    include={
                        "passive",
                        "durable",
                        "internal",
                        "auto_delete",
                        "arguments",
                    },
                ),
            )
            self._exchanges[exchange] = exch

            current = exchange
            while current.bind_to is not None:
                self._channel.declare_exchange(**model_to_dict(current.bind_to))
                self._channel.exchange_bind(
                    source=current.name,
                    destination=current.bind_to.name,
                    routing_key=current.routing_key,
                    arguments=current.bind_arguments,
                )
                current = current.bind_to

        return exch


def _wrap_pika_msg(func):
    @wraps(func)
    def pika_handler_func_wrapper(
        channel: blocking_connection.BlockingChannel,
        method_frame: spec.Basic.Deliver,
        header_frame: spec.BasicProperties,
        body: bytes,
        reraise_exc: bool = False,
    ):
        return func(
            (channel, method_frame, header_frame, body), reraise_exc=reraise_exc
        )

    return pika_handler_func_wrapper
